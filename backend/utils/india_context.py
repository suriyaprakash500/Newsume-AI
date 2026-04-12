"""India-specific relevance boosting for news articles."""

INDIA_SECTORS = {
    "fintech": ["upi", "razorpay", "phonepe", "paytm", "neft", "imps", "npci", "digital payments"],
    "public_infra": ["ondc", "aadhaar", "digilocker", "cowin", "india stack", "digital india"],
    "startup_ecosystem": [
        "indian startup", "bengaluru startup", "hyderabad startup",
        "funding india", "sequoia india", "accel india", "y combinator india",
    ],
    "gcc_hiring": [
        "gcc", "global capability center", "offshore development", "captive center",
        "india engineering hub", "india tech hub",
    ],
}

INDIA_CITIES = {
    "bengaluru": ["bengaluru", "bangalore", "blr"],
    "hyderabad": ["hyderabad", "hyd"],
    "pune": ["pune"],
    "chennai": ["chennai", "madras"],
    "ncr": ["delhi", "gurgaon", "gurugram", "noida", "ncr", "new delhi"],
    "mumbai": ["mumbai", "bombay"],
    "kolkata": ["kolkata", "calcutta"],
}

_INDIA_GENERAL = [
    "india", "indian", "bharat", "niti aayog", "meity",
    "nasscom", "infosys", "tcs", "wipro", "hcl tech",
]


def compute_india_boost(title: str, description: str) -> tuple[float, list[str]]:
    """
    Return a relevance boost (0.0 to 0.3) and matched India terms
    if article mentions Indian context.
    """
    text = f"{title} {description}".lower()
    matched_terms: list[str] = []

    for term in _INDIA_GENERAL:
        if term in text:
            matched_terms.append(term)

    for sector, terms in INDIA_SECTORS.items():
        for term in terms:
            if term in text:
                matched_terms.append(f"{sector}:{term}")

    for city, variants in INDIA_CITIES.items():
        for v in variants:
            if v in text:
                matched_terms.append(f"city:{city}")
                break

    if not matched_terms:
        return 0.0, []

    boost = min(0.3, len(matched_terms) * 0.05)
    return round(boost, 4), matched_terms


def get_city_demand_label(text: str) -> str:
    """Return the Indian city mentioned in the text, if any."""
    text_lower = text.lower()
    for city, variants in INDIA_CITIES.items():
        for v in variants:
            if v in text_lower:
                return city.title()
    return ""
