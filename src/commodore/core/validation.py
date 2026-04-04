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


_RULES = [_check_classification, _check_role]


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
