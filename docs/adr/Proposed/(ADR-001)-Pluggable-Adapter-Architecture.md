---
title: "Pluggable Adapter Architecture"
artifact: ADR-001
track: standing
status: Proposed
author: cristos
created: 2026-04-06
last-updated: 2026-04-06
linked-artifacts:
  - VISION-001
  - DESIGN-001
depends-on-artifacts: []
evidence-pool: ""
---

# Pluggable Adapter Architecture

## Context

Commodore's current hexagonal architecture (DESIGN-001) isolates the core domain from external systems through port interfaces. Adapters implement port protocols and are selected at configuration time. This works well for adapters that the core team ships (Cloudflare DNS, Docker Compose, Caddy).

However, the current design assumes all adapters are bundled with Commodore itself. A user who wants to add support for a new DNS provider (e.g., DNSMadeEasy), a new reverse proxy (e.g., Envoy), or a new VPS provider (e.g., Vultr) must fork Commodore and add their adapter to `src/commodore/adapters/`. This violates the core principle articulated in VISION-001: "Adding a new driven adapter requires implementing one port interface with zero core changes."

The gap: "zero core changes" is currently true for users who contribute upstream, but not for users who want local or private adapters.

## Decision

Adopt a **plugin architecture** for adapters. Commodore will discover and load adapters from external packages at runtime, enabling users to extend the platform without modifying the core codebase.

### Plugin Discovery

Adapters are discovered via Python entry points. A package declares its adapters in `pyproject.toml`:

```toml
[project.entry-points."commodore.adapters"]
dns_cloudflare = "commodore_dns_cloudflare:CloudflareDNSAdapter"
dns_route53 = "commodore_route53:Route53Adapter"
proxy_caddy = "commodore_caddy:CaddyAdapter"
```

Commodore's `AdapterRegistry` scans all registered entry points at startup and registers each adapter with its port type.

### Plugin Package Structure

A plugin package is a standard Python package with:

1. A `pyproject.toml` declaring entry points for one or more adapters
2. Adapter classes implementing port protocols from `commodore.ports`
3. Optional: provider-specific configuration schema extensions

Example minimal plugin:

```python
# commodore-vultr/src/commodore_vultr/__init__.py
from commodore.ports import Infrastructure

class VultrAdapter(Infrastructure):
    def provision_host(self, spec): ...
    def get_host_state(self, host): ...
    # ... rest of Infrastructure protocol
```

```toml
# commodore-vultr/pyproject.toml
[project]
name = "commodore-vultr"
dependencies = ["commodore-core>=1.0"]

[project.entry-points."commodore.adapters"]
infrastructure_vultr = "commodore_vultr:VultrAdapter"
```

### Configuration-Time Binding

The topology configuration remains unchanged. Users declare which provider to use:

```yaml
hosts:
  hetzner-vps:
    runtime: docker-compose
    dns_provider: cloudflare
    proxy_provider: caddy
    infrastructure_provider: hetzner  # built-in

  vultr-vps:
    runtime: docker-compose
    dns_provider: cloudflare
    proxy_provider: envoy  # external plugin
    infrastructure_provider: vultr  # external plugin
```

The `AdapterRegistry` resolves provider names to loaded plugins. If a provider is not found, `cdre validate` reports the missing plugin with install instructions.

### Built-in vs. External

Built-in adapters (Cloudflare DNS, Caddy, Docker Compose, etc.) remain in `src/commodore/adapters/`. They are discovered via the same entry point mechanism but registered from the core package. This ensures parity between built-in and external adapters.

External adapters are packages installed alongside Commodore (via pip, uv, or system packages). They can be:

- Published on PyPI for community use
- Installed from git URLs (e.g., private company adapters)
- Developed locally and installed in editable mode

### Health and Capability Protocol

All adapters implement `health() -> bool` (already in place per SPEC-015). Plugin adapters additionally declare their capabilities via port protocols they implement, enabling discovery without inspection.

## Alternatives Considered

### Alternative 1: Fork-based extension (current state)

Users fork Commodore and add adapters to `src/commodore/adapters/`. This requires:
- Maintaining a fork
- Merging upstream changes
- No clear distribution mechanism for private adapters

Rejected because it violates the core principle of zero core changes and creates maintenance burden.

### Alternative 2: Dynamic loading from directories

Scan a configured directory (e.g., `~/.config/commodore/plugins/`) for Python modules and load them. This avoids entry points but introduces security concerns (arbitrary code execution from user directories) and packaging complexity (no standard distribution mechanism).

Rejected because entry points provide a standardized, pip-compatible distribution model with dependency resolution.

### Alternative 3: Lua/WASM embedded scripting

Allow adapters to be written in an embedded language (Lua, WASM). This provides sandboxing but introduces:
- A bridge layer between core and plugin
- Limited access to standard library (HTTP clients, etc.)
- A new mental model for users

Rejected because Python-first development is a core value of Commodore. Users should use familiar tooling.

### Alternative 4: API-based adapters

Adapters run as separate processes communicating over HTTP or gRPC. This provides maximum isolation but:
- Adds latency and operational complexity
- Requires process management
- Overkill for single-operator deployments

Rejected because deployment simplicity is a core value. Commodore runs as a single CLI; no daemon is required.

## Consequences

### Positive

- **Extensibility:** Users can add adapters for any infrastructure provider without touching core
- **Third-party ecosystem:** Enables a plugin marketplace (DNS providers, reverse proxies, VPS hosts)
- **Private adapters:** Companies can maintain private adapters without publishing
- **Parity:** Built-in and external adapters use the same discovery mechanism
- **Testing isolation:** Adapters remain testable in isolation via port protocols

### Negative

- **Discovery complexity:** The `AdapterRegistry` must handle missing plugins, version mismatches, and dependency conflicts
- **Error messages:** When a configured provider has no installed plugin, error messages must guide the user to install it
- **Version coupling:** Plugin packages must stay compatible with the core's port protocol versions
- **Security:** Arbitrary code execution from installed packages (same risk as any pip package)

### Accepted Trade-offs

- The version coupling is acceptable because port protocols change rarely (ADR-protected)
- Error message quality is a UX concern, not an architecture blocker
- Security is delegated to Python's packaging ecosystem (same trust model as pip)

## Lifecycle

|| Phase | Date | Commit | Notes |
||-------|------|--------|-------|
|| Proposed | 2026-04-06 | -- | Initial creation |