"""Example plugin adapter for Commodore.

This demonstrates how to create a plugin adapter that:
1. Implements a port protocol (DNSPort)
2. Registers via entry points in pyproject.toml
3. Gets discovered automatically by Commodore

Install this plugin with: pip install ./docs/examples/commodore-plugin-example
"""

from __future__ import annotations

from typing import Any
from dataclasses import dataclass, field

from commodore.ports.driven.base import Change, Result
from commodore.ports.driven.dns import DNSState, DNSPort


@dataclass(frozen=True)
class ExampleDNSAdapter:
    """Example DNS adapter implementing DNSPort protocol.

    This is a minimal stub that demonstrates the plugin interface.
    In a real plugin, you would:
    - Connect to a DNS provider API (Route53, DigitalOcean, Gandi, etc.)
    - Implement current_state() to fetch records
    - Implement diff() to compute changes
    - Implement apply() to make changes
    """

    # Configuration passed from topology.yaml
    api_endpoint: str = "https://api.example.com"
    api_token: str | None = None

    def current_state(self) -> DNSState:
        """Return the current DNS state from the provider."""
        # In a real plugin, this would call the provider API
        # For this example, return empty state
        return DNSState(records=[])

    def diff(self, desired: list[dict[str, Any]]) -> list[Change]:
        """Compute the diff between current and desired state."""
        # In a real plugin, you would compare current_state() with desired
        # For this example, return empty diff
        return []

    def apply(self, changes: list[Change]) -> Result:
        """Apply the changes to the provider."""
        # In a real plugin, you would make API calls to apply changes
        # For this example, return success with no changes
        return Result(success=True, changes_applied=0, errors=[])

    def health(self) -> bool:
        """Check if the adapter can connect to the provider."""
        # In a real plugin, you would verify credentials/connectivity
        # For this example, always return True
        return True