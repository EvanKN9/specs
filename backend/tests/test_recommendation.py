from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from backend.app.db.base import Base
from backend.app.db.session import get_session
from backend.app.domain.recommendation import RecommendationInfeasible, RecommendationPreferences, RecommendationService
from backend.app.main import app
from backend.app.models.component import Component, ComponentCategory


def priced(category: ComponentCategory, source_id: str, price: str, specifications: dict) -> Component:
    return Component(
        category=category,
        manufacturer="Fixture",
        model_name=source_id,
        specifications=specifications,
        price=Decimal(price),
        currency="USD",
        price_source="test illustrative fixture",
        price_is_illustrative=True,
        source_name="recommendation-test",
        source_id=source_id,
    )


def catalog() -> list[Component]:
    return [
        priced(ComponentCategory.CPU, "cpu-entry", "199.99", {"socket": "AM5", "supported_chipsets": ["B650"], "tdp_w": 65, "cores": 6, "threads": 12, "performance_tier": "mid"}),
        priced(ComponentCategory.CPU, "cpu-high", "299.99", {"socket": "AM5", "supported_chipsets": ["B650"], "tdp_w": 120, "cores": 8, "threads": 16, "performance_tier": "high"}),
        priced(ComponentCategory.GPU, "gpu-mid", "229.99", {"tgp_w": 180, "psu_min_w": 600, "length_mm": 229, "vram_gb": 8, "performance_tier": "mid"}),
        priced(ComponentCategory.GPU, "gpu-high", "399.99", {"tgp_w": 245, "psu_min_w": 700, "length_mm": 267, "vram_gb": 12, "performance_tier": "high"}),
        priced(ComponentCategory.MOTHERBOARD, "mb-b650", "149.99", {"socket": "AM5", "chipset": "B650", "form_factor": "ATX", "ram_type": "DDR5", "m2_slots": 2}),
        priced(ComponentCategory.MEMORY, "ram-32", "79.99", {"ram_type": "DDR5", "capacity_gb": 32}),
        priced(ComponentCategory.MEMORY, "ram-64", "159.99", {"ram_type": "DDR5", "capacity_gb": 64}),
        priced(ComponentCategory.STORAGE, "ssd-2tb", "89.99", {"interface": "NVMe Gen4 x4", "capacity_gb": 2000, "read_mbps": 7000}),
        priced(ComponentCategory.STORAGE, "ssd-4tb", "159.99", {"interface": "NVMe Gen4 x4", "capacity_gb": 4000, "read_mbps": 7000}),
        priced(ComponentCategory.PSU, "psu-600", "89.99", {"wattage_w": 600}),
        priced(ComponentCategory.PSU, "psu-850", "119.99", {"wattage_w": 850}),
        priced(ComponentCategory.CASE, "case-atx", "79.99", {"supports_form_factors": ["ATX"], "max_gpu_length_mm": 300, "max_cpu_cooler_mm": 160}),
        priced(ComponentCategory.CPU_COOLER, "cooler-155", "39.99", {"socket_support": ["AM5"], "height_mm": 155}),
    ]


def test_recommendations_fit_budget_and_storage_requirement() -> None:
    service = RecommendationService()
    components = catalog()

    gaming = service.recommend(
        components,
        RecommendationPreferences(Decimal("1000"), "gaming", 1000, "any", "1440p"),
    )
    development = service.recommend(
        components,
        RecommendationPreferences(Decimal("1400"), "development", 3000, "preferred", None),
    )

    assert gaming.compatibility.status.value == "compatible"
    assert gaming.total_price <= Decimal("1000")
    assert development.total_price <= Decimal("1400")
    assert any(component.source_id == "ssd-4tb" for component in development.components)
    assert set(development.explanations) == {"cpu", "gpu", "motherboard", "memory", "psu"}


def test_recommendation_rejects_infeasible_budget_and_unavailable_wifi_requirement() -> None:
    service = RecommendationService()

    try:
        service.recommend(catalog(), RecommendationPreferences(Decimal("500"), "general", 1000, "any", None))
        assert False, "expected infeasible budget"
    except RecommendationInfeasible as exc:
        assert "budget" in str(exc).lower()

    try:
        service.recommend(catalog(), RecommendationPreferences(Decimal("1400"), "general", 1000, "required", None))
        assert False, "expected unavailable Wi-Fi requirement"
    except RecommendationInfeasible as exc:
        assert "wi-fi" in str(exc).lower()


def test_recommendation_api_returns_complete_explainable_build() -> None:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    components = catalog()
    with Session(engine) as session:
        session.add_all(components)
        session.commit()

    def override_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_session
    try:
        response = TestClient(app).post(
            "/api/v1/builds/recommend",
            json={
                "budget_usd": 1000,
                "workload": "gaming",
                "minimum_storage_gb": 1000,
                "wifi_preference": "any",
                "gaming_resolution": "1440p",
            },
        )

        body = response.json()
        assert response.status_code == 200
        assert body["status"] == "compatible"
        assert Decimal(body["estimated_total_price_usd"]) <= Decimal("1000")
        assert body["compatibility"]["status"] == "compatible"
        assert body["explanations"]["cpu"]
        assert body["explanations"]["psu"]
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_gaming_request_requires_resolution() -> None:
    response = TestClient(app).post(
        "/api/v1/builds/recommend",
        json={"budget_usd": 1000, "workload": "gaming"},
    )

    assert response.status_code == 422
