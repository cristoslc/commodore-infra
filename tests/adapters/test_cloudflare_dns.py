"""Tests for Cloudflare DNS adapter (SPEC-012).

These tests use a mock HTTP client to avoid hitting real Cloudflare API.
The adapter must satisfy the same DNSPort protocol as InMemoryDNS.
"""

from __future__ import annotations

import pytest
from commodore.adapters.dns.cloudflare import CloudflareDNS
from commodore.ports.driven.dns import DNSPort


class TestProtocolCompliance:
    def test_is_dns_port(self):
        adapter = CloudflareDNS(api_token="test-token", zone_id="test-zone")
        assert isinstance(adapter, DNSPort)

    def test_has_required_methods(self):
        adapter = CloudflareDNS(api_token="test-token", zone_id="test-zone")
        assert hasattr(adapter, "current_state")
        assert hasattr(adapter, "diff")
        assert hasattr(adapter, "apply")


class TestCloudflareAdapter:
    def test_current_state_with_mock(self):
        adapter = CloudflareDNS(
            api_token="test-token",
            zone_id="test-zone",
            _http_client=MockCloudflareClient(records=[
                {"id": "rec1", "name": "test.example.com", "type": "A", "content": "1.2.3.4"},
            ]),
        )
        state = adapter.current_state()
        assert len(state.records) == 1
        assert state.records[0]["name"] == "test.example.com"

    def test_diff_detects_new_record(self):
        adapter = CloudflareDNS(
            api_token="test-token",
            zone_id="test-zone",
            _http_client=MockCloudflareClient(records=[]),
        )
        changes = adapter.diff([{"name": "new.example.com", "type": "CNAME", "target": "proxy.example.com"}])
        assert len(changes) == 1
        assert changes[0].action == "create"

    def test_diff_detects_update(self):
        adapter = CloudflareDNS(
            api_token="test-token",
            zone_id="test-zone",
            _http_client=MockCloudflareClient(records=[
                {"id": "rec1", "name": "test.example.com", "type": "A", "content": "1.2.3.4"},
            ]),
        )
        changes = adapter.diff([{"name": "test.example.com", "type": "A", "target": "5.6.7.8"}])
        assert len(changes) == 1
        assert changes[0].action == "update"

    def test_diff_detects_delete(self):
        adapter = CloudflareDNS(
            api_token="test-token",
            zone_id="test-zone",
            _http_client=MockCloudflareClient(records=[
                {"id": "rec1", "name": "old.example.com", "type": "A", "content": "1.2.3.4"},
            ]),
        )
        changes = adapter.diff([])
        assert len(changes) == 1
        assert changes[0].action == "delete"

    def test_apply_creates_record(self):
        client = MockCloudflareClient(records=[])
        adapter = CloudflareDNS(api_token="test-token", zone_id="test-zone", _http_client=client)
        changes = adapter.diff([{"name": "new.example.com", "type": "CNAME", "target": "proxy.example.com"}])
        result = adapter.apply(changes)
        assert result.success
        assert result.changes_applied == 1
        assert len(client.records) == 1

    def test_port_error_on_api_failure(self):
        client = MockCloudflareClient(records=[], fail_on_apply=True)
        adapter = CloudflareDNS(api_token="test-token", zone_id="test-zone", _http_client=client)
        from commodore.ports.driven.base import Change
        changes = [Change(port="dns", action="create", resource_id="fail.example.com", before=None, after={"name": "fail.example.com", "type": "A", "target": "1.2.3.4"})]
        result = adapter.apply(changes)
        assert not result.success


class MockCloudflareClient:
    """Mock HTTP client for testing without real API calls."""

    def __init__(self, records: list[dict] | None = None, fail_on_apply: bool = False) -> None:
        self.records = list(records) if records else []
        self.fail_on_apply = fail_on_apply

    def list_records(self, zone_id: str) -> list[dict]:
        return list(self.records)

    def create_record(self, zone_id: str, record: dict) -> dict:
        if self.fail_on_apply:
            raise RuntimeError("API error: rate limited")
        record["id"] = f"rec{len(self.records) + 1}"
        self.records.append(record)
        return record

    def update_record(self, zone_id: str, record_id: str, record: dict) -> dict:
        if self.fail_on_apply:
            raise RuntimeError("API error: rate limited")
        self.records = [record if r.get("id") == record_id else r for r in self.records]
        return record

    def delete_record(self, zone_id: str, record_id: str) -> None:
        if self.fail_on_apply:
            raise RuntimeError("API error: rate limited")
        self.records = [r for r in self.records if r.get("id") != record_id]
