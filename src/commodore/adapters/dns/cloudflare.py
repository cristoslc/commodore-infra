"""Cloudflare DNS adapter (SPEC-012)."""

from __future__ import annotations

import urllib.request
import json
from typing import Any, Protocol

from commodore.ports.driven.base import Change, PortError, Result
from commodore.ports.driven.dns import DNSState


class CloudflareHTTPClient(Protocol):
    def list_records(self, zone_id: str) -> list[dict]: ...
    def create_record(self, zone_id: str, record: dict) -> dict: ...
    def update_record(self, zone_id: str, record_id: str, record: dict) -> dict: ...
    def delete_record(self, zone_id: str, record_id: str) -> None: ...


class RealCloudflareClient:
    """HTTP client for the Cloudflare API."""

    def __init__(self, api_token: str) -> None:
        self._token = api_token
        self._base = "https://api.cloudflare.com/client/v4"

    def _request(self, method: str, path: str, data: dict | None = None) -> dict:
        url = f"{self._base}{path}"
        body = json.dumps(data).encode() if data else None
        req = urllib.request.Request(url, data=body, method=method)
        req.add_header("Authorization", f"Bearer {self._token}")
        req.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())

    def list_records(self, zone_id: str) -> list[dict]:
        resp = self._request("GET", f"/zones/{zone_id}/dns_records")
        return resp.get("result", [])

    def create_record(self, zone_id: str, record: dict) -> dict:
        resp = self._request("POST", f"/zones/{zone_id}/dns_records", record)
        return resp.get("result", {})

    def update_record(self, zone_id: str, record_id: str, record: dict) -> dict:
        resp = self._request("PUT", f"/zones/{zone_id}/dns_records/{record_id}", record)
        return resp.get("result", {})

    def delete_record(self, zone_id: str, record_id: str) -> None:
        self._request("DELETE", f"/zones/{zone_id}/dns_records/{record_id}")


class CloudflareDNS:
    """DNSPort implementation using Cloudflare API."""

    def __init__(
        self,
        api_token: str,
        zone_id: str,
        _http_client: Any | None = None,
    ) -> None:
        self._zone_id = zone_id
        self._client: Any = _http_client or RealCloudflareClient(api_token)

    def current_state(self) -> DNSState:
        raw = self._client.list_records(self._zone_id)
        records = [
            {"id": r.get("id", ""), "name": r["name"], "type": r["type"], "target": r.get("content", r.get("target", ""))}
            for r in raw
        ]
        return DNSState(records=records)

    def diff(self, desired: list[dict[str, Any]]) -> list[Change]:
        current = self.current_state()
        current_by_name = {r["name"]: r for r in current.records}
        desired_by_name = {r["name"]: r for r in desired}

        changes: list[Change] = []
        for name, d in desired_by_name.items():
            if name not in current_by_name:
                changes.append(Change(port="dns", action="create", resource_id=name, before=None, after=d))
            else:
                cur = current_by_name[name]
                target = d.get("target", "")
                if cur.get("target", "") != target or cur.get("type", "") != d.get("type", ""):
                    changes.append(Change(port="dns", action="update", resource_id=name, before=cur, after=d))

        for name, cur in current_by_name.items():
            if name not in desired_by_name:
                changes.append(Change(port="dns", action="delete", resource_id=name, before=cur, after=None))

        return changes

    def apply(self, changes: list[Change]) -> Result:
        applied = 0
        errors: list[str] = []

        for change in changes:
            try:
                if change.action == "create":
                    record = {"name": change.resource_id, "type": change.after.get("type", "A"), "content": change.after.get("target", "")}
                    self._client.create_record(self._zone_id, record)
                elif change.action == "update":
                    record_id = change.before.get("id", "") if change.before else ""
                    record = {"name": change.resource_id, "type": change.after.get("type", "A"), "content": change.after.get("target", "")}
                    self._client.update_record(self._zone_id, record_id, record)
                elif change.action == "delete":
                    record_id = change.before.get("id", "") if change.before else ""
                    self._client.delete_record(self._zone_id, record_id)
                applied += 1
            except Exception as e:
                errors.append(f"DNS {change.action} failed for {change.resource_id}: {e}")

        return Result(success=len(errors) == 0, changes_applied=applied, errors=errors)
