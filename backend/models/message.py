from sqlalchemy import Column, String, DateTime, Boolean, Enum, Text, LargeBinary
from sqlalchemy.dialects.postgresql import UUID, BYTEA
from sqlalchemy.sql import func
from db.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
from datetime import datetime

class MediaType(str):
    IMAGE = "image"
    DOCUMENT = "document"

class Message(Base):
    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    jid: Mapped[str] = mapped_column(String(), nullable=False, index=True)
    instance: Mapped[str] = mapped_column(String(), nullable=False)
    content: Mapped[str] = mapped_column(String(), nullable=False, default="")
    media: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="scheduled")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    error: Mapped[str] = mapped_column(Text)

class MessageMedia(Base):
    __tablename__ = "message_media"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    media_name: Mapped[str] = mapped_column(String(), nullable=False)
    media_type: Mapped[str] = mapped_column(Enum(MediaType.IMAGE, MediaType.DOCUMENT, name="media_type_enum"), nullable=False)
    media_data: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)