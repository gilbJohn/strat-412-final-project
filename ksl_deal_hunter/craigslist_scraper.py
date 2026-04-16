"""
craigslist_scraper.py — Craigslist Salt Lake City listing scraper.

Fetches HTML from four Craigslist SLC search pages and extracts listing data
using regex. No JavaScript execution required — Craigslist serves server-rendered
HTML. Playwright is only used for the optional seller email extraction feature.

Search categories and their Craigslist URL codes:
  sya = computers & tech  (PC Parts & Electronics)
  vga = video gaming      (Video Games & Consoles)
  fua = furniture         (Furniture)
  sga = sporting goods    (Sporting Goods)

Each category is capped at a max price to filter out expensive listings.
A 2-second delay between requests keeps us from getting rate-limited.
"""

import re
import time
import urllib.request

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

SEARCH_URLS = [
    {
        "category": "PC Parts & Electronics",
        "url": "https://saltlakecity.craigslist.org/search/sya?max_price=500&sort=date",
    },
    {
        "category": "Video Games & Consoles",
        "url": "https://saltlakecity.craigslist.org/search/vga?max_price=200&sort=date",
    },
    {
        "category": "Furniture",
        "url": "https://saltlakecity.craigslist.org/search/fua?max_price=300&sort=date",
    },
    {
        "category": "Sporting Goods",
        "url": "https://saltlakecity.craigslist.org/search/sga?max_price=300&sort=date",
    },
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

BETWEEN_REQUESTS_SECONDS = 2


def _fetch(url: str) -> str:
    """Fetch the raw HTML for a URL using a browser-like user-agent header."""
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.read().decode("utf-8")


def _scrape_category(category: str, url: str) -> list:
    """
    Scrape a single Craigslist search page and return a list of listing dicts.
    Each dict has keys: title, price, category, url.

    Parses each <li class="cl-static-search-result"> block in one regex pass
    so title, price, and URL are always matched correctly to the same listing.
    """
    html = _fetch(url)

    pattern = re.compile(
        r'<li class="cl-static-search-result"[^>]*>\s*'
        r'<a href="([^"]+)">\s*'
        r'<div class="title">([^<]+)</div>'
        r'.*?<div class="price">([^<]*)</div>',
        re.DOTALL,
    )

    listings = []
    for href, title, price in pattern.findall(html):
        title = title.strip()
        price = price.strip() or "N/A"
        if not title:
            continue
        listings.append(
            {"title": title, "price": price, "category": category, "url": href}
        )

    return listings


def fetch_email_for_listing(url: str) -> str | None:
    """
    Open a Craigslist listing page with a real browser, click Reply,
    and return the seller's relay email address (or None if not found).
    This is intentionally slow — use only for high-value listings.
    """
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(
                headless=True,
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
            )
            context = browser.new_context(
                user_agent=HEADERS["User-Agent"],
                viewport={"width": 1280, "height": 800},
                locale="en-US",
            )
            context.add_init_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )
            page = context.new_page()
            page.goto(url, timeout=20_000)

            # Click the Reply button to reveal contact options
            try:
                page.click("#replylink, .reply-button-row button", timeout=5_000)
                # Wait for the mailto link to appear
                page.wait_for_selector("a[href^='mailto:']", timeout=5_000)
            except PlaywrightTimeout:
                browser.close()
                return None

            # Grab the first mailto: link
            mailto = page.get_attribute("a[href^='mailto:']", "href")
            browser.close()

            if mailto and mailto.startswith("mailto:"):
                return mailto[len("mailto:"):]
            return None
    except Exception:
        return None


def fetch_emails_for_listings(listings: list, min_score: int = 6) -> dict:
    """
    For each listing dict (must have 'url'), fetch the seller email.
    Returns a dict mapping url -> email (or None).
    Prints progress as it goes since this can be slow.
    """
    results = {}
    total = len(listings)
    for i, item in enumerate(listings, 1):
        url = item["url"]
        print(f"    [{i}/{total}] Fetching email for: {item.get('title', url)[:60]}")
        email = fetch_email_for_listing(url)
        results[url] = email
        if email:
            print(f"             -> {email}")
        else:
            print(f"             -> (no email found)")
        time.sleep(1)  # be polite
    return results


def scrape_all() -> list:
    """
    Scrape all configured Craigslist SLC search categories.
    Returns a deduplicated list of dicts with keys: title, price, category, url.
    Deduplication is done by URL — a listing appearing in multiple categories
    is only kept once.
    """
    all_listings = []

    for i, entry in enumerate(SEARCH_URLS):
        category = entry["category"]
        url = entry["url"]
        print(f"    Scraping: {category} ...")

        try:
            found = _scrape_category(category, url)
        except Exception as e:
            print(f"    [error] {category}: {e}")
            found = []

        print(f"    Found {len(found)} listings")
        all_listings.extend(found)

        if i < len(SEARCH_URLS) - 1:
            time.sleep(BETWEEN_REQUESTS_SECONDS)

    # Deduplicate by URL
    seen = set()
    unique = []
    for item in all_listings:
        if item["url"] not in seen:
            seen.add(item["url"])
            unique.append(item)

    return unique
