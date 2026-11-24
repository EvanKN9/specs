"""Component persistence operations."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.component import Component


class ComponentRepository:
    """Small repository boundary for component reads and writes."""

    def create(self, session: Session, component: Component) -> Component:
        session.add(component)
        session.flush()
        return component

    def get_by_id(self, session: Session, component_id: UUID) -> Component | None:
        return session.scalar(select(Component).where(Component.id == component_id))
