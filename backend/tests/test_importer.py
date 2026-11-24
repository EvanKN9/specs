from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.app.db.base import Base
from backend.app.models.component import Component, ComponentCategory
from backend.scripts.import_components import import_dataset


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
