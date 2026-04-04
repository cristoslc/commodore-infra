"""Tests for security classification model (SPEC-002)."""

from __future__ import annotations

import pytest
from commodore.core.models.classification import SecurityClassification, is_compatible


class TestSecurityClassification:
    def test_ordering(self):
        assert SecurityClassification.PUBLIC < SecurityClassification.AUTHENTICATED
        assert SecurityClassification.AUTHENTICATED < SecurityClassification.INTERNAL
        assert SecurityClassification.INTERNAL < SecurityClassification.CUSTODIAL

    def test_all_levels_exist(self):
        levels = {c.value for c in SecurityClassification}
        assert levels == {"public", "authenticated", "internal", "custodial"}


class TestCompatibility:
    def test_host_accepts_same_classification(self):
        for cls in SecurityClassification:
            assert is_compatible(service_classification=cls, host_classification=cls)

    def test_host_accepts_lower_classification(self):
        assert is_compatible(
            service_classification=SecurityClassification.PUBLIC,
            host_classification=SecurityClassification.INTERNAL,
        )
        assert is_compatible(
            service_classification=SecurityClassification.AUTHENTICATED,
            host_classification=SecurityClassification.CUSTODIAL,
        )

    def test_host_rejects_higher_classification(self):
        assert not is_compatible(
            service_classification=SecurityClassification.CUSTODIAL,
            host_classification=SecurityClassification.PUBLIC,
        )
        assert not is_compatible(
            service_classification=SecurityClassification.INTERNAL,
            host_classification=SecurityClassification.AUTHENTICATED,
        )

    def test_custodial_cannot_run_on_public(self):
        """Core safety invariant: custodial workloads never on public hosts."""
        assert not is_compatible(
            service_classification=SecurityClassification.CUSTODIAL,
            host_classification=SecurityClassification.PUBLIC,
        )
