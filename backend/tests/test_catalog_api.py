from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from backend.app.db.base import Base
from backend.app.db.session import get_session
from backend.app.main import app
from backend.app.models.component import Component, ComponentCategory


def _client_with_components() -> tuple[TestClient, object]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        session.add_all(
            [
                Component(
                    category=ComponentCategory.CPU,
                    manufacturer="AMD",
                    model_name="Ryzen Example",
                    specifications={"socket": "AM5"},
                    source_name="fixture",
                    source_id="cpu-1",
                ),
                Component(
                    category=ComponentCategory.GPU,
                    manufacturer="Example",
                    model_name="Example GPU",
                    specifications={"length_mm": 250},
                    source_name="fixture",
                    source_id="gpu-1",
                ),
                Component(
                    category=ComponentCategory.CPU,
                    manufacturer="Intel",
                    model_name="Core Example",
                    specifications={"socket": "LGA1851"},
                    source_name="fixture",
                    source_id="cpu-2",
                ),
            ]
        )
        session.commit()

    def override_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_session
    return TestClient(app), engine


def test_component_list_supports_category_filter_and_bounded_pagination() -> None:
    client, engine = _client_with_components()
    try:
        response = client.get("/api/v1/components", params={"category": "cpu", "limit": 1})

        assert response.status_code == 200
        body = response.json()
        assert body["total"] == 2
        assert body["limit"] == 1
        assert len(body["items"]) == 1
        assert body["items"][0]["category"] == "cpu"
        assert client.get("/api/v1/components", params={"limit": 101}).status_code == 422
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_component_retrieval_and_missing_id() -> None:
    client, engine = _client_with_components()
    try:
        listing = client.get("/api/v1/components").json()
        component_id = listing["items"][0]["id"]

        found = client.get(f"/api/v1/components/{component_id}")
        missing = client.get(f"/api/v1/components/{uuid4()}")

        assert found.status_code == 200
        assert found.json()["source_id"] == "cpu-1"
        assert missing.status_code == 404
    finally:
        app.dependency_overrides.clear()
        engine.dispose()
