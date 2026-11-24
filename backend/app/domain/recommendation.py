"""Deterministic catalog-based build recommendation service."""

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from ..models.component import Component, ComponentCategory
from .compatibility import CompatibilityEngine, CompatibilityResult, CompatibilityStatus


class RecommendationInfeasible(ValueError):
    """Raised when the catalog cannot satisfy the requested constraints."""


@dataclass(frozen=True)
class RecommendationPreferences:
    budget_usd: Decimal
    workload: str
    minimum_storage_gb: int
    wifi_preference: str
    gaming_resolution: str | None


@dataclass(frozen=True)
class BuildRecommendation:
    components: list[Component]
    total_price: Decimal
    compatibility: CompatibilityResult
    score: float
    scoring_summary: dict[str, Any]
    explanations: dict[str, str]


TIER_SCORE = {"entry": 25.0, "mid": 50.0, "high": 75.0, "flagship": 100.0}
MAX_PLATFORMS = 40
SHORTLIST_LIMITS = {
    ComponentCategory.CPU: 10,
    ComponentCategory.GPU: 10,
    ComponentCategory.MOTHERBOARD: 8,
    ComponentCategory.MEMORY: 6,
    ComponentCategory.STORAGE: 6,
    ComponentCategory.PSU: 6,
    ComponentCategory.CASE: 6,
    ComponentCategory.CPU_COOLER: 4,
}


class RecommendationService:
    """Search the current catalog with explicit, repeatable scoring assumptions."""

    def __init__(self, compatibility_engine: CompatibilityEngine | None = None) -> None:
        self.compatibility_engine = compatibility_engine or CompatibilityEngine()

    def recommend(
        self,
        components: list[Component],
        preferences: RecommendationPreferences,
    ) -> BuildRecommendation:
        if preferences.wifi_preference == "required":
            raise RecommendationInfeasible(
                "Wi-Fi is required, but the catalog has no structured motherboard Wi-Fi specification."
            )

        by_category = self._candidate_categories(components, preferences)
        missing_categories = [
            category.value
            for category in ComponentCategory
            if not by_category[category]
        ]
        if missing_categories:
            raise RecommendationInfeasible(
                "The catalog lacks complete, priced candidates for: " + ", ".join(missing_categories)
            )

        cheapest_complete = sum(
            (min(component.price for component in by_category[category]) for category in ComponentCategory),
            Decimal("0"),
        )
        if cheapest_complete > preferences.budget_usd:
            raise RecommendationInfeasible(
                f"Budget ${preferences.budget_usd:.2f} is below the cheapest complete catalog set "
                f"(${cheapest_complete:.2f})."
            )

        platforms = self._platform_candidates(by_category, preferences)
        if not platforms:
            raise RecommendationInfeasible(
                "No CPU, motherboard, memory, and storage combination satisfies the catalog constraints."
            )

        best: BuildRecommendation | None = None
        gpu_options = self._shortlist(by_category[ComponentCategory.GPU], preferences, ComponentCategory.GPU)
        psu_options = self._shortlist(by_category[ComponentCategory.PSU], preferences, ComponentCategory.PSU)
        case_options = self._shortlist(by_category[ComponentCategory.CASE], preferences, ComponentCategory.CASE)
        cooler_options = self._shortlist(
            by_category[ComponentCategory.CPU_COOLER], preferences, ComponentCategory.CPU_COOLER
        )
        for platform in platforms:
            cpu, motherboard, memory, storage = platform
            for gpu in gpu_options:
                for psu in psu_options:
                    for case in case_options:
                        if not self._case_gpu_fit(gpu, case):
                            continue
                        if not self._case_form_factor_fit(motherboard, case):
                            continue
                        for cooler in cooler_options:
                            if not self._cooler_fit(cpu, cooler, case):
                                continue
                            if not self._power_fit(cpu, gpu, psu):
                                continue
                            selected = [cpu, gpu, motherboard, memory, storage, psu, case, cooler]
                            total = sum((component.price or Decimal("0") for component in selected), Decimal("0"))
                            if total > preferences.budget_usd:
                                continue
                            compatibility = self.compatibility_engine.check(selected)
                            if compatibility.status is not CompatibilityStatus.COMPATIBLE:
                                continue
                            score, summary = self._score(selected, preferences, total)
                            candidate = BuildRecommendation(
                                components=selected,
                                total_price=total,
                                compatibility=compatibility,
                                score=score,
                                scoring_summary=summary,
                                explanations=self._explanations(selected, preferences, summary),
                            )
                            if best is None or self._candidate_key(candidate) > self._candidate_key(best):
                                best = candidate
        if best is None:
            raise RecommendationInfeasible(
                "No complete compatible configuration fits the requested budget and catalog constraints."
            )
        return best

    def _candidate_categories(
        self,
        components: list[Component],
        preferences: RecommendationPreferences,
    ) -> dict[ComponentCategory, list[Component]]:
        result: dict[ComponentCategory, list[Component]] = {category: [] for category in ComponentCategory}
        required_fields = {
            ComponentCategory.CPU: ("socket", "supported_chipsets", "tdp_w"),
            ComponentCategory.MOTHERBOARD: ("socket", "chipset", "form_factor", "ram_type", "m2_slots"),
            ComponentCategory.MEMORY: ("ram_type", "capacity_gb"),
            ComponentCategory.STORAGE: ("interface", "capacity_gb"),
            ComponentCategory.GPU: ("tgp_w", "psu_min_w", "length_mm"),
            ComponentCategory.PSU: ("wattage_w",),
            ComponentCategory.CASE: ("supports_form_factors", "max_gpu_length_mm", "max_cpu_cooler_mm"),
            ComponentCategory.CPU_COOLER: ("socket_support", "height_mm"),
        }
        for component in components:
            if component.price is None or not component.price_is_illustrative:
                continue
            specs = component.specifications
            if any(specs.get(field) in (None, "", []) for field in required_fields[component.category]):
                continue
            if component.category is ComponentCategory.STORAGE and specs.get("capacity_gb", 0) < preferences.minimum_storage_gb:
                continue
            result[component.category].append(component)
        return result

    def _platform_candidates(
        self,
        by_category: dict[ComponentCategory, list[Component]],
        preferences: RecommendationPreferences,
    ) -> list[tuple[Component, Component, Component, Component]]:
        candidates: list[tuple[float, Decimal, tuple[Component, Component, Component, Component]]] = []
        storage_options = self._shortlist(by_category[ComponentCategory.STORAGE], preferences, ComponentCategory.STORAGE)
        memory_options = self._shortlist(by_category[ComponentCategory.MEMORY], preferences, ComponentCategory.MEMORY)
        motherboard_options = self._shortlist(
            by_category[ComponentCategory.MOTHERBOARD], preferences, ComponentCategory.MOTHERBOARD
        )
        for cpu in self._shortlist(by_category[ComponentCategory.CPU], preferences, ComponentCategory.CPU):
            for motherboard in motherboard_options:
                if not self._cpu_motherboard_fit(cpu, motherboard):
                    continue
                for memory in memory_options:
                    if memory.specifications.get("ram_type") != motherboard.specifications.get("ram_type"):
                        continue
                    for storage in storage_options:
                        if not self._storage_fit(motherboard, [storage]):
                            continue
                        selected = (cpu, motherboard, memory, storage)
                        price = sum((component.price or Decimal("0") for component in selected), Decimal("0"))
                        if price >= preferences.budget_usd:
                            continue
                        score = sum(self._component_utility(component, preferences) for component in selected)
                        candidates.append((score, price, selected))
        candidates.sort(key=lambda item: (-item[0], item[1], tuple(str(component.id) for component in item[2])))
        cheapest = sorted(candidates, key=lambda item: (item[1], -item[0], tuple(str(component.id) for component in item[2])))
        selected = candidates[:MAX_PLATFORMS]
        for candidate in cheapest[:MAX_PLATFORMS]:
            if candidate not in selected:
                selected.append(candidate)
        return [candidate[2] for candidate in selected]

    def _shortlist(
        self,
        components: list[Component],
        preferences: RecommendationPreferences,
        category: ComponentCategory,
    ) -> list[Component]:
        ranked = sorted(
            components,
            key=lambda component: (-self._component_utility(component, preferences), component.price or Decimal("0"), str(component.id)),
        )
        cheapest = sorted(components, key=lambda component: (component.price or Decimal("0"), str(component.id)))
        limit = SHORTLIST_LIMITS[category]
        result: list[Component] = []
        for component in [*ranked[:limit], *cheapest[:limit]]:
            if component not in result:
                result.append(component)
        return result

    @staticmethod
    def _cpu_motherboard_fit(cpu: Component, motherboard: Component) -> bool:
        return (
            cpu.specifications.get("socket") == motherboard.specifications.get("socket")
            and motherboard.specifications.get("chipset") in cpu.specifications.get("supported_chipsets", [])
        )

    @staticmethod
    def _case_form_factor_fit(motherboard: Component, case: Component) -> bool:
        return str(motherboard.specifications.get("form_factor")).upper() in {
            str(value).upper() for value in case.specifications.get("supports_form_factors", [])
        }

    @staticmethod
    def _case_gpu_fit(gpu: Component, case: Component) -> bool:
        return gpu.specifications.get("length_mm", 0) <= case.specifications.get("max_gpu_length_mm", -1)

    @staticmethod
    def _cooler_fit(cpu: Component, cooler: Component, case: Component) -> bool:
        return (
            str(cpu.specifications.get("socket")).upper()
            in {str(value).upper() for value in cooler.specifications.get("socket_support", [])}
            and cooler.specifications.get("height_mm", 0) <= case.specifications.get("max_cpu_cooler_mm", -1)
        )

    @staticmethod
    def _storage_fit(motherboard: Component, storage: list[Component]) -> bool:
        interfaces = [str(component.specifications.get("interface", "")).upper() for component in storage]
        return all(interface.startswith("NVME") for interface in interfaces) and len(storage) <= motherboard.specifications.get("m2_slots", 0)

    @staticmethod
    def _power_fit(cpu: Component, gpu: Component, psu: Component) -> bool:
        estimated = cpu.specifications["tdp_w"] + gpu.specifications["tgp_w"] + 150
        required = max(int((estimated * 1.2) + 0.999999), gpu.specifications["psu_min_w"])
        return psu.specifications["wattage_w"] >= required

    def _component_utility(self, component: Component, preferences: RecommendationPreferences) -> float:
        specs = component.specifications
        tier = TIER_SCORE.get(specs.get("performance_tier"), 50.0)
        if component.category is ComponentCategory.CPU:
            cores = min(100.0, float(specs.get("cores", 8)) / 16 * 100)
            threads = min(100.0, float(specs.get("threads", 8)) / 32 * 100)
            return {
                "gaming": tier * 0.7 + cores * 0.3,
                "development": tier * 0.45 + threads * 0.55,
                "content_creation": tier * 0.45 + cores * 0.55,
                "productivity": tier * 0.6 + threads * 0.4,
                "general": tier * 0.6 + cores * 0.4,
            }[preferences.workload]
        if component.category is ComponentCategory.GPU:
            vram = min(100.0, float(specs.get("vram_gb", 8)) / 24 * 100)
            resolution_multiplier = {"1080p": 0.9, "1440p": 1.0, "4k": 1.1}.get(preferences.gaming_resolution, 1.0)
            gpu_score = (tier * 0.7 + vram * 0.3) * resolution_multiplier
            return {
                "gaming": gpu_score,
                "development": gpu_score * 0.55,
                "content_creation": gpu_score * 0.8,
                "productivity": gpu_score * 0.35,
                "general": gpu_score * 0.5,
            }[preferences.workload]
        if component.category is ComponentCategory.MEMORY:
            capacity = min(100.0, float(specs.get("capacity_gb", 16)) / 128 * 100)
            return capacity * {"gaming": 0.7, "development": 1.0, "content_creation": 1.0, "productivity": 0.8, "general": 0.75}[preferences.workload]
        if component.category is ComponentCategory.STORAGE:
            speed = min(100.0, float(specs.get("read_mbps", 3500)) / 14000 * 100)
            capacity = min(100.0, float(specs.get("capacity_gb", 1000)) / 4000 * 100)
            return (speed * 0.6 + capacity * 0.4) * {"gaming": 0.75, "development": 0.9, "content_creation": 1.0, "productivity": 0.9, "general": 0.8}[preferences.workload]
        if component.category is ComponentCategory.MOTHERBOARD and preferences.wifi_preference == "preferred":
            return 60.0 + (10.0 if "wifi" in component.model_name.lower() else 0.0)
        return 50.0

    def _score(
        self,
        components: list[Component],
        preferences: RecommendationPreferences,
        total: Decimal,
    ) -> tuple[float, dict[str, Any]]:
        workload_weights = {
            ComponentCategory.CPU: 0.32,
            ComponentCategory.GPU: 0.38 if preferences.workload == "gaming" else 0.25,
            ComponentCategory.MOTHERBOARD: 0.06,
            ComponentCategory.MEMORY: 0.10,
            ComponentCategory.STORAGE: 0.08,
            ComponentCategory.PSU: 0.03,
            ComponentCategory.CASE: 0.02,
            ComponentCategory.CPU_COOLER: 0.01,
        }
        performance = sum(
            self._component_utility(component, preferences) * workload_weights[component.category]
            for component in components
        )
        budget_fit = float(total / preferences.budget_usd * 100)
        value = min(100.0, performance / max(float(total) / 1000, 0.1))
        score = round(performance * 0.55 + value * 0.25 + budget_fit * 0.20, 4)
        return score, {
            "score": score,
            "performance_proxy": round(performance, 2),
            "value_proxy": round(value, 2),
            "budget_utilization_percent": round(budget_fit, 2),
            "assumptions": [
                "Performance uses catalog performance tiers and structured capacity/power fields as proxies.",
                "No benchmark FPS, retailer price, or measured performance is used.",
                "Compatibility is a hard gate; incompatible, incomplete, and unknown builds are discarded.",
            ],
        }

    @staticmethod
    def _candidate_key(candidate: BuildRecommendation) -> tuple[float, float, tuple[str, ...]]:
        return candidate.score, -float(candidate.total_price), tuple(str(component.id) for component in candidate.components)

    @staticmethod
    def _explanations(
        components: list[Component],
        preferences: RecommendationPreferences,
        summary: dict[str, Any],
    ) -> dict[str, str]:
        by_category = {component.category: component for component in components}
        cpu = by_category[ComponentCategory.CPU]
        gpu = by_category[ComponentCategory.GPU]
        motherboard = by_category[ComponentCategory.MOTHERBOARD]
        memory = by_category[ComponentCategory.MEMORY]
        psu = by_category[ComponentCategory.PSU]
        return {
            "cpu": f"Selected {cpu.model_name} for the {preferences.workload} workload using its catalog tier, core/thread data, and CPU socket/chipset compatibility.",
            "gpu": f"Selected {gpu.model_name} using its catalog tier, VRAM, and {preferences.gaming_resolution or 'workload-appropriate'} graphics weighting; this is not an FPS claim.",
            "motherboard": f"Selected {motherboard.model_name} because its {motherboard.specifications.get('socket')} socket, {motherboard.specifications.get('chipset')} chipset, and {motherboard.specifications.get('ram_type')} support the selected platform.",
            "memory": f"Selected {memory.model_name} because its {memory.specifications.get('capacity_gb')}GB {memory.specifications.get('ram_type')} capacity satisfies the workload scoring assumptions.",
            "psu": f"Selected {psu.model_name} because its {psu.specifications.get('wattage_w')}W capacity passes the deterministic power rule for the selected CPU and GPU.",
        }
