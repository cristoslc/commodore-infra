"""Tests for adapter registry (SPEC-005)."""

from __future__ import annotations

import pytest
from commodore.ports.registry import AdapterRegistry
from commodore.adapters.stubs import (
    InMemoryDNS,
    InMemoryReverseProxy,
    InMemoryLoadBalancer,
    InMemoryContainer,
    InMemorySecret,
    InMemoryInfrastructure,
)


class TestAdapterRegistry:
    def _full_registry(self) -> AdapterRegistry:
        return AdapterRegistry(
            dns=InMemoryDNS(),
            reverse_proxy=InMemoryReverseProxy(),
            load_balancer=InMemoryLoadBalancer(),
            container=InMemoryContainer(),
            secret=InMemorySecret(),
            infrastructure=InMemoryInfrastructure(),
        )

    def test_all_ports_accessible(self):
        reg = self._full_registry()
        assert reg.dns is not None
        assert reg.reverse_proxy is not None
        assert reg.load_balancer is not None
        assert reg.container is not None
        assert reg.secret is not None
        assert reg.infrastructure is not None

    def test_registry_is_frozen(self):
        reg = self._full_registry()
        with pytest.raises(AttributeError):
            reg.dns = InMemoryDNS()

    def test_partial_registry_allowed(self):
        """Not all ports need to be configured — only the ones the services need."""
        reg = AdapterRegistry(dns=InMemoryDNS())
        assert reg.dns is not None
        assert reg.reverse_proxy is None

    def test_from_config(self):
        """Registry can be built from a config dict mapping port names to adapter types."""
        reg = AdapterRegistry.from_config({
            "dns": {"type": "in_memory"},
            "container": {"type": "in_memory"},
        })
        assert reg.dns is not None
        assert reg.container is not None
        assert reg.reverse_proxy is None
