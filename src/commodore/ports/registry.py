"""Adapter registry (SPEC-005)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from commodore.ports.driven.dns import DNSPort
from commodore.ports.driven.reverse_proxy import ReverseProxyPort
from commodore.ports.driven.load_balancer import LoadBalancerPort
from commodore.ports.driven.container import ContainerPort
from commodore.ports.driven.secret import SecretPort
from commodore.ports.driven.infrastructure import InfrastructurePort


@dataclass(frozen=True)
class AdapterRegistry:
    dns: DNSPort | None = None
    reverse_proxy: ReverseProxyPort | None = None
    load_balancer: LoadBalancerPort | None = None
    container: ContainerPort | None = None
    secret: SecretPort | None = None
    infrastructure: InfrastructurePort | None = None

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> AdapterRegistry:
        from commodore.adapters.stubs import (
            InMemoryDNS,
            InMemoryReverseProxy,
            InMemoryLoadBalancer,
            InMemoryContainer,
            InMemorySecret,
            InMemoryInfrastructure,
        )

        adapter_map = {
            "dns": {"in_memory": InMemoryDNS},
            "reverse_proxy": {"in_memory": InMemoryReverseProxy},
            "load_balancer": {"in_memory": InMemoryLoadBalancer},
            "container": {"in_memory": InMemoryContainer},
            "secret": {"in_memory": InMemorySecret},
            "infrastructure": {"in_memory": InMemoryInfrastructure},
        }

        kwargs: dict[str, Any] = {}
        for port_name, port_config in config.items():
            adapter_type = port_config.get("type", "in_memory")
            if port_name in adapter_map and adapter_type in adapter_map[port_name]:
                kwargs[port_name] = adapter_map[port_name][adapter_type]()

        return cls(**kwargs)
