"""Idempotently import the TechFuelHQ PC Builder Parts dataset."""

import argparse
from collections import Counter
from datetime import datetime, timezone
from decimal import Decimal
import json
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

from sqlalchemy.engine import make_url
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..app.db.session import get_database_url, get_engine
from ..app.models.component import Component, ComponentCategory
from ..app.repositories.components import ComponentRepository

DATASET_URL = "https://techfuelhq.com/data/pc-builder-parts.json"
DATASET_NAME = "TechFuelHQ PC Builder Parts Dataset"
EXPECTED_DATABASE = "specs_dev"
CATEGORY_MAP = {
    "cpu": ComponentCategory.CPU,
    "gpu": ComponentCategory.GPU,
    "motherboard": ComponentCategory.MOTHERBOARD,
    "ram": ComponentCategory.MEMORY,
    "storage": ComponentCategory.STORAGE,
    "psu": ComponentCategory.PSU,
    "case": ComponentCategory.CASE,
}
SUPPLEMENTAL_DATASET_PATH = Path(__file__).resolve().parents[1] / "data" / "cpu_coolers.json"
DEMO_PRICING_PATH = Path(__file__).resolve().parents[1] / "data" / "demo_pricing.json"
IDENTITY_FIELDS = {"id", "vendor", "model", "source", "last_verified"}


def load_dataset(input_path: Path | None) -> dict[str, Any]:
    if input_path is not None:
        return json.loads(input_path.read_text(encoding="utf-8"))
    request = Request(DATASET_URL, headers={"User-Agent": "SPECS classroom MVP importer"})
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_verified_at(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value).replace(tzinfo=timezone.utc)


def database_name() -> str | None:
    return make_url(get_database_url()).database


def validate_database_target() -> None:
    if database_name() != EXPECTED_DATABASE:
        raise RuntimeError(f"Refusing import: configured database must be {EXPECTED_DATABASE}.")


def make_component(
    category_name: str,
    row: dict[str, Any],
    metadata: dict[str, Any],
) -> Component:
    category = CATEGORY_MAP[category_name]
    source_id = row.get("id")
    manufacturer = row.get("vendor")
    model_name = row.get("model")
    if not source_id or not manufacturer or not model_name:
        raise ValueError(f"Dataset row is missing an import identity in category {category_name!r}.")

    specifications = {
        key: value for key, value in row.items() if key not in IDENTITY_FIELDS
    }
    specifications["_dataset_category"] = category_name
    return Component(
        category=category,
        manufacturer=manufacturer,
        model_name=model_name,
        specifications=specifications,
        price=None,
        currency="USD",
        source_name=DATASET_NAME,
        source_id=source_id,
        source_url=row.get("source"),
        source_updated_at=parse_verified_at(row.get("last_verified")),
        source_license=metadata.get("license"),
        source_license_url=metadata.get("license_url"),
        source_attribution=metadata.get("attribution_required"),
    )


def make_supplemental_component(record: dict[str, Any], dataset: dict[str, Any]) -> Component:
    return Component(
        category=ComponentCategory.CPU_COOLER,
        manufacturer=record["manufacturer"],
        model_name=record["model_name"],
        specifications={**record["specifications"], "_supplemental_dataset": dataset["dataset_name"]},
        price=None,
        currency="USD",
        source_name=dataset["dataset_name"],
        source_id=record["source_id"],
        source_url=record["source_url"],
        source_updated_at=parse_verified_at(record.get("verified_at")),
        source_attribution=dataset.get("attribution"),
    )


def missing_field_report(dataset: dict[str, Any]) -> dict[str, dict[str, int]]:
    report: dict[str, dict[str, int]] = {}
    for category_name in CATEGORY_MAP:
        rows = dataset.get(category_name, [])
        field_counts: Counter[str] = Counter()
        fields = set().union(*(row.keys() for row in rows)) if rows else set()
        fields.update(IDENTITY_FIELDS)
        for row in rows:
            for field in fields:
                value = row.get(field)
                if value is None or value == "":
                    field_counts[field] += 1
        report[category_name] = dict(sorted(field_counts.items()))
    return report


def import_dataset(dataset: dict[str, Any], session: Session) -> dict[str, Any]:
    repository = ComponentRepository()
    metadata = dataset.get("_meta", {})
    counts: Counter[str] = Counter()
    created = 0
    updated = 0
    unsupported = sorted(
        key for key, value in dataset.items() if isinstance(value, list) and key not in CATEGORY_MAP
    )
    imported_categories = {category.value for category in CATEGORY_MAP.values()}
    missing_supported_categories = sorted(
        category.value for category in ComponentCategory if category.value not in imported_categories
    )

    for source_category, category in CATEGORY_MAP.items():
        for row in dataset.get(source_category, []):
            component, was_created = repository.upsert(
                session,
                make_component(source_category, row, metadata),
            )
            counts[category.value] += 1
            if was_created:
                created += 1
            else:
                updated += 1
    session.commit()
    return {
        "dataset_version": metadata.get("version"),
        "rows_seen": sum(counts.values()),
        "created": created,
        "updated": updated,
        "by_category": dict(sorted(counts.items())),
        "unsupported_categories": unsupported,
        "missing_supported_categories": missing_supported_categories,
        "missing_fields": missing_field_report(dataset),
        "prices_imported": 0,
        "price_note": "TechFuelHQ removed prices; imported prices are intentionally NULL.",
    }


def import_supplemental_dataset(dataset: dict[str, Any], session: Session) -> dict[str, int]:
    repository = ComponentRepository()
    created = 0
    updated = 0
    for record in dataset["records"]:
        _, was_created = repository.upsert(session, make_supplemental_component(record, dataset))
        if was_created:
            created += 1
        else:
            updated += 1
    return {"created": created, "updated": updated, "total": len(dataset["records"])}


def apply_demo_pricing(fixture: dict[str, Any], session: Session) -> dict[str, Any]:
    repository = ComponentRepository()
    priced = 0
    unpriced: list[str] = []
    for component in session.scalars(select(Component)).all():
        override = fixture.get("overrides", {}).get(component.source_id)
        if override is None:
            base = fixture["category_defaults"].get(component.category.value)
            if base is None:
                unpriced.append(str(component.id))
                continue
            tier_addition = fixture.get("tier_additions", {}).get(
                component.specifications.get("performance_tier"), 0.0
            )
            override = float(base) + float(tier_addition)
        repository.set_price(
            session,
            component,
            price=Decimal(str(override)),
            currency=fixture["currency"],
            source=fixture["price_source"],
            illustrative=bool(fixture["is_live"] is False and fixture["is_retailer_verified"] is False),
        )
        priced += 1
    session.commit()
    return {
        "fixture_name": fixture["fixture_name"],
        "priced": priced,
        "unpriced": unpriced,
        "total": priced + len(unpriced),
        "is_live": fixture["is_live"],
        "is_retailer_verified": fixture["is_retailer_verified"],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        help="Use a local JSON file instead of downloading the official dataset URL.",
    )
    parser.add_argument("--coolers", type=Path, default=SUPPLEMENTAL_DATASET_PATH)
    parser.add_argument("--pricing", type=Path, default=DEMO_PRICING_PATH)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    validate_database_target()
    dataset = load_dataset(args.input)
    coolers = load_json(args.coolers)
    pricing = load_json(args.pricing)
    with Session(get_engine()) as session:
        summary = import_dataset(dataset, session)
        summary["supplemental"] = import_supplemental_dataset(coolers, session)
        summary["pricing"] = apply_demo_pricing(pricing, session)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
