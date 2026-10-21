"""
Recommendation service — orchestrates the full recommendation pipeline.

Pipeline steps
--------------
1.  Load the farm (raise NotFoundError if missing).
2.  Resolve crop name and growth stage (from CropSelection or request fields).
3.  Load soil readings (all farm readings or specified IDs).
4.  Optionally fetch weather (degraded gracefully if unavailable).
5.  Run the ML classifier for a fertilizer category suggestion.
6.  Look up crop nutrient requirements from the reference table.
7.  Load active fertilizer products with usable prices.
8.  Run the LP optimizer.
9.  Persist the recommendation and return it.

The three outputs — ML suggestion, nutrient requirements, optimised plan —
are kept separate throughout and never conflated.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessError, NotFoundError
from app.ml.nutrient_estimator import predict_fertilizer_category
from app.models.fertilizer import FertilizerPrice, FertilizerProduct
from app.models.recommendation import Recommendation
from app.models.soil_reading import SoilReading
from app.optimization.constraints import get_nutrient_requirements
from app.optimization.fertilizer_optimizer import (
    FertilizerOption,
    OptimizationResult,
    optimize_fertilizer_cost,
)
from app.schemas.recommendation import (
    NutrientBalance,
    OptimizedFertilizerItem,
    RecommendationRequest,
    RecommendationResponse,
)
from app.services.farm_service import get_farm
from app.services.fertilizer_service import price_to_per_kg
from app.services.soil_service import get_soil_summary

logger = logging.getLogger("neerniti.recommendation_service")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


async def _resolve_crop(
    db: AsyncSession,
    farm_id: str,
    request: RecommendationRequest,
) -> tuple[str, str, Optional[str]]:
    """
    Return (crop_name, growth_stage, crop_selection_id).
    Prefers a stored CropSelection; falls back to inline request fields.
    """
    if request.crop_selection_id:
        from app.models.crop import CropReference, CropSelection
        result = await db.execute(
            select(CropSelection, CropReference.name)
            .join(CropReference, CropSelection.crop_reference_id == CropReference.id)
            .where(
                CropSelection.id == request.crop_selection_id,
                CropSelection.farm_id == farm_id,
            )
        )
        row = result.first()
        if row is None:
            raise NotFoundError("CropSelection", request.crop_selection_id)
        sel, crop_name = row
        return crop_name, sel.growth_stage, sel.id

    if not request.crop_name or not request.growth_stage:
        raise BusinessError(
            "Either crop_selection_id or both crop_name and growth_stage are required.",
            code="MISSING_CROP_INFO",
        )
    return request.crop_name, request.growth_stage, None


async def _load_readings(
    db: AsyncSession,
    farm_id: str,
    reading_ids: Optional[list[str]],
) -> list[SoilReading]:
    """Load specified or all soil readings for the farm."""
    query = select(SoilReading).where(SoilReading.farm_id == farm_id)
    if reading_ids:
        query = query.where(SoilReading.id.in_(reading_ids))
    result = await db.execute(query.order_by(SoilReading.collected_at.desc()))
    readings = list(result.scalars().all())
    if reading_ids and len(readings) != len(reading_ids):
        found_ids = {r.id for r in readings}
        missing = set(reading_ids) - found_ids
        raise NotFoundError("SoilReading", list(missing))
    return readings


async def _load_fertilizer_options(
    db: AsyncSession,
    allow_unverified: bool,
) -> tuple[list[FertilizerOption], list[str]]:
    """
    Load active fertilizer products with their best available price.
    Returns (options, warnings).
    """
    warnings: list[str] = []
    options: list[FertilizerOption] = []

    prod_result = await db.execute(
        select(FertilizerProduct).where(FertilizerProduct.is_active == True)  # noqa: E712
    )
    products = list(prod_result.scalars().all())

    for product in products:
        # Find best price: verified preferred; unverified used only if allowed
        price_query = (
            select(FertilizerPrice)
            .where(FertilizerPrice.product_id == product.id)
            .order_by(
                FertilizerPrice.is_verified.desc(),
                FertilizerPrice.created_at.desc(),
            )
        )
        if not allow_unverified:
            price_query = price_query.where(FertilizerPrice.is_verified == True)  # noqa: E712
        else:
            # Even with allow_unverified, exclude illustrative samples by default
            # unless they're the only option
            pass

        price_result = await db.execute(price_query.limit(10))
        prices = list(price_result.scalars().all())

        chosen_price: Optional[FertilizerPrice] = None
        price_per_kg: Optional[float] = None

        for p in prices:
            pkg = price_to_per_kg(p)
            if pkg is not None and pkg > 0:
                # Skip illustrative samples unless no other option
                if p.source == "illustrative_sample" and not allow_unverified:
                    continue
                chosen_price = p
                price_per_kg = pkg
                break

        # Fallback: try illustrative_sample if allow_unverified and nothing else found
        if chosen_price is None and allow_unverified:
            for p in prices:
                pkg = price_to_per_kg(p)
                if pkg is not None and pkg > 0:
                    chosen_price = p
                    price_per_kg = pkg
                    warnings.append(
                        f"Product '{product.name}' uses an illustrative sample price "
                        f"({p.price_value} {p.currency}/{p.price_unit.replace(p.currency + '/', '')}). "
                        "This is NOT a verified market price."
                    )
                    break

        if chosen_price is None or price_per_kg is None:
            logger.debug(
                "Skipping '%s' — no usable price found (allow_unverified=%s)",
                product.name, allow_unverified,
            )
            continue

        options.append(
            FertilizerOption(
                product_id=product.id,
                product_name=product.name,
                nitrogen_pct=product.nitrogen_pct,
                phosphorus_pct=product.phosphorus_pct,
                potassium_pct=product.potassium_pct,
                nutrient_as_elemental=product.nutrient_as_elemental,
                price_per_kg=price_per_kg,
                currency=chosen_price.currency,
                price_source=chosen_price.source,
                price_verified=chosen_price.is_verified,
                price_record_id=chosen_price.id,
                price_recorded_at=chosen_price.created_at,
            )
        )

    if not options:
        if allow_unverified:
            warnings.append(
                "No fertilizer products with any usable price found. "
                "Import prices via POST /api/v1/fertilizers/prices/import."
            )
        else:
            warnings.append(
                "No fertilizer products with verified prices found. "
                "Either import verified prices or set allow_unverified_prices=true."
            )

    return options, warnings


def _build_optimized_items(
    opt_result: OptimizationResult,
    options: list[FertilizerOption],
    area_ha: float,
) -> list[OptimizedFertilizerItem]:
    """
    Convert optimizer solution into OptimizedFertilizerItem list.
    Only include products with quantity > 0.01 kg/ha (filter solver noise).
    """
    from app.optimization.constraints import nutrient_content_per_ha

    items: list[OptimizedFertilizerItem] = []
    for i, (product_id, product_name, qty_per_ha) in enumerate(
        zip(opt_result.product_ids, opt_result.product_names, opt_result.quantities_kg_per_ha)
    ):
        if qty_per_ha < 0.01:
            continue
        opt = next(o for o in options if o.product_id == product_id)
        n_sup, p_sup, k_sup = nutrient_content_per_ha(
            qty_per_ha,
            opt.nitrogen_pct,
            opt.phosphorus_pct,
            opt.potassium_pct,
            opt.nutrient_as_elemental,
        )
        qty_total = qty_per_ha * area_ha
        cost_per_ha = qty_per_ha * opt.price_per_kg
        cost_total = qty_total * opt.price_per_kg

        items.append(
            OptimizedFertilizerItem(
                product_id=product_id,
                product_name=product_name,
                quantity_kg_per_ha=round(qty_per_ha, 3),
                quantity_kg_total=round(qty_total, 3),
                price_per_kg=opt.price_per_kg,
                cost_per_ha=round(cost_per_ha, 2),
                cost_total=round(cost_total, 2),
                currency=opt.currency,
                price_source=opt.price_source,
                price_verified=opt.price_verified,
                price_record_id=opt.price_record_id,
                price_recorded_at=opt.price_recorded_at,
                n_supplied_kg_per_ha=round(n_sup, 4),
                p_supplied_kg_per_ha=round(p_sup, 4),
                k_supplied_kg_per_ha=round(k_sup, 4),
            )
        )
    return items


# ---------------------------------------------------------------------------
# Main service function
# ---------------------------------------------------------------------------

async def create_recommendation(
    db: AsyncSession,
    farm_id: str,
    request: RecommendationRequest,
) -> Recommendation:
    """
    Generate and persist a fertilizer recommendation for a farm.
    Returns the persisted Recommendation ORM object.
    """
    all_warnings: list[str] = []
    assumptions: list[str] = [
        "Nutrient requirements are per-hectare approximate reference values (ICAR guidelines), "
        "not field-calibrated targets.",
        "Fertilizer nutrient composition values are from standard product labels.",
        "Optimization minimises total fertilizer cost subject to meeting ≥ nutrient targets.",
        "The LP solution is globally optimal for the given linear formulation.",
    ]

    # --- Step 1: Load farm ---
    farm = await get_farm(db, farm_id)

    # --- Step 2: Resolve crop ---
    crop_name, growth_stage, crop_selection_id = await _resolve_crop(
        db, farm_id, request
    )

    # --- Step 3: Determine cultivated area ---
    area_ha: float = 1.0
    if request.area_ha:
        area_ha = request.area_ha
    elif farm.area_value and farm.area_unit:
        # Convert farm area to hectares
        unit_to_ha = {"hectare": 1.0, "acre": 0.4047, "bigha": 0.2529, "sqm": 0.0001}
        factor = unit_to_ha.get(farm.area_unit, 1.0)
        area_ha = farm.area_value * factor
        assumptions.append(
            f"Area derived from farm record: {farm.area_value} {farm.area_unit} "
            f"= {area_ha:.4f} ha."
        )

    # --- Step 4: Load soil readings ---
    readings = await _load_readings(db, farm_id, request.soil_reading_ids)
    if not readings:
        all_warnings.append(
            "No soil readings found for this farm. "
            "Nutrient recommendations are based on crop reference values only, "
            "without soil-test correction."
        )

    # Compute soil summary snapshot
    soil_summary = await get_soil_summary(db, farm_id)
    soil_snapshot = soil_summary.model_dump()

    # --- Step 5: Fetch weather ---
    weather_response = None
    weather_snapshot = None

    if request.use_weather:
        if farm.latitude is None or farm.longitude is None:
            all_warnings.append(
                "Farm has no coordinates — weather data skipped. "
                "Add latitude and longitude to the farm for weather integration."
            )
        else:
            from app.services.weather_service import get_weather_for_farm
            try:
                weather_response = await get_weather_for_farm(
                    farm_id, farm.latitude, farm.longitude
                )
                weather_snapshot = weather_response.model_dump(mode="json")
            except RuntimeError as exc:
                all_warnings.append(
                    f"Weather data unavailable: {exc} "
                    "Recommendation proceeds without weather context."
                )

    # Irrigation water pH advisory
    if farm.irrigation_water_ph is not None:
        if farm.irrigation_water_ph < 6.0:
            all_warnings.append(
                f"Irrigation water pH is {farm.irrigation_water_ph:.1f} (acidic). "
                "Acidic irrigation water may increase soil acidity over time. "
                "Consult an agronomist before adjusting fertilizer rates based on this value."
            )
        elif farm.irrigation_water_ph > 8.0:
            all_warnings.append(
                f"Irrigation water pH is {farm.irrigation_water_ph:.1f} (alkaline). "
                "Alkaline water may affect micronutrient availability. "
                "No automatic fertilizer adjustment is made — consult an agronomist."
            )

    # --- Step 6: ML classifier ---
    ml_output, ml_warnings = predict_fertilizer_category(
        request=request,
        crop_name=crop_name,
        growth_stage=growth_stage,
        readings=readings,
        weather=weather_response,
    )
    all_warnings.extend(ml_warnings)

    ml_classifier_json = ml_output.model_dump() if ml_output else None

    # --- Step 7: Crop nutrient requirements ---
    nutrient_reqs, req_source = get_nutrient_requirements(crop_name, growth_stage)

    if nutrient_reqs is None:
        all_warnings.append(
            f"Crop '{crop_name}' (stage: {growth_stage}) is not in the nutrient "
            "reference table. Optimization skipped."
        )
        rec = Recommendation(
            farm_id=farm_id,
            crop_selection_id=crop_selection_id,
            soil_reading_ids=json.dumps(
                [r.id for r in readings] if readings else []
            ),
            weather_snapshot=json.dumps(weather_snapshot) if weather_snapshot else None,
            soil_summary_snapshot=json.dumps(soil_snapshot),
            ml_classifier_output=json.dumps(ml_classifier_json) if ml_classifier_json else None,
            ml_model_version="1.0.0",
            crop_nutrient_requirements=None,
            nutrient_requirement_source=req_source,
            optimization_status="skipped_no_requirements",
            optimization_result=None,
            estimated_total_cost=None,
            cost_currency=None,
            price_snapshot=None,
            warnings=json.dumps(all_warnings),
            assumptions=json.dumps(assumptions),
        )
        db.add(rec)
        await db.commit()
        await db.refresh(rec)
        return rec

    logger.info(
        "Nutrient requirements for %s/%s: N=%.1f P=%.1f K=%.1f kg/ha",
        crop_name, growth_stage,
        nutrient_reqs["N"], nutrient_reqs["P"], nutrient_reqs["K"],
    )

    # --- Step 8: Load fertilizer options ---
    options, price_warnings = await _load_fertilizer_options(
        db, request.allow_unverified_prices
    )
    all_warnings.extend(price_warnings)

    if not options:
        rec = Recommendation(
            farm_id=farm_id,
            crop_selection_id=crop_selection_id,
            soil_reading_ids=json.dumps([r.id for r in readings]),
            weather_snapshot=json.dumps(weather_snapshot) if weather_snapshot else None,
            soil_summary_snapshot=json.dumps(soil_snapshot),
            ml_classifier_output=json.dumps(ml_classifier_json) if ml_classifier_json else None,
            ml_model_version="1.0.0",
            crop_nutrient_requirements=json.dumps(nutrient_reqs),
            nutrient_requirement_source=req_source,
            optimization_status="skipped_no_prices",
            optimization_result=None,
            estimated_total_cost=None,
            cost_currency=None,
            price_snapshot=None,
            warnings=json.dumps(all_warnings),
            assumptions=json.dumps(assumptions),
        )
        db.add(rec)
        await db.commit()
        await db.refresh(rec)
        return rec

    # --- Step 9: Optimize ---
    opt_result: OptimizationResult = optimize_fertilizer_cost(
        options=options,
        n_required_kg_per_ha=nutrient_reqs["N"],
        p_required_kg_per_ha=nutrient_reqs["P"],
        k_required_kg_per_ha=nutrient_reqs["K"],
        area_ha=area_ha,
    )
    all_warnings.extend(opt_result.warnings)

    if not opt_result.is_optimal:
        assumptions.append(
            "Solver did not confirm global optimality. "
            f"Solver message: {opt_result.solver_message}"
        )

    # Build price snapshot for provenance
    price_snapshot_data = {
        opt.product_id: {
            "price_per_kg": opt.price_per_kg,
            "currency": opt.currency,
            "source": opt.price_source,
            "verified": opt.price_verified,
            "price_record_id": opt.price_record_id,
            "price_recorded_at": opt.price_recorded_at.isoformat(),
        }
        for opt in options
    }

    if opt_result.status == "feasible":
        items = _build_optimized_items(opt_result, options, area_ha)
        opt_result_json = [item.model_dump(mode="json") for item in items]
        total_cost = opt_result.total_cost_per_ha * area_ha
        cost_currency = opt_result.currency
    else:
        opt_result_json = None
        total_cost = None
        cost_currency = None

    # --- Step 10: Persist ---
    rec = Recommendation(
        farm_id=farm_id,
        crop_selection_id=crop_selection_id,
        soil_reading_ids=json.dumps([r.id for r in readings]),
        weather_snapshot=json.dumps(weather_snapshot) if weather_snapshot else None,
        soil_summary_snapshot=json.dumps(soil_snapshot),
        ml_classifier_output=json.dumps(ml_classifier_json) if ml_classifier_json else None,
        ml_model_version="1.0.0",
        crop_nutrient_requirements=json.dumps(nutrient_reqs),
        nutrient_requirement_source=req_source,
        optimization_status=opt_result.status,
        optimization_result=json.dumps(opt_result_json) if opt_result_json else None,
        estimated_total_cost=total_cost,
        cost_currency=cost_currency,
        price_snapshot=json.dumps(price_snapshot_data),
        warnings=json.dumps(all_warnings),
        assumptions=json.dumps(assumptions),
    )
    db.add(rec)
    await db.commit()
    await db.refresh(rec)

    logger.info(
        "Recommendation id=%s farm=%s crop=%s stage=%s status=%s cost=%.2f",
        rec.id, farm_id, crop_name, growth_stage,
        opt_result.status, total_cost or 0.0,
    )
    return rec


# ---------------------------------------------------------------------------
# Retrieval helpers
# ---------------------------------------------------------------------------

async def get_recommendation(
    db: AsyncSession, recommendation_id: str
) -> Recommendation:
    result = await db.execute(
        select(Recommendation).where(Recommendation.id == recommendation_id)
    )
    rec = result.scalar_one_or_none()
    if rec is None:
        raise NotFoundError("Recommendation", recommendation_id)
    return rec


async def list_recommendations(
    db: AsyncSession, farm_id: str
) -> list[Recommendation]:
    # Verify farm exists
    from app.models.farm import Farm
    farm_result = await db.execute(select(Farm).where(Farm.id == farm_id))
    if farm_result.scalar_one_or_none() is None:
        raise NotFoundError("Farm", farm_id)

    result = await db.execute(
        select(Recommendation)
        .where(Recommendation.farm_id == farm_id)
        .order_by(Recommendation.created_at.desc())
    )
    return list(result.scalars().all())


def recommendation_to_response(rec: Recommendation) -> RecommendationResponse:
    """Convert a Recommendation ORM object to the API response schema."""
    from app.schemas.recommendation import MLClassifierOutput

    # Deserialise JSON fields
    ml_output = None
    if rec.ml_classifier_output:
        try:
            raw = json.loads(rec.ml_classifier_output)
            if raw:
                ml_output = MLClassifierOutput(**raw)
        except Exception:
            pass

    opt_items = None
    if rec.optimization_result:
        try:
            raw_items = json.loads(rec.optimization_result)
            if raw_items:
                opt_items = [OptimizedFertilizerItem(**item) for item in raw_items]
        except Exception:
            pass

    nutrient_reqs = None
    nutrient_balance = None
    if rec.crop_nutrient_requirements:
        try:
            nutrient_reqs = json.loads(rec.crop_nutrient_requirements)
            if opt_items and nutrient_reqs:
                n_sup = sum(i.n_supplied_kg_per_ha for i in opt_items)
                p_sup = sum(i.p_supplied_kg_per_ha for i in opt_items)
                k_sup = sum(i.k_supplied_kg_per_ha for i in opt_items)
                nutrient_balance = NutrientBalance(
                    n_required_kg_per_ha=nutrient_reqs.get("N", 0),
                    p_required_kg_per_ha=nutrient_reqs.get("P", 0),
                    k_required_kg_per_ha=nutrient_reqs.get("K", 0),
                    n_supplied_kg_per_ha=round(n_sup, 4),
                    p_supplied_kg_per_ha=round(p_sup, 4),
                    k_supplied_kg_per_ha=round(k_sup, 4),
                    n_deficit_kg_per_ha=round(max(0, nutrient_reqs.get("N", 0) - n_sup), 4),
                    p_deficit_kg_per_ha=round(max(0, nutrient_reqs.get("P", 0) - p_sup), 4),
                    k_deficit_kg_per_ha=round(max(0, nutrient_reqs.get("K", 0) - k_sup), 4),
                )
        except Exception:
            pass

    warnings = []
    if rec.warnings:
        try:
            warnings = json.loads(rec.warnings)
        except Exception:
            warnings = [rec.warnings]

    assumptions_list = []
    if rec.assumptions:
        try:
            assumptions_list = json.loads(rec.assumptions)
        except Exception:
            assumptions_list = [rec.assumptions]

    return RecommendationResponse(
        id=rec.id,
        farm_id=rec.farm_id,
        crop_selection_id=rec.crop_selection_id,
        ml_classifier_suggestion=ml_output,
        nutrient_requirements=nutrient_reqs,
        nutrient_requirement_source=rec.nutrient_requirement_source,
        optimization_status=rec.optimization_status,
        recommended_fertilizers=opt_items,
        nutrient_balance=nutrient_balance,
        estimated_total_cost=rec.estimated_total_cost,
        cost_currency=rec.cost_currency,
        warnings=warnings,
        assumptions=assumptions_list,
        created_at=rec.created_at,
    )
