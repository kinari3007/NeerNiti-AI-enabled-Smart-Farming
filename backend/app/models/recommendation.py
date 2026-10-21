"""
Recommendation model.

A recommendation is the result of combining:
1. ML classifier output (fertilizer category suggestion — NOT nutrient quantities).
2. Agronomic nutrient requirements lookup (approximate reference values).
3. Cost-optimized fertilizer plan from the LP solver.

These three outputs are distinct and stored separately in this model.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    farm_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("farms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    crop_selection_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("crop_selections.id", ondelete="SET NULL"), nullable=True
    )

    # JSON-encoded list of soil reading IDs used in this recommendation
    soil_reading_ids: Mapped[str | None] = mapped_column(Text, nullable=True)

    # JSON snapshot of weather data at recommendation time
    weather_snapshot: Mapped[str | None] = mapped_column(Text, nullable=True)

    # JSON snapshot of aggregated soil statistics
    soil_summary_snapshot: Mapped[str | None] = mapped_column(Text, nullable=True)

    # --- ML classifier output ---
    # Category suggestion only. Does NOT represent validated nutrient quantities.
    ml_classifier_output: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON
    ml_model_version: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # --- Agronomic nutrient requirements ---
    # Approximate reference values, not field-specific calibrated requirements.
    crop_nutrient_requirements: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON {N, P, K}
    nutrient_requirement_source: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # --- Optimization result ---
    optimization_status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="pending"
    )
    # Possible values:
    #   pending              — not yet computed
    #   feasible             — optimizer found a valid solution
    #   infeasible           — no valid fertilizer combination exists for given constraints
    #   skipped_no_prices    — no verified prices available and unverified not permitted
    #   skipped_no_requirements — crop not in reference table
    #   error                — unexpected solver or data error

    # JSON list of OptimizedFertilizerItem dicts
    optimization_result: Mapped[str | None] = mapped_column(Text, nullable=True)
    estimated_total_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    cost_currency: Mapped[str | None] = mapped_column(String(10), nullable=True)

    # JSON snapshot of prices used — preserves price provenance at recommendation time
    price_snapshot: Mapped[str | None] = mapped_column(Text, nullable=True)

    # JSON list of warning strings
    warnings: Mapped[str | None] = mapped_column(Text, nullable=True)
    # JSON list of assumption strings
    assumptions: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    farm: Mapped["Farm"] = relationship(  # type: ignore[name-defined]
        "Farm", back_populates="recommendations"
    )
