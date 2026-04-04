"""Tests for Docker Compose adapter (SPEC-013).

Uses a mock SSH executor to avoid real SSH connections.
"""

from __future__ import annotations

from commodore.adapters.container.docker_compose import DockerComposeAdapter
from commodore.ports.driven.container import ContainerPort


class TestProtocolCompliance:
    def test_is_container_port(self):
        adapter = DockerComposeAdapter(ssh_host="test", project_dir="/opt/stacks", _executor=MockExecutor())
        assert isinstance(adapter, ContainerPort)


class TestDockerComposeAdapter:
    def test_current_state_empty(self):
        adapter = DockerComposeAdapter(ssh_host="test", project_dir="/opt/stacks", _executor=MockExecutor(ps_output="[]"))
        state = adapter.current_state()
        assert state.stacks == []

    def test_current_state_with_running(self):
        ps_json = '[{"Name": "jellyseerr", "State": "running", "Image": "test:latest"}]'
        adapter = DockerComposeAdapter(ssh_host="test", project_dir="/opt/stacks", _executor=MockExecutor(ps_output=ps_json))
        state = adapter.current_state()
        assert len(state.stacks) == 1

    def test_diff_new_stack(self):
        adapter = DockerComposeAdapter(ssh_host="test", project_dir="/opt/stacks", _executor=MockExecutor(ps_output="[]"))
        changes = adapter.diff([{"name": "jellyseerr", "image": "test:latest", "ports": [5055]}])
        assert len(changes) == 1
        assert changes[0].action == "create"

    def test_apply_creates_stack(self):
        executor = MockExecutor(ps_output="[]")
        adapter = DockerComposeAdapter(ssh_host="test", project_dir="/opt/stacks", _executor=executor)
        changes = adapter.diff([{"name": "jellyseerr", "image": "test:latest", "ports": [5055]}])
        result = adapter.apply(changes)
        assert result.success
        assert len(executor.commands_run) > 0


class MockExecutor:
    """Mock SSH command executor."""

    def __init__(self, ps_output: str = "[]", fail: bool = False) -> None:
        self.ps_output = ps_output
        self.fail = fail
        self.commands_run: list[str] = []

    def run(self, host: str, command: str) -> str:
        self.commands_run.append(command)
        if self.fail:
            raise RuntimeError("SSH connection failed")
        if "ps" in command and "--format" in command:
            return self.ps_output
        return ""
