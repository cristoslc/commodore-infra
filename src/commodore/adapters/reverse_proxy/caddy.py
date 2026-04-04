"""SSH+Caddy reverse proxy adapter (SPEC-014)."""

from __future__ import annotations

import re
from typing import Any, Protocol

from commodore.ports.driven.base import Change, Result
from commodore.ports.driven.reverse_proxy import ProxyState


class SSHExecutor(Protocol):
    def run(self, host: str, command: str) -> str: ...


class CaddyAdapter:
    """ReverseProxyPort implementation using Caddy managed over SSH."""

    def __init__(
        self,
        ssh_host: str,
        caddyfile_path: str = "/etc/caddy/Caddyfile",
        _executor: Any | None = None,
    ) -> None:
        self._host = ssh_host
        self._caddyfile_path = caddyfile_path
        self._executor: Any = _executor

    def current_state(self) -> ProxyState:
        output = self._executor.run(self._host, f"cat {self._caddyfile_path} 2>/dev/null || echo ''")
        routes = self._parse_caddyfile(output)
        return ProxyState(routes=routes)

    def diff(self, desired: list[dict[str, Any]]) -> list[Change]:
        current = self.current_state()
        current_by_name = {r["name"]: r for r in current.routes}
        desired_by_name = {r["name"]: r for r in desired}

        changes: list[Change] = []
        for name, d in desired_by_name.items():
            if name not in current_by_name:
                changes.append(Change(port="reverse_proxy", action="create", resource_id=name, before=None, after=d))
            else:
                cur = current_by_name[name]
                if cur.get("upstream") != d.get("upstream"):
                    changes.append(Change(port="reverse_proxy", action="update", resource_id=name, before=cur, after=d))

        for name in current_by_name:
            if name not in desired_by_name:
                changes.append(Change(port="reverse_proxy", action="delete", resource_id=name, before=current_by_name[name], after=None))

        return changes

    def apply(self, changes: list[Change]) -> Result:
        # Read current state, merge changes, write new Caddyfile, reload
        current = self.current_state()
        routes_by_name = {r["name"]: r for r in current.routes}

        for change in changes:
            if change.action in ("create", "update"):
                routes_by_name[change.resource_id] = change.after
            elif change.action == "delete":
                routes_by_name.pop(change.resource_id, None)

        caddyfile = self._generate_caddyfile(list(routes_by_name.values()))
        self._executor.run(self._host, f"cat > {self._caddyfile_path} << 'CDRE_EOF'\n{caddyfile}\nCDRE_EOF")
        self._executor.run(self._host, "caddy reload --config /etc/caddy/Caddyfile")

        return Result(success=True, changes_applied=len(changes))

    def validate(self, config: dict[str, Any]) -> list[str]:
        errors: list[str] = []
        if "upstream" not in config:
            errors.append("Missing 'upstream' in reverse proxy config")
        return errors

    def _parse_caddyfile(self, content: str) -> list[dict[str, Any]]:
        """Parse a simple Caddyfile into route dicts."""
        routes: list[dict[str, Any]] = []
        blocks = re.findall(r"(\S+)\s*\{([^}]*)\}", content)
        for domain, body in blocks:
            upstream_match = re.search(r"reverse_proxy\s+(\S+)", body)
            if upstream_match:
                routes.append({
                    "name": domain,
                    "upstream": upstream_match.group(1),
                    "tls": "auto",
                })
        return routes

    def _generate_caddyfile(self, routes: list[dict[str, Any]]) -> str:
        blocks = []
        for route in routes:
            name = route["name"]
            upstream = route.get("upstream", "")
            blocks.append(f"{name} {{\n  reverse_proxy {upstream}\n}}")
        return "\n\n".join(blocks) + "\n" if blocks else ""
