"""Tests for Drift Comparison (SPEC-019)."""

from __future__ import annotations

from commodore.core.snapshot import Snapshot, SnapshotMeta


class TestDriftComparison:
    """Compare discovered state against declared state."""

    def test_no_drift_when_snapshots_match(self):
        """No drift when snapshot matches declared state."""
        # Simulated snapshot (discovered)
        snapshot = Snapshot(
            meta=SnapshotMeta(id="snap-001", timestamp="2026-04-05T12:00:00+00:00"),
            hosts=[{"name": "web1", "address": "10.0.0.1", "state": "running"}],
            services=[{"name": "web.example.com", "type": "dns", "target": "10.0.0.1"}],
        )
        
        # Declared state (from cdre.yaml)
        declared_hosts = [{"name": "web1", "address": "10.0.0.1"}]
        declared_services = [{"name": "web.example.com", "type": "dns"}]
        
        # Compare: no differences
        drift = self._compare(snapshot, declared_hosts, declared_services)
        
        assert len(drift.hosts.added) == 0
        assert len(drift.services.added) == 0
        assert len(drift.hosts.removed) == 0
        assert len(drift.services.removed) == 0
        assert drift.status == "clean"

    def test_drift_when_service_missing(self):
        """Detect missing services."""
        snapshot = Snapshot(
            meta=SnapshotMeta(id="snap-002", timestamp="2026-04-05T12:00:00+00:00"),
            hosts=[],
            services=[{"name": "web.example.com", "type": "dns"}],
        )
        
        declared_services = [
            {"name": "web.example.com", "type": "dns"},
            {"name": "api.example.com", "type": "dns"},
        ]
        
        drift = self._compare(snapshot, [], declared_services)
        
        assert len(drift.services.added) == 0  # What exists but shouldn't
        assert len(drift.services.removed) == 1  # What declared but not found
        assert drift.services.removed[0]["name"] == "api.example.com"

    def test_drift_when_service_added(self):
        """Detect unexpected services."""
        snapshot = Snapshot(
            meta=SnapshotMeta(id="snap-003", timestamp="2026-04-05T12:00:00+00:00"),
            hosts=[],
            services=[
                {"name": "web.example.com", "type": "dns"},
                {"name": "api.example.com", "type": "dns"},
            ],
        )
        
        declared_services = [
            {"name": "web.example.com", "type": "dns"},
        ]
        
        drift = self._compare(snapshot, [], declared_services)
        
        assert len(drift.services.added) == 1
        assert drift.services.added[0]["name"] == "api.example.com"
        assert len(drift.services.removed) == 0

    def test_drift_when_host_modified(self):
        """Detect modified host state."""
        snapshot = Snapshot(
            meta=SnapshotMeta(id="snap-004", timestamp="2026-04-05T12:00:00+00:00"),
            hosts=[{"name": "web1", "address": "10.0.0.1", "state": "running"}],
            services=[],
        )
        
        declared_hosts = [{"name": "web1", "address": "10.0.0.2"}]
        
        drift = self._compare(snapshot, declared_hosts, [])
        
        assert len(drift.hosts.modified) == 1
        assert drift.hosts.modified[0]["name"] == "web1"

    def test_drift_output_formats(self):
        """Drift report provides JSON and human-readable formats."""
        snapshot = Snapshot(
            meta=SnapshotMeta(id="snap-005", timestamp="2026-04-05T12:00:00+00:00"),
            hosts=[],
            services=[{"name": "extra.example.com", "type": "dns"}],
        )
        
        declared_services = []
        drift = self._compare(snapshot, [], declared_services)
        
        # JSON format
        json_report = drift.to_json()
        assert "extra.example.com" in json_report
        assert '"status": "dirty"' in json_report
        
        # Human-readable format
        text_report = drift.format()
        assert "extra.example.com" in text_report
        assert "dirty" in text_report.lower()

    def _compare(
        self,
        snapshot: Snapshot,
        declared_hosts: list[dict],
        declared_services: list[dict],
    ):
        """Compare snapshot against declared state."""
        from commodore.core.drift import Drift, DriftReport
        
        # Simple comparison logic
        discovered_hosts = {h["name"]: h for h in snapshot.hosts}
        declared_hosts_map = {h["name"]: h for h in declared_hosts}
        
        hosts_added = [h for h in snapshot.hosts if h["name"] not in declared_hosts_map]
        hosts_removed = [h for h in declared_hosts if h["name"] not in discovered_hosts]
        
        # Check for state differences (simplified)
        hosts_modified = []
        for name, disc in discovered_hosts.items():
            if name in declared_hosts_map:
                dec = declared_hosts_map[name]
                if disc.get("address") != dec.get("address"):
                    hosts_modified.append({"name": name, "reason": "address changed"})
        
        discovered_services = {s["name"]: s for s in snapshot.services}
        declared_services_map = {s["name"]: s for s in declared_services}
        
        services_added = [s for s in snapshot.services if s["name"] not in declared_services_map]
        services_removed = [s for s in declared_services if s["name"] not in discovered_services]
        
        return DriftReport(
            hosts=Drift(added=hosts_added, removed=hosts_removed, modified=hosts_modified),
            services=Drift(added=services_added, removed=services_removed, modified=[]),
        )


class TestDriftReport:
    """Drift report structure."""

    def test_drift_report_empty(self):
        """Empty drift report has zero counts."""
        from commodore.core.drift import Drift, DriftReport
        
        report = DriftReport(
            hosts=Drift(added=[], removed=[], modified=[]),
            services=Drift(added=[], removed=[], modified=[]),
        )
        
        assert report.total_added == 0
        assert report.total_removed == 0
        assert report.total_modified == 0

    def test_drift_report_counts(self):
        """Drift report counts all drift."""
        from commodore.core.drift import Drift, DriftReport
        
        report = DriftReport(
            hosts=Drift(added=[{"name": "h1"}], removed=[{"name": "h2"}], modified=[{"name": "h3"}]),
            services=Drift(added=[{"name": "s1"}], removed=[{"name": "s2"}], modified=[]),
        )
        
        assert report.total_added == 2
        assert report.total_removed == 2
        assert report.total_modified == 1

    def test_drift_report_status(self):
        """Drift report has status."""
        from commodore.core.drift import Drift, DriftReport
        
        report = DriftReport(
            hosts=Drift(added=[], removed=[], modified=[]),
            services=Drift(added=[], removed=[], modified=[]),
        )
        
        assert report.status == "clean"
        
        report2 = DriftReport(
            hosts=Drift(added=[{"name": "h1"}], removed=[], modified=[]),
            services=Drift(added=[], removed=[], modified=[]),
        )
        
        assert report2.status == "dirty"