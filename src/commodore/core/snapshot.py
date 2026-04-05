"""Snapshot store for discovered state (SPEC-017)."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class SnapshotMeta:
    """Metadata for a discovery snapshot."""
    id: str
    timestamp: str
    hostsScanned: int = 0
    servicesDiscovered: int = 0
    adaptersUsed: list[str] = field(default_factory=list)


@dataclass
class Snapshot:
    """A discovery snapshot."""
    meta: SnapshotMeta
    hosts: list[dict[str, Any]]
    services: list[dict[str, Any]]
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dict for JSON serialization."""
        return {
            "meta": {
                "id": self.meta.id,
                "timestamp": self.meta.timestamp,
                "hostsScanned": self.meta.hostsScanned,
                "servicesDiscovered": self.meta.servicesDiscovered,
                "adaptersUsed": self.meta.adaptersUsed,
            },
            "hosts": self.hosts,
            "services": self.services,
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Snapshot:
        """Create from dict."""
        meta_data = data.get("meta", {})
        return cls(
            meta=SnapshotMeta(
                id=meta_data.get("id", ""),
                timestamp=meta_data.get("timestamp", ""),
                hostsScanned=meta_data.get("hostsScanned", 0),
                servicesDiscovered=meta_data.get("servicesDiscovered", 0),
                adaptersUsed=meta_data.get("adaptersUsed", []),
            ),
            hosts=data.get("hosts", []),
            services=data.get("services", []),
        )


class SnapshotStore:
    """Persists discovery snapshots to disk.
    
    Snapshots are stored as JSON files in `.snapshots/` directory.
    Each snapshot gets a unique ID and timestamped filename.
    """
    
    def __init__(self, base_dir: str | None = None) -> None:
        self.base_dir = Path(base_dir or ".snapshots")
        self.base_dir.mkdir(exist_ok=True)
    
    def save(self, snapshot: Snapshot) -> str:
        """Save a snapshot and return its ID."""
        snapshot_id = snapshot.meta.id
        filename = f"{snapshot_id}.json"
        filepath = self.base_dir / filename
        
        with open(filepath, "w") as f:
            json.dump(snapshot.to_dict(), f, indent=2)
        
        return snapshot_id
    
    def load(self, snapshot_id: str) -> Snapshot | None:
        """Load a snapshot by ID."""
        filepath = self.base_dir / f"{snapshot_id}.json"
        if not filepath.exists():
            return None
        
        with open(filepath) as f:
            data = json.load(f)
        
        return Snapshot.from_dict(data)
    
    def list(self) -> list[SnapshotMeta]:
        """List all snapshot metadatas."""
        snapshots = []
        for filepath in self.base_dir.glob("*.json"):
            try:
                with open(filepath) as f:
                    data = json.load(f)
                snapshots.append(SnapshotMeta(
                    id=data.get("meta", {}).get("id", ""),
                    timestamp=data.get("meta", {}).get("timestamp", ""),
                    hostsScanned=data.get("meta", {}).get("hostsScanned", 0),
                    servicesDiscovered=data.get("meta", {}).get("servicesDiscovered", 0),
                    adaptersUsed=data.get("meta", {}).get("adaptersUsed", []),
                ))
            except (json.JSONDecodeError, KeyError):
                continue
        
        # Sort by timestamp (newest first)
        snapshots.sort(key=lambda s: s.timestamp, reverse=True)
        return snapshots
    
    def delete(self, snapshot_id: str) -> bool:
        """Delete a snapshot by ID."""
        filepath = self.base_dir / f"{snapshot_id}.json"
        if filepath.exists():
            filepath.unlink()
            return True
        return False
    
    def create_snapshot(
        self,
        hosts: list[dict[str, Any]],
        services: list[dict[str, Any]],
        adapters: list[str] | None = None,
    ) -> Snapshot:
        """Create and save a new snapshot."""
        snapshot_id = f"discovery-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{hash((len(hosts), len(services))) % 1000:03d}"
        meta = SnapshotMeta(
            id=snapshot_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            hostsScanned=len(hosts),
            servicesDiscovered=len(services),
            adaptersUsed=adapters or [],
        )
        snapshot = Snapshot(
            meta=meta,
            hosts=hosts,
            services=services,
        )
        self.save(snapshot)
        return snapshot