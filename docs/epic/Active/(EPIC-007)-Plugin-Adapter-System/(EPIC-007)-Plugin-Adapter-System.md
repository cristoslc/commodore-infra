---
title: "Plugin Adapter System"
artifact: EPIC-007
track: container
status: Active
author: cristos
created: 2026-04-06
last-updated: 2026-04-06
parent-vision: VISION-001
parent-initiative: ""
priority-weight: high
success-criteria:
  - "A user can install a third-party adapter package (e.g., `pip install commodore-vultr`) and use it in their topology"
  - "`cdre validate` reports missing plugins with install instructions, not stack traces"
  - "Built-in adapters (Cloudflare, Caddy, Docker Compose) are discovered via the same mechanism as external plugins"
  - "A minimal external plugin example is documented in a `docs/examples/` directory"
  - "The AdapterRegistry loads all adapters at startup and resolves provider names to implementations"
depends-on-artifacts:
  - EPIC-001
  - EPIC-002
  - EPIC-005
  - ADR-001
addresses: []
evidence-pool: ""
---

# Plugin Adapter System

## Goal / Objective

Transform Commodore's adapter layer from bundled-only to genuinely pluggable. Today, "zero core changes to add an adapter" is true only if you contribute upstream. After this epic, it's true for any user with a Python package. This unlocks third-party ecosystem growth, private infrastructure adapters, and community contributions without core team involvement.

## Desired Outcomes

The [Infrastructure Operator](../../../persona/Active/(PERSONA-001)-Infrastructure-Operator/(PERSONA-001)-Infrastructure-Operator.md) can:

1. Install an adapter for a provider we don't ship (e.g., Vultr, DNSMadeEasy, DigitalOcean) via `pip install commodore-vultr` and use it in their topology YAML
2. Develop a private adapter for internal infrastructure without maintaining a fork
3. Contribute an adapter upstream if they choose, knowing it will be discovered by the same mechanism as built-in adapters

The ecosystem benefits: third-party developers can publish adapters independently, and the Commodore core remains lean (no vendor-specific adapter accumulation).

## Progress

|| Date | Activity | Status |
||------|----------|--------|
|| 2026-04-06 | EPIC-007 activation | Active |

## Scope Boundaries

**In scope:**
- Entry point discovery mechanism for adapter registration
- `AdapterRegistry` enhancement to load all adapters at startup and resolve provider names
- Configuration-time binding: topology YAML references provider names, registry resolves to implementations
- Graceful error messages when a configured provider has no installed plugin
- Documentation and example for minimal plugin creation

**Out of scope:**
- Plugin marketplace or plugin search command (future work)
- Plugin dependency conflict resolution beyond what pip/uv already provides
- Security sandboxing of plugin code (same trust model as any Python package)
- Versioning strategy for plugin compatibility (ADR candidate, not EPIC scope)

## Scope Model

The plugin system operates at three layers:

```
topology.yaml            configuration-time binding
    |
    v
AdapterRegistry          resolves provider name → implementation
    |
    v
entry_points              Python package metadata [pyproject.toml]
    |
    v
Plugin Package            external Python package with adapter(s)
```

**Configuration layer:** Users write `infrastructure_provider: vultr` in topology YAML. No changes to configuration DSL.

**Registry layer:** The `AdapterRegistry` (from EPIC-005) gains a `discover_adapters()` method that scans `commodore.adapters` entry points. It maintains the mapping from provider names to implementations.

**Discovery layer:** Standard Python packaging. Plugin authors declare adapters in `pyproject.toml`. Users install the plugin via pip/uv. No special discovery CLI.

## Child Specs

|| Spec | Title | Priority | Dependencies | Status |
||------|-------|----------|--------------|--------|
|| SPEC-020 | Entry Point Discovery Mechanism | high | SPEC-005 | Proposed |
|| SPEC-021 | AdapterRegistry Plugin Loading | high | SPEC-005, SPEC-020 | Proposed |
|| SPEC-022 | Plugin Missing Error Handling | medium | SPEC-021 | Proposed |
|| SPEC-023 | Plugin Development Guide | medium | SPEC-020, SPEC-021 | Proposed |

**Dependency chain:** SPEC-020 (entry points) → SPEC-021 (registry loading) → SPEC-022 (error handling) + SPEC-023 (docs). All depend on SPEC-005 (Adapter Registry) from EPIC-005.

**Parallel opportunities:** SPEC-022 and SPEC-023 can proceed in parallel after SPEC-021 completes.

## Key Dependencies

- **[EPIC-001](../../Complete/(EPIC-001)-Core-Domain-Models/(EPIC-001)-Core-Domain-Models.md)** (Core Domain Models) — plugin adapters use the same domain types (Service, Host, Topology)
- **[EPIC-002](../../Complete/(EPIC-002)-Hexagonal-Port-Framework/(EPIC-002)-Hexagonal-Port-Framework.md)** (Hexagonal Port Framework) — plugin adapters implement port protocols from `commodore.ports`
- **[EPIC-005](../../Complete/(EPIC-005)-Initial-Driven-Adapters/(EPIC-005)-Initial-Driven-Adapters.md)** (Initial Driven Adapters) — establishes the `AdapterRegistry` pattern that we extend with plugin discovery
- **[ADR-001](../../../adr/Proposed/(ADR-001)-Pluggable-Adapter-Architecture.md)** (Pluggable Adapter Architecture) — the architectural decision that this epic implements

## Architectural Notes

The entry point mechanism chosen in ADR-001 ensures:

1. **Standard discovery:** Python's `importlib.metadata.entry_points()` provides a well-supported discovery mechanism
2. **Package parity:** Built-in adapters register via the same entry points (from the core package) as external plugins
3. **No fork required:** Users never touch `src/commodore/adapters/` for custom adapters
4. **Clean separation:** Plugin packages depend on `commodore-core` (or just the port protocols) but not on other adapters

The existing `AdapterRegistry` (SPEC-005) handles provider-to-adapter mapping. This epic adds discovery (scanning entry points) and missing-provider error handling. The registry's existing `get_adapter(port, provider)` API stays unchanged.

## Lifecycle

|| Phase | Date | Commit | Notes |
||-------|------|--------|-------|
|| Active | 2026-04-06 | -- | Initial creation |