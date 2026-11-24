from uuid import UUID

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.app.db.base import Base
from backend.app.db.health import check_database_connection
from backend.app.models.component import Component, ComponentCategory
from backend.app.repositories.components import ComponentRepository


def test_database_connectivity_check_uses_a_read_only_query() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")

    assert check_database_connection(engine) is True


def test_component_repository_round_trip_isolated_from_postgres() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    repository = ComponentRepository()

    with Session(engine) as session:
        component = repository.create(
            session,
            Component(
                category=ComponentCategory.CPU,
                manufacturer="Example",
                model_name="Example CPU",
                specifications={"socket": "AM5", "cores": 8},
            ),
        )
        session.commit()
        component_id = component.id

        loaded = repository.get_by_id(session, component_id)

    assert isinstance(component_id, UUID)
    assert loaded is not None
    assert loaded.category is ComponentCategory.CPU
    assert loaded.specifications["socket"] == "AM5"
    assert loaded.currency == "USD"


def test_component_categories_are_limited_to_the_initial_eight() -> None:
    assert {category.value for category in ComponentCategory} == {
        "cpu",
        "gpu",
        "motherboard",
        "memory",
        "storage",
        "psu",
        "case",
        "cpu_cooler",
    }
