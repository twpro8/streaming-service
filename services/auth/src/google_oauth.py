import logging
from urllib.parse import urlencode

from src.config import settings


log = logging.getLogger(__name__)


def generate_google_oauth_redirect_uri(state: str):
    base_url = "https://accounts.google.com/o/oauth2/v2/auth"
    params = {
        "client_id": settings.OAUTH_GOOGLE_CLIENT_ID,
        "redirect_uri": settings.OAUTH_GOOGLE_REDIRECT_URL,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
    }
    return f"{base_url}?{urlencode(params)}"
