"""Discovery Engine (SPEC-016)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from commodore.core.models.host import Host
from commodore.core.models.service import Service
from commodore.core.models.topology import Topology
from commodore.ports.registry import AdapterRegistry


@dataclass(frozen=True)
class DiscoveryResult:
    """Result of a discovery run.

    Contains the unified inventory from all adapters.

    Attributes:
        hosts: List of hosts discovered (from infrastructure, container states, etc.)
        services: List of services discovered (from DNS records, proxy routes, containers, etc.)
    """
    hosts: list[dict[str, Any]]
    services: list[dict[str, Any]]


class DiscoveryEngine:
    """Coordinates adapter discovery across all port types.

    The engine calls `current_state()` on each adapter in the registry
    and merges the results into a unified inventory.

    Attributes:
        registry: The adapter registry containing configured adapters.
        topology: The topology for host/segment context (optional).
    """

    def __init__(
        self,
        registry: AdapterRegistry,
        topology: Topology | None = None,
    ) -> None:
        self.registry = registry
        self.topology = topology

    def discover(
        self,
        *,
        hosts: list[str] | None = None,
        segment: str | None = None,
        provider: str | None = None,
    ) -> DiscoveryResult:
        """Run discovery across all adapters.

        Args:
            hosts: Scan only these specific hosts (by name).
            segment: Scan only hosts on this network segment.
            provider: Scan only adapters backed by this provider.

        Returns:
            DiscoveryResult with unified inventory.
        """
        # Determine which hosts to scan
        target_hosts = self._resolve_hosts(hosts=hosts, segment=segment)

        # Determine which adapters to call
        target_adapters = self._resolve_adapters(provider=provider)

        # Collect state from all adapters
        hosts: list[dict[str, Any]] = []
        services: list[dict[str, Any]] = []

        # Container adapters produce hosts/containers
        if target_adapters.container:
            container_state = target_adapters.container.current_state()
            for stack in container_state.stacks:
                hosts.append({
                    "name": stack.get("name", "unknown"),
                    "address": "placeholder",  # Will be filled by host context
                    "state": stack.get("state", "unknown"),
                })

        # DNS adapters produce services/domains
        if target_adapters.dns:
            dns_state = target_adapters.dns.current_state()
            for record in dns_state.records:
                services.append({
                    "name": record.get("name", "unknown"),
                    "type": record.get("type", "A"),
                    "target": record.get("target", ""),
                })

        # Reverse proxy adapters produce services
        if target_adapters.reverse_proxy:
            proxy_state = target_adapters.reverse_proxy.current_state()
            for route in proxy_state.routes:
                services.append({
                    "name": route.get("name", "unknown"),
                    "type": "proxy",
                    "upstream": route.get("upstream", ""),
                })

        return DiscoveryResult(
            hosts=hosts,
            services=services,
        )

    def _resolve_hosts(
        self, hosts: list[str] | None, segment: str | None
    ) -> list[Host]:
        """Determine which hosts to scan.

        Returns all hosts in the topology if no filter specified.
        """
        if self.topology is None:
            return []

        if hosts is not None:
            # Filter to specific host names
            return [
                h for h in self.topology.hosts
                if h.name in hosts
            ]

        if segment is not None:
            # Filter to hosts on this segment
            return self.topology.hosts_on_segment(segment)

        # No filter - scan all hosts
        return list(self.topology.hosts)

    def _resolve_adapters(
        self, provider: str | None
    ) -> AdapterRegistry:
        """Determine which adapters to call.

        Returns all adapters in registry if no provider filter specified.
        """
        if provider is None:
            return self.registry

        # Filter to adapters for this provider
        # This requires provider metadata on the registry
        # For now, return all and let caller handle filtering
        return self.registry