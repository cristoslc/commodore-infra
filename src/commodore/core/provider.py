"""Provider model for adapter wiring (SPEC-015)."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import AbstractSet, Iterable


@dataclass(frozen=True)
class Provider:
    """A provider that backs one or more port adapters.
    
    Providers group adapters by their underlying infrastructure. For example,
    "cloudflare" can back both DNS and reverse proxy adapters with the same
    credentials.
    
    Attributes:
        name: Unique identifier for this provider (e.g., "cloudflare", "hetzner").
        credential_ref: How to resolve credentials. Supports:
            - "env:VAR_NAME" - read from environment variable
            - "direct_value" - literal value (for testing)
            - None - no credentials required
        port_types: Which port types this provider supports.
    """
    name: str
    credential_ref: str | None = None
    port_types: AbstractSet[str] = frozenset()
    
    def __init__(
        self,
        name: str,
        credential_ref: str | None = None,
        port_types: Iterable[str] | AbstractSet[str] = frozenset(),
    ) -> None:
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "credential_ref", credential_ref)
        # Normalize to frozenset for immutability
        if isinstance(port_types, frozenset):
            object.__setattr__(self, "port_types", port_types)
        else:
            object.__setattr__(self, "port_types", frozenset(port_types))
    
    def resolve_credential(self) -> str | None:
        """Resolve the credential reference to its actual value.
        
        Returns:
            The resolved credential value, or None if the reference cannot be resolved.
        
        Resolution rules:
            - "env:VAR_NAME" -> value of environment variable VAR_NAME (None if not set)
            - "direct_value" -> "direct_value" (literal)
            - None -> None
        """
        if self.credential_ref is None:
            return None
        
        if self.credential_ref.startswith("env:"):
            var_name = self.credential_ref[4:]
            return os.environ.get(var_name)
        
        # Direct value - return as-is
        return self.credential_ref
    
    def has_port(self, port_name: str) -> bool:
        """Check if this provider supports a given port type.
        
        Args:
            port_name: The port type to check (e.g., "dns", "reverse_proxy").
        
        Returns:
            True if this provider supports the port type.
        """
        return port_name in self.port_types