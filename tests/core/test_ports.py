"""Tests for port protocol definitions (SPEC-004)."""

from __future__ import annotations

from typing import runtime_checkable

from commodore.core.models.classification import SecurityClassification
from commodore.core.models.host import Host
from commodore.core.models.service import ContainerSpec, DNSRecord, IngressRule, Service
from commodore.ports.driven.base import Change, PortError, Result
from commodore.ports.driven.dns import DNSPort, DNSState
from commodore.ports.driven.reverse_proxy import ReverseProxyPort, ProxyState
from commodore.ports.driven.load_balancer import LoadBalancerPort, LBState
from commodore.ports.driven.container import ContainerPort, ContainerState
from commodore.ports.driven.secret import SecretPort
from commodore.ports.driven.infrastructure import InfrastructurePort, InfraState


class TestPortProtocolsExist:
    """All 6 port protocols are importable and are runtime-checkable Protocols."""

    def test_dns_port_is_protocol(self):
        assert runtime_checkable(DNSPort)

    def test_reverse_proxy_port_is_protocol(self):
        assert runtime_checkable(ReverseProxyPort)

    def test_load_balancer_port_is_protocol(self):
        assert runtime_checkable(LoadBalancerPort)

    def test_container_port_is_protocol(self):
        assert runtime_checkable(ContainerPort)

    def test_secret_port_is_protocol(self):
        assert runtime_checkable(SecretPort)

    def test_infrastructure_port_is_protocol(self):
        assert runtime_checkable(InfrastructurePort)


class TestSharedTypes:
    """Change and Result types are defined and usable."""

    def test_change_creation(self):
        change = Change(
            port="dns",
            action="create",
            resource_id="requests.example.com",
            before=None,
            after={"type": "CNAME", "target": "proxy.example.com"},
        )
        assert change.port == "dns"
        assert change.action == "create"

    def test_result_success(self):
        result = Result(success=True, changes_applied=1, errors=[])
        assert result.success
        assert result.changes_applied == 1

    def test_result_failure(self):
        result = Result(success=False, changes_applied=0, errors=["connection timeout"])
        assert not result.success
        assert len(result.errors) == 1

    def test_port_error(self):
        err = PortError("dns", "Failed to create record: API rate limited")
        assert err.port == "dns"
        assert "rate limited" in str(err)


class TestDNSPortContract:
    """DNSPort has the required methods."""

    def test_has_current_state(self):
        assert hasattr(DNSPort, "current_state")

    def test_has_diff(self):
        assert hasattr(DNSPort, "diff")

    def test_has_apply(self):
        assert hasattr(DNSPort, "apply")


class TestReverseProxyPortContract:
    """ReverseProxyPort has the required methods including validate."""

    def test_has_current_state(self):
        assert hasattr(ReverseProxyPort, "current_state")

    def test_has_diff(self):
        assert hasattr(ReverseProxyPort, "diff")

    def test_has_apply(self):
        assert hasattr(ReverseProxyPort, "apply")

    def test_has_validate(self):
        assert hasattr(ReverseProxyPort, "validate")


class TestSecretPortContract:
    """SecretPort has get, get_batch, health."""

    def test_has_get(self):
        assert hasattr(SecretPort, "get")

    def test_has_get_batch(self):
        assert hasattr(SecretPort, "get_batch")

    def test_has_health(self):
        assert hasattr(SecretPort, "health")


class TestStateTypes:
    """State types for each port are importable and constructable."""

    def test_dns_state(self):
        state = DNSState(records=[])
        assert state.records == []

    def test_proxy_state(self):
        state = ProxyState(routes=[])
        assert state.routes == []

    def test_lb_state(self):
        state = LBState(backends=[])
        assert state.backends == []

    def test_container_state(self):
        state = ContainerState(stacks=[])
        assert state.stacks == []

    def test_infra_state(self):
        state = InfraState(hosts=[])
        assert state.hosts == []
