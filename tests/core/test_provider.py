"""Tests for Provider model (SPEC-015)."""

from __future__ import annotations

import pytest

from commodore.core.provider import Provider


class TestProviderDataclass:
    """Provider dataclass with name, credential_ref, port_types."""

    def test_provider_creation_minimal(self):
        """Provider can be created with just name."""
        provider = Provider(name="cloudflare")
        assert provider.name == "cloudflare"
        assert provider.credential_ref is None
        assert provider.port_types == frozenset()

    def test_provider_creation_full(self):
        """Provider can be created with all fields."""
        provider = Provider(
            name="cloudflare",
            credential_ref="env:CLOUDFLARE_API_TOKEN",
            port_types=frozenset(["dns", "reverse_proxy"]),
        )
        assert provider.name == "cloudflare"
        assert provider.credential_ref == "env:CLOUDFLARE_API_TOKEN"
        assert provider.port_types == frozenset(["dns", "reverse_proxy"])

    def test_provider_is_frozen(self):
        """Provider is immutable after creation."""
        provider = Provider(name="hetzner")
        with pytest.raises(AttributeError):
            provider.name = "other"  # type: ignore

    def test_provider_port_types_accepts_iterable(self):
        """Provider port_types can be created from list, set, or frozenset."""
        from_list = Provider(name="test", port_types=["dns", "container"])
        from_set = Provider(name="test", port_types={"dns", "container"})
        from_frozen = Provider(name="test", port_types=frozenset(["dns", "container"]))
        
        assert from_list.port_types == from_set.port_types == from_frozen.port_types

    def test_provider_equality(self):
        """Providers with same fields are equal."""
        p1 = Provider(
            name="cloudflare",
            credential_ref="env:CF_TOKEN",
            port_types=frozenset(["dns", "reverse_proxy"]),
        )
        p2 = Provider(
            name="cloudflare",
            credential_ref="env:CF_TOKEN",
            port_types=frozenset(["dns", "reverse_proxy"]),
        )
        assert p1 == p2

    def test_provider_hashable(self):
        """Provider can be used in sets and dicts."""
        p1 = Provider(name="cloudflare", port_types=frozenset(["dns"]))
        p2 = Provider(name="hetzner", port_types=frozenset(["infrastructure"]))
        providers = {p1, p2}
        assert len(providers) == 2


class TestProviderCredentialResolution:
    """Credential reference resolution."""

    def test_credential_ref_env_prefix(self):
        """Credential refs with env: prefix resolve to env vars."""
        import os
        os.environ["TEST_API_TOKEN"] = "secret123"
        try:
            provider = Provider(name="test", credential_ref="env:TEST_API_TOKEN")
            resolved = provider.resolve_credential()
            assert resolved == "secret123"
        finally:
            del os.environ["TEST_API_TOKEN"]

    def test_credential_ref_missing_env_returns_none(self):
        """Missing env var returns None instead of raising."""
        provider = Provider(name="test", credential_ref="env:NONEXISTENT_VAR")
        resolved = provider.resolve_credential()
        assert resolved is None

    def test_credential_ref_direct_value(self):
        """Credential refs without prefix are returned as-is."""
        provider = Provider(name="test", credential_ref="direct_token_value")
        resolved = provider.resolve_credential()
        assert resolved == "direct_token_value"

    def test_credential_ref_none_returns_none(self):
        """None credential_ref returns None."""
        provider = Provider(name="test", credential_ref=None)
        resolved = provider.resolve_credential()
        assert resolved is None


class TestProviderPortTypes:
    """Port type validation."""

    def test_valid_port_types(self):
        """Valid port types are accepted."""
        provider = Provider(
            name="cloudflare",
            port_types=frozenset(["dns", "reverse_proxy", "load_balancer", "container", "secret", "infrastructure"]),
        )
        assert len(provider.port_types) == 6

    def test_has_port(self):
        """has_port checks if provider serves a port type."""
        provider = Provider(name="hetzner", port_types=frozenset(["infrastructure", "dns"]))
        assert provider.has_port("infrastructure") is True
        assert provider.has_port("dns") is True
        assert provider.has_port("reverse_proxy") is False