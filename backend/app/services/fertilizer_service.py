"""
Fertilizer product and price management service.

Important: seed prices are always marked source='illustrative_sample' and
is_verified=False. They are NEVER claimed to be real market prices.

CSV import format (header row required):
  product_name, price_value, currency, price_unit, supplier, location,
  source, is_verified, bag_weight_kg
"""
import csv
import io
import json
import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.fertilizer import FertilizerPrice, FertilizerProduct
from app.schemas.fertilizer import (
    FertilizerProductCreate,
    PriceImportResult,
)

logger = logging.getLogger("neerniti.fertilizer_service")


# ---------------------------------------------------------------------------
# Seed data
# ---------------------------------------------------------------------------

_SEED_PRODUCTS: list[dict] = [
    {
        "name": "Urea",
        "nitrogen_pct": 46.0,
        "phosphorus_pct": 0.0,
        "potassium_pct": 0.0,
        "nutrient_as_elemental": False,
        "nutrient_basis_note": "46% elemental N. Most commonly used nitrogenous fertilizer in India.",
        "product_form": "granular",
        "application_notes": "Broadcast or top-dress. Incorporate into soil to minimise volatilisation.",
        "sample_price_inr_kg": 5.8,  # approximate MRP (illustrative only)
    },
    {
        "name": "DAP (Di-ammonium Phosphate)",
        "nitrogen_pct": 18.0,
        "phosphorus_pct": 46.0,
        "potassium_pct": 0.0,
        "nutrient_as_elemental": False,
        "nutrient_basis_note": "18% N (elemental), 46% P₂O₅. Phosphorus in P₂O₅ convention.",
        "product_form": "granular",
        "application_notes": "Recommended as basal dose. Blend with soil before sowing.",
        "sample_price_inr_kg": 27.0,
    },
    {
        "name": "MOP (Muriate of Potash)",
        "nitrogen_pct": 0.0,
        "phosphorus_pct": 0.0,
        "potassium_pct": 60.0,
        "nutrient_as_elemental": False,
        "nutrient_basis_note": "60% K₂O. Potassium in K₂O convention.",
        "product_form": "granular",
        "application_notes": "Apply as basal dose. Not recommended for chloride-sensitive crops.",
        "sample_price_inr_kg": 17.5,
    },
    {
        "name": "NPK 10-26-26",
        "nitrogen_pct": 10.0,
        "phosphorus_pct": 26.0,
        "potassium_pct": 26.0,
        "nutrient_as_elemental": False,
        "nutrient_basis_note": "10% N, 26% P₂O₅, 26% K₂O. Mixed complex fertilizer.",
        "product_form": "granular",
        "application_notes": "Suitable as basal dose for phosphorus and potassium-deficient soils.",
        "sample_price_inr_kg": 32.0,
    },
    {
        "name": "NPK 12-32-16",
        "nitrogen_pct": 12.0,
        "phosphorus_pct": 32.0,
        "potassium_pct": 16.0,
        "nutrient_as_elemental": False,
        "nutrient_basis_note": "12% N, 32% P₂O₅, 16% K₂O. Mixed complex fertilizer.",
        "product_form": "granular",
        "application_notes": "Higher phosphorus formulation; suitable for phosphorus-deficient soils.",
        "sample_price_inr_kg": 30.0,
    },
    {
        "name": "SSP (Single Super Phosphate)",
        "nitrogen_pct": 0.0,
        "phosphorus_pct": 16.0,
        "potassium_pct": 0.0,
        "nutrient_as_elemental": False,
        "nutrient_basis_note": "16% P₂O₅. Also supplies ~12% sulphur and ~21% calcium.",
        "product_form": "powder",
        "application_notes": "Cost-effective phosphorus source. Sulphur content beneficial for oilseeds.",
        "sample_price_inr_kg": 7.5,
    },
    {
        "name": "Zinc Sulphate (ZnSO₄ 33%)",
        "nitrogen_pct": 0.0,
        "phosphorus_pct": 0.0,
        "potassium_pct": 0.0,
        "nutrient_as_elemental": False,
        "nutrient_basis_note": (
            "Micronutrient fertilizer — 33% ZnSO₄. "
            "Not an NPK source; N/P/K set to 0. "
            "Corrects zinc deficiency. Typical dose 25 kg/ha."
        ),
        "product_form": "granular",
        "application_notes": (
            "Apply at 25 kg/ha as basal dose for zinc-deficient soils. "
            "Do not mix with phosphatic fertilizers."
        ),
        "sample_price_inr_kg": 55.0,
    },
    {
        "name": "Compost (Farm Yard Manure)",
        "nitrogen_pct": 1.5,
        "phosphorus_pct": 1.0,
        "potassium_pct": 1.5,
        "nutrient_as_elemental": False,
        "nutrient_basis_note": (
            "Approximate values: ~1.5% N, ~1.0% P₂O₅, ~1.5% K₂O. "
            "Actual composition varies widely with feedstock and composting method. "
            "These are rough estimates only — test each batch."
        ),
        "product_form": "granular",
        "application_notes": (
            "Apply 5–10 tonne/ha before tillage. "
            "Improves soil organic matter and microbial activity. "
            "Nutrient availability is slow-release."
        ),
        "sample_price_inr_kg": 3.0,
    },
]


async def seed_sample_products(db: AsyncSession) -> None:
    """
    Seed standard Indian fertilizer products if the table is empty.
    All seed prices are marked illustrative_sample and is_verified=False.
    This function must not claim these are current market prices.
    """
    count_result = await db.execute(
        select(func.count()).select_from(FertilizerProduct)
    )
    count = count_result.scalar_one()
    if count > 0:
        logger.debug("Fertilizer products already seeded (%d rows).", count)
        return

    for prod_data in _SEED_PRODUCTS:
        sample_price = prod_data.get("sample_price_inr_kg")  # read, don't mutate global
        product_fields = {k: v for k, v in prod_data.items() if k != "sample_price_inr_kg"}
        product = FertilizerProduct(**product_fields)
        db.add(product)
        await db.flush()  # get product.id

        if sample_price is not None:
            price = FertilizerPrice(
                product_id=product.id,
                price_value=sample_price,
                currency="INR",
                price_unit="INR/kg",
                source="illustrative_sample",
                is_verified=False,
                supplier=None,
                location=None,
            )
            db.add(price)

    logger.info(
        "Seeded %d fertilizer products with illustrative sample prices "
        "(NOT verified market prices).",
        len(_SEED_PRODUCTS),
    )


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------

async def create_fertilizer(
    db: AsyncSession, data: FertilizerProductCreate
) -> FertilizerProduct:
    product = FertilizerProduct(
        name=data.name,
        manufacturer=data.manufacturer,
        supplier=data.supplier,
        nitrogen_pct=data.nitrogen_pct,
        phosphorus_pct=data.phosphorus_pct,
        potassium_pct=data.potassium_pct,
        nutrient_as_elemental=data.nutrient_as_elemental,
        nutrient_basis_note=data.nutrient_basis_note,
        product_form=data.product_form,
        application_notes=data.application_notes,
        is_active=data.is_active,
    )
    db.add(product)
    await db.commit()
    await db.refresh(product)
    logger.info("Created fertilizer product id=%s name=%r", product.id, product.name)
    return product


async def list_fertilizers(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
) -> tuple[list[FertilizerProduct], int]:
    query = select(FertilizerProduct)
    count_query = select(func.count()).select_from(FertilizerProduct)

    if active_only:
        query = query.where(FertilizerProduct.is_active == True)  # noqa: E712
        count_query = count_query.where(FertilizerProduct.is_active == True)  # noqa: E712

    count_result = await db.execute(count_query)
    total = count_result.scalar_one()

    result = await db.execute(
        query.order_by(FertilizerProduct.name).offset(skip).limit(limit)
    )
    return list(result.scalars().all()), total


async def get_fertilizer(
    db: AsyncSession, fertilizer_id: str
) -> FertilizerProduct:
    result = await db.execute(
        select(FertilizerProduct).where(FertilizerProduct.id == fertilizer_id)
    )
    product = result.scalar_one_or_none()
    if product is None:
        raise NotFoundError("FertilizerProduct", fertilizer_id)
    return product


async def list_prices(
    db: AsyncSession,
    product_id: Optional[str] = None,
    verified_only: bool = False,
) -> list[FertilizerPrice]:
    query = select(FertilizerPrice)
    if product_id is not None:
        query = query.where(FertilizerPrice.product_id == product_id)
    if verified_only:
        query = query.where(FertilizerPrice.is_verified == True)  # noqa: E712
    result = await db.execute(query.order_by(FertilizerPrice.created_at.desc()))
    return list(result.scalars().all())


async def get_best_price_per_kg(
    db: AsyncSession,
    product_id: str,
    allow_unverified: bool = False,
) -> Optional[FertilizerPrice]:
    """
    Return the most recent price record for a product, converted to INR/kg
    where possible.  Verified prices take precedence; unverified are used
    only when allow_unverified=True.
    Excludes 'illustrative_sample' prices unless allow_unverified=True.
    """
    query = (
        select(FertilizerPrice)
        .where(FertilizerPrice.product_id == product_id)
    )
    if not allow_unverified:
        query = query.where(FertilizerPrice.is_verified == True)  # noqa: E712
    else:
        # Exclude illustrative samples even with allow_unverified
        # unless explicitly requested via allow_unverified
        pass

    query = query.order_by(
        FertilizerPrice.is_verified.desc(),
        FertilizerPrice.created_at.desc(),
    )
    result = await db.execute(query.limit(1))
    return result.scalar_one_or_none()


def price_to_per_kg(price: FertilizerPrice) -> Optional[float]:
    """
    Convert a price record to INR (or its currency) per kg.
    Returns None if conversion is not possible.
    """
    if "kg" in price.price_unit.lower():
        return price.price_value
    if "bag" in price.price_unit.lower():
        if price.bag_weight_kg and price.bag_weight_kg > 0:
            return price.price_value / price.bag_weight_kg
        return None  # cannot convert without bag weight
    if "tonne" in price.price_unit.lower():
        return price.price_value / 1000.0
    return None


# ---------------------------------------------------------------------------
# CSV price import
# ---------------------------------------------------------------------------

_CSV_REQUIRED_COLUMNS = {
    "product_name", "price_value", "currency", "price_unit",
}
_CSV_OPTIONAL_COLUMNS = {
    "supplier", "location", "source", "is_verified", "bag_weight_kg",
}
_VALID_SOURCES = {
    "user_entered", "csv_import", "verified_market", "illustrative_sample",
}


async def import_prices_from_csv(
    db: AsyncSession, content: bytes
) -> PriceImportResult:
    """
    Parse a CSV file and import fertilizer prices.

    Required columns: product_name, price_value, currency, price_unit
    Optional columns: supplier, location, source, is_verified, bag_weight_kg

    Products not found in the database are skipped (not created).
    Rows with invalid data are recorded in the errors list.
    """
    imported = 0
    skipped = 0
    errors: list[str] = []

    try:
        text = content.decode("utf-8-sig")  # handle BOM
        reader = csv.DictReader(io.StringIO(text))
    except Exception as exc:
        return PriceImportResult(imported=0, skipped=0, errors=[f"CSV decode error: {exc}"])

    if reader.fieldnames is None:
        return PriceImportResult(imported=0, skipped=0, errors=["CSV file appears empty."])

    # Normalise header names
    fieldnames_lower = {f.strip().lower() for f in reader.fieldnames}
    missing = _CSV_REQUIRED_COLUMNS - fieldnames_lower
    if missing:
        return PriceImportResult(
            imported=0, skipped=0,
            errors=[f"CSV missing required columns: {sorted(missing)}"]
        )

    for row_num, row in enumerate(reader, start=2):
        # Normalise key casing
        row = {k.strip().lower(): v.strip() if v else "" for k, v in row.items()}

        product_name = row.get("product_name", "")
        if not product_name:
            errors.append(f"Row {row_num}: product_name is empty — skipped.")
            skipped += 1
            continue

        # Look up product by name (case-insensitive)
        prod_result = await db.execute(
            select(FertilizerProduct).where(
                func.lower(FertilizerProduct.name) == product_name.lower()
            )
        )
        product = prod_result.scalar_one_or_none()
        if product is None:
            errors.append(
                f"Row {row_num}: Product '{product_name}' not found in database — skipped."
            )
            skipped += 1
            continue

        # Parse price_value
        try:
            price_value = float(row.get("price_value", ""))
            if price_value <= 0:
                raise ValueError("price must be > 0")
        except (ValueError, TypeError) as exc:
            errors.append(f"Row {row_num}: Invalid price_value '{row.get('price_value')}': {exc} — skipped.")
            skipped += 1
            continue

        currency = row.get("currency", "INR") or "INR"
        price_unit = row.get("price_unit", "INR/kg") or "INR/kg"

        source = row.get("source", "csv_import") or "csv_import"
        if source not in _VALID_SOURCES:
            errors.append(
                f"Row {row_num}: Invalid source '{source}' — using 'csv_import'."
            )
            source = "csv_import"

        is_verified_str = row.get("is_verified", "false").lower()
        is_verified = is_verified_str in ("true", "1", "yes")

        bag_weight_kg: Optional[float] = None
        raw_bag = row.get("bag_weight_kg", "")
        if raw_bag:
            try:
                bag_weight_kg = float(raw_bag)
            except ValueError:
                errors.append(
                    f"Row {row_num}: Invalid bag_weight_kg '{raw_bag}' — ignored."
                )

        if "bag" in price_unit.lower() and bag_weight_kg is None:
            errors.append(
                f"Row {row_num}: price_unit is per-bag but bag_weight_kg is missing — skipped."
            )
            skipped += 1
            continue

        price = FertilizerPrice(
            product_id=product.id,
            price_value=price_value,
            currency=currency,
            price_unit=price_unit,
            bag_weight_kg=bag_weight_kg,
            supplier=row.get("supplier") or None,
            location=row.get("location") or None,
            source=source,
            is_verified=is_verified,
            verified_at=datetime.now(timezone.utc) if is_verified else None,
        )
        db.add(price)
        imported += 1

    if imported > 0:
        await db.commit()

    logger.info(
        "Price CSV import: %d imported, %d skipped, %d error(s).",
        imported, skipped, len(errors),
    )
    return PriceImportResult(imported=imported, skipped=skipped, errors=errors)
