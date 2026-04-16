"""
database.py — All SQLite logic for the Craigslist Deal Hunter.

Creates and manages deals.db (SQLite file) in the same directory as this script.
The database is created automatically on first run — no setup required.

Table: listings
  Stores every scraped listing with its title, price, category, URL, score,
  and whether it has been emailed. The url column has a UNIQUE constraint so
  duplicate listings are silently ignored on insert.

  Added for analysis: human_score (INTEGER) — binary 1/0 scored manually.
  Add this column once with:
    ALTER TABLE listings ADD COLUMN human_score INTEGER;
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "deals.db")


def _connect():
    """Return a new SQLite connection to deals.db."""
    return sqlite3.connect(DB_PATH)


def init_db():
    """Create the database and listings table if they don't exist yet.
    Also migrates older databases that are missing the seller_email column."""
    with _connect() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS listings (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                title        TEXT NOT NULL,
                price        TEXT,
                category     TEXT,
                url          TEXT UNIQUE,
                score        INTEGER DEFAULT 0,
                reason       TEXT,
                scraped_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                emailed      INTEGER DEFAULT 0,
                seller_email TEXT
            )
        """)
        # Migrate existing DBs that don't have the seller_email column yet
        cols = [r[1] for r in con.execute("PRAGMA table_info(listings)").fetchall()]
        if "seller_email" not in cols:
            con.execute("ALTER TABLE listings ADD COLUMN seller_email TEXT")
        con.commit()


def insert_listing(listing: dict) -> bool:
    """
    Insert a listing dict into the database.
    Uses INSERT OR IGNORE so duplicate URLs are silently skipped.
    Returns True if a new row was inserted, False if it was a duplicate.
    Expected keys: title, price, category, url.
    """
    with _connect() as con:
        cur = con.execute(
            """
            INSERT OR IGNORE INTO listings (title, price, category, url)
            VALUES (:title, :price, :category, :url)
            """,
            listing,
        )
        con.commit()
        return cur.rowcount > 0


def update_email(url: str, email: str):
    """Store the seller's contact email for a listing."""
    with _connect() as con:
        con.execute(
            "UPDATE listings SET seller_email = ? WHERE url = ?",
            (email, url),
        )
        con.commit()


def get_listings_without_email(min_score: int = 6, limit: int = 10) -> list:
    """Return up to `limit` scored listings above min_score that don't have an email yet."""
    with _connect() as con:
        con.row_factory = sqlite3.Row
        rows = con.execute(
            """
            SELECT * FROM listings
            WHERE score >= ? AND (seller_email IS NULL OR seller_email = '')
            ORDER BY score DESC
            LIMIT ?
            """,
            (min_score, limit),
        ).fetchall()
    return [dict(r) for r in rows]


def update_score(url: str, score: int, reason: str):
    """Update the score and reason for a listing by URL."""
    with _connect() as con:
        con.execute(
            "UPDATE listings SET score = ?, reason = ? WHERE url = ?",
            (score, reason, url),
        )
        con.commit()


def get_unscored() -> list:
    """Return all listings that have not been scored yet (score = 0)."""
    with _connect() as con:
        con.row_factory = sqlite3.Row
        rows = con.execute(
            "SELECT * FROM listings WHERE score = 0"
        ).fetchall()
    return [dict(r) for r in rows]


def get_top_deals(min_score: int = 6) -> list:
    """Return un-emailed listings at or above min_score, best first."""
    with _connect() as con:
        con.row_factory = sqlite3.Row
        rows = con.execute(
            """
            SELECT * FROM listings
            WHERE score >= ? AND emailed = 0
            ORDER BY score DESC
            """,
            (min_score,),
        ).fetchall()
    return [dict(r) for r in rows]


def mark_emailed(urls: list):
    """Mark a list of URLs as emailed."""
    if not urls:
        return
    with _connect() as con:
        con.executemany(
            "UPDATE listings SET emailed = 1 WHERE url = ?",
            [(u,) for u in urls],
        )
        con.commit()


def get_stats() -> dict:
    """Return aggregate stats for CLI display."""
    with _connect() as con:
        con.row_factory = sqlite3.Row

        total = con.execute("SELECT COUNT(*) AS n FROM listings").fetchone()["n"]
        avg_score = con.execute(
            "SELECT ROUND(AVG(score), 2) AS a FROM listings WHERE score > 0"
        ).fetchone()["a"]

        rows = con.execute(
            """
            SELECT category,
                   COUNT(*)             AS total,
                   ROUND(AVG(score), 1) AS avg_score
            FROM listings
            GROUP BY category
            ORDER BY total DESC
            """
        ).fetchall()

    return {
        "total": total,
        "avg_score": avg_score or 0.0,
        "by_category": [dict(r) for r in rows],
    }
