---
title: "CLI discover Command"
artifact: SPEC-018
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
  - SPEC-016
  - SPEC-017
addresses:
  - JOURNEY-001.PP-01
evidence-pool: ""
source-issue: ""
swain-do: required
---

# CLI discover Command

## Problem Statement

The discovery engine and snapshot store have no user-facing interface. The operator needs a CLI command that scopes a discovery run, displays results in readable or machine-parseable formats, and integrates with the snapshot history.

## Desired Outcomes

`cdre discover` becomes the operator's primary tool for answering "what's running?" It prints a clear, actionable inventory and auto-saves a snapshot. The output adapts to the use case: a human at a terminal gets a table, a script gets JSON, and an onboarding workflow gets draft YAML service definitions.

## External Behavior

**Commands:**
```
cdre discover [OPTIONS]              # full scan (probe credentials)
cdre discover --host <name>          # single host
cdre discover --segment <name>       # network segment
cdre discover --provider <name>      # provider (cross-port)

cdre discover history [OPTIONS]      # list past snapshots
cdre discover diff <id-a> <id-b>     # diff two snapshots
cdre discover diff --latest          # diff latest snapshot against declared state
```

**Output format flags:**
- `--format table` (default) — human-readable table grouped by host, then port type.
- `--format json` — full `DiscoveredState` as JSON.
- `--format yaml` — draft service YAML definitions reverse-engineered from discovered state.

**Table output example:**
```
Host: nas (10.0.0.10) [internal] segment:lan
  Containers:
    jellyseerr   jellyseerr/jellyseerr:latest   ports: 5055   running
    sonarr       linuxserver/sonarr:latest       ports: 8989   running
  Proxy routes:
    jellyseerr.example.com -> 10.0.0.10:5055
  DNS:
    jellyseerr.example.com  CNAME  proxy.example.com

Host: edge (203.0.113.5) [public] segment:dmz
  Proxy routes:
    (none discovered)
  DNS:
    edge.example.com  A  203.0.113.5

Unreachable: hetzner-infra (connection refused)
Snapshot saved: .cdre/snapshots/2026-04-04T21-33-57Z_full.json
```

**Draft YAML mode:**
```yaml
# Discovered from host: nas at 2026-04-04T21:33:57Z
# Review and edit before using with cdre apply
- name: jellyseerr
  classification: internal  # inferred from host classification
  container:
    image: jellyseerr/jellyseerr:latest
    ports: [5055]
  dns:
    - name: jellyseerr.example.com
      type: CNAME
      target: proxy.example.com
  ingress:
    - type: reverse_proxy
      upstream: 10.0.0.10:5055
```

**Preconditions:**
- `cdre.yaml` exists with provider configuration (SPEC-015).
- Topology is loaded for segment and host resolution.

**Postconditions:**
- Results are displayed in the requested format.
- A snapshot is auto-saved (unless `--no-save` is passed).
- Exit code 0 on success, 1 on partial failure (some adapters unreachable), 2 on total failure.

## Acceptance Criteria

- Given no scope flags, when adapters are configured, then all healthy adapters are scanned and results displayed.
- Given `--host nas`, when the host exists in topology, then only that host is scanned.
- Given `--host missing`, when the host does not exist, then an error is printed and exit code is 2.
- Given `--segment dmz`, when the topology has hosts on that segment, then all segment hosts are scanned.
- Given `--provider cloudflare`, when Cloudflare is configured, then DNS and proxy adapters for Cloudflare are queried.
- Given `--format json`, then output is valid JSON that deserializes to `DiscoveredState`.
- Given `--format yaml`, then output is valid YAML service definitions with classification inferred from host.
- Given a successful discovery, when `--no-save` is not set, then a snapshot file is created.
- Given `cdre discover history`, then past snapshots are listed with timestamp, scope, and resource count.
- Given `cdre discover diff <a> <b>`, then the diff between two snapshots is displayed with added/removed/changed resources.
- Given `cdre discover diff --latest`, then the most recent snapshot is compared against the declared state from `cdre.yaml`.

## Scope & Constraints

- Draft YAML is best-effort. It infers classification from the host, names from container/DNS names, and groups correlated resources. The operator must review and edit before using with `cdre apply`.
- The `history` and `diff` subcommands are thin wrappers around SPEC-017's snapshot store.
- Color output in table mode follows terminal capabilities (no color when piped).
- `--provider` and `--host` are mutually exclusive. `--segment` and `--host` are mutually exclusive. `--provider` and `--segment` can combine (scan provider's adapters but only for hosts in the segment).

## Implementation Approach

1. **TDD: Argument parsing** — define the Click command group with scope flags and format options. Test that conflicting flags produce errors.
2. **TDD: Table formatter** — given a `DiscoveredState`, produce the grouped table output. Test with fixtures.
3. **TDD: JSON formatter** — serialize `DiscoveredState` to JSON. Test round-trip.
4. **TDD: YAML draft formatter** — reverse-engineer service definitions from discovered resources. Test classification inference from host, name extraction, and grouping.
5. **TDD: History and diff subcommands** — wire snapshot store queries to CLI output. Test with fixture snapshot directories.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-04 | | Initial creation |
