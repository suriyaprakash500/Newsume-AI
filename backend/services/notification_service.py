from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Optional

import httpx

from config.settings import settings

logger = logging.getLogger(__name__)

_last_notification: dict[str, str] = {}


def is_quiet_hours(quiet_start: int, quiet_end: int, timezone_str: str = "Asia/Kolkata") -> bool:
    """Check if current time falls within quiet hours."""
    try:
        from zoneinfo import ZoneInfo
        now = datetime.now(ZoneInfo(timezone_str))
        hour = now.hour
        if quiet_start > quiet_end:
            return hour >= quiet_start or hour < quiet_end
        return quiet_start <= hour < quiet_end
    except Exception:
        return False


def was_notified_today(device_id: str) -> bool:
    """Enforce max 1 notification per device per day."""
    today = datetime.utcnow().strftime("%Y-%m-%d")
    return _last_notification.get(device_id) == today


def send_push_notification(
    fcm_token: str,
    title: str,
    body: str,
    data: Optional[dict] = None,
    device_id: str = "",
    notify_enabled: bool = True,
    quiet_start: int = 22,
    quiet_end: int = 7,
):
    if not notify_enabled:
        logger.info(f"Notifications disabled for {device_id[:10]}...")
        return

    if is_quiet_hours(quiet_start, quiet_end):
        logger.info(f"Quiet hours active — skipping notification for {device_id[:10]}...")
        return

    if device_id and was_notified_today(device_id):
        logger.info(f"Already notified today — skipping for {device_id[:10]}...")
        return

    if not fcm_token:
        logger.info("Skipping push notification (no FCM token).")
        return

    # Use FCM legacy HTTP API (lightweight, no firebase-admin SDK needed)
    fcm_server_key = getattr(settings, "fcm_server_key", "")
    if not fcm_server_key:
        logger.info("Skipping push notification (no FCM server key configured).")
        return

    try:
        payload = {
            "to": fcm_token,
            "notification": {"title": title, "body": body},
            "data": data or {},
        }
        resp = httpx.post(
            "https://fcm.googleapis.com/fcm/send",
            json=payload,
            headers={
                "Authorization": f"key={fcm_server_key}",
                "Content-Type": "application/json",
            },
            timeout=10.0,
        )
        if resp.status_code == 200:
            if device_id:
                _last_notification[device_id] = datetime.utcnow().strftime("%Y-%m-%d")
            logger.info(f"Push notification sent to {device_id[:10]}...")
        else:
            logger.warning(f"FCM responded with {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        logger.error(f"Push notification failed: {e}")
