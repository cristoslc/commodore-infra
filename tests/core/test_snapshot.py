"""Tests for Snapshot Store (SPEC-017)."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from commodore.core.snapshot import Snapshot, SnapshotMeta, SnapshotStore


class TestSnapshot:
    """Snapshot structure and serialization."""

    def test_snapshot_to_dict(self):
        """Snapshot serializes to dict correctly."""
        meta = SnapshotMeta(
            id="test-001",
            timestamp="2026-04-05T12:00:00+00:00",
            hostsScanned=3,
            servicesDiscovered=5,
            adaptersUsed=["dns", "container"],
        )
        snapshot = Snapshot(
            meta=meta,
            hosts=[{"name": "host1", "state": "running"}],
            services=[{"name": "svc1", "type": "dns"}],
        )
        
        result = snapshot.to_dict()
        
        assert result["meta"]["id"] == "test-001"
        assert result["meta"]["hostsScanned"] == 3
        assert len(result["hosts"]) == 1
        assert len(result["services"]) == 1

    def test_snapshot_from_dict(self):
        """Snapshot deserializes from dict correctly."""
        data = {
            "meta": {
                "id": "test-002",
                "timestamp": "2026-04-05T12:00:00+00:00",
                "hostsScanned": 2,
                "servicesDiscovered": 3,
                "adaptersUsed": ["reverse_proxy"],
            },
            "hosts": [{"name": "web1", "state": "running"}],
            "services": [{"name": "example.com", "type": "proxy"}],
        }
        
        snapshot = Snapshot.from_dict(data)
        
        assert snapshot.meta.id == "test-002"
        assert snapshot.meta.hostsScanned == 2
        assert len(snapshot.hosts) == 1
        assert len(snapshot.services) == 1

    def test_snapshot_round_trip(self):
        """Snapshot survives round-trip through dict."""
        original = Snapshot(
            meta=SnapshotMeta(id="rt-001", timestamp="2026-01-01T00:00:00+00:00"),
            hosts=[{"name": "test"}],
            services=[{"name": "svc", "type": "dns"}],
        )
        
        serialized = original.to_dict()
        restored = Snapshot.from_dict(serialized)
        
        assert original.meta.id == restored.meta.id
        assert original.meta.timestamp == restored.meta.timestamp
        assert original.hosts == restored.hosts
        assert original.services == restored.services


class TestSnapshotStore:
    """Snapshot persistence to disk."""

    def test_save_and_load(self):
        """Save and load a snapshot."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store = SnapshotStore(base_dir=tmpdir)
            
            snapshot = Snapshot(
                meta=SnapshotMeta(
                    id="test-001",
                    timestamp="2026-04-05T12:00:00+00:00",
                ),
                hosts=[{"name": "host1"}],
                services=[{"name": "svc1"}],
            )
            
            saved_id = store.save(snapshot)
            
            loaded = store.load(saved_id)
            assert loaded is not None
            assert loaded.meta.id == "test-001"
            assert len(loaded.hosts) == 1

    def test_list_snapshots(self):
        """List returns sorted metadatas."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store = SnapshotStore(base_dir=tmpdir)
            
            # Create multiple snapshots
            store.save(Snapshot(
                meta=SnapshotMeta(id="s1", timestamp="2026-04-05T10:00:00+00:00"),
                hosts=[], services=[],
            ))
            store.save(Snapshot(
                meta=SnapshotMeta(id="s2", timestamp="2026-04-05T12:00:00+00:00"),
                hosts=[], services=[],
            ))
            store.save(Snapshot(
                meta=SnapshotMeta(id="s3", timestamp="2026-04-05T11:00:00+00:00"),
                hosts=[], services=[],
            ))
            
            listings = store.list()
            
            # Should be sorted newest first
            assert len(listings) == 3
            assert listings[0].id == "s2"  # Newest
            assert listings[1].id == "s3"
            assert listings[2].id == "s1"

    def test_delete_snapshot(self):
        """Delete removes the snapshot file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store = SnapshotStore(base_dir=tmpdir)
            
            snapshot = Snapshot(
                meta=SnapshotMeta(id="delete-me", timestamp="2026-01-01T00:00:00+00:00"),
                hosts=[], services=[],
            )
            
            store.save(snapshot)
            assert (Path(tmpdir) / "delete-me.json").exists()
            
            deleted = store.delete("delete-me")
            assert deleted is True
            assert not (Path(tmpdir) / "delete-me.json").exists()

    def test_create_snapshot(self):
        """Create generates unique ID and saves."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store = SnapshotStore(base_dir=tmpdir)
            
            snapshot = store.create_snapshot(
                hosts=[{"name": "host1"}],
                services=[{"name": "svc1"}],
                adapters=["dns"],
            )
            
            assert snapshot.meta.id.startswith("discovery-")
            assert len(snapshot.hosts) == 1
            assert len(snapshot.services) == 1
            assert "dns" in snapshot.meta.adaptersUsed

    def test_load_missing_snapshot(self):
        """Load returns None for non-existent snapshot."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store = SnapshotStore(base_dir=tmpdir)
            
            result = store.load("nonexistent")
            assert result is None