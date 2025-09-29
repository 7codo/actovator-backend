from app.core import settings
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta, timezone
from typing import Any
from google.auth.transport.requests import Request
from sqlmodel import Session, select

from app.db.models import AccountModel  # adjust import path as needed


def _utc_now() -> datetime:
    """Return a timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


def get_service(user_id: str, *, db: Session) -> Any:
    """
    Build and return a Google SearchConsole service object.

    If the access token is expired/missing we refresh it with Google,
    persist the new tokens in AccountModel and then build the service.
    """
    # 1. Load the account row that owns these tokens
    stmt = select(AccountModel).where(AccountModel.user_id == user_id)
    account = db.exec(stmt).one_or_none()
    if not account:
        raise RuntimeError("Account row not found for the supplied access_token")

    # 2. Build a Credentials object from the row
    creds = Credentials(
        token=account.access_token,
        refresh_token=account.refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
        scopes=["https://www.googleapis.com/auth/webmasters.readonly"],
    )

    # 3. Refresh if necessary
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())

            # 4. Persist the new tokens
            account.access_token = creds.token
            account.access_token_expires_at = _utc_now() + timedelta(
                seconds=creds.expiry.timestamp() - _utc_now().timestamp()
            )
            if creds.refresh_token:  # Google sometimes issues a new refresh token
                account.refresh_token = creds.refresh_token
            account.updated_at = _utc_now()
            db.add(account)
            db.commit()
            db.refresh(account)
        else:
            raise RuntimeError("Credentials can neither be validated nor refreshed")

    # 5. Build and return the service
    return build("searchconsole", "v1", credentials=creds, cache_discovery=False)
