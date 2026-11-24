"""Component catalog read endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from ..db.session import get_session
from ..models.component import Component, ComponentCategory
from ..repositories.components import ComponentRepository

router = APIRouter(prefix="/components", tags=["components"])
repository = ComponentRepository()


class ComponentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    category: ComponentCategory
    manufacturer: str
    model_name: str
    specifications: dict
    price: str | None
    currency: str
    source_name: str | None
    source_id: str | None
    source_url: str | None
    source_updated_at: str | None
    source_license: str | None
    source_license_url: str | None
    source_attribution: str | None


class ComponentListResponse(BaseModel):
    items: list[ComponentResponse]
    total: int
    offset: int
    limit: int


def _to_response(component: Component) -> ComponentResponse:
    return ComponentResponse(
        id=component.id,
        category=component.category,
        manufacturer=component.manufacturer,
        model_name=component.model_name,
        specifications=component.specifications,
        price=str(component.price) if component.price is not None else None,
        currency=component.currency,
        source_name=component.source_name,
        source_id=component.source_id,
        source_url=component.source_url,
        source_updated_at=component.source_updated_at.isoformat() if component.source_updated_at else None,
        source_license=component.source_license,
        source_license_url=component.source_license_url,
        source_attribution=component.source_attribution,
    )


@router.get("", response_model=ComponentListResponse)
def list_components(
    category: ComponentCategory | None = Query(default=None),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    session: Session = Depends(get_session),
) -> ComponentListResponse:
    components, total = repository.list(session, category=category, offset=offset, limit=limit)
    return ComponentListResponse(
        items=[_to_response(component) for component in components],
        total=total,
        offset=offset,
        limit=limit,
    )


@router.get("/{component_id}", response_model=ComponentResponse)
def get_component(component_id: UUID, session: Session = Depends(get_session)) -> ComponentResponse:
    component = repository.get_by_id(session, component_id)
    if component is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Component not found")
    return _to_response(component)
