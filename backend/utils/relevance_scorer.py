import json
import re

from utils.india_context import compute_india_boost


def compute_relevance(
    title: str,
    description: str,
    skills: list[str],
    keywords: list[str],
    source_trust: float = 0.5,
    india_mode: bool = True,
) -> tuple[float, list[str]]:
    """
    Score an article's relevance against a user's skill/keyword profile.
    Incorporates source trust score and optional India relevance boost.
    Returns (score, list_of_matched_terms).
    """
    text_lower = f"{title} {description}".lower()
    all_terms = list({t.lower().strip() for t in skills + keywords if t.strip()})
    matched = []
    for term in all_terms:
        pattern = re.compile(r"\b" + re.escape(term) + r"\b", re.IGNORECASE)
        if pattern.search(text_lower):
            matched.append(term)

    if not all_terms:
        return 0.0, []

    skill_score = len(matched) / len(all_terms)
    combined = (skill_score * 0.6) + (source_trust * 0.25)

    if india_mode:
        india_boost, india_terms = compute_india_boost(title, description)
        combined += india_boost * 0.15
        matched.extend(india_terms)

    return round(min(combined, 1.0), 4), matched


def rank_articles(
    articles: list[dict], skills: list[str], keywords: list[str]
) -> list[dict]:
    """Attach relevance_score and matched_skills to each article dict, then sort."""
    for article in articles:
        title = article.get("title", "")
        description = article.get("description", "")
        trust = article.get("source_trust_score", 0.5)
        score, matched = compute_relevance(title, description, skills, keywords, trust)
        article["relevance_score"] = score
        article["matched_skills"] = json.dumps(matched)
    articles.sort(key=lambda a: a["relevance_score"], reverse=True)
    return articles
