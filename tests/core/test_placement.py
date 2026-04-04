"""Tests for placement validation (SPEC-003)."""

from __future__ import annotations

from commodore.core.models.classification import SecurityClassification
from commodore.core.models.host import Host
from commodore.core.models.service import Service, ContainerSpec
from commodore.core.models.topology import Topology
from commodore.core.validation import validate_placement, validate_all_placements, ValidationError


def _svc(name: str = "test-svc", classification: SecurityClassification = SecurityClassification.INTERNAL) -> Service:
    return Service(
        name=name,
        classification=classification,
        container=ContainerSpec(image="test:latest", ports=[80]),
    )


def _host(
    name: str = "test-host",
    roles: frozenset[str] = frozenset({"container"}),
    classification: SecurityClassification = SecurityClassification.INTERNAL,
) -> Host:
    return Host(name=name, address="10.0.0.1", roles=roles, classification=classification)


def _topo(*hosts: Host) -> Topology:
    return Topology(hosts=tuple(hosts))


class TestValidatePlacement:
    def test_valid_placement_returns_empty(self):
        svc = _svc()
        host = _host()
        topo = _topo(host)
        errors = validate_placement(svc, host, topo)
        assert errors == []

    def test_classification_mismatch(self):
        svc = _svc(classification=SecurityClassification.CUSTODIAL)
        host = _host(classification=SecurityClassification.PUBLIC)
        topo = _topo(host)
        errors = validate_placement(svc, host, topo)
        assert len(errors) >= 1
        assert any(e.rule == "classification_compatibility" for e in errors)

    def test_missing_container_role(self):
        svc = _svc()
        host = _host(roles=frozenset({"reverse-proxy"}))
        topo = _topo(host)
        errors = validate_placement(svc, host, topo)
        assert len(errors) >= 1
        assert any(e.rule == "role_compatibility" for e in errors)

    def test_returns_all_violations_not_just_first(self):
        svc = _svc(classification=SecurityClassification.CUSTODIAL)
        host = _host(roles=frozenset({"reverse-proxy"}), classification=SecurityClassification.PUBLIC)
        topo = _topo(host)
        errors = validate_placement(svc, host, topo)
        rules = {e.rule for e in errors}
        assert "classification_compatibility" in rules
        assert "role_compatibility" in rules

    def test_error_references_service_and_host_names(self):
        svc = _svc(name="jellyseerr", classification=SecurityClassification.CUSTODIAL)
        host = _host(name="public-edge", classification=SecurityClassification.PUBLIC)
        topo = _topo(host)
        errors = validate_placement(svc, host, topo)
        for error in errors:
            assert "jellyseerr" in error.message or "public-edge" in error.message

    def test_validation_error_has_required_fields(self):
        svc = _svc(classification=SecurityClassification.CUSTODIAL)
        host = _host(classification=SecurityClassification.PUBLIC)
        topo = _topo(host)
        errors = validate_placement(svc, host, topo)
        error = errors[0]
        assert isinstance(error, ValidationError)
        assert hasattr(error, "severity")
        assert hasattr(error, "rule")
        assert hasattr(error, "message")


class TestValidateAllPlacements:
    def test_batch_validation(self):
        svc_ok = _svc(name="web")
        svc_bad = _svc(name="custodial", classification=SecurityClassification.CUSTODIAL)
        host = _host(classification=SecurityClassification.INTERNAL)
        topo = _topo(host)
        results = validate_all_placements([svc_ok, svc_bad], topo)
        assert results["web"] == []
        assert len(results["custodial"]) >= 1

    def test_batch_with_no_compatible_hosts(self):
        svc = _svc(name="isolated")
        host = _host(roles=frozenset({"storage"}))
        topo = _topo(host)
        results = validate_all_placements([svc], topo)
        assert len(results["isolated"]) >= 1
