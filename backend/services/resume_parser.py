import json
from sqlalchemy.orm import Session

from utils.text_parser import extract_text
from services.skill_extractor import extract_profile_from_text
from repositories.user_profile_repo import upsert_profile


async def process_resume(db: Session, device_id: str, file_bytes: bytes, filename: str) -> dict:
    raw_text = extract_text(file_bytes, filename)
    profile_data = await extract_profile_from_text(raw_text)

    db_data = {
        "name": profile_data.get("name", ""),
        "email": profile_data.get("email", ""),
        "skills": json.dumps(profile_data.get("skills", [])),
        "certifications": json.dumps(profile_data.get("certifications", [])),
        "experience": json.dumps(profile_data.get("experience", [])),
        "education": json.dumps(profile_data.get("education", [])),
        "keywords": json.dumps(profile_data.get("keywords", [])),
        "raw_text": raw_text,
        "resume_filename": filename,
    }

    profile = upsert_profile(db, device_id, db_data)

    return {
        "device_id": profile.device_id,
        "name": profile.name,
        "skills": json.loads(profile.skills),
        "certifications": json.loads(profile.certifications),
        "experience": json.loads(profile.experience),
        "education": json.loads(profile.education),
        "keywords": json.loads(profile.keywords),
        "version": profile.version,
        "resume_filename": profile.resume_filename,
    }
