"""
Crop reference catalogue and farm-level crop selections.
"""
import uuid
from datetime import datetime, timezone, date

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class CropReference(Base):
    """
    Immutable reference catalogue of supported crops.
    Seeded at startup; not modified by normal API users.
    """

    __tablename__ = "crop_references"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # JSON-encoded list of typical growth stage strings
    typical_growth_stages: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    crop_selections: Mapped[list["CropSelection"]] = relationship(
        "CropSelection", back_populates="crop_reference"
    )


class CropSelection(Base):
    """
    A specific crop growing on a specific farm at a specific time.
    """

    __tablename__ = "crop_selections"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    farm_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("farms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    crop_reference_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("crop_references.id"), nullable=False, index=True
    )

    variety: Mapped[str | None] = mapped_column(String(100), nullable=True)
    growth_stage: Mapped[str] = mapped_column(String(50), nullable=False)
    planting_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    expected_area_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    expected_area_unit: Mapped[str | None] = mapped_column(String(20), nullable=True)
    expected_yield_kg_per_ha: Mapped[float | None] = mapped_column(Float, nullable=True)

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    farm: Mapped["Farm"] = relationship(  # type: ignore[name-defined]
        "Farm", back_populates="crop_selections"
    )
    crop_reference: Mapped["CropReference"] = relationship(
        "CropReference", back_populates="crop_selections"
    )
