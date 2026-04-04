"""Tests for diff-plan-apply engine (SPEC-007, SPEC-008, SPEC-009)."""

from __future__ import annotations

import pytest
from commodore.adapters.stubs import InMemoryDNS, InMemoryReverseProxy, InMemoryContainer, InMemorySecret, InMemoryInfrastructure, InMemoryLoadBalancer
from commodore.core.models.classification import SecurityClassification
from commodore.core.models.host import Host
from commodore.core.models.service import ContainerSpec, DNSRecord, IngressRule, Service
from commodore.core.models.topology import Topology
from commodore.core.engine import collect_state, compute_diff, generate_plan, apply_plan, ApplyResult, CurrentState
from commodore.ports.registry import AdapterRegistry


def _registry(**overrides) -> AdapterRegistry:
    defaults = dict(
        dns=InMemoryDNS(),
        reverse_proxy=InMemoryReverseProxy(),
        load_balancer=InMemoryLoadBalancer(),
        container=InMemoryContainer(),
        secret=InMemorySecret(),
        infrastructure=InMemoryInfrastructure(),
    )
    defaults.update(overrides)
    return AdapterRegistry(**defaults)


def _topology() -> Topology:
    return Topology(hosts=(
        Host(name="nas", address="10.0.0.10", roles=frozenset({"container", "storage"}), classification=SecurityClassification.INTERNAL),
        Host(name="proxy", address="10.0.0.1", roles=frozenset({"reverse-proxy", "load-balancer"}), classification=SecurityClassification.INTERNAL),
    ))


def _service() -> Service:
    return Service(
        name="jellyseerr",
        classification=SecurityClassification.AUTHENTICATED,
        container=ContainerSpec(image="fallenbagel/jellyseerr:latest", ports=[5055]),
        dns=[DNSRecord(name="requests.example.com", type="CNAME", target="proxy.example.com")],
        ingress=[IngressRule(type="reverse_proxy", upstream="http://nas:5055", tls="auto")],
    )


class TestCollectState:
    def test_collect_from_empty_registry(self):
        reg = _registry()
        state = collect_state(reg)
        assert state.dns.records == []
        assert state.container.stacks == []

    def test_collect_with_preloaded_data(self):
        reg = _registry(dns=InMemoryDNS(records=[{"name": "old.example.com", "type": "A", "target": "1.2.3.4"}]))
        state = collect_state(reg)
        assert len(state.dns.records) == 1


class TestComputeDiff:
    def test_diff_with_new_service(self):
        reg = _registry()
        state = collect_state(reg)
        changes = compute_diff(state, [_service()], reg)
        assert len(changes) > 0
        ports_touched = {c.port for c in changes}
        assert "dns" in ports_touched
        assert "container" in ports_touched

    def test_diff_empty_when_nothing_desired(self):
        reg = _registry()
        state = collect_state(reg)
        changes = compute_diff(state, [], reg)
        assert changes == []


class TestGeneratePlan:
    def test_plan_from_diff(self):
        reg = _registry()
        state = collect_state(reg)
        changes = compute_diff(state, [_service()], reg)
        topo = _topology()
        plan = generate_plan(changes, topo)
        assert len(plan.steps) > 0
        assert plan.format() != ""

    def test_empty_plan(self):
        topo = _topology()
        plan = generate_plan([], topo)
        assert len(plan.steps) == 0

    def test_plan_ordering_dns_before_proxy(self):
        reg = _registry()
        state = collect_state(reg)
        changes = compute_diff(state, [_service()], reg)
        topo = _topology()
        plan = generate_plan(changes, topo)
        port_order = [s.change.port for s in plan.steps]
        if "dns" in port_order and "reverse_proxy" in port_order:
            assert port_order.index("dns") < port_order.index("reverse_proxy")


class TestApplyPlan:
    def test_apply_succeeds(self):
        reg = _registry()
        state = collect_state(reg)
        changes = compute_diff(state, [_service()], reg)
        topo = _topology()
        plan = generate_plan(changes, topo)
        result = apply_plan(plan, reg)
        assert isinstance(result, ApplyResult)
        assert result.success
        assert result.steps_succeeded > 0
        assert result.steps_failed == 0

    def test_apply_is_idempotent(self):
        reg = _registry()
        # First apply
        state = collect_state(reg)
        changes = compute_diff(state, [_service()], reg)
        plan = generate_plan(changes, _topology())
        apply_plan(plan, reg)
        # Second apply — should be no-op
        state2 = collect_state(reg)
        changes2 = compute_diff(state2, [_service()], reg)
        assert changes2 == []

    def test_apply_result_tracks_errors(self):
        """ApplyResult has the right fields."""
        result = ApplyResult(success=False, steps_succeeded=1, steps_failed=1, errors=["DNS timeout"])
        assert not result.success
        assert len(result.errors) == 1
