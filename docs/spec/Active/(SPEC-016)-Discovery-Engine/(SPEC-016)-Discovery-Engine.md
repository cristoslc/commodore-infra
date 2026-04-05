---
title: "Discovery Engine"
artifact: SPEC-016
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
  - SPEC-015
  - SPEC-007
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Discovery Engine

## Problem Statement

The diff-plan-apply engine works forward: declared YAML to desired state to changes. There is no reverse path — no way to query live infrastructure and build a unified picture of what's deployed. Each adapter's `current_state()` returns typed data per port, but nothing coordinates queries across adapters, resolves scope (host, segment, provider), filters results, or correlates cross-port data (e.g., "this DNS record points to this host running this container behind this proxy route").

## Desired Outcomes

The operator gets a single function call that takes a scope and returns a correlated, cross-port inventory. The discovery engine handles fan-out (querying multiple hosts in a segment), credential probing (auto-detecting available adapters), and result merging into a unified `DiscoveredState` model.

## External Behavior

**Inputs:**
- A scope selector: one of `FullScan`, `ProviderScope(name)`, `SegmentScope(name)`, `HostScope(name)`.
- An `AdapterRegistry` with real adapters wired (from SPEC-015).
- A `Topology` (for segment and host resolution).

**Outputs:**
- `DiscoveredState` dataclass containing:
  - Per-port state (DNS records, container stacks, proxy routes, infra resources) — same typed objects from the existing port protocols.
  - A `resources` list of `DiscoveredResource` objects that cross-reference port data: each resource has a name, host, provider, and a dict of per-port entries.
  - A `scope` field recording what was scanned.
  - A `timestamp` field (UTC ISO 8601).
  - An `unreachable` list of adapters that failed `health()` and were skipped.

**Preconditions:**
- At least one adapter is configured and healthy.

**Postconditions:**
- Every healthy adapter within scope has been queried exactly once.
- Results are merged by resource identity (name + host).
- Unhealthy adapters are listed in `unreachable`, not silently dropped.

## Acceptance Criteria

- Given `HostScope("nas")`, when the Docker Compose adapter for `nas` is healthy, then `DiscoveredState.resources` contains entries for each running container on that host.
- Given `HostScope("nas")`, when DNS records exist that resolve to the host's IP, then those records appear in the same host's resource entries.
- Given `SegmentScope("dmz")`, when the topology has 3 hosts on the `dmz` segment, then each host is scanned and results are merged.
- Given `ProviderScope("cloudflare")`, when Cloudflare backs DNS and proxy, then both are queried and results are correlated.
- Given `FullScan` with 2 healthy adapters and 1 unhealthy, then the 2 healthy adapters are queried and the unhealthy one appears in `unreachable`.
- Given a DNS record `app.example.com -> 10.0.0.5` and a container `app` running on host `nas` at `10.0.0.5`, then the `DiscoveredResource` for `app` links the DNS record and the container entry.
- Given an adapter that raises an exception during `current_state()`, then the error is captured in `unreachable` and other adapters continue.

## Scope & Constraints

- Discovery is read-only — it calls `current_state()` and `health()`, never `apply()` or `diff()`.
- Cross-port correlation uses IP address and name matching heuristics. Perfect correlation is not required — unmatched entries appear as standalone resources.
- The engine does not persist results (that's SPEC-017).
- Concurrent adapter queries are out of scope for v1 (sequential is fine for a homelab scale).

## Implementation Approach

1. **TDD: Scope resolution** — given a scope enum and topology, produce the list of (adapter, host) pairs to query. Test each scope type.
2. **TDD: Fan-out and collection** — query each adapter's `current_state()`, handle errors gracefully, collect into per-port results. Test with stubs that simulate failures.
3. **TDD: Cross-port correlation** — match DNS targets to host IPs, proxy upstreams to container ports. Build `DiscoveredResource` entries. Test with known topology fixtures.
4. **TDD: DiscoveredState assembly** — merge per-port results and correlated resources into the final model. Test round-trip serialization.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-04 | | Initial creation |
