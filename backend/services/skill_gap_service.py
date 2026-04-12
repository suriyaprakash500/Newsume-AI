from __future__ import annotations

import logging

from utils.llm_client import generate_json, validate_keys

logger = logging.getLogger(__name__)

_SKILL_GAP_PROMPT = """You are a career advisor. Compare a user's current skills against recent tech news trends and identify skill gaps.

Return ONLY valid JSON:
{{
  "trending_skills": ["skill1", "skill2", "skill3"],
  "missing_skills": ["skill the user lacks but market demands"],
  "recommendation": "1-2 sentence advice on what to learn next",
  "resume_suggestions": ["specific change 1", "specific change 2"]
}}

User's current skills: {skills}
User's seniority level: {seniority}

Recent trending articles (title + snippet):
{articles_block}
"""

_REQUIRED_SHAPE = {
    "trending_skills": list,
    "missing_skills": list,
    "recommendation": str,
    "resume_suggestions": list,
}


async def generate_skill_gap_report(
    skills: list[str],
    seniority: str,
    recent_articles: list[dict],
) -> dict:
    articles_block = "\n".join(
        f"- {a.get('title', '')} — {a.get('description', '')[:150]}"
        for a in recent_articles[:20]
    )

    prompt = _SKILL_GAP_PROMPT.format(
        skills=", ".join(skills[:20]),
        seniority=seniority,
        articles_block=articles_block,
    )

    result = await generate_json(prompt)
    if result is not None:
        return validate_keys(result, _REQUIRED_SHAPE)

    return _fallback_report(skills, recent_articles)


def _fallback_report(skills: list[str], articles: list[dict]) -> dict:
    article_text = " ".join(
        f"{a.get('title', '')} {a.get('description', '')[:100]}"
        for a in articles[:20]
    ).lower()

    trending = set()
    common_tech = [
        "ai", "llm", "kubernetes", "rust", "golang", "typescript",
        "nextjs", "graphql", "terraform", "docker", "aws", "gcp",
        "azure", "react", "python", "java", "spring boot",
    ]
    skills_lower = {s.lower() for s in skills}
    for term in common_tech:
        if term in article_text:
            trending.add(term)

    missing = [t for t in trending if t not in skills_lower]

    return validate_keys({
        "trending_skills": list(trending)[:10],
        "missing_skills": missing[:5],
        "recommendation": f"Consider learning {', '.join(missing[:3]) or 'emerging tools in your domain'}.",
        "resume_suggestions": [f"Add {m} to your skills section" for m in missing[:3]],
    }, _REQUIRED_SHAPE)
