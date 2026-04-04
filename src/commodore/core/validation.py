"""Placement validation (SPEC-003)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from commodore.core.models.classification import is_compatible
from commodore.core.models.host import Host
from commodore.core.models.service import Service
from commodore.core.models.topology import Topology


@dataclass(frozen=True)
class ValidationError:
    severity: str
    rule: str
    message: str


def _check_classification(service: Service, host: Host, _topology: Topology) -> list[ValidationError]:
    if not is_compatible(service_classification=service.classification, host_classification=host.classification):
        return [
            ValidationError(
                severity="error",
                rule="classification_compatibility",
                message=(
                    f"Service '{service.name}' has classification '{service.classification.value}' "
                    f"which cannot run on host '{host.name}' with classification '{host.classification.value}'"
                ),
            )
        ]
    return []


def _check_role(service: Service, host: Host, _topology: Topology) -> list[ValidationError]:
    if "container" not in host.roles:
        return [
            ValidationError(
                severity="error",
                rule="role_compatibility",
                message=(
                    f"Service '{service.name}' requires 'container' role "
                    f"but host '{host.name}' has roles: {sorted(host.roles)}"
                ),
            )
        ]
    return []


def _parse_upstream_host(upstream: str) -> str | None:
    """Extract hostname from upstream URL like 'http://nas:5055'."""
    if not upstream:
        return None
    # Strip scheme
    host_part = upstream.split("//", 1)[-1] if "//" in upstream else upstream
    # Strip port and path
    host_part = host_part.split(":")[0].split("/")[0]
    return host_part if host_part else None


def _check_network_reachability(service: Service, host: Host, topology: Topology) -> list[ValidationError]:
    errors: list[ValidationError] = []
    for rule in service.ingress:
        target_name = _parse_upstream_host(rule.upstream)
        if not target_name:
            continue
        target_host = topology.get_host(target_name)
        if target_host is None:
            errors.append(
                ValidationError(
                    severity="warning",
                    rule="network_reachability",
                    message=(
                        f"Service '{service.name}' ingress references host '{target_name}' "
                        f"which is not in the topology"
                    ),
                )
            )
            continue
        if not topology.can_reach(host, target_host):
            errors.append(
                ValidationError(
                    severity="error",
                    rule="network_reachability",
                    message=(
                        f"Service '{service.name}' on host '{host.name}' (segments: {sorted(host.segments)}) "
                        f"cannot reach upstream host '{target_name}' (segments: {sorted(target_host.segments)})"
                    ),
                )
            )
    return errors


_RULES = [_check_classification, _check_role, _check_network_reachability]


def validate_placement(service: Service, host: Host, topology: Topology) -> list[ValidationError]:
    errors: list[ValidationError] = []
    for rule in _RULES:
        errors.extend(rule(service, host, topology))
    return errors


def validate_all_placements(
    services: Sequence[Service],
    topology: Topology,
) -> dict[str, list[ValidationError]]:
    results: dict[str, list[ValidationError]] = {}
    for service in services:
        all_errors: list[ValidationError] = []
        for host in topology.hosts:
            all_errors.extend(validate_placement(service, host, topology))
        results[service.name] = all_errors
    return results
