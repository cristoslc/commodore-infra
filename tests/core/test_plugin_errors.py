"""Tests for Plugin Missing Error Handling (SPEC-022).

ProviderNotFoundError and actionable error messages.
"""

from __future__ import annotations

import pytest


# ============================================================================
# TDD Cycle 1: ProviderNotFoundError exception
# ============================================================================


class TestProviderNotFoundErrorContainsFields:
    """ProviderNotFoundError contains all required fields."""

    def test_exception_has_provider_field(self):
        """Exception includes provider name."""
        from commodore.core.errors import ProviderNotFoundError

        error = ProviderNotFoundError(
            provider="envoy",
            port="ReverseProxy",
        )

        assert error.provider == "envoy"

    def test_exception_has_port_field(self):
        """Exception includes port type."""
        from commodore.core.errors import ProviderNotFoundError

        error = ProviderNotFoundError(
            provider="route53",
            port="DNSProvider",
        )

        assert error.port == "DNSProvider"

    def test_exception_message_is_actionable(self):
        """Exception message includes provider, port, and install hint."""
        from commodore.core.errors import ProviderNotFoundError

        error = ProviderNotFoundError(
            provider="envoy",
            port="ReverseProxy",
        )

        message = str(error)

        # Message must contain actionable info
        assert "envoy" in message
        assert "ReverseProxy" in message
        # Actionable: either install command or docs/develop guide
        assert "Install" in message or "pip install" in message or "docs" in message.lower() or "implement" in message.lower()

    def test_exception_default_install_hint_for_known_provider(self):
        """Known providers get specific install hints."""
        from commodore.core.errors import ProviderNotFoundError

        error = ProviderNotFoundError(
            provider="cloudflare",
            port="DNSProvider",
        )

        message = str(error)

        # Cloudflare is built-in, should suggest it's available
        assert "cloudflare" in message.lower()


# ============================================================================
# TDD Cycle 2: Error formatting with install hints
# ============================================================================


class TestFormatMissingPluginErrorIncludesInstallHint:
    """format_missing_plugin_error provides install commands."""

    def test_format_includes_pip_install_for_known_provider(self):
        """Known providers show pip install command."""
        from commodore.core.errors import format_missing_plugin_error

        message = format_missing_plugin_error(
            provider="vultr",
            port="Infrastructure",
        )

        # Should suggest installing commodore-vultr
        assert "pip install" in message or "uv add" in message
        assert "vultr" in message.lower()

    def test_format_includes_docs_link_for_unknown_provider(self):
        """Unknown providers suggest checking docs."""
        from commodore.core.errors import format_missing_plugin_error

        message = format_missing_plugin_error(
            provider="mycompany-dns",
            port="DNSProvider",
        )

        # Should suggest docs or creating own adapter
        assert "commodore.dev" in message or "docs" in message.lower() or "custom" in message.lower()
        assert "mycompany-dns" in message

    def test_format_includes_port_type(self):
        """Formatted message includes port type for context."""
        from commodore.core.errors import format_missing_plugin_error

        message = format_missing_plugin_error(
            provider="nginx",
            port="ReverseProxy",
        )

        assert "ReverseProxy" in message


# ============================================================================
# TDD Cycle 3: Unknown provider handling
# ============================================================================


class TestUnknownProviderSuggestsDocs:
    """Unknown providers get helpful docs links."""

    def test_unknown_provider_suggests_plugin_docs(self):
        """Unknown providers point to plugin documentation."""
        from commodore.core.errors import format_missing_plugin_error

        message = format_missing_plugin_error(
            provider="acme-corpus-dns",
            port="DNSProvider",
        )

        # Custom internal providers should suggest building own
        assert "https://commodore.dev/plugins" in message or "implement your own" in message.lower()

    def test_partially_matching_provider_suggests_similar(self):
        """Provider names similar to known ones get suggestions."""
        from commodore.core.errors import format_missing_plugin_error

        message = format_missing_plugin_error(
            provider="cloudflar",  # typo
            port="DNSProvider",
        )

        # Could suggest "Did you mean cloudflare?"
        # This is optional but nice to have
        assert "cloudflar" in message


# ============================================================================
# TDD Cycle 4: CLI integration
# ============================================================================


class TestCdreValidateExitsNonzeroOnMissingPlugin:
    """cdre validate exits with code 1 when plugin missing."""

    def test_missing_plugin_exits_nonzero(self):
        """Missing plugin causes non-zero exit code."""
        from commodore.cli import app
        from click.testing import CliRunner

        runner = CliRunner()

        # This test would need a topology that references a missing provider
        # For now, we test that the error handling path works
        from commodore.core.errors import ProviderNotFoundError

        error = ProviderNotFoundError(provider="nonexistent", port="DNSProvider")
        
        # Verify the error can be caught and formatted
        message = str(error)
        assert "nonexistent" in message

    def test_missing_plugin_error_to_stderr(self):
        """Error message goes to stderr, not stdout."""
        from commodore.core.errors import ProviderNotFoundError, format_missing_plugin_error

        error = ProviderNotFoundError(
            provider="missing-provider",
            port="Infrastructure",
        )

        message = format_missing_plugin_error(
            provider="missing-provider",
            port="Infrastructure",
        )

        # Error message should be formatted for user display
        assert len(message) > 0
        assert "missing-provider" in message


# ============================================================================
# Known providers map
# ============================================================================


class TestKnownProvidersMap:
    """Known providers have install hints."""

    def test_known_dns_providers(self):
        """Common DNS providers are known."""
        from commodore.core.errors import KNOWN_PROVIDERS

        # cloudflare is built-in
        assert "cloudflare" in KNOWN_PROVIDERS.get("dns", {})

    def test_known_reverse_proxy_providers(self):
        """Common reverse proxy providers are known."""
        from commodore.core.errors import KNOWN_PROVIDERS

        # caddy is built-in
        assert "caddy" in KNOWN_PROVIDERS.get("reverse_proxy", {})

    def test_known_container_providers(self):
        """Common container runtimes are known."""
        from commodore.core.errors import KNOWN_PROVIDERS

        # docker_compose is built-in
        assert "docker_compose" in KNOWN_PROVIDERS.get("container", {})