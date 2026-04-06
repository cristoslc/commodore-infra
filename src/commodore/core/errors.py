"""Plugin error handling (SPEC-022).

ProviderNotFoundError for missing plugins with actionable messages.
"""

from __future__ import annotations

from typing import ClassVar


# Known providers map: {port_type: {provider_name: install_hint}}
KNOWN_PROVIDERS: dict[str, dict[str, str]] = {
    "dns": {
        "cloudflare": "commodore (built-in)",
        "route53": "commodore-route53",
        "digitalocean": "commodore-digitalocean",
        "gandi": "commodore-gandi",
    },
    "reverse_proxy": {
        "caddy": "commodore (built-in)",
        "nginx": "commodore-nginx",
        "traefik": "commodore-traefik",
        "envoy": "commodore-envoy",
    },
    "container": {
        "docker_compose": "commodore (built-in)",
        "kubernetes": "commodore-kubernetes",
        "nomad": "commodore-nomad",
    },
    "load_balancer": {
        "haproxy": "commodore-haproxy",
        "nginx": "commodore-nginx",
    },
    "secret": {
        "vault": "commodore-vault",
        "aws_secrets": "commodore-aws-secrets",
    },
    "infrastructure": {
        "hetzner": "commodore (built-in)",
        "vultr": "commodore-vultr",
        "digitalocean": "commodore-digitalocean",
        "aws": "commodore-aws",
    },
}


class ProviderNotFoundError(Exception):
    """Raised when a configured provider has no installed adapter.

    Attributes:
        provider: The provider name from configuration.
        port: The port type (DNSProvider, ReverseProxy, etc.).

    Example:
        >>> raise ProviderNotFoundError("envoy", "ReverseProxy")
        ProviderNotFoundError: Missing plugin for provider 'envoy' (port: ReverseProxy).
        Install: pip install commodore-envoy
    """

    def __init__(self, provider: str, port: str) -> None:
        self.provider = provider
        self.port = port
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        """Format the error message with install hint."""
        return format_missing_plugin_error(self.provider, self.port)


def format_missing_plugin_error(provider: str, port: str) -> str:
    """Format an actionable error message for missing plugins.

    Args:
        provider: The provider name that is missing.
        port: The port type that needs the provider.

    Returns:
        Formatted error message with install hint or docs link.
    """
    # Normalize port type name (remove "Port" suffix if present)
    port_name = port.replace("Port", "").replace("Provider", "")

    # Check if this is a known provider
    port_providers = KNOWN_PROVIDERS.get(port_name.lower(), {})
    port_providers.update(KNOWN_PROVIDERS.get(port.lower(), {}))

    if provider in port_providers:
        install_hint = port_providers[provider]
        if install_hint == "commodore (built-in)":
            return (
                f"Provider '{provider}' is a built-in adapter for {port} "
                f"but was not found in discovery. This may indicate a corrupted installation. "
                f"Try reinstalling commodore."
            )
        else:
            return (
                f"Missing plugin for provider '{provider}' (port: {port}). "
                f"Install: pip install {install_hint}"
            )

    # Unknown provider - suggest checking docs or implementing custom
    return (
        f"Missing plugin for provider '{provider}' (port: {port}). "
        f"Check https://commodore.dev/plugins for available plugins, "
        f"or implement your own adapter by following the plugin development guide."
    )