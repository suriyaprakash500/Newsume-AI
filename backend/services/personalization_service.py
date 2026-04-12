from __future__ import annotations

"""Apply user personalization preferences to article ranking."""

VALID_TOPICS = [
    "ai", "machine learning", "deep learning", "frontend", "backend",
    "cloud", "devops", "mobile", "android", "ios", "web", "data science",
    "cybersecurity", "blockchain", "fintech", "database", "api", "microservices",
]

VALID_SENIORITY = ["student", "junior", "mid", "senior", "lead"]


def apply_topic_filter(
    articles: list[dict],
    preferred: list[str],
    blocked: list[str],
) -> list[dict]:
    """Boost preferred topics and filter out blocked ones."""
    if not preferred and not blocked:
        return articles

    preferred_lower = {t.lower() for t in preferred}
    blocked_lower = {t.lower() for t in blocked}
    filtered = []

    for article in articles:
        text = f"{article.get('title', '')} {article.get('description', '')}".lower()

        if any(b in text for b in blocked_lower):
            continue

        if preferred_lower and any(p in text for p in preferred_lower):
            article["relevance_score"] = min(
                article.get("relevance_score", 0) + 0.1, 1.0
            )

        filtered.append(article)

    return filtered


def apply_seniority_filter(articles: list[dict], seniority: str) -> list[dict]:
    """Adjust ranking hints based on seniority level."""
    seniority = seniority.lower() if seniority else "mid"

    beginner_signals = ["tutorial", "beginner", "introduction", "getting started", "101", "basics"]
    advanced_signals = ["architecture", "scale", "distributed", "system design", "advanced", "deep dive"]

    for article in articles:
        text = f"{article.get('title', '')} {article.get('description', '')}".lower()

        if seniority in ("student", "junior"):
            if any(s in text for s in beginner_signals):
                article["relevance_score"] = min(
                    article.get("relevance_score", 0) + 0.05, 1.0
                )
        elif seniority in ("senior", "lead"):
            if any(s in text for s in advanced_signals):
                article["relevance_score"] = min(
                    article.get("relevance_score", 0) + 0.05, 1.0
                )

    return articles
