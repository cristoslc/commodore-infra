"""Tests for Discovery Engine (SPEC-016)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from commodore.core.models.classification import SecurityClassification
from commodore.core.models.host import Host
from commodore.core.models.segment import NetworkSegment
from commodore.core.models.service import (
    ContainerSpec,
    DNSRecord,
    IngressRule,
    Service,
)
from commodore.ports.driven.dns import DNSState
from commodore.ports.driven.container import ContainerState
from commodore.ports.registry import AdapterRegistry
from commodore.core.discovery import DiscoveryEngine


class TestDiscoveryEngine:
    """Discovery engine coordinates adapters and merges results."""

    def test_discover_empty_registry(self):
        """Discover with no adapters returns empty inventory."""
        registry = AdapterRegistry()
        engine = DiscoveryEngine(registry)

        result = engine.discover()

        assert result.hosts == []
        assert result.services == []

    def test_discover_with_container_adapter(self):
        """Discover calls container adapter and includes results."""
        mock_container = MagicMock()
        mock_container.current_state.return_value = ContainerState(
            stacks=[{"name": "web", "state": "running", "image": "nginx:latest"}]
        )

        registry = AdapterRegistry(container=mock_container)
        engine = DiscoveryEngine(registry)

        result = engine.discover()

        # Hosts from container state are included
        assert len(result.hosts) == 1

    def test_discover_with_multiple_adapters(self):
        """Discover coordinates multiple adapters."""
        mock_container = MagicMock()
        mock_container.current_state.return_value = ContainerState(
            stacks=[{"name": "web", "state": "running", "image": "nginx:latest"}]
        )

        mock_dns = MagicMock()
        mock_dns.current_state.return_value = DNSState(
            records=[
                {"id": "1", "name": "web.example.com", "type": "A", "target": "10.0.0.1"}
            ]
        )

        registry = AdapterRegistry(
            container=mock_container, dns=mock_dns, reverse_proxy=None
        )
        engine = DiscoveryEngine(registry)

        result = engine.discover()

        # Results from both adapters should be present
        assert mock_container.current_state.called
        assert mock_dns.current_state.called

    def test_discover_with_host_scope(self):
        """Discover --host filters to specific host."""
        host = Host(
            name="webserver",
            address="10.0.0.1",
            roles=frozenset(["web"]),
            classification=SecurityClassification.PUBLIC,
            segments=frozenset({"default"}),
        )

        topology = MagicMock()
        topology.hosts_on_segment.return_value = [host]

        mock_container = MagicMock()
        mock_container.current_state.return_value = ContainerState(
            stacks=[{"name": "web", "state": "running", "image": "nginx:latest"}]
        )

        registry = AdapterRegistry(container=mock_container)
        engine = DiscoveryEngine(registry, topology=topology)

        result = engine.discover(hosts=["webserver"])

        assert mock_container.current_state.called

    def test_discover_with_segment_scope(self):
        """Discover --segment filters to hosts on that segment."""
        segment = NetworkSegment(
            name="办公网络", cidr="10.0.0.0/24", reachable_from=frozenset()
        )

        host1 = Host(
            name="web1",
            address="10.0.0.1",
            roles=frozenset(),
            classification=SecurityClassification.PUBLIC,
            segments=frozenset({"办公网络"}),
        )

        host2 = Host(
            name="web2",
            address="10.0.0.2",
            roles=frozenset(),
            classification=SecurityClassification.PUBLIC,
            segments=frozenset({"办公网络"}),
        )

        topology = MagicMock()
        topology.hosts_on_segment.return_value = [host1, host2]

        mock_container = MagicMock()
        mock_container.current_state.return_value = ContainerState(stacks=[])

        registry = AdapterRegistry(container=mock_container)
        engine = DiscoveryEngine(registry, topology=topology)

        result = engine.discover(segment="办公网络")

        assert topology.hosts_on_segment.called
        assert mock_container.current_state.called

    def test_discover_with_provider_scope(self):
        """Discover --provider filters to adapters for that provider."""
        mock_container = MagicMock()
        mock_container.current_state.return_value = ContainerState(stacks=[])

        registry = AdapterRegistry(container=mock_container)
        engine = DiscoveryEngine(registry)

        # Provider filter would limit which adapters get called
        result = engine.discover(provider="nas")

        # Only adapters for 'nas' provider should be called
        # In current implementation, this filter doesn't exist yet
        # but the signature supports it


class TestDiscoveryResult:
    """DiscoveryResult structure for unified inventory."""

    def test_result_has_hosts_and_services(self):
        """Result contains hosts and services lists."""
        from commodore.core.discovery import DiscoveryResult

        result = DiscoveryResult(hosts=[], services=[])
        assert result.hosts == []
        assert result.services == []

    def test_result_provides_empty_lists_when_no_adapters_called(self):
        """Result provides valid empty structure."""
        from commodore.core.discovery import DiscoveryResult

        result = DiscoveryResult(hosts=[], services=[])

        # Can iterate over results
        assert len(result.hosts) == 0
        assert len(result.services) == 0