# Plugin Development Guide

This guide explains how to create a plugin adapter for Commodore.

## Overview

Commodore uses Python entry points for plugin discovery. A plugin is a standard Python package that:

1. Implements one or more port protocols (`DNSPort`, `ReverseProxyPort`, `ContainerPort`, etc.)
2. Declares adapters via `[project.entry-points."commodore.adapters"]`
3. Depends on `commodore-core` for port protocol definitions

## Quick Start

See `docs/examples/commodore-plugin-example/` for a minimal working plugin.

### 1. Create the Package Structure

```
commodore-myprovider/
├── pyproject.toml
├── src/
│   └── commodore_myprovider/
│       └── __init__.py    # Contains your adapter class
└── tests/
    └── test_adapter.py
```

### 2. Define Your Adapter

```python
# src/commodore_myprovider/__init__.py
from commodore.ports.driven.dns import DNSPort, DNSState

class MyDNSAdapter:
    """DNS adapter for MyProvider."""

    def __init__(self, api_token: str, zone_id: str):
        self.api_token = api_token
        self.zone_id = zone_id

    def current_state(self) -> DNSState:
        # Fetch records from API
        ...

    def diff(self, desired):
        # Compute changes needed
        ...

    def apply(self, changes):
        # Apply changes to API
        ...

    def health(self) -> bool:
        # Verify connectivity/credentials
        ...
```

### 3. Register via Entry Points

```toml
# pyproject.toml
[project]
name = "commodore-myprovider"
dependencies = ["commodore>=0.1.0"]

[project.entry-points."commodore.adapters"]
# Format: {port}_{provider} = module:AdapterClass
dns_myprovider = "commodore_myprovider:MyDNSAdapter"
```

### 4. Use in Topology

```yaml
# topology.yaml
providers:
  myprovider:
    credentials: env:MYPROVIDER_API_TOKEN
    zone_id: env:MYPROVIDER_ZONE_ID
    ports: [dns]

hosts:
  webserver:
    dns_provider: myprovider
    ...
```

## Port Protocols

### DNSPort

Implement for DNS providers (Route53, Cloudflare, DigitalOcean, etc.):

```python
from commodore.ports.driven.dns import DNSPort, DNSState
from commodore.ports.driven.base import Change, Result
from typing import Any

class MyDNSAdapter:
    def current_state(self) -> DNSState:
        """Return current DNS records."""
        records = self._fetch_records()
        return DNSState(records=records)

    def diff(self, desired: list[dict[str, Any]]) -> list[Change]:
        """Compute changes between current and desired state."""
        current = self.current_state()
        # Compare and return changes
        ...

    def apply(self, changes: list[Change]) -> Result:
        """Apply changes to DNS provider."""
        for change in changes:
            if change.action == "create":
                self._create_record(change.after)
            elif change.action == "update":
                self._update_record(change.before["id"], change.after)
            elif change.action == "delete":
                self._delete_record(change.before["id"])
        return Result(success=True, changes_applied=len(changes))

    def health(self) -> bool:
        """Verify API connectivity."""
        try:
            self._fetch_records()
            return True
        except Exception:
            return False
```

### ReverseProxyPort

Implement for reverse proxies (Nginx, Traefik, Envoy, Caddy, etc.):

```python
from commodore.ports.driven.reverse_proxy import ReverseProxyPort, ReverseProxyState

class MyProxyAdapter:
    def current_state(self) -> ReverseProxyState:
        """Return current proxy routes."""
        ...

    def diff(self, desired):
        ...

    def apply(self, changes):
        ...

    def health(self) -> bool:
        ...
```

### ContainerPort

Implement for container runtimes (Docker Compose, Kubernetes, Nomad, etc.):

```python
from commodore.ports.driven.container import ContainerPort, ContainerState

class MyContainerAdapter:
    def current_state(self) -> ContainerState:
        """Return running containers/stacks."""
        ...

    def diff(self, desired):
        ...

    def apply(self, changes):
        ...

    def health(self) -> bool:
        ...
```

### LoadBalancerPort

Implement for load balancers (HAProxy, NLB, etc.)

### SecretPort

Implement for secret stores (Vault, AWS Secrets Manager, etc.)

### InfrastructurePort

Implement for infrastructure providers (Vultr, DigitalOcean, AWS EC2, etc.)

## Configuration

Adapters receive configuration from `topology.yaml`:

```yaml
providers:
  myprovider:
    credentials: env:MYPROVIDER_API_TOKEN  # Resolved from environment
    zone_id: env:MYPROVIDER_ZONE_ID
    ports: [dns, reverse_proxy]
```

The `AdapterRegistry` resolves `env:VAR_NAME` references before passing values to your adapter.

## Testing Your Plugin

```python
# tests/test_adapter.py
import pytest
from commodore_myprovider import MyDNSAdapter
from commodore.ports.driven.dns import DNSState

def test_adapter_implements_dns_port():
    """Verify adapter implements DNSPort protocol."""
    adapter = MyDNSAdapter(api_token="test", zone_id="test")

    # Check protocol compliance
    assert hasattr(adapter, "current_state")
    assert hasattr(adapter, "diff")
    assert hasattr(adapter, "apply")
    assert hasattr(adapter, "health")

def test_current_state_returns_dns_state():
    adapter = MyDNSAdapter(api_token="test", zone_id="test")
    state = adapter.current_state()
    assert isinstance(state, DNSState)
```

## Publishing

Publish to PyPI:

```bash
# Build
python -m build

# Upload
twine upload dist/*

# Or use uv
uv build
uv publish
```

Users can then install your plugin:

```bash
pip install commodore-myprovider
# or
uv add commodore-myprovider
```

## Multiple Adapters in One Package

If your package provides multiple adapters:

```toml
[project.entry-points."commodore.adapters"]
dns_myprovider = "commodore_myprovider:MyDNSAdapter"
reverse_proxy_myprovider = "commodore_myprovider:MyProxyAdapter"
```

## Error Handling

Raise `ProviderNotFoundError` if a required dependency is missing:

```python
from commodore.core.errors import ProviderNotFoundError

class MyDNSAdapter:
    def __init__(self, api_token: str, zone_id: str):
        try:
            import myprovider_sdk
        except ImportError:
            raise ProviderNotFoundError(
                provider="myprovider",
                port="DNSPort"
            )
        self.client = myprovider_sdk.Client(api_token)
```

## Best Practices

1. **Minimal dependencies**: Only depend on `commodore-core` if you need port definitions
2. **Clear naming**: Use `{port}_{provider}` for entry point names
3. **Configuration validation**: Raise clear errors for missing config
4. **Health checks**: Verify credentials/connectivity in `health()`
5. **Idempotent apply**: `apply()` should be safe to call multiple times
6. **Structured logging**: Use Python's `logging` module

## Getting Started Checklist

- [ ] Create package structure with `pyproject.toml`
- [ ] Implement port protocol methods
- [ ] Add entry points in `pyproject.toml`
- [ ] Write unit tests
- [ ] Test with `cdre validate`
- [ ] Document configuration in README
- [ ] Publish to PyPI