"""Component persistence operations."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..models.component import Component, ComponentCategory


class ComponentRepository:
    """Small repository boundary for component reads and writes."""

    def create(self, session: Session, component: Component) -> Component:
        session.add(component)
        session.flush()
        return component

    def get_by_id(self, session: Session, component_id: UUID) -> Component | None:
        return session.scalar(select(Component).where(Component.id == component_id))

    def get_by_ids(self, session: Session, component_ids: list[UUID]) -> list[Component]:
        """Return catalog components matching the requested IDs."""
        return list(session.scalars(select(Component).where(Component.id.in_(component_ids))))

    def list_all(self, session: Session) -> list[Component]:
        """Return the complete catalog in a stable order."""
        return list(
            session.scalars(
                select(Component).order_by(Component.category, Component.manufacturer, Component.model_name, Component.id)
            )
        )

    def get_by_source_identity(
        self, session: Session, source_name: str, source_id: str
    ) -> Component | None:
        return session.scalar(
            select(Component).where(
                Component.source_name == source_name,
                Component.source_id == source_id,
            )
        )

    def set_price(
        self,
        session: Session,
        component: Component,
        *,
        price,
        currency: str,
        source: str,
        illustrative: bool,
    ) -> Component:
        component.price = price
        component.currency = currency
        component.price_source = source
        component.price_is_illustrative = illustrative
        session.flush()
        return component

    def list(
        self,
        session: Session,
        *,
        category: ComponentCategory | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Component], int]:
        filters = [Component.category == category] if category else []
        items = list(
            session.scalars(
                select(Component)
                .where(*filters)
                .order_by(Component.category, Component.manufacturer, Component.model_name, Component.id)
                .offset(offset)
                .limit(limit)
            )
        )
        total = session.scalar(select(func.count()).select_from(Component).where(*filters)) or 0
        return items, total

    def upsert(self, session: Session, component: Component) -> tuple[Component, bool]:
        """Insert or update one source-owned component, returning (record, created)."""
        if not component.source_name or not component.source_id:
            raise ValueError("idempotent imports require source_name and source_id")
        existing = self.get_by_source_identity(session, component.source_name, component.source_id)
        if existing is None:
            session.add(component)
            session.flush()
            return component, True

        for attribute in (
            "category",
            "manufacturer",
            "model_name",
            "specifications",
            "currency",
            "source_url",
            "source_updated_at",
            "source_license",
            "source_license_url",
            "source_attribution",
        ):
            setattr(existing, attribute, getattr(component, attribute))
        if component.price is not None:
            existing.price = component.price
            existing.price_source = component.price_source
            existing.price_is_illustrative = component.price_is_illustrative
        session.flush()
        return existing, False
