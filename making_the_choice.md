# Checkpoint 3: Making the Choice
**STRAT 412 | One-Page Project Proposal**

---

## Project Title
**KSL Deal Hunter — Automated Secondhand Market Intelligence for Salt Lake City**

---

## The Question

How can a buyer in the Salt Lake City secondhand market systematically identify underpriced listings on KSL Classifieds before they sell, across multiple product categories, without spending hours manually browsing?

---

## The Problem (Complication)

KSL Classifieds is the dominant secondhand marketplace in Utah, with hundreds of new listings posted daily across categories like electronics, furniture, sporting goods, and video games. The challenge for a value-conscious buyer is that good deals disappear quickly — often within hours — and manually monitoring multiple categories throughout the day is impractical. There is no built-in deal-scoring or price-comparison feature on KSL; buyers must rely entirely on their own judgment and timing.

This creates an information asymmetry problem: sellers who misprice listings (either from lack of research or urgency to sell) inadvertently create arbitrage opportunities that only highly attentive buyers can capture. The strategic question is whether that attentiveness can be automated and systematized.

---

## The Solution (Answer)

Build an automated pipeline that:
1. **Scrapes** new KSL Classifieds listings daily across target categories
2. **Scores** each listing using an AI model (Claude) that evaluates price relative to typical market value, listing quality, and deal attractiveness
3. **Stores** all listings and scores in a structured SQLite database
4. **Delivers** a daily email digest of only the top-scored deals, ranked by score

This turns a time-intensive manual process into a passive, data-driven alert system.

---

## Type of Analysis

| Layer | Tool | Purpose |
|-------|------|---------|
| Data Collection | **Python** (Playwright web scraper) | Automated daily scraping of KSL listing cards (title, price, category, URL) |
| Data Storage & Querying | **SQL** (SQLite via Python) | Store listings, track which have been scored/emailed, run aggregate queries (avg score by category, top deals, deal velocity) |
| AI Scoring | Python + Claude API | Each listing is scored 1–10 with a written reason; scores reflect deal quality relative to typical resale value |
| Reporting | Python (HTML email digest) | Filtered, ranked daily email of best deals above a minimum score threshold |

The analysis answers both an operational question (which specific listings are deals right now?) and a strategic one (which categories and price ranges yield the most deals over time?).

---

## Data Needed

- **Live listing data** scraped from `classifieds.ksl.com`: title, asking price, category, listing URL, date posted
- **Historical listing data** accumulated in the SQLite database over multiple weeks to enable trend analysis (e.g., average time-to-sell for high-scored listings, score distribution by category)
- **Market reference prices** embedded implicitly in the AI scoring model's training knowledge (e.g., typical resale value of a PS5, a standing desk, a road bike)

No paid data sources are required. All data is collected through automated scraping of publicly available listings.

---

## Why This Project

This project applies all three analytical layers covered in STRAT 412 — Python for automation, SQL for data management and querying, and AI-assisted scoring as a novel analytical tool — to a concrete personal finance use case. The question is realistic, the data is freely available, and the output is immediately useful. It also demonstrates how strategic analysis tools can be applied beyond corporate settings to individual decision-making.
