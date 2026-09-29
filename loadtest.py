#!/usr/bin/env python3
"""Real-browser login timing against AAP gateway (Playwright / Chromium).

Each login uses a fresh browser context (no cookies, no cache), fills the
login form, submits, and waits for the landing page navigation to render.

Emits one JSON line per login to results/<run>.jsonl and pushes it to Loki.
"""
import argparse
import asyncio
import json
import os
import random
import time
import urllib.request

from playwright.async_api import async_playwright

URL = os.environ["AAP_URL"].rstrip("/")
LOKI = os.environ.get("LOKI_URL", "")
LOGIN_PATH = "/api/gateway/v1/login/"
RESULTS_DIR = "/work/results"
SHOTS_DIR = "/work/shots"

USERNAME_SELECTOR = "#pf-login-username-id"
PASSWORD_SELECTOR = "#pf-login-password-id"
SUBMIT_SELECTOR = "button[type=submit]"
LANDING_SELECTOR = "[data-cy=page-navigation]"
ERROR_SELECTOR = ".pf-v5-c-alert.pf-m-danger, .pf-v6-c-alert.pf-m-danger, .pf-v5-c-helper-text__item.pf-m-error, .pf-v6-c-helper-text__item.pf-m-error"
FAILED_FORM_SELECTOR = "form, main"

PHASES = ["first", "steady", "pool-first", "concurrent", "cold"]


def push_loki(labels, records):
    if not LOKI or not records:
        return
    body = {"streams": [{"stream": labels, "values": [[str(int(r["ts"] * 1e9)), json.dumps(r)] for r in records]}]}
    req = urllib.request.Request(f"{LOKI}/loki/api/v1/push", data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=10).read()
    except Exception as e:
        print(f"loki push failed: {e}", flush=True)


def is_login_post(r):
    return LOGIN_PATH in r.url and r.request.method == "POST"


async def post_timing(resp, rec):
    """Browser-side timing of the login POST, relative to the start of the request."""
    # No wait for resp.finished(): the login answers with a redirect, which never
    # reports as finished. responseEnd is recorded only when the browser has it.
    try:
        t = resp.request.timing
    except Exception:
        return
    if t.get("responseStart", -1) >= 0:
        rec["post_ttfb_ms"] = round(t["responseStart"], 1)
        if t.get("requestStart", -1) >= 0:
            rec["post_wait_ms"] = round(t["responseStart"] - t["requestStart"], 1)
    if t.get("responseEnd", -1) >= 0:
        rec["post_response_end_ms"] = round(t["responseEnd"], 1)


async def shot(page, name):
    try:
        await page.screenshot(path=f"{SHOTS_DIR}/{name}.png")
    except Exception:
        pass


async def one_login(browser, user, password, meta, it, slot):
    rec = dict(meta, user=user, iter=it, slot=slot, ts=time.time(), ok=False, outcome="error")
    tag = f"{meta['run']}-r{meta['rep']}-c{meta['cell_seq']}-{meta['scale']}-{meta['toggle']}-{meta['phase']}-{user}-{it}"
    ctx = await browser.new_context(ignore_https_errors=True, viewport={"width": 1440, "height": 900})
    page = await ctx.new_page()
    seen = {}

    def on_response(r):
        # fallback so a received POST response is recorded whatever fails afterwards
        if "ms" not in seen and "t1" in seen and is_login_post(r):
            seen["ms"], seen["status"] = round((time.perf_counter() - seen["t1"]) * 1000, 1), r.status

    page.on("response", on_response)
    try:
        t0 = time.perf_counter()
        await page.goto(URL, wait_until="domcontentloaded", timeout=90000)
        await page.wait_for_selector(USERNAME_SELECTOR, timeout=90000)
        rec["login_page_ms"] = round((time.perf_counter() - t0) * 1000, 1)

        await page.fill(USERNAME_SELECTOR, user)
        await page.fill(PASSWORD_SELECTOR, password)

        t1 = seen["t1"] = time.perf_counter()
        async with page.expect_response(is_login_post, timeout=180000) as resp_info:
            await page.click(SUBMIT_SELECTOR)
        resp = await resp_info.value
        rec["login_post_ms"] = round((time.perf_counter() - t1) * 1000, 1)
        rec["login_status"] = resp.status

        if resp.status >= 400:
            # gateway/proxy rejected the login; the form shows the error inline
            rec["outcome"] = f"http_{resp.status}"
            await post_timing(resp, rec)
            await page.wait_for_timeout(500)
            await shot(page, f"fail-{tag}")
            rec["message"] = (await page.locator(FAILED_FORM_SELECTOR).first.inner_text())[:200].replace("\n", " | ")
            return rec

        landing = page.locator(LANDING_SELECTOR)
        denied = page.locator(ERROR_SELECTOR)
        await landing.or_(denied).first.wait_for(state="visible", timeout=180000)
        rec["submit_to_landing_ms"] = round((time.perf_counter() - t1) * 1000, 1)
        if await landing.count() and await landing.first.is_visible():
            rec["ok"], rec["outcome"] = True, "logged_in"
        else:
            rec["outcome"] = "denied"
            rec["message"] = (await denied.first.inner_text())[:200]
        await post_timing(resp, rec)
    except Exception as e:
        rec["error"] = f"{type(e).__name__}: {str(e)[:300]}"
        await shot(page, f"fail-{tag}")
    finally:
        if "ms" in seen:
            rec.setdefault("login_post_ms", seen["ms"])
            rec.setdefault("login_status", seen["status"])
        if rec["outcome"] == "error" and rec.get("login_status", 0) >= 400:
            rec["outcome"] = f"http_{rec['login_status']}"
        await ctx.close()
    return rec


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--scale", required=True, help="number of team mappers configured")
    ap.add_argument("--toggle", required=True, choices=["off", "on"])
    ap.add_argument("--users", required=True, help="comma separated usernames")
    ap.add_argument("--iterations", type=int, default=30, help="logins per user")
    ap.add_argument("--concurrency", type=int, default=1)
    ap.add_argument("--phase", default="steady", choices=PHASES)
    ap.add_argument("--cell-seq", type=int, default=1, help="position of this cell in the run sequence")
    ap.add_argument("--rep", type=int, default=1, help="repetition of the whole sequence")
    ap.add_argument("--think-min", type=float, default=0.5, help="seconds, lower bound of the pause before each login of a worker")
    ap.add_argument("--think-max", type=float, default=2.0, help="seconds, 0 disables think time")
    ap.add_argument("--think-seed", type=int, default=None, help="default: taken from the clock, recorded either way")
    a = ap.parse_args()
    if a.think_max < a.think_min or a.think_min < 0:
        ap.error("need 0 <= think-min <= think-max")

    users = a.users.split(",")
    seed = a.think_seed if a.think_seed is not None else int(time.time())
    # one reproducible stream per phase invocation
    rng = random.Random(f"{seed}:{a.rep}:{a.cell_seq}:{a.phase}:{a.concurrency}")
    meta = {
        "run": a.run,
        "scale": int(a.scale),
        "toggle": a.toggle,
        "concurrency": a.concurrency,
        "phase": a.phase,
        "cell_seq": a.cell_seq,
        "rep": a.rep,
        "think_seed": seed,
    }
    labels = {k: str(meta[k]) for k in ("run", "scale", "toggle", "concurrency", "phase", "cell_seq", "rep")}
    labels["job"] = "aap-perf"
    os.makedirs(RESULTS_DIR, exist_ok=True)
    os.makedirs(SHOTS_DIR, exist_ok=True)
    out = os.open(f"{RESULTS_DIR}/{a.run}.jsonl", os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
    out_lock = asyncio.Lock()
    password = os.environ["PERF_PASS"]
    loop = asyncio.get_running_loop()

    async def save(rec):
        # one write() per record on an O_APPEND descriptor, serialised across coroutines
        line = (json.dumps(rec) + "\n").encode()
        async with out_lock:
            os.write(out, line)
            os.fsync(out)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        queue = asyncio.Queue()
        for it in range(a.iterations):
            for u in users:
                queue.put_nowait((u, it))

        async def worker(slot):
            done = 0
            while True:
                try:
                    u, it = queue.get_nowait()
                except asyncio.QueueEmpty:
                    return
                think = rng.uniform(a.think_min, a.think_max) if done and a.think_max > 0 else 0.0
                if think:
                    await asyncio.sleep(think)
                rec = await one_login(browser, u, password, dict(meta, think_ms=round(think * 1000)), it, slot)
                done += 1
                await save(rec)
                # off the event loop: a slow push must not stall the other browsers
                await loop.run_in_executor(None, push_loki, dict(labels, user=u), [rec])
                print(
                    f"{a.phase} r{a.rep} c{a.cell_seq} scale={a.scale} toggle={a.toggle} c={a.concurrency} {u} #{it}: {rec['outcome']} "
                    f"post={rec.get('login_post_ms')}ms landing={rec.get('submit_to_landing_ms')}ms {rec.get('error', '')}",
                    flush=True,
                )

        await asyncio.gather(*(worker(s) for s in range(a.concurrency)))
        await browser.close()
    os.close(out)


if __name__ == "__main__":
    asyncio.run(main())
