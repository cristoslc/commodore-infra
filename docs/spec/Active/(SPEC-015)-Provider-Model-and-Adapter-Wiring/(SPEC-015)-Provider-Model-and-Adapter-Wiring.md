---
title: "Provider Model and Adapter Wiring"
artifact: SPEC-015
track: implementable
status: Active
author: cristos
created: 2026-04-04
last-updated: 2026-04-04
priority-weight: high
type: ""
parent-epic: EPIC-006
parent-initiative: ""
linked-artifacts: []
depends-on-artifacts:
  - SPEC-004
  - SPEC-005
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Provider Model and Adapter Wiring

## Problem Statement

Adapters today are instantiated per-port with no grouping concept. Cloudflare serves both DNS and proxy, Hetzner serves infrastructure and DNS, but nothing in the domain model captures this relationship. Discovery needs to answer "scan everything Cloudflare manages" — that requires a provider-to-ports mapping. Separately, `AdapterRegistry.from_config()` only knows `in_memory` adapters; real adapters can't be instantiated from config.

## Desired Outcomes

The operator can reference providers by name in config and CLI commands. The system knows that `cloudflare` means "DNS adapter + proxy adapter backed by Cloudflare credentials." Real adapters are wired into the registry from project config, so `cdre` commands work against live infrastructure — not just in-memory stubs.

## External Behavior

**Inputs:**
- Provider configuration in `cdre.yaml` or a dedicated `providers.yaml`:
  ```yaml
  providers:
    cloudflare:
      credentials: env:CLOUDFLARE_API_TOKEN
      zone_id: env:CLOUDFLARE_ZONE_ID
      ports: [dns, reverse_proxy]
    hetzner:
      credentials: env:HETZNER_API_TOKEN
      ports: [infrastructure, dns]
    nas:
      ssh_host: nas.local
      ports: [container]
      project_dir: /opt/stacks
  ```
- A `health()` method on each port protocol that returns a pass/fail without side effects.

**Outputs:**
- `Provider` dataclass: name, credential reference, list of port types it backs.
- `AdapterRegistry.from_config()` extended to instantiate real adapters (Cloudflare, Docker Compose, Caddy) from provider config.
- `provider_for_port(port_name) -> Provider | None` lookup.
- `adapters_for_provider(provider_name) -> list[PortAdapter]` lookup.

**Preconditions:**
- Port protocols (SPEC-004) and adapter registry (SPEC-005) exist.

**Postconditions:**
- Each configured provider has its adapters instantiated and registered.
- `health()` on each port returns a boolean without mutating state.

## Acceptance Criteria

- Given a provider config with `cloudflare` mapping to `[dns, reverse_proxy]`, when the registry is built, then both DNS and proxy adapters are Cloudflare instances sharing the same credentials.
- Given a provider config referencing `env:CLOUDFLARE_API_TOKEN`, when the env var is set, then the adapter is constructed with the token value.
- Given a provider config referencing `env:MISSING_VAR`, when the env var is not set, then the provider is skipped with a warning (not a crash).
- Given an adapter with valid credentials, when `health()` is called, then it returns True without modifying any resources.
- Given an adapter with invalid credentials, when `health()` is called, then it returns False.
- Given `adapters_for_provider("cloudflare")`, when Cloudflare is configured, then it returns both the DNS and proxy adapter instances.

## Scope & Constraints

- Credential resolution supports `env:VAR_NAME` only for v1. Secret store integration is out of scope.
- The `health()` method should be lightweight — a single API call or SSH connection test, not a full state scan.
- Provider config schema must be extensible for future providers without core changes.
- Does not cover provider auto-detection from environment (that's SPEC-016's credential probing).

## Implementation Approach

1. **TDD: Provider model** — define `Provider` dataclass with name, credential_ref, port_types. Test round-trip construction and lookup methods.
2. **TDD: health() protocol** — add `health() -> bool` to the base port protocol. Implement on all existing adapters (Cloudflare: verify token, Docker Compose: SSH connectivity, Caddy: SSH + file readable). Add to stubs (always returns True).
3. **TDD: Registry wiring** — extend `AdapterRegistry.from_config()` with real adapter constructors. Test that provider config produces correct adapter instances. Test credential env var resolution and missing var handling.
4. **TDD: Provider lookup** — `provider_for_port()` and `adapters_for_provider()` methods. Test cross-port grouping.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-04 | | Initial creation |
