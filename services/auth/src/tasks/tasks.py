import logging
import asyncio
from datetime import datetime, timezone, timedelta

import smtplib
from email.message import EmailMessage

from src.tasks.celery_app import app
from src.config import settings
from src.managers.db import DBManager
from src.db import null_pool_session_maker
from src.models.users import UserORM
from src.models.refresh_tokens import RefreshTokenORM


log = logging.getLogger(__name__)


@app.task
def send_verification_email(to_email: str, code: str):
    message = EmailMessage()
    message["From"] = settings.SMTP_FROM
    message["To"] = to_email
    message["Subject"] = "Email verification"
    message.set_content(f"Your verification code: {code}")

    with smtplib.SMTP(
        settings.SMTP_HOST,
        settings.SMTP_PORT,
        timeout=settings.SMTP_TIMEOUT,
    ) as smtp:
        smtp.starttls()
        smtp.login(settings.SMTP_USER, settings.SMTP_PASS)
        smtp.send_message(message)
        log.debug(f"SMTP: Email sent to {to_email}")


async def delete_inactive_users():
    async with DBManager(session_factory=null_pool_session_maker) as db:
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(hours=24)
        await db.users.delete(UserORM.created_at <= cutoff, is_active=False)
        await db.commit()


async def delete_expired_refresh_tokens():
    async with DBManager(session_factory=null_pool_session_maker) as db:
        now = datetime.now(timezone.utc)
        await db.refresh_tokens.delete(RefreshTokenORM.expires_at <= now)
        await db.commit()


@app.task
def delete_inactive_users_task():
    asyncio.run(delete_inactive_users())
    log.info("Deleted inactive users")


@app.task
def delete_expired_refresh_tokens_task():
    asyncio.run(delete_expired_refresh_tokens())
    log.info("Deleted expired refresh tokens")
