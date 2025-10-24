import logging
import smtplib
from email.message import EmailMessage

from src.tasks.celery_app import app
from src.config import settings


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
