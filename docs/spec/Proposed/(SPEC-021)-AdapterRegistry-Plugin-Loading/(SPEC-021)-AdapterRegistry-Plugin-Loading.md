---
title: "AdapterRegistry Plugin Loading"
artifact: SPEC-021
track: implementable
status: Complete
author: cristos
created: 2026-04-06
last-updated: 2026-04-06
priority-weight: high
type: ""
parent-epic: EPIC-007
parent-initiative: ""
linked-artifacts:
  - ADR-001
depends-on-artifacts:
  - SPEC-005
  - SPEC-020
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# AdapterRegistry Plugin Loading

## Problem Statement

The existing `AdapterRegistry` (SPEC-005) constructs adapters from hardcoded provider names. It has no mechanism to map topology configuration (e.g., `dns_provider: cloudflare`) to plugin-discovered adapters. Plugin packages exist, but the registry cannot use them.

## Desired Outcomes

The `AdapterRegistry` loads adapters discovered by SPEC-020 and resolves provider names from topology configuration to adapter instances. Configuration remains unchanged — users write `dns_provider: cloudflare` whether the adapter is built-in or a plugin.

## External Behavior

**Inputs:**
- Topology configuration (YAML) with provider names like `cloudflare`, `vultr`, `envoy`
- Discovered adapters from SPEC-020's `discover_adapters()`

**Outputs:**
- Configured `AdapterRegistry` instance with `get_adapter(port, provider)` returning the correct adapter class

**Preconditions:**
- Discovery has run (SPEC-020)
- Required adapters are installed (or missing plugin error from SPEC-022)

**Postconditions:**
- Registry has adapter instances for each configured provider
- `health()` calls work on loaded adapters
- Registry is immutable after construction

**Constraints:**
- Adapter instantiation happens at registry construction time
- Adapters are singletons (one instance per provider per port)
- Errors during instantiation surface with provider name and port type

## Acceptance Criteria

**Given** topology configuration with `dns_provider: cloudflare`
**When** `AdapterRegistry` is constructed
**Then** `registry.get_adapter(DNSProvider, "cloudflare")` returns a CloudflareDNSAdapter instance

**Given** topology configuration with `infrastructure_provider: vultr` (plugin)
**When** `AdapterRegistry` is constructed with discovered plugins
**Then** `registry.get_adapter(Infrastructure, "vultr")` returns a VultrAdapter instance from the plugin

**Given** built-in and plugin adapters for the same port
**When** `get_adapter()` is called for each
**Then** both return correctly typed adapter instances (parity)

**Given** topology refers to a provider not discovered
**When** `get_adapter()` is called for that provider
**Then** raises `ProviderNotFoundError` with install hint (delegated to SPEC-022)

## Verification

<!-- Populated when entering Testing phase. -->

|| Criterion | Evidence | Result |
||-----------|----------|--------|
| Built-in provider resolves | | |
| Plugin provider resolves | | |
| Parity between built-in and plugin | | |
| Singleton per provider/port | | |
| Health check works | | |

## Scope & Constraints

**In scope:**
- Extending `AdapterRegistry.__init__()` to accept discovered adapters
- Provider name → adapter class resolution
- Adapter instantiation with provider-specific config
- Singleton enforcement per (port, provider) tuple

**Out of scope:**
- Error message formatting for missing providers (SPEC-022)
- Discovery mechanism itself (SPEC-020)

## Implementation Approach

**TDD Cycle 1: Extend registry**
1. Write test: `test_registry_accepts_discovered_adapters()`
2. Implement: `AdapterRegistry.__init__(config, discovered=DiscoveryResult)`
3. Assert: Registry stores discovered adapters

**TDD Cycle 2: Provider resolution**
1. Write test: `test_get_adapter_resolves_provider_name()`
2. Implement: Lookup provider name in discovered mapping, instantiate adapter
3. Assert: Correct adapter class returned

**TDD Cycle 3: Plugin parity**
1. Write test: `test_plugin_and_builtin_use_same_code_path()`
2. Implement: No special casing — both use discovery result
3. Assert: Behavior identical

**TDD Cycle 4: Singleton enforcement**
1. Write test: `test_same_provider_returns_same_instance()`
2. Implement: Cache instances by (port, provider)
3. Assert: Multiple calls return same object

## Lifecycle

|| Phase | Date | Commit | Notes |
||-------|------|--------|-------|
|| Proposed | 2026-04-06 | -- | Decomposed from EPIC-007 |