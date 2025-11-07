from src.db.database import Base
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from src.schemas.roles_schemas import Roles
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.institution import Institution

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    role: Mapped[str] = mapped_column(Enum(Roles), nullable=False, server_default='user')
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    institution_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("institution.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    institution: Mapped[list["Institution"]] = relationship("Institution", back_populates="users", passive_deletes=True)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name} ({self.username})"

    def __repr__(self) -> str:
        return (
            f"<User id={self.id} username='{self.username}' "
            f"email='{self.email}' verified={self.is_verified}>"
        )