"""
scorer.py — Rule-based scoring for KSL Classifieds listings.

No external API calls required. Each listing is scored 1-10 based on
keyword matching and price thresholds.
"""

from database import update_score

# Keywords that suggest a desirable item — each adds +1 to score
KEYWORDS_UP = [
    "rtx", "gpu", "nintendo", "ps5", "xbox", "retro",
    "desk", "weights", "cpu", "ssd", "ram", "keyboard",
    "monitor", "bike", "treadmill", "ps4", "gameboy",
]

# Keywords that suggest a damaged or incomplete item — each subtracts 2
KEYWORDS_DOWN = [
    "broken", "for parts", "cracked", "missing",
    "damaged", "not working", "as is", "spares",
]


def score_listing(title: str, price: str, category: str) -> tuple[int, str]:
    """
    Score a single listing using keyword and price rules.
    Returns (score, reason) where score is clamped to [1, 10].
    """
    score = 5  # baseline
    title_lower = title.lower()

    for kw in KEYWORDS_UP:
        if kw in title_lower:
            score += 1

    for kw in KEYWORDS_DOWN:
        if kw in title_lower:
            score -= 2

    # Price bonus — target range is $0–$50
    try:
        p = float(price.replace("$", "").replace(",", "").strip())
        if p == 0:
            score += 3   # free is always exceptional
        elif p <= 10:
            score += 2
        elif p <= 50:
            score += 1
        # $50+ gets no bonus
    except (ValueError, AttributeError):
        pass

    return max(1, min(10, score)), "Rule-based score."


def score_listings(listings: list) -> int:
    """
    Score a list of listing dicts and write results to the DB.
    Each dict must have: title, price, category, url.
    Returns the number of listings scored.
    """
    if not listings:
        return 0

    for item in listings:
        s, reason = score_listing(item["title"], item["price"], item["category"])
        update_score(item["url"], s, reason)

    return len(listings)
