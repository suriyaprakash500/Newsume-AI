from __future__ import annotations

from sqlalchemy.orm import Session

from models.user_profile import UserProfile


def get_profile_by_device(db: Session, device_id: str) -> UserProfile | None:
    return db.query(UserProfile).filter(UserProfile.device_id == device_id).first()


def get_all_profiles(db: Session) -> list[UserProfile]:
    return db.query(UserProfile).all()


def upsert_profile(db: Session, device_id: str, data: dict) -> UserProfile:
    profile = get_profile_by_device(db, device_id)
    if profile:
        data["version"] = (profile.version or 0) + 1
        for key, value in data.items():
            setattr(profile, key, value)
    else:
        profile = UserProfile(device_id=device_id, **data)
        db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def update_fcm_token(db: Session, device_id: str, token: str) -> UserProfile | None:
    profile = get_profile_by_device(db, device_id)
    if profile:
        profile.fcm_token = token
        db.commit()
        db.refresh(profile)
    return profile


def delete_profile(db: Session, device_id: str) -> bool:
    deleted = db.query(UserProfile).filter(UserProfile.device_id == device_id).delete()
    db.commit()
    return deleted > 0
