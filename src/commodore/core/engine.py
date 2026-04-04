"""Diff-plan-apply engine (SPEC-007, SPEC-008, SPEC-009)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence

from commodore.core.models.service import Service
from commodore.core.models.topology import Topology
from commodore.ports.driven.base import Change, PortError, Result
from commodore.ports.driven.dns import DNSState
from commodore.ports.driven.reverse_proxy import ProxyState
from commodore.ports.driven.load_balancer import LBState
from commodore.ports.driven.container import ContainerState
from commodore.ports.driven.infrastructure import InfraState as InfraPortState
from commodore.ports.registry import AdapterRegistry


# --- SPEC-007: State Collection & Diff ---


@dataclass(frozen=True)
class CurrentState:
    dns: DNSState = field(default_factory=lambda: DNSState())
    reverse_proxy: ProxyState = field(default_factory=lambda: ProxyState())
    load_balancer: LBState = field(default_factory=lambda: LBState())
    container: ContainerState = field(default_factory=lambda: ContainerState())
    infrastructure: InfraPortState = field(default_factory=lambda: InfraPortState())


def collect_state(registry: AdapterRegistry) -> CurrentState:
    return CurrentState(
        dns=registry.dns.current_state() if registry.dns else DNSState(),
        reverse_proxy=registry.reverse_proxy.current_state() if registry.reverse_proxy else ProxyState(),
        load_balancer=registry.load_balancer.current_state() if registry.load_balancer else LBState(),
        container=registry.container.current_state() if registry.container else ContainerState(),
        infrastructure=registry.infrastructure.current_state() if registry.infrastructure else InfraPortState(),
    )


def _service_to_desired(service: Service) -> dict[str, list[dict[str, Any]]]:
    """Convert a service definition into desired state per port."""
    desired: dict[str, list[dict[str, Any]]] = {}

    if service.dns:
        desired["dns"] = [{"name": r.name, "type": r.type, "target": r.target} for r in service.dns]

    if service.ingress:
        desired["reverse_proxy"] = [
            {"name": f"{service.name}-{rule.type}", "upstream": rule.upstream, "tls": rule.tls}
            for rule in service.ingress
            if rule.type == "reverse_proxy"
        ]

    desired["container"] = [{"name": service.name, "image": service.container.image, "ports": list(service.container.ports)}]

    return desired


def compute_diff(
    current: CurrentState,
    desired_services: Sequence[Service],
    registry: AdapterRegistry,
) -> list[Change]:
    all_changes: list[Change] = []

    # Aggregate desired state from all services
    all_desired: dict[str, list[dict[str, Any]]] = {}
    for svc in desired_services:
        svc_desired = _service_to_desired(svc)
        for port, items in svc_desired.items():
            all_desired.setdefault(port, []).extend(items)

    # Diff each port
    if registry.dns and "dns" in all_desired:
        all_changes.extend(registry.dns.diff(all_desired["dns"]))
    if registry.reverse_proxy and "reverse_proxy" in all_desired:
        all_changes.extend(registry.reverse_proxy.diff(all_desired["reverse_proxy"]))
    if registry.load_balancer and "load_balancer" in all_desired:
        all_changes.extend(registry.load_balancer.diff(all_desired["load_balancer"]))
    if registry.container and "container" in all_desired:
        all_changes.extend(registry.container.diff(all_desired["container"]))

    return all_changes


# --- SPEC-008: Plan Generation ---

PORT_ORDER = ["dns", "container", "load_balancer", "reverse_proxy", "infrastructure"]


@dataclass(frozen=True)
class PlanStep:
    change: Change
    order: int


@dataclass(frozen=True)
class Plan:
    steps: tuple[PlanStep, ...] = ()

    def format(self) -> str:
        if not self.steps:
            return "No changes."
        lines = []
        for step in self.steps:
            c = step.change
            lines.append(f"  [{c.port}] {c.action} {c.resource_id}")
        return "Plan:\n" + "\n".join(lines)


def generate_plan(changes: list[Change], topology: Topology) -> Plan:
    if not changes:
        return Plan()

    def sort_key(c: Change) -> int:
        try:
            return PORT_ORDER.index(c.port)
        except ValueError:
            return len(PORT_ORDER)

    sorted_changes = sorted(changes, key=sort_key)
    steps = tuple(PlanStep(change=c, order=i) for i, c in enumerate(sorted_changes))
    return Plan(steps=steps)


# --- SPEC-009: Apply Execution ---


@dataclass(frozen=True)
class ApplyResult:
    success: bool
    steps_succeeded: int
    steps_failed: int
    errors: list[str] = field(default_factory=list)


def _get_port_adapter(registry: AdapterRegistry, port_name: str) -> Any:
    return getattr(registry, port_name, None)


def apply_plan(plan: Plan, registry: AdapterRegistry) -> ApplyResult:
    if not plan.steps:
        return ApplyResult(success=True, steps_succeeded=0, steps_failed=0)

    # Group changes by port for batch apply
    by_port: dict[str, list[Change]] = {}
    for step in plan.steps:
        by_port.setdefault(step.change.port, []).append(step.change)

    succeeded = 0
    failed = 0
    errors: list[str] = []

    for port_name, changes in by_port.items():
        adapter = _get_port_adapter(registry, port_name)
        if adapter is None:
            failed += len(changes)
            errors.append(f"No adapter configured for port '{port_name}'")
            continue

        try:
            result = adapter.apply(changes)
            if result.success:
                succeeded += result.changes_applied
            else:
                failed += len(changes)
                errors.extend(result.errors)
        except PortError as e:
            failed += len(changes)
            errors.append(str(e))

    return ApplyResult(
        success=failed == 0,
        steps_succeeded=succeeded,
        steps_failed=failed,
        errors=errors,
    )
