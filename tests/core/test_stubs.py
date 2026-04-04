"""Tests for in-memory stub adapters (SPEC-006)."""

from __future__ import annotations

from commodore.adapters.stubs import (
    InMemoryDNS,
    InMemoryReverseProxy,
    InMemoryLoadBalancer,
    InMemoryContainer,
    InMemorySecret,
    InMemoryInfrastructure,
)
from commodore.ports.driven.dns import DNSPort
from commodore.ports.driven.reverse_proxy import ReverseProxyPort
from commodore.ports.driven.load_balancer import LoadBalancerPort
from commodore.ports.driven.container import ContainerPort
from commodore.ports.driven.secret import SecretPort
from commodore.ports.driven.infrastructure import InfrastructurePort


class TestStubProtocolCompliance:
    """Each stub satisfies its port protocol."""

    def test_dns_stub_is_dns_port(self):
        assert isinstance(InMemoryDNS(), DNSPort)

    def test_reverse_proxy_stub_is_proxy_port(self):
        assert isinstance(InMemoryReverseProxy(), ReverseProxyPort)

    def test_load_balancer_stub_is_lb_port(self):
        assert isinstance(InMemoryLoadBalancer(), LoadBalancerPort)

    def test_container_stub_is_container_port(self):
        assert isinstance(InMemoryContainer(), ContainerPort)

    def test_secret_stub_is_secret_port(self):
        assert isinstance(InMemorySecret(), SecretPort)

    def test_infrastructure_stub_is_infra_port(self):
        assert isinstance(InMemoryInfrastructure(), InfrastructurePort)


class TestDNSStub:
    def test_empty_state(self):
        dns = InMemoryDNS()
        state = dns.current_state()
        assert state.records == []

    def test_preload_and_diff(self):
        dns = InMemoryDNS(records=[{"name": "old.example.com", "type": "A", "target": "1.2.3.4"}])
        changes = dns.diff([{"name": "new.example.com", "type": "CNAME", "target": "proxy.example.com"}])
        assert len(changes) >= 1

    def test_apply_changes(self):
        dns = InMemoryDNS()
        changes = dns.diff([{"name": "test.example.com", "type": "A", "target": "1.2.3.4"}])
        result = dns.apply(changes)
        assert result.success
        state = dns.current_state()
        assert len(state.records) == 1

    def test_reset(self):
        dns = InMemoryDNS(records=[{"name": "test.example.com", "type": "A", "target": "1.2.3.4"}])
        dns.reset()
        assert dns.current_state().records == []


class TestSecretStub:
    def test_get(self):
        secret = InMemorySecret(secrets={"db_pass": "hunter2"})
        assert secret.get("db_pass") == "hunter2"

    def test_get_batch(self):
        secret = InMemorySecret(secrets={"a": "1", "b": "2", "c": "3"})
        batch = secret.get_batch(["a", "c"])
        assert batch == {"a": "1", "c": "3"}

    def test_health(self):
        secret = InMemorySecret()
        assert secret.health() is True

    def test_reset(self):
        secret = InMemorySecret(secrets={"key": "val"})
        secret.reset()
        assert secret.get("key") == ""


class TestContainerStub:
    def test_empty_state(self):
        ct = InMemoryContainer()
        assert ct.current_state().stacks == []

    def test_diff_and_apply(self):
        ct = InMemoryContainer()
        changes = ct.diff([{"name": "jellyseerr", "image": "test:latest"}])
        result = ct.apply(changes)
        assert result.success
        assert len(ct.current_state().stacks) == 1

    def test_reset(self):
        ct = InMemoryContainer(stacks=[{"name": "test"}])
        ct.reset()
        assert ct.current_state().stacks == []
