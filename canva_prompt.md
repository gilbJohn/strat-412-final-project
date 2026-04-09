# Canva Presentation Prompt
Use this prompt with Claude + Canva MCP to generate the slide deck.

---

## Prompt

```
Create a 10-slide professional presentation in Canva for a college business analytics class (STRAT 412). The project is called "KSL Deal Hunter." Use a clean, modern design — dark navy or charcoal background with white/light text and one accent color (orange or teal works well). Make it look polished but not over-designed. Here is the full slide-by-slide content:

---

Slide 1 — Title: "KSL Classifieds: Utah's Secondhand Marketplace"
Subtitle label: SITUATION
Body:
- KSL Classifieds is the dominant C2C marketplace in Utah
- Hundreds of new listings posted daily: electronics, furniture, sporting goods, video games
- No built-in deal-scoring, price comparison, or alert system for buyers
- Buyers rely on manual browsing, timing, and personal market knowledge
Visual note: include a simple icon or placeholder for a marketplace screenshot

---

Slide 2 — Title: "Good Deals Disappear in Hours"
Subtitle label: COMPLICATION
Body:
- Underpriced listings sell fast — often within hours of posting
- Monitoring multiple categories multiple times per day is impractical
- Information asymmetry: sellers who misprice create arbitrage opportunities only attentive buyers capture
- There is no scalable manual solution
Visual note: simple left-to-right flow: "Deal Posted → Sells Quickly → Missed by Most Buyers"

---

Slide 3 — Title: "Can Deal-Hunting Be Automated?"
Subtitle label: QUESTION
Body (large centered quote block):
"How can a buyer in the Salt Lake City secondhand market systematically identify underpriced listings on KSL Classifieds before they sell, across multiple product categories, without spending hours manually browsing?"
Visual note: minimal slide — just the question large and centered

---

Slide 4 — Title: "KSL Deal Hunter — Automated Deal Intelligence"
Subtitle label: ANSWER
Body (numbered list):
1. SCRAPE — Pull new listings from KSL across target categories
2. SCORE — Claude AI evaluates each listing (1–10) for deal quality
3. STORE — All data saved to a SQLite database
4. DELIVER — Daily email digest of top-scored deals
Visual note: horizontal four-step pipeline diagram with icons for each step

---

Slide 5 — Title: "Automated Scraping with Python + Playwright"
Subtitle label: METHOD — DATA COLLECTION
Body:
- Playwright headless browser scrapes KSL listing cards (title, price, category, URL, date)
- Covers 4+ categories: Electronics, Video Games, Furniture, Sporting Goods
- New listings deduplicated before storing
- Example: 136 listings scraped → 89 new added to DB
Visual note: code/terminal aesthetic — show a small monospace code block or terminal output

---

Slide 6 — Title: "Claude Scores Every Listing for Deal Quality"
Subtitle label: METHOD — AI SCORING
Body:
- Each listing is sent to the Claude API (title + price)
- Returns a score (1–10) and written reason
- Example: "PS5 listed at $250 — typical resale $350–$400, strong deal → Score: 9"
- Fully automated — no human judgment required
Visual note: show an example scored listing as a card or table row (title | price | score | reason)

---

Slide 7 — Title: "All Data Stored and Queryable in SQLite"
Subtitle label: METHOD — DATA STORAGE
Body:
- SQLite database stores every listing, score, reason, category, and timestamp
- Enables aggregate analysis:
  • Average score by category
  • Top deals of all time
  • Deal velocity over time
- Database grows over time → historical trends become visible
Visual note: small SQL query snippet + a simple result table

---

Slide 8 — Title: "What the Data Shows"
Subtitle label: RESULTS
Body:
- [Placeholder: insert real numbers from deals.db]
- High-scoring deals (8+) cluster in specific categories
- Sample top deal: [real example from database]
Visual note: bar chart — average score by category; or a top-10 deals table. Leave placeholder space.

---

Slide 9 — Title: "Limitations & Caveats"
Subtitle label: ASSUMPTIONS
Body:
- Claude's scoring relies on training knowledge — can be wrong for niche or regional items
- No image analysis — scoring based on title and price only
- KSL's HTML may change, requiring scraper updates
- Database is local; no cloud backup or multi-user access

---

Slide 10 — Title: "Turning Passive Browsing Into Active Intelligence"
Subtitle label: CONCLUSIONS
Body:
- The pipeline automates deal-hunting end-to-end
- Any buyer receives a ranked daily digest with zero manual effort
- Strategic implication: data tools designed for business apply directly to personal finance decisions
- Next steps: expand categories, add image scoring, build a web dashboard
Visual note: show a sample email digest screenshot or mockup as the final visual

---

Design instructions:
- Consistent font: use a sans-serif like Inter, DM Sans, or Poppins
- Slide numbers in bottom corner
- Section label (SITUATION / COMPLICATION / etc.) in small caps above each title as a colored tag
- Keep body text large enough to read from across the room (min 20pt equivalent)
- Use subtle divider lines or spacing to separate content blocks
- Do not overcrowd any slide — less is more
```
