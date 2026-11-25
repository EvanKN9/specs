"""Deterministic build recommendation API."""

from decimal import Decimal
from enum import Enum
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, model_validator
from sqlalchemy.orm import Session

from ..db.session import get_session
from ..domain.compatibility import CompatibilityStatus
from ..domain.recommendation import (
    RecommendationInfeasible,
    RecommendationPreferences,
    RecommendationService,
)
from ..models.component import ComponentCategory
from ..repositories.components import ComponentRepository
from .compatibility import CompatibilityCheckResponse, _rule_response
from .components import ComponentResponse, _to_response

router = APIRouter(prefix="/builds", tags=["builds"])
repository = ComponentRepository()
service = RecommendationService()


class Workload(str, Enum):
    GAMING = "gaming"
    DEVELOPMENT = "development"
    CONTENT_CREATION = "content_creation"
    PRODUCTIVITY = "productivity"
    GENERAL = "general"


class WifiPreference(str, Enum):
    ANY = "any"
    PREFERRED = "preferred"
    REQUIRED = "required"


class GamingResolution(str, Enum):
    P1080 = "1080p"
    P1440 = "1440p"
    K4 = "4k"


class RecommendationRequest(BaseModel):
    budget_usd: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    workload: Workload
    minimum_storage_gb: int = Field(default=1000, ge=1, le=100000)
    wifi_preference: WifiPreference = WifiPreference.ANY
    gaming_resolution: GamingResolution | None = None

    @model_validator(mode="after")
    def validate_resolution(self) -> "RecommendationRequest":
        if self.workload is Workload.GAMING and self.gaming_resolution is None:
            raise ValueError("gaming_resolution is required for the gaming workload")
        return self


class RecommendationResponse(BaseModel):
    status: Literal["compatible"]
    budget_usd: str
    estimated_total_price_usd: str
    workload: Workload
    minimum_storage_gb: int
    selected_components: list[ComponentResponse]
    compatibility: CompatibilityCheckResponse
    score: float
    scoring_summary: dict[str, object]
    explanations: dict[str, str]


@router.post("/recommend", response_model=RecommendationResponse)
def recommend_build(
    request: RecommendationRequest,
    session: Session = Depends(get_session),
) -> RecommendationResponse:
    preferences = RecommendationPreferences(
        budget_usd=request.budget_usd,
        workload=request.workload.value,
        minimum_storage_gb=request.minimum_storage_gb,
        wifi_preference=request.wifi_preference.value,
        gaming_resolution=request.gaming_resolution.value if request.gaming_resolution else None,
    )
    try:
        recommendation = service.recommend(repository.list_all(session), preferences)
    except RecommendationInfeasible as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "infeasible_recommendation", "message": str(exc)},
        ) from exc

    if recommendation.compatibility.status is not CompatibilityStatus.COMPATIBLE:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal recommendation validation failed.",
        )
    compatibility = recommendation.compatibility
    return RecommendationResponse(
        status="compatible",
        budget_usd=str(request.budget_usd),
        estimated_total_price_usd=str(recommendation.total_price),
        workload=request.workload,
        minimum_storage_gb=request.minimum_storage_gb,
        selected_components=[_to_response(component) for component in recommendation.components],
        compatibility=CompatibilityCheckResponse(
            status=compatibility.status.value,
            component_ids=compatibility.component_ids,
            rules=[_rule_response(rule) for rule in compatibility.rules],
            explanations=compatibility.explanations,
            missing_specifications=compatibility.missing_specifications,
        ),
        score=recommendation.score,
        scoring_summary=recommendation.scoring_summary,
        explanations=recommendation.explanations,
    )
