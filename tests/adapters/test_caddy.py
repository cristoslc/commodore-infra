"""Tests for SSH+Caddy reverse proxy adapter (SPEC-014).

Uses a mock SSH executor to avoid real SSH connections.
"""

from __future__ import annotations

from commodore.adapters.reverse_proxy.caddy import CaddyAdapter
from commodore.ports.driven.reverse_proxy import ReverseProxyPort


class TestProtocolCompliance:
    def test_is_reverse_proxy_port(self):
        adapter = CaddyAdapter(ssh_host="test", caddyfile_path="/etc/caddy/Caddyfile", _executor=MockExecutor())
        assert isinstance(adapter, ReverseProxyPort)


class TestCaddyAdapter:
    def test_current_state_empty(self):
        adapter = CaddyAdapter(ssh_host="test", caddyfile_path="/etc/caddy/Caddyfile", _executor=MockExecutor(cat_output=""))
        state = adapter.current_state()
        assert state.routes == []

    def test_current_state_with_routes(self):
        caddyfile = "requests.example.com {\n  reverse_proxy http://nas:5055\n}\n"
        adapter = CaddyAdapter(ssh_host="test", caddyfile_path="/etc/caddy/Caddyfile", _executor=MockExecutor(cat_output=caddyfile))
        state = adapter.current_state()
        assert len(state.routes) == 1

    def test_diff_new_route(self):
        adapter = CaddyAdapter(ssh_host="test", caddyfile_path="/etc/caddy/Caddyfile", _executor=MockExecutor(cat_output=""))
        changes = adapter.diff([{"name": "requests.example.com", "upstream": "http://nas:5055", "tls": "auto"}])
        assert len(changes) == 1
        assert changes[0].action == "create"

    def test_apply_updates_caddyfile(self):
        executor = MockExecutor(cat_output="")
        adapter = CaddyAdapter(ssh_host="test", caddyfile_path="/etc/caddy/Caddyfile", _executor=executor)
        changes = adapter.diff([{"name": "requests.example.com", "upstream": "http://nas:5055", "tls": "auto"}])
        result = adapter.apply(changes)
        assert result.success
        assert any("caddy reload" in cmd for cmd in executor.commands_run)

    def test_validate_missing_upstream(self):
        adapter = CaddyAdapter(ssh_host="test", caddyfile_path="/etc/caddy/Caddyfile", _executor=MockExecutor())
        errors = adapter.validate({"name": "test.example.com"})
        assert len(errors) > 0
        assert "upstream" in errors[0].lower()

    def test_validate_valid_config(self):
        adapter = CaddyAdapter(ssh_host="test", caddyfile_path="/etc/caddy/Caddyfile", _executor=MockExecutor())
        errors = adapter.validate({"name": "test.example.com", "upstream": "http://localhost:8080"})
        assert errors == []


class MockExecutor:
    """Mock SSH command executor."""

    def __init__(self, cat_output: str = "", fail: bool = False) -> None:
        self.cat_output = cat_output
        self.fail = fail
        self.commands_run: list[str] = []

    def run(self, host: str, command: str) -> str:
        self.commands_run.append(command)
        if self.fail:
            raise RuntimeError("SSH connection failed")
        if "cat" in command:
            return self.cat_output
        return ""
