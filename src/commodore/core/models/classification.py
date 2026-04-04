"""Security classification model (SPEC-002)."""

from __future__ import annotations

import enum


class SecurityClassification(enum.Enum):
    PUBLIC = "public"
    AUTHENTICATED = "authenticated"
    INTERNAL = "internal"
    CUSTODIAL = "custodial"

    def __lt__(self, other: SecurityClassification) -> bool:
        order = list(SecurityClassification)
        return order.index(self) < order.index(other)

    def __le__(self, other: SecurityClassification) -> bool:
        return self == other or self < other

    def __gt__(self, other: SecurityClassification) -> bool:
        return not self <= other

    def __ge__(self, other: SecurityClassification) -> bool:
        return not self < other


def is_compatible(
    *,
    service_classification: SecurityClassification,
    host_classification: SecurityClassification,
) -> bool:
    """A host can run services at its own classification level or below."""
    return service_classification <= host_classification
