from datetime import datetime
from typing import Optional
from sqlmodel import Column, Field, ForeignKey, SQLModel


class SessionModel(SQLModel, table=True):
    __tablename__: str = "session"

    id: str = Field(primary_key=True, nullable=False)
    expires_at: datetime = Field(nullable=False)
    token: str = Field(nullable=False, unique=True)
    created_at: datetime = Field(nullable=False)
    updated_at: datetime = Field(nullable=False)
    ip_address: Optional[str] = Field(default=None)
    user_agent: Optional[str] = Field(default=None)
    user_id: str = Field(
        sa_column=Column(ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    )


class AccountModel(SQLModel, table=True):
    __tablename__: str = "account"

    id: str = Field(primary_key=True)
    account_id: str = Field(nullable=False)
    provider_id: str = Field(nullable=False)
    user_id: str = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    access_token: Optional[str] = Field(default=None)
    refresh_token: Optional[str] = Field(default=None)
    id_token: Optional[str] = Field(default=None)
    access_token_expires_at: Optional[datetime] = Field(default=None)
    refresh_token_expires_at: Optional[datetime] = Field(default=None)
    scope: Optional[str] = Field(default=None)
    password: Optional[str] = Field(default=None)
    created_at: datetime = Field(nullable=False)
    updated_at: datetime = Field(nullable=False)


class UserModel(SQLModel, table=True):
    __tablename__: str = "user"

    id: str = Field(primary_key=True, nullable=False)
    name: str = Field(nullable=False)
    email: str = Field(nullable=False, unique=True)
    email_verified: bool = Field(default=False, nullable=False)
    image: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)
