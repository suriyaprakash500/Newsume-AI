from __future__ import annotations

import re

from utils.llm_client import generate_json, validate_keys

_MAX_RESUME_CHARS = 8000

_EXTRACTION_PROMPT = """You are an expert resume analyzer. Extract structured information from the following resume text.
Return ONLY valid JSON with these exact keys:
{
  "name": "full name",
  "email": "email address",
  "skills": ["skill1", "skill2", ...],
  "certifications": ["cert1", "cert2", ...],
  "experience": ["role1 at company1", "role2 at company2", ...],
  "education": ["degree1 from university1", ...],
  "keywords": ["domain keyword1", "technology keyword2", ...]
}

Rules:
- "skills" should include programming languages, frameworks, tools, soft skills.
- "keywords" should include industry domains, buzzwords, and technologies mentioned.
- Keep each item concise (under 10 words).
- If a field has no data, return an empty list [].

Resume text:
"""

_REQUIRED_SHAPE = {
    "name": str,
    "email": str,
    "skills": list,
    "certifications": list,
    "experience": list,
    "education": list,
    "keywords": list,
}


def _truncate_resume(text: str) -> str:
    """Keep first N chars, preserving last complete line."""
    if len(text) <= _MAX_RESUME_CHARS:
        return text
    truncated = text[:_MAX_RESUME_CHARS]
    last_newline = truncated.rfind("\n")
    if last_newline > _MAX_RESUME_CHARS * 0.8:
        truncated = truncated[:last_newline]
    return truncated + "\n\n[... resume truncated for processing ...]"


async def extract_profile_from_text(resume_text: str) -> dict:
    trimmed = _truncate_resume(resume_text)

    result = await generate_json(_EXTRACTION_PROMPT + trimmed)
    if result is not None:
        return validate_keys(result, _REQUIRED_SHAPE)

    return _fallback_extraction(resume_text)


_EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

_EXPERIENCE_SIGNALS = {"engineer", "developer", "manager", "analyst", "intern", "lead", "architect", "consultant", "designer"}

_TECH_TERMS = {
    "python", "java", "kotlin", "javascript", "typescript", "react",
    "angular", "vue", "node", "django", "flask", "fastapi", "spring",
    "docker", "kubernetes", "aws", "azure", "gcp", "sql", "nosql",
    "mongodb", "postgresql", "redis", "git", "ci/cd", "machine learning",
    "deep learning", "tensorflow", "pytorch", "android", "ios", "flutter",
    "rust", "go", "c++", "c#", ".net", "html", "css", "graphql",
    "rest", "api", "microservices", "agile", "scrum", "devops",
}


def _fallback_extraction(text: str) -> dict:
    lines = text.split("\n")
    text_lower = text.lower()

    email_match = _EMAIL_RE.search(text)
    email = email_match.group(0) if email_match else ""

    name = ""
    for line in lines[:5]:
        stripped = line.strip()
        if stripped and not _EMAIL_RE.match(stripped) and len(stripped) < 60:
            name = stripped
            break

    skills = [t for t in _TECH_TERMS if t in text_lower]

    experience = []
    for line in lines:
        stripped = line.strip()
        low = stripped.lower()
        if any(sig in low for sig in _EXPERIENCE_SIGNALS) and 10 < len(stripped) < 120:
            experience.append(stripped)
        if len(experience) >= 10:
            break

    keywords = []
    for line in lines:
        stripped = line.strip()
        if 3 < len(stripped) < 60 and stripped not in experience:
            keywords.append(stripped)
        if len(keywords) >= 20:
            break

    return validate_keys({
        "name": name,
        "email": email,
        "skills": skills[:30],
        "certifications": [],
        "experience": experience[:10],
        "education": [],
        "keywords": keywords,
    }, _REQUIRED_SHAPE)
