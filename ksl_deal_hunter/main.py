"""
main.py — CLI entry point for the Craigslist Deal Hunter.

This is the only file you need to run. It orchestrates the full pipeline:
  1. Scrape  — pull fresh listings from Craigslist SLC
  2. Score   — assign each unscored listing a 1-10 deal score
  3. Email   — send an HTML digest of the top deals

Usage:
  python main.py                  # full pipeline: scrape -> score -> email
  python main.py --scrape-only    # scrape & store only (no scoring or email)
  python main.py --score-only     # score unscored listings in DB only
  python main.py --email-only     # send digest of top deals already in DB
  python main.py --stats          # print DB statistics and exit
  python main.py --min-score 8    # override minimum score threshold (default 6)

Requirements:
  - .env file with GMAIL_ADDRESS, GMAIL_APP_PASSWORD, EMAIL_TO
  - pip install playwright python-dotenv
  - playwright install chromium
"""

import argparse
import sys

from dotenv import load_dotenv

import database
import craigslist_scraper
import scorer
import emailer

load_dotenv()


def cmd_scrape():
    """Scrape all Craigslist SLC categories and insert new listings into the DB."""
    print("[1/3] Scraping Craigslist SLC...")
    database.init_db()
    listings = craigslist_scraper.scrape_all()
    # insert_listing returns True for new rows, False for duplicates (URL already exists)
    new = sum(1 for item in listings if database.insert_listing(item))
    print(f"    Scraped {len(listings)} listings — {new} new added to DB.")
    return listings


def cmd_score(label: str = "[?/?]"):
    """Score all listings in the DB that haven't been scored yet (score = 0)."""
    unscored = database.get_unscored()
    count = len(unscored)
    if count == 0:
        print(f"{label} No unscored listings found.")
        return 0
    print(f"{label} Scoring {count} listings...")
    scored = scorer.score_listings(unscored)
    print(f"    {scored} listings scored.")
    return scored


def cmd_email(min_score: int, label: str = "[?/?]"):
    """Send an HTML digest email of the top deals above min_score."""
    deals = database.get_top_deals(min_score=min_score)
    print(f"{label} Sending digest ({len(deals)} deals, min score {min_score})...")
    emailer.send_digest(deals)


def cmd_stats():
    """Print aggregate statistics from the database."""
    database.init_db()
    stats = database.get_stats()
    print("\n--- Craigslist Deal Hunter DB Stats ---")
    print(f"  Total listings : {stats['total']}")
    print(f"  Avg score      : {stats['avg_score']}")
    print("\n  By category:")
    if stats["by_category"]:
        for row in stats["by_category"]:
            print(
                f"    {row['category']:<28} "
                f"{row['total']:>4} listings   avg {row['avg_score']}"
            )
    else:
        print("    (no data yet)")
    print("--------------------------------\n")


def main():
    parser = argparse.ArgumentParser(
        description="Craigslist SLC deal hunter — scrape, score, email."
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--scrape-only", action="store_true",
        help="Scrape and store listings; skip scoring and email"
    )
    group.add_argument(
        "--score-only", action="store_true",
        help="Score unscored listings in DB; skip scrape and email"
    )
    group.add_argument(
        "--email-only", action="store_true",
        help="Send digest of top deals already in DB"
    )
    group.add_argument(
        "--stats", action="store_true",
        help="Print DB statistics and exit"
    )
    parser.add_argument(
        "--min-score", type=int, default=6, metavar="N",
        help="Minimum deal score to include in email (default: 6)"
    )
    args = parser.parse_args()

    database.init_db()

    # ── --stats ────────────────────────────────────────────────────────────────
    if args.stats:
        cmd_stats()
        sys.exit(0)

    # ── --scrape-only ─────────────────────────────────────────────────────────
    if args.scrape_only:
        cmd_scrape()
        sys.exit(0)

    # ── --score-only ─────────────────────────────────────────────────────────
    if args.score_only:
        cmd_score(label="[1/1]")
        sys.exit(0)

    # ── --email-only ─────────────────────────────────────────────────────────
    if args.email_only:
        cmd_email(args.min_score, label="[1/1]")
        sys.exit(0)

    # ── Full pipeline ─────────────────────────────────────────────────────────
    cmd_scrape()
    cmd_score(label="[2/3]")
    cmd_email(args.min_score, label="[3/3]")

    print("\nDone.")


if __name__ == "__main__":
    main()
