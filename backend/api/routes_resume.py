from __future__ import annotations

import json
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from services.resume_parser import process_resume
from repositories.user_profile_repo import get_profile_by_device, update_fcm_token, upsert_profile

router = APIRouter(prefix="/resume", tags=["Resume"])


def _serialize_profile(profile) -> dict:
    """Shared helper to build a profile response dict."""
    return {
        "device_id": profile.device_id,
        "name": profile.name or "",
        "skills": json.loads(profile.skills or "[]"),
        "certifications": json.loads(profile.certifications or "[]"),
        "experience": json.loads(profile.experience or "[]"),
        "education": json.loads(profile.education or "[]"),
        "keywords": json.loads(profile.keywords or "[]"),
        "version": profile.version,
        "resume_filename": profile.resume_filename or "",
    }


@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    device_id: str = Form(...),
    db: Session = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided.")

    allowed = (".pdf", ".docx")
    if not any(file.filename.lower().endswith(ext) for ext in allowed):
        raise HTTPException(status_code=400, detail=f"Unsupported file type. Use: {allowed}")

    file_bytes = await file.read()
    if len(file_bytes) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 10 MB).")

    result = await process_resume(db, device_id, file_bytes, file.filename)
    return {"status": "success", "profile": result}


@router.get("/profile/{device_id}")
def get_profile(device_id: str, db: Session = Depends(get_db)):
    profile = get_profile_by_device(db, device_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found.")
    return _serialize_profile(profile)


class EditProfileRequest(BaseModel):
    skills: Optional[List[str]] = None
    certifications: Optional[List[str]] = None
    experience: Optional[List[str]] = None
    education: Optional[List[str]] = None
    keywords: Optional[List[str]] = None


@router.put("/profile/{device_id}")
def edit_profile(device_id: str, body: EditProfileRequest, db: Session = Depends(get_db)):
    """User-editable profile fields after resume extraction."""
    existing = get_profile_by_device(db, device_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Profile not found. Upload resume first.")

    update_data = {}
    if body.skills is not None:
        update_data["skills"] = json.dumps(body.skills)
    if body.certifications is not None:
        update_data["certifications"] = json.dumps(body.certifications)
    if body.experience is not None:
        update_data["experience"] = json.dumps(body.experience)
    if body.education is not None:
        update_data["education"] = json.dumps(body.education)
    if body.keywords is not None:
        update_data["keywords"] = json.dumps(body.keywords)

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update.")

    profile = upsert_profile(db, device_id, update_data)
    return {"status": "success", "profile": _serialize_profile(profile)}


@router.post("/fcm-token")
def register_fcm_token(
    device_id: str = Form(...),
    fcm_token: str = Form(...),
    db: Session = Depends(get_db),
):
    profile = update_fcm_token(db, device_id, fcm_token)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found. Upload resume first.")
    return {"status": "success"}
