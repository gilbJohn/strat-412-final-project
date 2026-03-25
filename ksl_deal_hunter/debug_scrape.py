"""
debug_scrape.py -- Diagnose why the scraper finds 0 listings.

Run from the ksl_deal_hunter/ directory:
    python debug_scrape.py
"""

import time
from playwright.sync_api import sync_playwright

TEST_URL = (
    "https://classifieds.ksl.com/search/"
    "?category=Computers+%26+Software&priceMax=500&sort=newest"
)

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

SELECTORS_TO_TEST = [
    "div.listing-item",
    "li.listing",
    "[class*='ListingItem']",
    "[class*='listing-card']",
    "[class*='Listing']",
    "[class*='listing']",
    "article",
    "ul li",
    "div[class*='Card']",
    "div[class*='card']",
    "div[class*='item']",
    "div[class*='Item']",
    "div[class*='result']",
    "div[class*='Result']",
]

with sync_playwright() as pw:
    browser = pw.chromium.launch(
        headless=True,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-dev-shm-usage",
        ],
    )
    context = browser.new_context(
        user_agent=USER_AGENT,
        viewport={"width": 1280, "height": 800},
        locale="en-US",
        timezone_id="America/Denver",
    )
    context.add_init_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )
    page = context.new_page()

    print(f"Loading: {TEST_URL}")
    page.goto(TEST_URL, timeout=30_000)
    print("Waiting 5s for React hydration...")
    time.sleep(5)

    print(f"Page title: {page.title()}")

    html = page.content()
    with open("page_dump.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"HTML saved to page_dump.html ({len(html):,} bytes)\n")

    print("-- Selector results --")
    for sel in SELECTORS_TO_TEST:
        try:
            elements = page.query_selector_all(sel)
            count = len(elements)
            marker = "  <-- HIT" if count > 0 else ""
            print(f"  {count:>4}  {sel}{marker}")
        except Exception as e:
            print(f"  ERR   {sel}  ({e})")

    print("\n-- Anchors containing '/listing/' --")
    anchors = page.query_selector_all("a[href*='/listing/']")
    print(f"  Total: {len(anchors)}")
    for a in anchors[:3]:
        print(f"  {a.get_attribute('href')}  |  {a.inner_text().strip()[:60]}")

    browser.close()

print("\nDone. Open page_dump.html to inspect the rendered HTML.")
