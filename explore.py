#!/usr/bin/env python3
"""One-off UI exploration: find the toggle in Access Management pages."""
import os
import re
import sys

from playwright.sync_api import sync_playwright

URL = os.environ["AAP_URL"].rstrip("/")
AUTH_ID = sys.argv[1] if len(sys.argv) > 1 else "3"
OUT = "/work/shots"
PATTERN = re.compile(r"revoke|non-?\s?matching|block|does not match|do not match", re.I)

TOGGLES_JS = """els => els.map(e => [e.id, e.name, e.getAttribute('data-cy'), e.checked,
  (e.closest('.pf-v5-c-form__group,.pf-v6-c-form__group,label')||e.parentElement).innerText.slice(0,400)])"""


def dump(page, name):
    page.wait_for_timeout(2500)
    page.screenshot(path=f"{OUT}/{name}.png", full_page=True)
    text = page.inner_text("body")
    open(f"{OUT}/{name}.txt", "w").write(f"URL: {page.url}\n\n{text}")
    print(f"\n=== {name}: {page.url}")
    for m in PATTERN.finditer(text):
        s, e = max(0, m.start() - 150), min(len(text), m.end() + 250)
        print("  MATCH:", repr(text[s:e]))
    toggles = page.eval_on_selector_all("input[type=checkbox], input[type=radio]", TOGGLES_JS)
    if toggles:
        print("  toggles:", toggles)
    return text


with sync_playwright() as p:
    browser = p.chromium.launch()
    ctx = browser.new_context(ignore_https_errors=True, viewport={"width": 1600, "height": 1400})
    page = ctx.new_page()
    api_calls = []
    page.on("request", lambda r: api_calls.append(f"{r.method} {r.url}") if "/api/" in r.url and r.method != "GET" else None)

    page.goto(URL, wait_until="networkidle")
    page.fill("#pf-login-username-id", os.environ["AAP_USER"])
    page.fill("#pf-login-password-id", os.environ["AAP_PASS"])
    page.click("button[type=submit]")
    page.wait_for_url(re.compile(r".*/overview.*"), timeout=60000)

    text = dump(page, "10-overview")
    print("  access nav:", page.eval_on_selector_all("[data-cy^='access'], [data-cy*='authenticat'], [data-cy*='users'], [data-cy*='settings']", "els => els.map(e => [e.getAttribute('data-cy'), e.getAttribute('href'), e.innerText.slice(0,40)])"))

    dump(page.goto(f"{URL}/access/authenticators/{AUTH_ID}/details", wait_until="networkidle") and page, "11-auth-details")
    print("  tabs/links:", page.eval_on_selector_all("a[href*='/access/authenticators/'], [role=tab]", "els => els.map(e => [e.getAttribute('href'), e.innerText.slice(0,40)])"))

    for sub in ("mapping", "mappings", "maps"):
        page.goto(f"{URL}/access/authenticators/{AUTH_ID}/{sub}", wait_until="networkidle")
        t = dump(page, f"12-auth-{sub}")
        if "perf-allow" in t or "perf-map" in t:
            print("  mapping links:", page.eval_on_selector_all("a[href*='map']", "els => els.map(e => [e.getAttribute('href'), e.innerText.slice(0,40)])"))
            print("  buttons:", page.eval_on_selector_all("button", "els => els.map(e => [e.getAttribute('data-cy'), e.innerText.slice(0,40)]).filter(x => x[0] || x[1])"))
            break

    # Edit wizard: step through every page
    page.goto(f"{URL}/access/authenticators/{AUTH_ID}/edit", wait_until="networkidle")
    dump(page, "13-edit-step0")
    for step in range(1, 5):
        nxt = page.locator("button:has-text('Next'):not([disabled])")
        if not nxt.count():
            break
        nxt.first.click()
        dump(page, f"13-edit-step{step}")
        # expand any collapsed mapping cards
        for b in page.locator("button[aria-expanded=false]").all()[:3]:
            try:
                b.click(timeout=2000)
            except Exception:
                pass
        dump(page, f"13-edit-step{step}-expanded")

    # Users list + edit form
    page.goto(f"{URL}/access/users", wait_until="networkidle")
    dump(page, "14-users")
    links = page.eval_on_selector_all("a[href*='/access/users/']", "els => els.map(e => [e.getAttribute('href'), e.innerText.slice(0,40)])")
    print("  user links:", links)
    perf = [l for l in links if l[1].startswith("perf-")]
    if perf:
        uid = re.search(r"/users/(\d+)", perf[0][0]).group(1)
        page.goto(f"{URL}/access/users/{uid}/details", wait_until="networkidle")
        dump(page, "15-user-details")
        page.goto(f"{URL}/access/users/{uid}/edit", wait_until="networkidle")
        dump(page, "16-user-edit")

    # Platform settings pages that might host it
    for path in ("settings/gateway", "settings/platform-gateway", "settings/user-preferences", "settings/system"):
        page.goto(f"{URL}/{path}", wait_until="networkidle")
        dump(page, "17-" + path.replace("/", "-"))

    print("\nnon-GET api calls seen:", api_calls)
    browser.close()
