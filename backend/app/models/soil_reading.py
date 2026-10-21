"""
SoilReading database model.

All soil measurements are optional because not every sensor measures every parameter.
Missing values are stored as NULL — they are never replaced with fabricated values.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class SoilReading(Base):
    __tablename__ = "soil_readings"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    farm_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("farms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Sampling location within the farm
    sampling_latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    sampling_longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    sampling_location_description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # --- Soil parameters (all nullable) ---

    soil_ph: Mapped[float | None] = mapped_column(Float, nullable=True)

    electrical_conductivity: Mapped[float | None] = mapped_column(Float, nullable=True)
    ec_unit: Mapped[str | None] = mapped_column(String(20), nullable=True)  # dS/m, mS/cm

    soil_moisture: Mapped[float | None] = mapped_column(Float, nullable=True)
    moisture_unit: Mapped[str | None] = mapped_column(String(20), nullable=True)  # %, volumetric

    # NPK — units must be consistent across readings used in the same aggregation
    nitrogen: Mapped[float | None] = mapped_column(Float, nullable=True)
    phosphorus: Mapped[float | None] = mapped_column(Float, nullable=True)
    potassium: Mapped[float | None] = mapped_column(Float, nullable=True)
    npk_unit: Mapped[str | None] = mapped_column(String(30), nullable=True)  # mg/kg, kg/ha, ppm

    organic_carbon: Mapped[float | None] = mapped_column(Float, nullable=True)
    organic_carbon_unit: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # --- Metadata ---

    # sensor, manual, import
    data_source: Mapped[str] = mapped_column(String(50), nullable=False, default="manual")
    sensor_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Validation status — False if any flags were raised during ingestion
    is_validated: Mapped[bool] = mapped_column(Boolean, default=False)
    # JSON-encoded list of validation flag strings, e.g. '["pH outside typical range"]'
    validation_flags: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    farm: Mapped["Farm"] = relationship(  # type: ignore[name-defined]
        "Farm", back_populates="soil_readings"
    )
