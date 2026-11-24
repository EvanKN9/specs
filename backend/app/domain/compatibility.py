"""Deterministic, explainable PC compatibility rules."""

from dataclasses import dataclass, field
from enum import Enum
from math import ceil
from typing import Any, Iterable
from uuid import UUID

from ..models.component import Component, ComponentCategory


class CompatibilityStatus(str, Enum):
    COMPATIBLE = "compatible"
    INCOMPATIBLE = "incompatible"
    UNKNOWN = "unknown"
    INCOMPLETE = "incomplete"


@dataclass(frozen=True)
class RuleResult:
    rule: str
    status: CompatibilityStatus
    explanation: str
    component_ids: list[UUID] = field(default_factory=list)
    missing_specifications: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CompatibilityResult:
    status: CompatibilityStatus
    rules: list[RuleResult]
    explanations: list[str]
    component_ids: list[UUID]
    missing_specifications: list[str]


def _category(components: Iterable[Component], category: ComponentCategory) -> list[Component]:
    return [component for component in components if component.category == category]


def _spec(component: Component | None, key: str) -> Any:
    return component.specifications.get(key) if component else None


def _ids(*components: Component | None) -> list[UUID]:
    return [component.id for component in components if component is not None]


def _missing(component: Component | None, key: str) -> str:
    category = component.category.value if component else "component"
    return f"{category}.{key}"


def _unknown(rule: str, message: str, components: list[Component]) -> RuleResult:
    return RuleResult(rule, CompatibilityStatus.UNKNOWN, message, [component.id for component in components])


def _incomplete(
    rule: str,
    message: str,
    components: list[Component],
    missing: list[str],
) -> RuleResult:
    return RuleResult(
        rule,
        CompatibilityStatus.INCOMPLETE,
        message,
        [component.id for component in components],
        missing,
    )


class CompatibilityEngine:
    """Evaluate catalog components without network calls or heuristic fallbacks."""

    def check(self, components: list[Component]) -> CompatibilityResult:
        rules = [
            self._socket_rule(components),
            self._chipset_rule(components),
            self._form_factor_rule(components),
            self._ram_rule(components),
            self._power_rule(components),
            self._gpu_length_rule(components),
            self._cooler_rule(components),
            self._storage_rule(components),
        ]
        status = self._overall_status(rules)
        return CompatibilityResult(
            status=status,
            rules=rules,
            explanations=[rule.explanation for rule in rules],
            component_ids=[component.id for component in components],
            missing_specifications=sorted(
                {missing for rule in rules for missing in rule.missing_specifications}
            ),
        )

    @staticmethod
    def _overall_status(rules: list[RuleResult]) -> CompatibilityStatus:
        statuses = {rule.status for rule in rules}
        if CompatibilityStatus.INCOMPATIBLE in statuses:
            return CompatibilityStatus.INCOMPATIBLE
        if CompatibilityStatus.INCOMPLETE in statuses:
            return CompatibilityStatus.INCOMPLETE
        if CompatibilityStatus.UNKNOWN in statuses:
            return CompatibilityStatus.UNKNOWN
        return CompatibilityStatus.COMPATIBLE

    def _socket_rule(self, components: list[Component]) -> RuleResult:
        cpus = _category(components, ComponentCategory.CPU)
        boards = _category(components, ComponentCategory.MOTHERBOARD)
        if not cpus or not boards:
            return _unknown("cpu_motherboard_socket", "Socket compatibility needs one CPU and one motherboard.", cpus + boards)
        cpu, board = cpus[0], boards[0]
        missing = [_missing(cpu, "socket")] if _spec(cpu, "socket") is None else []
        missing += [_missing(board, "socket")] if _spec(board, "socket") is None else []
        if missing:
            return _incomplete("cpu_motherboard_socket", "Socket compatibility cannot be evaluated because a socket is missing.", [cpu, board], missing)
        if _spec(cpu, "socket") == _spec(board, "socket"):
            return RuleResult("cpu_motherboard_socket", CompatibilityStatus.COMPATIBLE, f"CPU socket {_spec(cpu, 'socket')} matches the motherboard socket.", _ids(cpu, board))
        return RuleResult("cpu_motherboard_socket", CompatibilityStatus.INCOMPATIBLE, f"CPU socket {_spec(cpu, 'socket')} does not match motherboard socket {_spec(board, 'socket')}.", _ids(cpu, board))

    def _chipset_rule(self, components: list[Component]) -> RuleResult:
        cpus = _category(components, ComponentCategory.CPU)
        boards = _category(components, ComponentCategory.MOTHERBOARD)
        if not cpus or not boards:
            return _unknown("cpu_motherboard_chipset", "Chipset compatibility needs one CPU and one motherboard.", cpus + boards)
        cpu, board = cpus[0], boards[0]
        supported = _spec(cpu, "supported_chipsets")
        chipset = _spec(board, "chipset")
        missing = []
        if not isinstance(supported, list) or not supported:
            missing.append(_missing(cpu, "supported_chipsets"))
        if not chipset:
            missing.append(_missing(board, "chipset"))
        if missing:
            return _incomplete("cpu_motherboard_chipset", "Chipset compatibility cannot be evaluated because chipset data is incomplete.", [cpu, board], missing)
        if chipset in supported:
            return RuleResult("cpu_motherboard_chipset", CompatibilityStatus.COMPATIBLE, f"Motherboard chipset {chipset} is listed for the CPU.", _ids(cpu, board))
        return RuleResult("cpu_motherboard_chipset", CompatibilityStatus.INCOMPATIBLE, f"Motherboard chipset {chipset} is not listed for the CPU.", _ids(cpu, board))

    def _form_factor_rule(self, components: list[Component]) -> RuleResult:
        boards = _category(components, ComponentCategory.MOTHERBOARD)
        cases = _category(components, ComponentCategory.CASE)
        if not boards or not cases:
            return _unknown("motherboard_case_form_factor", "Form-factor compatibility needs one motherboard and one case.", boards + cases)
        board, case = boards[0], cases[0]
        form_factor = _spec(board, "form_factor")
        supported = _spec(case, "supports_form_factors")
        missing = []
        if not form_factor:
            missing.append(_missing(board, "form_factor"))
        if not isinstance(supported, list) or not supported:
            missing.append(_missing(case, "supports_form_factors"))
        if missing:
            return _incomplete("motherboard_case_form_factor", "Case form-factor support is not fully documented.", [board, case], missing)
        normalized = {str(value).upper() for value in supported}
        if str(form_factor).upper() in normalized:
            return RuleResult("motherboard_case_form_factor", CompatibilityStatus.COMPATIBLE, f"Case supports motherboard form factor {form_factor}.", _ids(board, case))
        return RuleResult("motherboard_case_form_factor", CompatibilityStatus.INCOMPATIBLE, f"Case does not list motherboard form factor {form_factor}.", _ids(board, case))

    def _ram_rule(self, components: list[Component]) -> RuleResult:
        boards = _category(components, ComponentCategory.MOTHERBOARD)
        memories = _category(components, ComponentCategory.MEMORY)
        if not boards or not memories:
            return _unknown("motherboard_memory_generation", "Memory generation needs one motherboard and at least one memory kit.", boards + memories)
        board = boards[0]
        board_type = _spec(board, "ram_type")
        missing = [_missing(board, "ram_type")] if not board_type else []
        incompatible = []
        for memory in memories:
            memory_type = _spec(memory, "ram_type")
            if not memory_type:
                missing.append(_missing(memory, "ram_type"))
            elif board_type and memory_type != board_type:
                incompatible.append(memory)
        if incompatible:
            return RuleResult("motherboard_memory_generation", CompatibilityStatus.INCOMPATIBLE, f"Memory generation does not match motherboard RAM type {board_type}.", [component.id for component in [board, *memories]])
        if missing:
            return _incomplete("motherboard_memory_generation", "Memory generation cannot be fully evaluated because RAM type data is missing.", [board, *memories], missing)
        return RuleResult("motherboard_memory_generation", CompatibilityStatus.COMPATIBLE, f"All selected memory kits use motherboard RAM type {board_type}.", [component.id for component in [board, *memories]])

    def _power_rule(self, components: list[Component]) -> RuleResult:
        cpus = _category(components, ComponentCategory.CPU)
        gpus = _category(components, ComponentCategory.GPU)
        psus = _category(components, ComponentCategory.PSU)
        if not cpus or not gpus or not psus:
            return _unknown("psu_power_budget", "Power sizing needs one CPU, at least one GPU, and one PSU.", cpus + gpus + psus)
        cpu, psu = cpus[0], psus[0]
        missing = []
        cpu_power = _spec(cpu, "tdp_w")
        if not isinstance(cpu_power, (int, float)):
            missing.append(_missing(cpu, "tdp_w"))
        gpu_power = 0
        gpu_minimum = 0
        for gpu in gpus:
            tgp = _spec(gpu, "tgp_w")
            minimum = _spec(gpu, "psu_min_w")
            if not isinstance(tgp, (int, float)):
                missing.append(_missing(gpu, "tgp_w"))
            else:
                gpu_power += tgp
            if not isinstance(minimum, (int, float)):
                missing.append(_missing(gpu, "psu_min_w"))
            else:
                gpu_minimum = max(gpu_minimum, minimum)
        psu_wattage = _spec(psu, "wattage_w")
        if not isinstance(psu_wattage, (int, float)):
            missing.append(_missing(psu, "wattage_w"))
        if missing:
            return _incomplete("psu_power_budget", "Power compatibility cannot be fully evaluated because power specifications are missing.", [cpu, *gpus, psu], missing)
        estimated = cpu_power + gpu_power + 150
        required = max(ceil(estimated * 1.2), gpu_minimum)
        details = {"estimated_system_power_w": estimated, "required_psu_w": required, "psu_wattage_w": psu_wattage}
        if psu_wattage >= required:
            return RuleResult("psu_power_budget", CompatibilityStatus.COMPATIBLE, f"PSU capacity {psu_wattage}W meets the estimated {required}W requirement.", [component.id for component in [cpu, *gpus, psu]], details=details)
        return RuleResult("psu_power_budget", CompatibilityStatus.INCOMPATIBLE, f"PSU capacity {psu_wattage}W is below the estimated {required}W requirement.", [component.id for component in [cpu, *gpus, psu]], details=details)

    def _gpu_length_rule(self, components: list[Component]) -> RuleResult:
        gpus = _category(components, ComponentCategory.GPU)
        cases = _category(components, ComponentCategory.CASE)
        if not gpus or not cases:
            return _unknown("gpu_case_length", "GPU length needs at least one GPU and one case.", gpus + cases)
        case = cases[0]
        clearance = _spec(case, "max_gpu_length_mm")
        missing = [_missing(case, "max_gpu_length_mm")] if not isinstance(clearance, (int, float)) else []
        for gpu in gpus:
            length = _spec(gpu, "length_mm")
            if not isinstance(length, (int, float)):
                missing.append(_missing(gpu, "length_mm"))
            elif isinstance(clearance, (int, float)) and length > clearance:
                return RuleResult("gpu_case_length", CompatibilityStatus.INCOMPATIBLE, f"GPU length {length}mm exceeds case clearance {clearance}mm.", [component.id for component in [*gpus, case]])
        if missing:
            return _incomplete("gpu_case_length", "GPU and case physical fit cannot be fully evaluated because length data is missing.", [*gpus, case], missing)
        return RuleResult("gpu_case_length", CompatibilityStatus.COMPATIBLE, f"All selected GPUs fit within the case GPU clearance of {clearance}mm.", [component.id for component in [*gpus, case]])

    def _cooler_rule(self, components: list[Component]) -> RuleResult:
        cpus = _category(components, ComponentCategory.CPU)
        coolers = _category(components, ComponentCategory.CPU_COOLER)
        cases = _category(components, ComponentCategory.CASE)
        if not cpus or not coolers or not cases:
            return _unknown("cpu_cooler_fit", "Cooler fit needs one CPU, one CPU cooler, and one case.", cpus + coolers + cases)
        cpu, cooler, case = cpus[0], coolers[0], cases[0]
        sockets = _spec(cooler, "socket_support")
        cpu_socket = _spec(cpu, "socket")
        height = _spec(cooler, "height_mm")
        clearance = _spec(case, "max_cpu_cooler_mm")
        missing = []
        if not isinstance(sockets, list) or not sockets:
            missing.append(_missing(cooler, "socket_support"))
        if not cpu_socket:
            missing.append(_missing(cpu, "socket"))
        if not isinstance(height, (int, float)):
            missing.append(_missing(cooler, "height_mm"))
        if not isinstance(clearance, (int, float)):
            missing.append(_missing(case, "max_cpu_cooler_mm"))
        if missing:
            return _incomplete("cpu_cooler_fit", "CPU cooler fit cannot be fully evaluated because socket or height data is missing.", [cpu, cooler, case], missing)
        normalized_sockets = {str(socket).upper() for socket in sockets}
        if str(cpu_socket).upper() not in normalized_sockets:
            return RuleResult("cpu_cooler_fit", CompatibilityStatus.INCOMPATIBLE, f"Cooler does not list CPU socket {cpu_socket}.", _ids(cpu, cooler, case))
        if height > clearance:
            return RuleResult("cpu_cooler_fit", CompatibilityStatus.INCOMPATIBLE, f"Cooler height {height}mm exceeds case clearance {clearance}mm.", _ids(cpu, cooler, case))
        return RuleResult("cpu_cooler_fit", CompatibilityStatus.COMPATIBLE, f"Cooler supports CPU socket {cpu_socket} and fits the case clearance of {clearance}mm.", _ids(cpu, cooler, case))

    def _storage_rule(self, components: list[Component]) -> RuleResult:
        boards = _category(components, ComponentCategory.MOTHERBOARD)
        storage = _category(components, ComponentCategory.STORAGE)
        if not boards or not storage:
            return _unknown("storage_interface", "Storage interface needs one motherboard and at least one storage device.", boards + storage)
        board = boards[0]
        m2_slots = _spec(board, "m2_slots")
        missing = [_missing(board, "m2_slots")] if not isinstance(m2_slots, int) else []
        nvme_count = 0
        for device in storage:
            interface = _spec(device, "interface")
            if not interface:
                missing.append(_missing(device, "interface"))
            elif str(interface).upper().startswith("NVME"):
                nvme_count += 1
            elif str(interface).upper().startswith("SATA"):
                missing.append(_missing(board, "sata_ports"))
            else:
                return RuleResult("storage_interface", CompatibilityStatus.UNKNOWN, f"Storage interface {interface} is not covered by the current deterministic rules.", [component.id for component in [board, *storage]])
        if isinstance(m2_slots, int) and nvme_count > m2_slots:
            return RuleResult("storage_interface", CompatibilityStatus.INCOMPATIBLE, f"Selected NVMe devices require {nvme_count} M.2 slots but the motherboard lists {m2_slots}.", [component.id for component in [board, *storage]])
        if missing:
            return _incomplete("storage_interface", "Storage compatibility cannot be fully evaluated because interface or slot data is missing.", [board, *storage], missing)
        return RuleResult("storage_interface", CompatibilityStatus.COMPATIBLE, f"Selected NVMe devices fit within the motherboard's {m2_slots} listed M.2 slots.", [component.id for component in [board, *storage]])
