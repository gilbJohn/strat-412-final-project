# Presentation Outline — KSL Deal Hunter
**STRAT 412 | Checkpoint 4**

---

## Slide 1 — Company / Context Background *(Situation)*

**Title:** KSL Classifieds: Utah's Secondhand Marketplace

**Content:**
- KSL Classifieds is the dominant C2C marketplace in Utah (larger than Craigslist in the region)
- Hundreds of new listings posted daily across categories: electronics, furniture, sporting goods, video games
- No built-in deal-scoring, price comparison, or alert system for buyers
- Buyers rely entirely on manual browsing, timing, and personal market knowledge

**Visuals:** Screenshot of KSL Classifieds homepage / category page

---

## Slide 2 — Managerial Problem *(Complication)*

**Title:** Good Deals Disappear in Hours — Manual Monitoring Is Impractical

**Content:**
- Underpriced listings sell fast (often within hours of posting)
- A value-conscious buyer would need to check multiple categories multiple times per day to consistently find deals
- Information asymmetry: sellers who misprice listings create arbitrage opportunities, but only highly attentive buyers capture them
- There is no scalable manual solution to this problem

**Visuals:** Conceptual diagram — "deal posted → sells quickly → missed by most buyers"

---

## Slide 3 — The Question *(Question)*

**Title:** Can deal-hunting be automated and systematized?

**Content:**
> How can a buyer in the Salt Lake City secondhand market systematically identify underpriced listings on KSL Classifieds before they sell, across multiple product categories, without spending hours manually browsing?

**Visuals:** Clean text slide — just the question, large

---

## Slide 4 — The Solution *(Answer)*

**Title:** KSL Deal Hunter — An Automated Deal Intelligence Pipeline

**Content:**
The system runs four steps automatically every day:
1. **Scrape** — Pull new listings from KSL across target categories
2. **Score** — Claude AI evaluates each listing (1–10) for deal quality vs. typical market value
3. **Store** — All listings and scores saved to a SQLite database
4. **Deliver** — Daily email digest of top-scored deals, ranked by score

**Visuals:** Simple four-step pipeline diagram (Scrape → Score → Store → Deliver)

---

## Slide 5 — Method: Data Collection *(Python / Web Scraping)*

**Title:** Automated Scraping with Python + Playwright

**Content:**
- Playwright headless browser scrapes KSL listing cards (title, price, category, URL, date posted)
- Runs across 4+ categories: PC Parts & Electronics, Video Games & Consoles, Furniture, Sporting Goods
- New listings are deduplicated against the database before storing
- Example run: 136 listings scraped → 89 new added to DB

**Visuals:** Code snippet showing scraper / terminal output from a real run

---

## Slide 6 — Method: AI Scoring *(Claude API)*

**Title:** Claude Scores Every Listing for Deal Quality

**Content:**
- Each listing title + price is sent to Claude via the Anthropic API
- Claude returns a score (1–10) and a written reason (e.g., "PS5 listed at $250 — typical resale is $350–$400, strong deal")
- Scores reflect: price vs. typical resale value, listing completeness, deal attractiveness
- No human judgment required — fully automated

**Visuals:** Example scored listing (title, price, score, reason) from real database output

---

## Slide 7 — Method: Data Storage & SQL Queries *(SQLite)*

**Title:** All Data Stored and Queryable in SQLite

**Content:**
- SQLite database (`deals.db`) stores every listing, score, reason, category, and timestamp
- Enables aggregate queries across the full dataset:
  - Average score by category
  - Top deals of all time
  - Deal velocity (how quickly high-scored listings appear)
- Database grows over time → historical trend analysis becomes possible

**Visuals:** SQL query + result table (e.g., avg score by category)

---

## Slide 8 — Results: What the Data Shows

**Title:** Findings from Running the Pipeline

**Content:**
- [Insert real numbers from your deals.db — e.g., X listings scored, category with highest avg score, example top-10 deals]
- High-scoring deals (8+) cluster in: [top categories from your data]
- Average score across all listings: [X]
- Sample top deal: [real example from DB]

**Visuals:** Table or bar chart — average score by category; sample top-deals list

---

## Slide 9 — Limitations & Caveats

**Title:** What This System Does Not Do (Yet)

**Content:**
- Claude's scoring relies on training-data knowledge of typical prices — it can be wrong for niche or regional items
- No image analysis — listing quality based on title/price only
- KSL's HTML structure may change, requiring scraper updates
- Database is local; no cloud backup or multi-user access

---

## Slide 10 — Recommendations / Conclusions *(Answer)*

**Title:** Turning Passive Browsing Into Active Intelligence

**Content:**
- The system successfully automates the deal-hunting workflow end-to-end
- Any buyer can now receive a ranked daily digest without manual effort
- Strategic implication: data tools originally designed for corporate analysis apply directly to individual financial decisions
- Next steps: expand categories, add image scoring, build a simple web dashboard

**Visuals:** Final email digest screenshot — what the user actually receives each morning

---

## Presentation Notes

- **Target time:** ~6 minutes (roughly 30–45 seconds per slide)
- **Live demo option:** Run `python main.py --stats` live or show a pre-recorded terminal clip
- **Key proof points to hit:** real scraper output, real scored listings from DB, real email digest
