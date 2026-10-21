"""
Farm database model.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Farm(Base):
    __tablename__ = "farms"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    # Coordinates (both required together or both absent)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Farm area
    area_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    area_unit: Mapped[str | None] = mapped_column(String(20), nullable=True)  # hectare, acre, sqm, bigha

    location_description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Irrigation water pH — optional, affects recommendations if available
    irrigation_water_ph: Mapped[float | None] = mapped_column(Float, nullable=True)
    irrigation_water_ph_source: Mapped[str | None] = mapped_column(String(100), nullable=True)
    irrigation_water_ph_timestamp: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    # Relationships
    soil_readings: Mapped[list["SoilReading"]] = relationship(  # type: ignore[name-defined]
        "SoilReading", back_populates="farm", cascade="all, delete-orphan", lazy="select"
    )
    crop_selections: Mapped[list["CropSelection"]] = relationship(  # type: ignore[name-defined]
        "CropSelection", back_populates="farm", cascade="all, delete-orphan", lazy="select"
    )
    recommendations: Mapped[list["Recommendation"]] = relationship(  # type: ignore[name-defined]
        "Recommendation", back_populates="farm", cascade="all, delete-orphan", lazy="select"
    )
