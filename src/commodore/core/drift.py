"""Drift comparison between discovered and declared state (SPEC-019)."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Drift:
    """Drift for a single category (hosts or services)."""
    added: list[dict[str, Any]] = field(default_factory=list)
    removed: list[dict[str, Any]] = field(default_factory=list)
    modified: list[dict[str, Any]] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.added) + len(self.removed) + len(self.modified)


@dataclass
class DriftReport:
    """Complete drift report comparing discovered vs declared state."""
    hosts: Drift = field(default_factory=Drift)
    services: Drift = field(default_factory=Drift)

    @property
    def total_added(self) -> int:
        """Total items added (discoveried that aren't declared)."""
        return len(self.hosts.added) + len(self.services.added)

    @property
    def total_removed(self) -> int:
        """Total items removed (declared but not discovered)."""
        return len(self.hosts.removed) + len(self.services.removed)

    @property
    def total_modified(self) -> int:
        """Total items modified (state differs)."""
        return len(self.hosts.modified) + len(self.services.modified)

    @property
    def total(self) -> int:
        """Total drift items."""
        return self.total_added + self.total_removed + self.total_modified

    @property
    def status(self) -> str:
        """Overall drift status."""
        if self.total == 0:
            return "clean"
        return "dirty"

    def to_json(self) -> str:
        """Serialize to JSON."""
        return json.dumps({
            "status": self.status,
            "hosts": {
                "added": self.hosts.added,
                "removed": self.hosts.removed,
                "modified": self.hosts.modified,
            },
            "services": {
                "added": self.services.added,
                "removed": self.services.removed,
                "modified": self.services.modified,
            },
        }, indent=2)

    def format(self) -> str:
        """Format as human-readable text."""
        lines = [f"Drift Report: {self.status.upper()}"]
        
        if self.total == 0:
            lines.append("No drift detected. Discovered state matches declared state.")
            return "\n".join(lines)
        
        if self.hosts.added:
            lines.append(f"\n-hosts (found but not declared):")
            for h in self.hosts.added:
                lines.append(f"  + {h.get('name', 'unknown')}")
        
        if self.hosts.removed:
            lines.append(f"\n-hosts (declared but not found):")
            for h in self.hosts.removed:
                lines.append(f"  - {h.get('name', 'unknown')}")
        
        if self.hosts.modified:
            lines.append(f"\n-hosts (state changed):")
            for h in self.hosts.modified:
                lines.append(f"  ~ {h.get('name', 'unknown')}: {h.get('reason', 'modified')}")
        
        if self.services.added:
            lines.append(f"\n-services (found but not declared):")
            for s in self.services.added:
                lines.append(f"  + {s.get('name', 'unknown')} ({s.get('type', 'unknown')})")
        
        if self.services.removed:
            lines.append(f"\n-services (declared but not found):")
            for s in self.services.removed:
                lines.append(f"  - {s.get('name', 'unknown')} ({s.get('type', 'unknown')})")
        
        return "\n".join(lines)