"""Adapter registry (SPEC-005, SPEC-015)."""

from __future__ import annotations

import os
import warnings
from dataclasses import dataclass, field
from typing import Any

from commodore.core.provider import Provider
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
    _providers: tuple[Provider, ...] = ()
    _provider_map: dict[str, str] = field(default_factory=dict)  # port_name -> provider_name

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

    @classmethod
    def from_provider_config(cls, config: dict[str, Any]) -> AdapterRegistry:
        """Build registry from provider configuration.
        
        Args:
            config: Configuration dict with "providers" key mapping provider names
                    to their configuration.
        
        Returns:
            AdapterRegistry with adapters for each provider's ports.
        
        Provider config format:
            providers:
              cloudflare:
                credentials: env:CLOUDFLARE_API_TOKEN
                zone_id: env:CLOUDFLARE_ZONE_ID
                ports: [dns, reverse_proxy]
              nas:
                ssh_host: nas.local
                project_dir: /opt/stacks
                ports: [container]
        """
        providers_config = config.get("providers", {})
        providers: list[Provider] = []
        provider_map: dict[str, str] = {}
        dns: DNSPort | None = None
        reverse_proxy: ReverseProxyPort | None = None
        load_balancer: LoadBalancerPort | None = None
        container: ContainerPort | None = None
        secret: SecretPort | None = None
        infrastructure: InfrastructurePort | None = None

        for provider_name, provider_cfg in providers_config.items():
            cfg = dict(provider_cfg)  # Copy to avoid mutation
            
            # Resolve credentials
            cred_ref = cfg.get("credentials")
            if cred_ref and cred_ref.startswith("env:"):
                var_name = cred_ref[4:]
                cred_value = os.environ.get(var_name)
                if cred_value is None:
                    warnings.warn(
                        f"Provider {provider_name}: environment variable {var_name} not set, skipping",
                        UserWarning,
                    )
                    continue
            else:
                cred_value = cred_ref

            # Create provider
            port_types = frozenset(cfg.get("ports", []))
            provider = Provider(
                name=provider_name,
                credential_ref=cred_ref,
                port_types=port_types,
            )
            providers.append(provider)

            # Create adapters for each port type
            for port_type in port_types:
                provider_map[port_type] = provider_name
                
                if port_type == "dns":
                    dns = cls._create_dns_adapter(provider_name, cfg, cred_value)
                elif port_type == "reverse_proxy":
                    reverse_proxy = cls._create_reverse_proxy_adapter(provider_name, cfg, cred_value)
                elif port_type == "container":
                    container = cls._create_container_adapter(provider_name, cfg, cred_value)
                # load_balancer and infrastructure adapters may be added later

        return cls(
            dns=dns,
            reverse_proxy=reverse_proxy,
            load_balancer=load_balancer,
            container=container,
            secret=secret,
            infrastructure=infrastructure,
            _providers=tuple(providers),
            _provider_map=provider_map,
        )

    @staticmethod
    def _create_dns_adapter(
        provider_name: str,
        cfg: dict[str, Any],
        cred_value: str | None,
    ) -> DNSPort:
        """Create a DNS adapter for the provider."""
        if provider_name == "cloudflare":
            from commodore.adapters.dns.cloudflare import CloudflareDNS
            # Resolve zone_id from env if needed
            zone_id = cfg.get("zone_id", "")
            if zone_id and zone_id.startswith("env:"):
                zone_id = os.environ.get(zone_id[4:], "")
            return CloudflareDNS(api_token=cred_value or "", zone_id=zone_id)
        else:
            # Fallback to in-memory stub
            from commodore.adapters.stubs import InMemoryDNS
            return InMemoryDNS()

    @staticmethod
    def _create_reverse_proxy_adapter(
        provider_name: str,
        cfg: dict[str, Any],
        cred_value: str | None,
    ) -> ReverseProxyPort:
        """Create a reverse proxy adapter for the provider."""
        if provider_name == "cloudflare":
            # Cloudflare proxy is handled via CloudflareDNS for now
            # This may be split into separate proxy adapter later
            from commodore.adapters.stubs import InMemoryReverseProxy
            return InMemoryReverseProxy()
        elif "ssh_host" in cfg:
            from commodore.adapters.reverse_proxy.caddy import CaddyAdapter
            return CaddyAdapter(
                ssh_host=cfg["ssh_host"],
                caddyfile_path=cfg.get("caddyfile_path", "/etc/caddy/Caddyfile"),
            )
        else:
            from commodore.adapters.stubs import InMemoryReverseProxy
            return InMemoryReverseProxy()

    @staticmethod
    def _create_container_adapter(
        provider_name: str,
        cfg: dict[str, Any],
        cred_value: str | None,
    ) -> ContainerPort:
        """Create a container adapter for the provider."""
        if "ssh_host" in cfg:
            from commodore.adapters.container.docker_compose import DockerComposeAdapter
            return DockerComposeAdapter(
                ssh_host=cfg["ssh_host"],
                project_dir=cfg.get("project_dir", "/opt/stacks"),
            )
        else:
            from commodore.adapters.stubs import InMemoryContainer
            return InMemoryContainer()

    def provider_for_port(self, port_name: str) -> Provider | None:
        """Return the Provider backing a given port type.
        
        Args:
            port_name: The port type (dns, reverse_proxy, etc.)
        
        Returns:
            The Provider instance or None if no provider backs this port.
        """
        provider_name = self._provider_map.get(port_name)
        if provider_name is None:
            return None
        for provider in self._providers:
            if provider.name == provider_name:
                return provider
        return None

    def adapters_for_provider(self, provider_name: str) -> dict[str, Any]:
        """Return all adapters for a named provider.
        
        Args:
            provider_name: The provider name from config.
        
        Returns:
            Dict mapping port type to adapter instance for this provider.
        """
        result: dict[str, Any] = {}
        for port_type, pname in self._provider_map.items():
            if pname == provider_name:
                adapter = getattr(self, port_type, None)
                if adapter is not None:
                    result[port_type] = adapter
        return result
