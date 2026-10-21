"""
Fertilizer product catalogue and price records.

Nutrient accounting convention (documented here to avoid confusion):
  - nitrogen_pct   = % elemental N  (e.g. Urea = 46%)
  - phosphorus_pct = % P₂O₅  (fertilizer label convention)
  - potassium_pct  = % K₂O   (fertilizer label convention)

  Exception: if nutrient_as_elemental = True, phosphorus_pct and
  potassium_pct store elemental P% and K% respectively.

Conversion factors (if needed):
  P_elemental  = P₂O₅ × 0.4364
  K_elemental  = K₂O  × 0.8301
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class FertilizerProduct(Base):
    __tablename__ = "fertilizer_products"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    manufacturer: Mapped[str | None] = mapped_column(String(200), nullable=True)
    supplier: Mapped[str | None] = mapped_column(String(200), nullable=True)

    # Nutrient composition — see module docstring for convention
    nitrogen_pct: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    phosphorus_pct: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    potassium_pct: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    nutrient_as_elemental: Mapped[bool] = mapped_column(Boolean, default=False)
    nutrient_basis_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    product_form: Mapped[str | None] = mapped_column(String(50), nullable=True)  # granular, liquid, powder
    application_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    prices: Mapped[list["FertilizerPrice"]] = relationship(
        "FertilizerPrice", back_populates="product", cascade="all, delete-orphan"
    )


class FertilizerPrice(Base):
    """
    Price record for a fertilizer product.

    source values and their meaning:
      user_entered       — entered via API by an authenticated user
      csv_import         — imported from a CSV file via the admin import endpoint
      verified_market    — confirmed against a real market price source
      illustrative_sample — seed data for demonstration; NOT a real price
    """

    __tablename__ = "fertilizer_prices"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    product_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("fertilizer_products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    price_value: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), nullable=False, default="INR")
    price_unit: Mapped[str] = mapped_column(String(30), nullable=False, default="INR/kg")
    # kg weight of bag — required when price_unit is per-bag
    bag_weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)

    supplier: Mapped[str | None] = mapped_column(String(200), nullable=True)
    location: Mapped[str | None] = mapped_column(String(200), nullable=True)

    # See class docstring for valid source values
    source: Mapped[str] = mapped_column(String(50), nullable=False, default="user_entered")

    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    valid_from: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    valid_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    product: Mapped["FertilizerProduct"] = relationship(
        "FertilizerProduct", back_populates="prices"
    )
