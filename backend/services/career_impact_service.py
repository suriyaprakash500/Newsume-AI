from __future__ import annotations

import hashlib
import logging
from utils.llm_client import generate_json, validate_keys

logger = logging.getLogger(__name__)

_impact_cache: dict[str, dict] = {}

_BATCH_IMPACT_PROMPT = """You are a career advisor for tech professionals. For each article below, generate a brief career impact card.

Return ONLY valid JSON — a list of objects in the SAME order as articles:
[
  {{
    "why_it_matters": "1-2 sentence career relevance",
    "who_should_care": "target audience",
    "action_next": "one concrete next step"
  }},
  ...
]

User skills: {skills}
User keywords: {keywords}

Articles:
{articles_block}
"""

_DIGEST_PROMPT = """You are a tech career advisor. Summarize these articles into a daily 2-minute career digest.

Return ONLY valid JSON:
{{
  "bullets": ["bullet1", "bullet2", "bullet3", "bullet4", "bullet5"],
  "recommended_action": "one specific action the user should take today"
}}

User skills: {skills}

Articles:
{articles_text}
"""

_IMPACT_KEYS = {"why_it_matters": str, "who_should_care": str, "action_next": str}
_DIGEST_KEYS = {"bullets": list, "recommended_action": str}


def _article_hash(title: str) -> str:
    return hashlib.md5(title.strip().lower().encode()).hexdigest()


async def generate_career_impacts_batch(
    articles: list[dict],
    skills: list[str],
    keywords: list[str],
    max_batch: int = 5,
) -> list[dict]:
    """Generate career impact cards for multiple articles in one LLM call."""
    to_process = []
    results: dict[int, dict] = {}

    for i, article in enumerate(articles[:max_batch]):
        h = _article_hash(article.get("title", ""))
        if h in _impact_cache:
            results[i] = _impact_cache[h]
        else:
            to_process.append((i, article, h))

    if to_process:
        articles_block = "\n".join(
            f"{idx + 1}. Title: {a.get('title', '')}\n   Description: {a.get('description', '')[:200]}"
            for idx, (_, a, _) in enumerate(to_process)
        )

        prompt = _BATCH_IMPACT_PROMPT.format(
            skills=", ".join(skills[:15]),
            keywords=", ".join(keywords[:10]),
            articles_block=articles_block,
        )

        raw = await generate_json(prompt)

        if isinstance(raw, list):
            for j, (orig_idx, article, h) in enumerate(to_process):
                if j < len(raw) and isinstance(raw[j], dict):
                    validated = validate_keys(raw[j], _IMPACT_KEYS)
                else:
                    validated = _fallback_impact(
                        article.get("title", ""), article.get("description", ""), skills
                    )
                _impact_cache[h] = validated
                results[orig_idx] = validated
        else:
            for orig_idx, article, h in to_process:
                fb = _fallback_impact(
                    article.get("title", ""), article.get("description", ""), skills
                )
                _impact_cache[h] = fb
                results[orig_idx] = fb

    return [results.get(i, _fallback_impact("", "", skills)) for i in range(len(articles[:max_batch]))]


async def generate_career_impact(
    title: str,
    description: str,
    skills: list[str],
    keywords: list[str],
) -> dict:
    """Single-article convenience wrapper (uses batch internally)."""
    batch = await generate_career_impacts_batch(
        [{"title": title, "description": description}], skills, keywords, max_batch=1
    )
    return batch[0] if batch else _fallback_impact(title, description, skills)


async def generate_daily_digest(
    articles: list[dict],
    skills: list[str],
) -> dict:
    if not articles:
        return _fallback_digest(articles)

    articles_text = "\n".join(
        f"- {a.get('title', '')} — {a.get('description', '')[:200]}"
        for a in articles[:10]
    )

    prompt = _DIGEST_PROMPT.format(
        skills=", ".join(skills[:15]),
        articles_text=articles_text,
    )

    result = await generate_json(prompt)
    if result is not None:
        return validate_keys(result, _DIGEST_KEYS)

    return _fallback_digest(articles)


def _fallback_impact(title: str, description: str, skills: list[str]) -> dict:
    matched = [s for s in skills if s.lower() in (title + description).lower()]
    return validate_keys({
        "why_it_matters": f"This article relates to {', '.join(matched[:3]) or 'your field'}.",
        "who_should_care": "Tech professionals with relevant skills",
        "action_next": "Read the full article and note any new tools or approaches.",
    }, _IMPACT_KEYS)


def _fallback_digest(articles: list[dict]) -> dict:
    bullets = [a.get("title", "News item") for a in articles[:5]]
    return validate_keys({
        "bullets": bullets if bullets else ["No articles available today."],
        "recommended_action": "Review the latest articles and identify one new skill to explore.",
    }, _DIGEST_KEYS)
