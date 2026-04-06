"""Plugin Discovery (SPEC-020).

Entry point discovery for adapter registration.
"""

from __future__ import annotations

import importlib.metadata
from dataclasses import dataclass, field
from typing import Protocol, Type, runtime_checkable


@dataclass(frozen=True)
class DiscoveryResult:
    """Result of plugin discovery.

    Contains discovered adapters and any errors encountered.

    Attributes:
        adapters: Mapping of adapter name to entry point (not yet loaded).
        errors: List of error messages for adapters that failed to load.
    """
    adapters: dict[str, importlib.metadata.EntryPoint] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)


def discover_adapters(
    group: str = "commodore.adapters",
) -> DiscoveryResult:
    """Discover all registered adapters via Python entry points.

    Scans entry points in the specified group and returns a mapping
    of adapter names to their entry points (not loaded).

    Args:
        group: Entry point group to scan (default: "commodore.adapters")

    Returns:
        DiscoveryResult with adapters dict and errors list.
    """
    adapters: dict[str, importlib.metadata.EntryPoint] = {}
    errors: list[str] = []

    try:
        # Python 3.10+: entry_points() returns SelectableGroups
        eps = importlib.metadata.entry_points()
        if hasattr(eps, "select"):
            # SelectableGroups interface
            adapter_eps = eps.select(group=group)
        else:
            # Legacy dict interface (Python < 3.10)
            adapter_eps = eps.get(group, [])
    except Exception as e:
        # Return empty result on error
        return DiscoveryResult(adapters={}, errors=[f"Failed to discover adapters: {e}"])

    for ep in adapter_eps:
        # Check if entry point already exists with same name
        if ep.name in adapters:
            errors.append(
                f"Duplicate entry point '{ep.name}': {ep.value} "
                f"(existing: {adapters[ep.name].value})"
            )
            continue
        adapters[ep.name] = ep

    return DiscoveryResult(adapters=adapters, errors=errors)


def validate_adapter(
    adapter_class: Type,
    port_protocol: type,
) -> bool:
    """Validate that an adapter class implements a port protocol.

    Uses runtime_checkable Protocol to check if the adapter class
    implements the required methods.

    Args:
        adapter_class: The adapter class to validate.
        port_protocol: The Protocol class to check against.

    Returns:
        True if adapter implements the protocol, False otherwise.
    """
    # For Protocol classes with @runtime_checkable, isinstance works
    if hasattr(port_protocol, "__protocol_attrs__"):
        # This is a Protocol class
        if not isinstance(adapter_class, type):
            # Not a class, can't validate
            return False
        # Create instance to check (if adapter has no-arg constructor)
        try:
            instance = adapter_class()
            return isinstance(instance, port_protocol)
        except Exception:
            # Can't instantiate, try structural check
            return _check_protocol_structural(adapter_class, port_protocol)
    else:
        # Not a Protocol, use issubclass
        try:
            return issubclass(adapter_class, port_protocol)
        except TypeError:
            return False


def _check_protocol_structural(
    adapter_class: Type,
    protocol: type,
) -> bool:
    """Check if adapter implements protocol methods structurally.

    Used when runtime_checkable isinstance check fails (e.g.,
    when adapter can't be instantiated).
    """
    if not hasattr(protocol, "__protocol_attrs__"):
        return False

    required_methods = protocol.__protocol_attrs__
    for method_name in required_methods:
        if not hasattr(adapter_class, method_name):
            return False

    return True


def load_adapter(
    entry_point: importlib.metadata.EntryPoint,
    port_protocol: type,
) -> tuple[Type | None, str | None]:
    """Load an adapter from an entry point with validation.

    Attempts to load the entry point and validate it against
    the port protocol.

    Args:
        entry_point: The entry point to load.
        port_protocol: The expected port protocol.

    Returns:
        Tuple of (adapter_class, error_message).
        adapter_class is None if loading failed.
        error_message is None if loading succeeded.
    """
    try:
        adapter_class = entry_point.load()
        if validate_adapter(adapter_class, port_protocol):
            return adapter_class, None
        else:
            return None, (
                f"Adapter '{entry_point.name}' does not implement "
                f"required protocol {port_protocol.__name__}"
            )
    except ImportError as e:
        return None, (
            f"Failed to load adapter '{entry_point.name}': {e}"
        )
    except Exception as e:
        return None, (
            f"Unexpected error loading adapter '{entry_point.name}': {e}"
        )