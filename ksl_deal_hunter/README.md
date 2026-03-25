# KSL Deal Hunter

A CLI tool that scrapes KSL Classifieds, scores listings with Claude AI, stores
everything in a local SQLite database, and emails you an HTML digest of the best
deals.

---

## Setup

### 1. Install dependencies

```bash
pip install playwright anthropic python-dotenv
playwright install chromium
```

### 2. Configure credentials

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

```
ANTHROPIC_API_KEY=sk-ant-...
GMAIL_ADDRESS=you@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
EMAIL_TO=recipient@gmail.com
```

### 3. Get a Gmail App Password

Regular Gmail passwords won't work — Google requires an App Password for
third-party SMTP access.

1. Go to your Google Account → **Security**
2. Enable **2-Step Verification** (required)
3. Search for **App passwords** in the search bar
4. Select app: **Mail** / device: **Other** → name it "KSL Deal Hunter"
5. Copy the 16-character password into your `.env` as `GMAIL_APP_PASSWORD`

---

## Usage

Run everything from inside the `ksl_deal_hunter/` directory:

```bash
cd ksl_deal_hunter
```

| Command | What it does |
|---|---|
| `python main.py` | Full pipeline: scrape → score → email |
| `python main.py --scrape-only` | Scrape & store listings, skip scoring and email |
| `python main.py --score-only` | Score any unscored listings already in DB |
| `python main.py --email-only` | Send digest of top deals already in DB |
| `python main.py --stats` | Print DB statistics (counts, avg scores by category) |
| `python main.py --min-score 8` | Only email listings scored 8 or higher |
| `python main.py --email-only --min-score 9` | Email only exceptional deals |

### Example output

```
[1/3] Scraping KSL Classifieds...
    Scraping: PC Parts & Electronics ...
    Found 32 listings
    Scraping: Video Games & Consoles ...
    Found 28 listings
    Scraping: Furniture ...
    Found 41 listings
    Scraping: Sporting Goods ...
    Found 35 listings
    Scraped 136 listings — 89 new added to DB.
[2/3] Scoring 89 listings with Claude...
    89 listings scored.
[3/3] Sending digest (14 deals, min score 6)...
    Email sent to you@gmail.com

Done.
```

---

## SQL Queries

The database is stored as `deals.db` in the project folder. Query it directly
with the `sqlite3` CLI (`sqlite3 deals.db`) or any DB browser:

```sql
-- Average score and count per category
SELECT category, AVG(score), COUNT(*) FROM listings GROUP BY category;

-- Best recent deals
SELECT * FROM listings WHERE score >= 8 ORDER BY scraped_at DESC LIMIT 20;

-- Deals not yet emailed
SELECT * FROM listings WHERE emailed = 0 AND score >= 6;

-- All-time top 10
SELECT title, price, category, score, reason
FROM listings ORDER BY score DESC LIMIT 10;

-- Delete old low-scoring listings to keep DB tidy
DELETE FROM listings WHERE score < 4 AND scraped_at < date('now', '-30 days');
```

---

## Scheduling

### Mac / Linux (cron)

Run the full pipeline every morning at 7 AM:

```bash
crontab -e
```

Add:
```
0 7 * * * cd /path/to/ksl_deal_hunter && /usr/bin/python3 main.py >> /tmp/ksl_deals.log 2>&1
```

### Windows (Task Scheduler)

1. Open **Task Scheduler** → **Create Basic Task**
2. Trigger: **Daily** at your preferred time
3. Action: **Start a program**
   - Program: `C:\path\to\python.exe`
   - Arguments: `main.py`
   - Start in: `C:\path\to\ksl_deal_hunter\`
4. Finish

---

## Project Structure

```
ksl_deal_hunter/
├── main.py          # CLI entry point; orchestrates the pipeline
├── ksl_scraper.py   # Playwright-based KSL scraper
├── database.py      # All SQLite logic (deals.db)
├── scorer.py        # Claude API scoring
├── emailer.py       # Gmail SMTP digest sender
├── .env.example     # Credential template
└── README.md        # This file
```

---

## Troubleshooting

**No listings scraped** — KSL may have updated their React component class names.
Open `classifieds.ksl.com` in Chrome, right-click a listing card → Inspect, and
find the current CSS class. Update `CARD_SELECTORS` at the top of `ksl_scraper.py`.

**Gmail auth error** — Make sure you're using the App Password (16 chars, spaces
optional), not your regular Google password.

**Claude returns invalid JSON** — The scorer strips markdown fences automatically.
If parsing still fails, check your `ANTHROPIC_API_KEY` and quota.
