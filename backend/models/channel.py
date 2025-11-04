# models/channel.py
from db.database import Base
from datetime import datetime
from enum import Enum as PyEnum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
    String, Boolean, DateTime, ForeignKey, Index, Integer,
    UniqueConstraint, Text
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy import Enum as SAEnum
from sqlalchemy.sql import func

from schemas.channels_schemas import Provider

if TYPE_CHECKING:
    from models.institution import Institution

class CredentialType(str, PyEnum):
    API_KEY = "API_KEY"
    TOKEN = "TOKEN"
    BASIC_AUTH = "BASIC_AUTH"
    OAUTH = "OAUTH"
    SECRET = "SECRET"

class ChannelType(Base):
    __tablename__ = "channel_type"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[Provider] = mapped_column(
        SAEnum(Provider, name="provider_enum", native_enum=True),
        nullable=False,
        unique=True
    )
    channels: Mapped[list["Channel"]] = relationship(
        back_populates="type",
        cascade="all, delete-orphan"
    )

class Channel(Base):
    __tablename__ = "channels"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    channel_type_id: Mapped[int] = mapped_column(
        ForeignKey("channel_type.id", ondelete="RESTRICT"),
        nullable=False
    )
    post_endpoint: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    webhook_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    metadata_: Mapped[dict | None] = mapped_column(
        "metadata", JSONB, nullable=True
    )
    institution_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("institution.id", ondelete="SET NULL"),
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
        onupdate=func.now(), nullable=False
    )
    type: Mapped["ChannelType"] = relationship(back_populates="channels")
    credentials: Mapped[list["ChannelCredential"]] = relationship(
        back_populates="channel",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    if TYPE_CHECKING:
        institution: Mapped["Institution"]

    __table_args__ = (
        Index("ix_channels_type", "channel_type_id"),
        Index("ix_channels_created_at", "created_at"),
    )

class ChannelCredential(Base):
    __tablename__ = "channel_credentials"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    channel_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("channels.id", ondelete="CASCADE"),
        nullable=False
    )
    credential_type: Mapped[CredentialType] = mapped_column(
        SAEnum(CredentialType, name="credential_type_enum", native_enum=True),
        nullable=False
    )
    value_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
        onupdate=func.now(), nullable=False
    )
    channel: Mapped["Channel"] = relationship(back_populates="credentials")

    __table_args__ = (
        UniqueConstraint(
            "channel_id", "credential_type", "active",
            name="uq_channel_cred_active_one_per_type"
        ),
        Index("ix_channel_credentials_channel", "channel_id"),
        Index("ix_channel_credentials_active", "active"),
        Index("ix_channel_credentials_expires_at", "expires_at"),
    )