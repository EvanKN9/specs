from sqlalchemy import create_engine
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.db.base import Base
from backend.app.models.component import Component, ComponentCategory
from backend.scripts.import_components import (
    DEMO_PRICING_PATH,
    SUPPLEMENTAL_DATASET_PATH,
    apply_demo_pricing,
    import_dataset,
    import_supplemental_dataset,
    load_json,
)


def _dataset() -> dict:
    return {
        "_meta": {
            "version": "test",
            "license": "CC BY 4.0",
            "license_url": "https://creativecommons.org/licenses/by/4.0/",
            "attribution_required": "Test attribution",
        },
        "cpu": [
            {
                "id": "cpu-example",
                "vendor": "Example",
                "model": "Example CPU",
                "socket": "AM5",
                "source": "https://example.test/cpu",
                "last_verified": "2026-11-01",
            }
        ],
        "gpu": [],
        "motherboard": [],
        "ram": [],
        "storage": [],
        "psu": [],
        "case": [],
    }


def test_import_is_idempotent_and_preserves_source_metadata() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        first = import_dataset(_dataset(), session)
        second = import_dataset(_dataset(), session)

        rows = session.query(Component).all()

    assert first["created"] == 1
    assert first["updated"] == 0
    assert second["created"] == 0
    assert second["updated"] == 1
    assert len(rows) == 1
    assert rows[0].category is ComponentCategory.CPU
    assert rows[0].source_id == "cpu-example"
    assert rows[0].source_license == "CC BY 4.0"
    assert rows[0].price is None
    engine.dispose()


def test_supplemental_coolers_and_demo_prices_are_repeatable() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    cooler_fixture = load_json(SUPPLEMENTAL_DATASET_PATH)
    pricing_fixture = load_json(DEMO_PRICING_PATH)

    with Session(engine) as session:
        import_dataset(_dataset(), session)
        first_coolers = import_supplemental_dataset(cooler_fixture, session)
        first_pricing = apply_demo_pricing(pricing_fixture, session)
        second_coolers = import_supplemental_dataset(cooler_fixture, session)
        second_pricing = apply_demo_pricing(pricing_fixture, session)
        rows = session.scalars(select(Component)).all()

    coolers = [row for row in rows if row.category is ComponentCategory.CPU_COOLER]
    assert first_coolers == {"created": 6, "updated": 0, "total": 6}
    assert second_coolers == {"created": 0, "updated": 6, "total": 6}
    assert first_pricing["priced"] == second_pricing["priced"] == 7
    assert first_pricing["unpriced"] == second_pricing["unpriced"] == []
    assert len(coolers) == 6
    assert all(row.price_is_illustrative for row in rows)
    assert all(row.price_source == pricing_fixture["price_source"] for row in rows)
    assert all(row.specifications["height_mm"] > 0 for row in coolers)
    assert all(row.specifications["socket_support"] for row in coolers)
    engine.dispose()
