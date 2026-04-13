"""
general_scorer.py — Enhanced rule-based scoring for craigslist listings.

- Broad category coverage
- Weighted keyword scoring
- Hard price cap exclusion
- Multiple keyword tiers (luxury, underrated, urgency, etc.)
"""

from database import update_score

# 🔼 High-value keywords (strong resale / demand)
KEYWORDS_HIGH = [
    "iphone", "ipad", "macbook", "laptop", "gaming pc", "pc",
    "rtx", "gpu", "ps5", "xbox", "nintendo switch",
    "snap-on", "milwaukee", "dewalt", "tool set",
    "peloton", "treadmill", "weights",
    "camera", "sony", "canon",
    "tv", "oled", "monitor",
]

# 🔼 Medium-value keywords (common flips)
KEYWORDS_MED = [
    "desk", "chair", "dresser", "couch", "table",
    "bike", "mountain bike", "road bike",
    "mini fridge", "microwave", "washer", "dryer",
    "keyboard", "mouse", "headphones",
    "grill", "bbq", "lawn mower",
]

# 💎 Luxury / premium brands (often underpriced = big upside)
KEYWORDS_LUXURY = [
    "herman miller", "steelcase", "rolex", "omega",
    "patagonia", "arcteryx", "arc'teryx",
    "yeti", "dyson", "vitra",
]

# 🔥 Underrated deal signals (people trying to get rid of stuff fast)
KEYWORDS_UNDERRATED = [
    "moving", "must go", "need gone", "today only",
    "first come", "pickup today", "cash only",
    "obo", "or best offer",
]

# ⚡ Urgency / distress selling
KEYWORDS_URGENCY = [
    "urgent", "leaving town", "out of state",
    "everything must go", "estate sale",
]

# 📦 Bundle / value signals
KEYWORDS_BUNDLE = [
    "bundle", "lot", "set", "pair",
    "multiple", "collection", "included",
]

# 🌦️ Seasonal opportunities (can flip depending on timing)
KEYWORDS_SEASONAL = [
    "snowboard", "skis", "heater", "ac unit",
    "fan", "patio", "outdoor furniture",
]

# 🏷️ Strong general brands (resellable across categories)
KEYWORDS_BRANDS = [
    "apple", "samsung", "bosch", "lg", "whirlpool",
    "nike", "adidas", "north face",
]

# 🔽 Negative keywords (avoid)
KEYWORDS_NEGATIVE = [
    "broken", "for parts", "cracked", "missing",
    "damaged", "not working", "as is", "spares",
    "read description", "no power", "needs repair",
]


def parse_price(price: str) -> float:
    try:
        return float(price.replace("$", "").replace(",", "").strip())
    except (ValueError, AttributeError):
        return -1  # unknown price


def score_listing(title: str, price: str, category: str) -> tuple[int, str]:
    """
    Returns (score, reason)
    Score range: 0–10
    """
    title_lower = title.lower()
    p = parse_price(price)

    # 🚫 HARD FILTER: exclude expensive listings
    if p > 1000:
        return 0, "Excluded: price above $1000"

    score = 5  # baseline

    # 🔼 High-value matches (+2 each)
    for kw in KEYWORDS_HIGH:
        if kw in title_lower:
            score += 2

    # 🔼 Medium matches (+1 each)
    for kw in KEYWORDS_MED:
        if kw in title_lower:
            score += 1

    # 💎 Luxury boost (+3 each)
    for kw in KEYWORDS_LUXURY:
        if kw in title_lower:
            score += 3

    # 🔥 Underrated signals (+2 each)
    for kw in KEYWORDS_UNDERRATED:
        if kw in title_lower:
            score += 2

    # ⚡ Urgency (+2 each)
    for kw in KEYWORDS_URGENCY:
        if kw in title_lower:
            score += 2

    # 📦 Bundles (+1 each)
    for kw in KEYWORDS_BUNDLE:
        if kw in title_lower:
            score += 1

    # 🌦️ Seasonal (+1 each)
    for kw in KEYWORDS_SEASONAL:
        if kw in title_lower:
            score += 1

    # 🏷️ Brands (+1 each)
    for kw in KEYWORDS_BRANDS:
        if kw in title_lower:
            score += 1

    # 🔽 Negative matches (-3 each)
    for kw in KEYWORDS_NEGATIVE:
        if kw in title_lower:
            score -= 3

    # 💰 Price scoring (deal quality)
    if p == 0:
        score += 4
    elif 0 < p <= 20:
        score += 3
    elif p <= 50:
        score += 2
    elif p <= 150:
        score += 1
    elif p == -1:
        score -= 1  # unknown price penalty

    # 📦 Category bonus
    category = (category or "").lower()
    if any(c in category for c in ["electronics", "furniture", "tools", "appliances"]):
        score += 1

    # Clamp score
    score = max(0, min(10, score))

    return score, "Enhanced multi-category scoring"


def score_listings(listings: list) -> int:
    if not listings:
        return 0

    for item in listings:
        s, reason = score_listing(
            item["title"],
            item["price"],
            item.get("category", "Unknown")
        )
        update_score(item["url"], s, reason)

    return len(listings)
