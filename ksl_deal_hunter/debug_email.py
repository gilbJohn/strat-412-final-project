"""
debug_email.py — Figure out what selectors/structure Craigslist uses
for the reply/email flow on a real listing page.

Usage:
    python debug_email.py <listing_url>
    python debug_email.py  (uses a hardcoded test URL from the DB)
"""
import sys
import re
import sqlite3
import os
import time
from playwright.sync_api import sync_playwright

DB_PATH = os.path.join(os.path.dirname(__file__), "deals.db")

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

# --- get a URL to test ---
if len(sys.argv) > 1:
    url = sys.argv[1]
else:
    con = sqlite3.connect(DB_PATH)
    row = con.execute("SELECT url FROM listings ORDER BY score DESC LIMIT 1").fetchone()
    con.close()
    if not row:
        print("No listings in DB. Run main.py --scrape-only first, or pass a URL.")
        sys.exit(1)
    url = row[0]

print(f"Testing URL: {url}\n")

with sync_playwright() as pw:
    browser = pw.chromium.launch(
        headless=False,  # visible so you can watch what happens
        args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
    )
    context = browser.new_context(
        user_agent=USER_AGENT,
        viewport={"width": 1280, "height": 900},
        locale="en-US",
    )
    context.add_init_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )
    page = context.new_page()
    page.goto(url, timeout=30_000)
    time.sleep(3)

    # Save initial HTML
    html_before = page.content()
    with open("email_debug_before.html", "w", encoding="utf-8") as f:
        f.write(html_before)
    page.screenshot(path="email_debug_before.png")
    print("Saved: email_debug_before.html / .png")

    # Check for any emails already on the page (before clicking anything)
    email_pattern = re.compile(r'[\w.+-]+@[\w-]+\.[\w.]+')
    emails_found = email_pattern.findall(html_before)
    emails_found = [e for e in emails_found if not e.endswith(('.png', '.js', '.css', '.svg'))]
    print(f"\nEmails visible BEFORE clicking reply: {emails_found[:10]}")

    # Try every plausible selector for a reply button
    reply_selectors = [
        "#replylink",
        "button.reply-button",
        ".reply-button-row button",
        "a.reply-button",
        "[data-role='reply']",
        "button:has-text('Reply')",
        "a:has-text('Reply')",
        ".reply-button",
    ]

    print("\n-- Reply button candidates --")
    clicked = False
    for sel in reply_selectors:
        try:
            els = page.query_selector_all(sel)
            if els:
                print(f"  FOUND ({len(els)}): {sel}")
                if not clicked:
                    els[0].click()
                    clicked = True
                    print(f"  -> Clicked: {sel}")
            else:
                print(f"  none:  {sel}")
        except Exception as e:
            print(f"  ERR:   {sel}  ({e})")

    if clicked:
        time.sleep(3)
        html_after = page.content()
        with open("email_debug_after.html", "w", encoding="utf-8") as f:
            f.write(html_after)
        page.screenshot(path="email_debug_after.png")
        print("\nSaved: email_debug_after.html / .png  (after clicking reply)")

        emails_after = email_pattern.findall(html_after)
        emails_after = [e for e in emails_after if not e.endswith(('.png', '.js', '.css', '.svg'))]
        print(f"\nEmails visible AFTER clicking reply: {emails_after[:10]}")

        # Check for mailto links
        mailto_links = page.query_selector_all("a[href^='mailto:']")
        print(f"\nmailto: links after click: {len(mailto_links)}")
        for a in mailto_links[:5]:
            print(f"  {a.get_attribute('href')}  |  '{a.inner_text().strip()}'")

        # Check all visible buttons/links that appeared
        print("\n-- Buttons/links visible after reply click --")
        for el in page.query_selector_all("button, a[href]")[:30]:
            txt = el.inner_text().strip()[:50]
            href = el.get_attribute("href") or ""
            if txt or "mailto" in href:
                print(f"  [{el.tag_name()}] '{txt}'  href='{href[:80]}'")
    else:
        print("\nNo reply button found. Check email_debug_before.html for page structure.")

    input("\nPress Enter to close browser...")
    browser.close()

print("\nDone.")
