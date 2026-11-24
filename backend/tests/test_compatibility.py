from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from backend.app.db.base import Base
from backend.app.db.session import get_session
from backend.app.domain.compatibility import CompatibilityEngine, CompatibilityStatus
from backend.app.main import app
from backend.app.models.component import Component, ComponentCategory


def make_component(category: ComponentCategory, specifications: dict) -> Component:
    return Component(
        category=category,
        manufacturer="Fixture",
        model_name=f"{category.value} fixture",
        specifications=specifications,
        source_name="compatibility-test",
        source_id=f"{category.value}-{uuid4()}",
    )


def complete_components(overrides: dict[ComponentCategory, dict] | None = None) -> list[Component]:
    specs = {
        ComponentCategory.CPU: {"socket": "AM5", "supported_chipsets": ["B650"], "tdp_w": 65},
        ComponentCategory.MOTHERBOARD: {
            "socket": "AM5",
            "chipset": "B650",
            "form_factor": "ATX",
            "ram_type": "DDR5",
            "m2_slots": 1,
        },
        ComponentCategory.MEMORY: {"ram_type": "DDR5"},
        ComponentCategory.STORAGE: {"interface": "NVMe Gen4 x4"},
        ComponentCategory.GPU: {"tgp_w": 180, "psu_min_w": 600, "length_mm": 229},
        ComponentCategory.PSU: {"wattage_w": 600},
        ComponentCategory.CASE: {
            "supports_form_factors": ["ATX"],
            "max_gpu_length_mm": 229,
            "max_cpu_cooler_mm": 155,
        },
        ComponentCategory.CPU_COOLER: {"socket_support": ["AM5"], "height_mm": 155},
    }
    for category, changes in (overrides or {}).items():
        specs[category] = {**specs[category], **changes}
    return [make_component(category, values) for category, values in specs.items()]


def test_complete_configuration_is_compatible() -> None:
    result = CompatibilityEngine().check(complete_components())

    assert result.status is CompatibilityStatus.COMPATIBLE
    assert all(rule.status is CompatibilityStatus.COMPATIBLE for rule in result.rules)
    assert result.missing_specifications == []


def test_socket_and_power_conflicts_are_incompatible() -> None:
    components = complete_components(
        {
            ComponentCategory.MOTHERBOARD: {"socket": "LGA1700"},
            ComponentCategory.PSU: {"wattage_w": 400},
        }
    )

    result = CompatibilityEngine().check(components)

    assert result.status is CompatibilityStatus.INCOMPATIBLE
    assert result.rules[0].status is CompatibilityStatus.INCOMPATIBLE
    assert next(rule for rule in result.rules if rule.rule == "psu_power_budget").status is CompatibilityStatus.INCOMPATIBLE


def test_missing_critical_specification_is_incomplete() -> None:
    result = CompatibilityEngine().check(
        complete_components({ComponentCategory.GPU: {"length_mm": None}})
    )

    assert result.status is CompatibilityStatus.INCOMPLETE
    gpu_rule = next(rule for rule in result.rules if rule.rule == "gpu_case_length")
    assert gpu_rule.status is CompatibilityStatus.INCOMPLETE
    assert "gpu.length_mm" in gpu_rule.missing_specifications


def test_partial_configuration_is_unknown() -> None:
    result = CompatibilityEngine().check(
        [make_component(ComponentCategory.CPU, {"socket": "AM5", "tdp_w": 65})]
    )

    assert result.status is CompatibilityStatus.UNKNOWN
    assert all(rule.status is not CompatibilityStatus.COMPATIBLE for rule in result.rules)


def test_clearance_boundaries_are_compatible() -> None:
    result = CompatibilityEngine().check(complete_components())

    gpu_rule = next(rule for rule in result.rules if rule.rule == "gpu_case_length")
    cooler_rule = next(rule for rule in result.rules if rule.rule == "cpu_cooler_fit")
    assert gpu_rule.status is CompatibilityStatus.COMPATIBLE
    assert cooler_rule.status is CompatibilityStatus.COMPATIBLE


def test_catalog_api_validates_ids_and_duplicates() -> None:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    components = complete_components()
    with Session(engine) as session:
        session.add_all(components)
        session.commit()
        ids = [component.id for component in components]

    def override_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_session
    client = TestClient(app)
    try:
        compatible = client.post("/api/v1/compatibility/check", json={"component_ids": [str(value) for value in ids]})
        duplicate = client.post("/api/v1/compatibility/check", json={"component_ids": [str(ids[0]), str(ids[0])]})
        missing = client.post("/api/v1/compatibility/check", json={"component_ids": [str(uuid4())]})

        assert compatible.status_code == 200
        assert compatible.json()["status"] == "compatible"
        assert duplicate.status_code == 422
        assert missing.status_code == 404
    finally:
        app.dependency_overrides.clear()
        engine.dispose()
