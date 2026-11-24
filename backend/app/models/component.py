"""Initial component catalog data model."""

from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import (
    JSON,
    CheckConstraint,
    DateTime,
    Enum as SqlEnum,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column

from ..db.base import Base


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ComponentCategory(str, Enum):
    """Supported component categories for the initial catalog model."""

    CPU = "cpu"
    GPU = "gpu"
    MOTHERBOARD = "motherboard"
    MEMORY = "memory"
    STORAGE = "storage"
    PSU = "psu"
    CASE = "case"
    CPU_COOLER = "cpu_cooler"


class Component(Base):
    """A normalized PC component record."""

    __tablename__ = "components"
    __table_args__ = (
        UniqueConstraint("source_name", "source_id", name="uq_components_source_identity"),
        CheckConstraint(
            "category IN ('cpu', 'gpu', 'motherboard', 'memory', 'storage', 'psu', 'case', 'cpu_cooler')",
            name="ck_components_category",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    category: Mapped[ComponentCategory] = mapped_column(
        SqlEnum(
            ComponentCategory,
            name="component_category",
            native_enum=False,
            values_callable=lambda enum: [member.value for member in enum],
            length=32,
        ),
        nullable=False,
    )
    manufacturer: Mapped[str] = mapped_column(String(120), nullable=False)
    model_name: Mapped[str] = mapped_column(String(200), nullable=False)
    specifications: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    price_source: Mapped[str | None] = mapped_column(String(160), nullable=True)
    price_is_illustrative: Mapped[bool] = mapped_column(nullable=False, default=False)
    source_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    source_id: Mapped[str | None] = mapped_column(String(160), nullable=True)
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    source_license: Mapped[str | None] = mapped_column(String(80), nullable=True)
    source_license_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_attribution: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utc_now, onupdate=_utc_now
    )
