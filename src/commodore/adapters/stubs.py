"""In-memory stub adapters for all 6 ports (SPEC-006)."""

from __future__ import annotations

from typing import Any

from commodore.ports.driven.base import Change, Result
from commodore.ports.driven.dns import DNSState
from commodore.ports.driven.reverse_proxy import ProxyState
from commodore.ports.driven.load_balancer import LBState
from commodore.ports.driven.container import ContainerState
from commodore.ports.driven.infrastructure import InfraState


def _diff_lists(current: list[dict[str, Any]], desired: list[dict[str, Any]], port: str, key: str = "name") -> list[Change]:
    current_by_key = {r[key]: r for r in current if key in r}
    desired_by_key = {r[key]: r for r in desired if key in r}
    changes: list[Change] = []
    for k, d in desired_by_key.items():
        if k not in current_by_key:
            changes.append(Change(port=port, action="create", resource_id=k, before=None, after=d))
        elif current_by_key[k] != d:
            changes.append(Change(port=port, action="update", resource_id=k, before=current_by_key[k], after=d))
    for k in current_by_key:
        if k not in desired_by_key:
            changes.append(Change(port=port, action="delete", resource_id=k, before=current_by_key[k], after=None))
    return changes


class InMemoryDNS:
    def __init__(self, records: list[dict[str, Any]] | None = None) -> None:
        self._records: list[dict[str, Any]] = list(records) if records else []

    def current_state(self) -> DNSState:
        return DNSState(records=list(self._records))

    def diff(self, desired: list[dict[str, Any]]) -> list[Change]:
        return _diff_lists(self._records, desired, "dns")

    def apply(self, changes: list[Change]) -> Result:
        for c in changes:
            if c.action == "create":
                self._records.append(c.after)
            elif c.action == "update":
                self._records = [c.after if r.get("name") == c.resource_id else r for r in self._records]
            elif c.action == "delete":
                self._records = [r for r in self._records if r.get("name") != c.resource_id]
        return Result(success=True, changes_applied=len(changes))

    def health(self) -> bool:
        return True

    def reset(self) -> None:
        self._records.clear()


class InMemoryReverseProxy:
    def __init__(self, routes: list[dict[str, Any]] | None = None) -> None:
        self._routes: list[dict[str, Any]] = list(routes) if routes else []

    def current_state(self) -> ProxyState:
        return ProxyState(routes=list(self._routes))

    def diff(self, desired: list[dict[str, Any]]) -> list[Change]:
        return _diff_lists(self._routes, desired, "reverse_proxy")

    def apply(self, changes: list[Change]) -> Result:
        for c in changes:
            if c.action == "create":
                self._routes.append(c.after)
            elif c.action == "update":
                self._routes = [c.after if r.get("name") == c.resource_id else r for r in self._routes]
            elif c.action == "delete":
                self._routes = [r for r in self._routes if r.get("name") != c.resource_id]
        return Result(success=True, changes_applied=len(changes))

    def validate(self, config: dict[str, Any]) -> list[str]:
        errors: list[str] = []
        if "upstream" not in config:
            errors.append("Missing 'upstream' in reverse proxy config")
        return errors

    def health(self) -> bool:
        return True

    def reset(self) -> None:
        self._routes.clear()


class InMemoryLoadBalancer:
    def __init__(self, backends: list[dict[str, Any]] | None = None) -> None:
        self._backends: list[dict[str, Any]] = list(backends) if backends else []

    def current_state(self) -> LBState:
        return LBState(backends=list(self._backends))

    def diff(self, desired: list[dict[str, Any]]) -> list[Change]:
        return _diff_lists(self._backends, desired, "load_balancer")

    def apply(self, changes: list[Change]) -> Result:
        for c in changes:
            if c.action == "create":
                self._backends.append(c.after)
            elif c.action == "update":
                self._backends = [c.after if r.get("name") == c.resource_id else r for r in self._backends]
            elif c.action == "delete":
                self._backends = [r for r in self._backends if r.get("name") != c.resource_id]
        return Result(success=True, changes_applied=len(changes))

    def health(self) -> bool:
        return True

    def reset(self) -> None:
        self._backends.clear()


class InMemoryContainer:
    def __init__(self, stacks: list[dict[str, Any]] | None = None) -> None:
        self._stacks: list[dict[str, Any]] = list(stacks) if stacks else []

    def current_state(self) -> ContainerState:
        return ContainerState(stacks=list(self._stacks))

    def diff(self, desired: list[dict[str, Any]]) -> list[Change]:
        return _diff_lists(self._stacks, desired, "container")

    def apply(self, changes: list[Change]) -> Result:
        for c in changes:
            if c.action == "create":
                self._stacks.append(c.after)
            elif c.action == "update":
                self._stacks = [c.after if r.get("name") == c.resource_id else r for r in self._stacks]
            elif c.action == "delete":
                self._stacks = [r for r in self._stacks if r.get("name") != c.resource_id]
        return Result(success=True, changes_applied=len(changes))

    def health(self) -> bool:
        return True

    def reset(self) -> None:
        self._stacks.clear()


class InMemorySecret:
    def __init__(self, secrets: dict[str, str] | None = None) -> None:
        self._secrets: dict[str, str] = dict(secrets) if secrets else {}

    def get(self, ref: str) -> str:
        return self._secrets.get(ref, "")

    def get_batch(self, refs: list[str]) -> dict[str, str]:
        return {ref: self._secrets.get(ref, "") for ref in refs}

    def health(self) -> bool:
        return True

    def reset(self) -> None:
        self._secrets.clear()


class InMemoryInfrastructure:
    def __init__(self, hosts: list[dict[str, Any]] | None = None) -> None:
        self._hosts: list[dict[str, Any]] = list(hosts) if hosts else []

    def current_state(self) -> InfraState:
        return InfraState(hosts=list(self._hosts))

    def diff(self, desired: list[dict[str, Any]]) -> list[Change]:
        return _diff_lists(self._hosts, desired, "infrastructure")

    def apply(self, changes: list[Change]) -> Result:
        for c in changes:
            if c.action == "create":
                self._hosts.append(c.after)
            elif c.action == "update":
                self._hosts = [c.after if r.get("name") == c.resource_id else r for r in self._hosts]
            elif c.action == "delete":
                self._hosts = [r for r in self._hosts if r.get("name") != c.resource_id]
        return Result(success=True, changes_applied=len(changes))

    def health(self) -> bool:
        return True

    def reset(self) -> None:
        self._hosts.clear()
