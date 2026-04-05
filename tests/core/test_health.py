"""Tests for health() method on all port protocols (SPEC-015)."""

from __future__ import annotations

import pytest

from commodore.adapters.stubs import (
    InMemoryDNS,
    InMemoryReverseProxy,
    InMemoryLoadBalancer,
    InMemoryContainer,
    InMemorySecret,
    InMemoryInfrastructure,
)
from commodore.adapters.dns.cloudflare import CloudflareDNS
from commodore.adapters.reverse_proxy.caddy import CaddyAdapter
from commodore.adapters.container.docker_compose import DockerComposeAdapter


class TestStubAdapterHealth:
    """All stub adapters health() returns True."""

    def test_in_memory_dns_health(self):
        """InMemoryDNS.health() returns True."""
        adapter = InMemoryDNS()
        assert adapter.health() is True

    def test_in_memory_reverse_proxy_health(self):
        """InMemoryReverseProxy.health() returns True."""
        adapter = InMemoryReverseProxy()
        assert adapter.health() is True

    def test_in_memory_load_balancer_health(self):
        """InMemoryLoadBalancer.health() returns True."""
        adapter = InMemoryLoadBalancer()
        assert adapter.health() is True

    def test_in_memory_container_health(self):
        """InMemoryContainer.health() returns True."""
        adapter = InMemoryContainer()
        assert adapter.health() is True

    def test_in_memory_secret_health(self):
        """InMemorySecret.health() returns True."""
        adapter = InMemorySecret()
        assert adapter.health() is True

    def test_in_memory_infrastructure_health(self):
        """InMemoryInfrastructure.health() returns True."""
        adapter = InMemoryInfrastructure()
        assert adapter.health() is True


class TestCloudflareDNSHealth:
    """Cloudflare DNS adapter health check."""

    def test_health_with_valid_token(self, monkeypatch):
        """health() returns True when API token is valid."""
        # Mock HTTP client that succeeds
        class MockClient:
            def list_records(self, zone_id):
                return []  # Success
        
        adapter = CloudflareDNS(
            api_token="valid_token",
            zone_id="zone123",
            _http_client=MockClient(),
        )
        assert adapter.health() is True

    def test_health_with_invalid_token(self, monkeypatch):
        """health() returns False when API token is invalid."""
        # Mock HTTP client that fails
        class MockClient:
            def list_records(self, zone_id):
                raise Exception("403 Forbidden")
        
        adapter = CloudflareDNS(
            api_token="invalid_token",
            zone_id="zone123",
            _http_client=MockClient(),
        )
        assert adapter.health() is False


class TestCaddyAdapterHealth:
    """Caddy adapter health check."""

    def test_health_with_ssh_connectivity(self):
        """health() returns True when SSH connection succeeds."""
        class MockExecutor:
            def run(self, host, command):
                return ""  # Success
        
        adapter = CaddyAdapter(
            ssh_host="nas.local",
            caddyfile_path="/etc/caddy/Caddyfile",
            _executor=MockExecutor(),
        )
        assert adapter.health() is True

    def test_health_with_ssh_failure(self):
        """health() returns False when SSH connection fails."""
        class MockExecutor:
            def run(self, host, command):
                raise RuntimeError("SSH connection refused")
        
        adapter = CaddyAdapter(
            ssh_host="unreachable.local",
            caddyfile_path="/etc/caddy/Caddyfile",
            _executor=MockExecutor(),
        )
        assert adapter.health() is False


class TestDockerComposeAdapterHealth:
    """Docker Compose adapter health check."""

    def test_health_with_ssh_connectivity(self):
        """health() returns True when SSH connection succeeds."""
        class MockExecutor:
            def run(self, host, command):
                return "[]"
        
        adapter = DockerComposeAdapter(
            ssh_host="nas.local",
            project_dir="/opt/stacks",
            _executor=MockExecutor(),
        )
        assert adapter.health() is True

    def test_health_with_ssh_failure(self):
        """health() returns False when SSH connection fails."""
        class MockExecutor:
            def run(self, host, command):
                raise RuntimeError("SSH connection refused")
        
        adapter = DockerComposeAdapter(
            ssh_host="unreachable.local",
            project_dir="/opt/stacks",
            _executor=MockExecutor(),
        )
        assert adapter.health() is False