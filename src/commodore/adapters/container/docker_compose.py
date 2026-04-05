"""Docker Compose adapter (SPEC-013)."""

from __future__ import annotations

import json
from typing import Any, Protocol

from commodore.ports.driven.base import Change, Result
from commodore.ports.driven.container import ContainerState


class SSHExecutor(Protocol):
    def run(self, host: str, command: str) -> str: ...


class RealSSHExecutor:
    """Execute commands on remote hosts via SSH."""

    def run(self, host: str, command: str) -> str:
        import subprocess
        result = subprocess.run(
            ["ssh", host, command],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            raise RuntimeError(f"SSH command failed on {host}: {result.stderr}")
        return result.stdout


class DockerComposeAdapter:
    """ContainerPort implementation using Docker Compose over SSH."""

    def __init__(
        self,
        ssh_host: str,
        project_dir: str,
        _executor: Any | None = None,
    ) -> None:
        self._host = ssh_host
        self._project_dir = project_dir
        self._executor: Any = _executor or RealSSHExecutor()

    def current_state(self) -> ContainerState:
        output = self._executor.run(self._host, f"cd {self._project_dir} && docker compose ps --format json 2>/dev/null || echo '[]'")
        try:
            stacks = json.loads(output)
            if isinstance(stacks, dict):
                stacks = [stacks]
        except json.JSONDecodeError:
            stacks = []
        return ContainerState(stacks=[{"name": s.get("Name", ""), "state": s.get("State", ""), "image": s.get("Image", "")} for s in stacks])

    def diff(self, desired: list[dict[str, Any]]) -> list[Change]:
        current = self.current_state()
        current_by_name = {s["name"]: s for s in current.stacks}
        desired_by_name = {s["name"]: s for s in desired}

        changes: list[Change] = []
        for name, d in desired_by_name.items():
            if name not in current_by_name:
                changes.append(Change(port="container", action="create", resource_id=name, before=None, after=d))
            else:
                cur = current_by_name[name]
                if cur.get("image") != d.get("image"):
                    changes.append(Change(port="container", action="update", resource_id=name, before=cur, after=d))

        for name in current_by_name:
            if name not in desired_by_name:
                changes.append(Change(port="container", action="delete", resource_id=name, before=current_by_name[name], after=None))

        return changes

    def apply(self, changes: list[Change]) -> Result:
        applied = 0
        errors: list[str] = []

        for change in changes:
            try:
                if change.action in ("create", "update"):
                    compose_yaml = self._generate_compose(change.after)
                    self._executor.run(self._host, f"mkdir -p {self._project_dir}/{change.resource_id}")
                    self._executor.run(self._host, f"cat > {self._project_dir}/{change.resource_id}/docker-compose.yml << 'CDRE_EOF'\n{compose_yaml}\nCDRE_EOF")
                    self._executor.run(self._host, f"cd {self._project_dir}/{change.resource_id} && docker compose up -d")
                elif change.action == "delete":
                    self._executor.run(self._host, f"cd {self._project_dir}/{change.resource_id} && docker compose down")
                applied += 1
            except Exception as e:
                errors.append(f"Container {change.action} failed for {change.resource_id}: {e}")

        return Result(success=len(errors) == 0, changes_applied=applied, errors=errors)

    def _generate_compose(self, spec: dict[str, Any]) -> str:
        name = spec.get("name", "service")
        image = spec.get("image", "")
        ports = spec.get("ports", [])
        port_lines = "\n".join(f'      - "{p}:{p}"' for p in ports)
        return f"""services:
  {name}:
    image: {image}
    ports:
{port_lines}
    restart: unless-stopped
"""

    def health(self) -> bool:
        """Verify SSH connectivity by running a test command."""
        try:
            self._executor.run(self._host, "echo ok")
            return True
        except Exception:
            return False
