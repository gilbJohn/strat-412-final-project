"""
scorer.py — Rule-based deal scorer for the Craigslist Deal Hunter.

Assigns each listing a score from 1 to 10 with no external API calls.
Scoring logic:
  - Baseline score of 5 for every listing
  - KEYWORDS_UP:   high-value items add +1 each (e.g. gpu, ps5, bike)
  - KEYWORDS_DOWN: damaged/incomplete items subtract -2 each (e.g. broken, for parts)
  - Price bonus:   free = +3, under $10 = +2, $11-$50 = +1, $51+ = no bonus
  - Final score is clamped to [1, 10]
"""

from database import update_score

# Desirable item keywords — each match adds +1 to the score
KEYWORDS_UP = [
    "rtx", "gpu", "nintendo", "ps5", "xbox", "retro",
    "desk", "weights", "cpu", "ssd", "ram", "keyboard",
    "monitor", "bike", "treadmill", "ps4", "gameboy",
]

# Damage/condition keywords — each match subtracts -2 from the score
KEYWORDS_DOWN = [
    "broken", "for parts", "cracked", "missing",
    "damaged", "not working", "as is", "spares",
]


def score_listing(title: str, price: str, category: str) -> tuple[int, str]:
    """
    Score a single Craigslist listing using keyword and price rules.
    Returns (score, reason) where score is clamped to [1, 10].
    """
    score = 5  # every listing starts at a neutral baseline
    title_lower = title.lower()

    # Apply keyword bonuses
    for kw in KEYWORDS_UP:
        if kw in title_lower:
            score += 1

    # Apply keyword penalties
    for kw in KEYWORDS_DOWN:
        if kw in title_lower:
            score -= 2

    # Apply price bonus — cheap items score higher
    try:
        p = float(price.replace("$", "").replace(",", "").strip())
        if p == 0:
            score += 3   # free items are always exceptional
        elif p <= 10:
            score += 2
        elif p <= 50:
            score += 1
        # over $50 gets no bonus
    except (ValueError, AttributeError):
        pass  # price string was "N/A" or unparseable — no bonus applied

    return max(1, min(10, score)), "Rule-based score."


def score_listings(listings: list) -> int:
    """
    Score a list of listing dicts and write results back to the database.
    Each dict must have keys: title, price, category, url.
    Returns the number of listings scored.
    """
    if not listings:
        return 0

    for item in listings:
        s, reason = score_listing(item["title"], item["price"], item["category"])
        update_score(item["url"], s, reason)

    return len(listings)
