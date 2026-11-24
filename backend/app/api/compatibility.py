"""Compatibility checking API."""

from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..db.session import get_session
from ..domain.compatibility import CompatibilityEngine, CompatibilityStatus, RuleResult
from ..models.component import ComponentCategory
from ..repositories.components import ComponentRepository

router = APIRouter(prefix="/compatibility", tags=["compatibility"])
repository = ComponentRepository()
engine = CompatibilityEngine()


class CompatibilityCheckRequest(BaseModel):
    component_ids: list[UUID] = Field(min_length=1, max_length=32)


class RuleResultResponse(BaseModel):
    rule: str
    status: Literal["compatible", "incompatible", "unknown", "incomplete"]
    explanation: str
    component_ids: list[UUID]
    missing_specifications: list[str]
    details: dict[str, object]


class CompatibilityCheckResponse(BaseModel):
    status: Literal["compatible", "incompatible", "unknown", "incomplete"]
    component_ids: list[UUID]
    rules: list[RuleResultResponse]
    explanations: list[str]
    missing_specifications: list[str]


def _rule_response(rule: RuleResult) -> RuleResultResponse:
    return RuleResultResponse(
        rule=rule.rule,
        status=rule.status.value,
        explanation=rule.explanation,
        component_ids=rule.component_ids,
        missing_specifications=rule.missing_specifications,
        details=rule.details,
    )


@router.post("/check", response_model=CompatibilityCheckResponse)
def check_compatibility(
    request: CompatibilityCheckRequest,
    session: Session = Depends(get_session),
) -> CompatibilityCheckResponse:
    if len(set(request.component_ids)) != len(request.component_ids):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Duplicate component IDs are not allowed.",
        )

    components = repository.get_by_ids(session, request.component_ids)
    found_ids = {component.id for component in components}
    missing_ids = [component_id for component_id in request.component_ids if component_id not in found_ids]
    if missing_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "Component IDs were not found.", "component_ids": [str(component_id) for component_id in missing_ids]},
        )

    counts: dict[ComponentCategory, int] = {}
    for component in components:
        counts[component.category] = counts.get(component.category, 0) + 1
    singleton_categories = {
        ComponentCategory.CPU,
        ComponentCategory.MOTHERBOARD,
        ComponentCategory.PSU,
        ComponentCategory.CASE,
        ComponentCategory.CPU_COOLER,
    }
    duplicates = [category.value for category in singleton_categories if counts.get(category, 0) > 1]
    if duplicates:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"message": "Only one component is supported for these categories.", "categories": sorted(duplicates)},
        )

    result = engine.check([next(component for component in components if component.id == component_id) for component_id in request.component_ids])
    return CompatibilityCheckResponse(
        status=result.status.value,
        component_ids=result.component_ids,
        rules=[_rule_response(rule) for rule in result.rules],
        explanations=result.explanations,
        missing_specifications=result.missing_specifications,
    )
