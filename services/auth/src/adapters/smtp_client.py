import logging
from email.message import EmailMessage

import aiosmtplib
from aiosmtplib.errors import SMTPConnectError
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type


log = logging.getLogger(__name__)


class SMTPClient:
    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        app_name: str,
        timeout: float = 10,
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.timeout = timeout
        self.app_name = app_name or username

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_fixed(2),
        retry=retry_if_exception_type(SMTPConnectError),
    )
    async def send_email(self, to_email: str, subject: str, body: str):
        message = EmailMessage()
        message["From"] = self.app_name
        message["To"] = to_email
        message["Subject"] = subject
        message.set_content(body)

        try:
            await aiosmtplib.send(
                message,
                hostname=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                start_tls=True,
                timeout=self.timeout,
            )
        except SMTPConnectError:
            log.error("SMTP: Connection failed. Retrying...")
            raise
        except Exception as e:
            log.exception(f"SMTP: Failed to send email: {e}")
