---
title: "Environment Discovery"
artifact: EPIC-006
track: container
status: Active
author: cristos
created: 2026-04-04
last-updated: 2026-04-05
parent-vision: VISION-001
parent-initiative: ""
priority-weight: high
success-criteria:
  - "Running `cdre discover` with no arguments produces a useful inventory by probing available adapters and credentials"
  - "Running `cdre discover --host <name>` scans a single host and reports running containers, proxy routes, and DNS records that reference it"
  - "Running `cdre discover --segment <name>` scans all hosts in a network segment"
  - "Running `cdre discover --provider <name>` scans a provider across port types (e.g. Hetzner covers infrastructure + DNS, Cloudflare covers DNS + proxy)"
  - "Discovery output is structured (JSON and human-readable table) and can be piped into `cdre diff` to compare against declared state"
  - "Discovery respects security classification -- a custodial host's inventory is not mixed into public-facing output without explicit opt-in"
depends-on-artifacts:
  - EPIC-001
  - EPIC-002
  - EPIC-005
addresses:
  - JOURNEY-001.PP-01
evidence-pool: ""
---

# Environment Discovery

## Goal / Objective

Give the operator an on-the-ground snapshot of what is actually running across their infrastructure. Today, `cdre` can only work forward from declared YAML to desired state. It has no way to answer "what's already out there?" Discovery closes this gap by querying real adapters and assembling a unified inventory -- the same domain model used for planning, but populated from live infrastructure instead of config files.

## Desired Outcomes

The infrastructure operator ([PERSONA-001](../../../persona/Active/(PERSONA-001)-Infrastructure-Operator/(PERSONA-001)-Infrastructure-Operator.md)) gains the ability to audit what exists before declaring what should exist. This serves three use cases:

1. **Onboarding** -- point `cdre discover` at existing infrastructure and get a starting inventory. No need to hand-write YAML for services that are already running.
2. **Drift detection** -- compare discovered state against declared state to find unmanaged resources, missing services, or configuration drift.
3. **Exploration** -- answer "what's on this host?" or "what DNS records does Cloudflare have?" without logging into each system separately.

## Progress

<!-- Auto-populated from session digests. See progress.md for full log. -->

## Scope Boundaries

**In scope:**
- A `cdre discover` CLI command with scope selectors (no args, `--host`, `--segment`, `--provider`)
- A discovery engine that coordinates `current_state()` calls across adapters and merges results
- Scope resolution: mapping `--provider hetzner` to the right set of port adapters
- Output formatters: human-readable table, JSON, and a "draft YAML" mode that generates service definitions from discovered state
- Credential probing: when no scope is given, check which adapters have valid credentials and scan those
- Classification-aware output grouping

**Out of scope:**
- Continuous monitoring or polling (discovery is point-in-time)
- Auto-remediation based on discovered drift (that's `cdre apply`)
- New adapter implementations -- this epic uses the existing port `current_state()` protocol
- Agent discovery (finding hosts that aren't already in the topology)

## Scope Model

Discovery operates at four levels, from broadest to narrowest:

```
no scope          scan everything reachable (probe credentials)
  |
--provider X      scan all ports backed by provider X
  |
--segment X       scan all hosts on network segment X
  |
--host X          scan one host
```

A **provider** can span multiple port types. Hetzner provides both infrastructure (VMs) and DNS. Cloudflare provides DNS and reverse proxy. The discovery engine needs a provider-to-ports mapping so that `--provider cloudflare` queries both DNS and proxy adapters backed by Cloudflare.

A **segment** maps to a set of hosts via the existing `Topology.hosts_on_segment()` method. Discovery iterates those hosts and queries each adapter that applies.

A **host** is the narrowest scope. Discovery queries container, proxy, and infrastructure adapters for that specific host, plus any DNS records that resolve to it.

**No scope** is the most interesting case. The engine checks which adapters are configured and have valid credentials (a new `health()` or `probe()` method on the port protocol), then scans all of them. This is the "just show me what you can see" mode.

## Child Specs

| Spec | Title | Priority | Dependencies |
|------|-------|----------|-------------|
| SPEC-015 | Provider Model and Adapter Wiring | high | SPEC-004, SPEC-005 |
| SPEC-016 | Discovery Engine | high | SPEC-015, SPEC-007 |
| SPEC-017 | Snapshot Store | medium | SPEC-016 |
| SPEC-018 | CLI discover Command | high | SPEC-016, SPEC-017 |
| SPEC-019 | Drift Comparison | medium | SPEC-016, SPEC-017 |

**Dependency chain:** SPEC-015 (provider model) -> SPEC-016 (engine) -> SPEC-017 (snapshots) + SPEC-018 (CLI) + SPEC-019 (drift). SPEC-015 is the critical path -- everything else depends on providers being wired.

## Key Dependencies

- **[EPIC-001](../../Complete/(EPIC-001)-Core-Domain-Models/(EPIC-001)-Core-Domain-Models.md)** (Core Domain Models) -- discovery produces the same `Service`, `Host`, `Topology` types
- **[EPIC-002](../../Complete/(EPIC-002)-Hexagonal-Port-Framework/(EPIC-002)-Hexagonal-Port-Framework.md)** (Hexagonal Port Framework) -- discovery calls `current_state()` on port adapters
- **[EPIC-005](../../Complete/(EPIC-005)-Initial-Driven-Adapters/(EPIC-005)-Initial-Driven-Adapters.md)** (Initial Driven Adapters) -- real adapters (Cloudflare, Docker Compose, Caddy) must implement `current_state()` against live infrastructure

The existing `current_state()` protocol returns typed state objects per port. Discovery wraps these into a unified view. No changes to the port protocol are needed -- but a `health()` method on `PortBase` would help credential probing (SPEC-016).

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-04 | | Initial creation |
