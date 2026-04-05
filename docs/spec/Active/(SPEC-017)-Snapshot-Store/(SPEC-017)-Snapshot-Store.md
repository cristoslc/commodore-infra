---
title: "Snapshot Store"
artifact: SPEC-017
track: implementable
status: Active
author: cristos
created: 2026-04-04
last-updated: 2026-04-04
priority-weight: medium
type: ""
parent-epic: EPIC-006
parent-initiative: ""
linked-artifacts: []
depends-on-artifacts:
  - SPEC-016
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Snapshot Store

## Problem Statement

Discovery produces a point-in-time snapshot, but there is no way to persist it. Without history, the operator can't answer "what changed since last week?", "when did this container first appear?", or "show me the state before I ran apply." Discovery snapshots are ephemeral — printed and lost.

## Desired Outcomes

Every discovery run is saved automatically. The operator can query history — list snapshots, compare two snapshots, filter by scope or time range. This turns discovery from a one-shot diagnostic into an audit trail and change-detection tool.

## External Behavior

**Inputs:**
- A `DiscoveredState` object from the discovery engine (SPEC-016).
- Storage location: `.cdre/snapshots/` in the project directory (default), configurable via `cdre.yaml`.

**Outputs:**
- A snapshot file written per discovery run. Format: JSONL or individual JSON files, named by timestamp and scope.
  ```
  .cdre/snapshots/
    2026-04-04T21-33-57Z_full.json
    2026-04-04T22-10-03Z_host-nas.json
    2026-04-05T09-00-00Z_provider-cloudflare.json
  ```
- A `SnapshotIndex` that supports queries:
  - `list(scope_filter?, time_range?) -> list[SnapshotMetadata]`
  - `load(snapshot_id) -> DiscoveredState`
  - `diff(snapshot_a, snapshot_b) -> SnapshotDiff`
  - `latest(scope?) -> DiscoveredState | None`

**Preconditions:**
- The project directory is writable.

**Postconditions:**
- Each discovery run produces exactly one snapshot file.
- Snapshot files are self-contained (include scope, timestamp, and full state).
- The snapshot directory is gitignored by default (live state, not config).

## Acceptance Criteria

- Given a discovery run, when it completes, then a snapshot file is written to `.cdre/snapshots/` with the correct timestamp and scope in the filename.
- Given two snapshots of the same scope taken at different times, when `diff()` is called, then it reports added, removed, and changed resources.
- Given `list(scope_filter="host-nas")`, when 5 snapshots exist (3 for `nas`, 2 for `full`), then only the 3 `nas` snapshots are returned.
- Given `list(time_range=(start, end))`, when snapshots exist before, during, and after the range, then only snapshots within the range are returned.
- Given `latest(scope="full")`, when 3 full snapshots exist, then the most recent is returned.
- Given a snapshot file on disk, when loaded, then the `DiscoveredState` object round-trips without data loss.
- Given `.cdre/snapshots/` does not exist, when the first discovery runs, then the directory is created and `.cdre/` is added to `.gitignore` if not already present.
- Given a `SnapshotDiff` between two full scans, when a container was added on host `nas`, then the diff reports `added: container "new-app" on host "nas"`.

## Scope & Constraints

- Snapshot retention policy is out of scope for v1. All snapshots are kept. Pruning can come later.
- No database — plain JSON files on the filesystem. The index is rebuilt from filenames on startup (no separate index file to corrupt).
- Snapshot diffs compare resource-level changes, not raw JSON equality. Two snapshots with the same resources in different order are considered equal.
- Snapshots are not encrypted. If the operator runs discovery against custodial infrastructure, the snapshot contains that data in plaintext. Classification-aware redaction is a future concern.

## Implementation Approach

1. **TDD: Write and read** — serialize `DiscoveredState` to JSON, write to timestamped file, read it back. Test round-trip fidelity.
2. **TDD: Index queries** — build `SnapshotIndex` from a directory of files. Test `list()` with scope and time filters, test `latest()`.
3. **TDD: Snapshot diff** — compare two `DiscoveredState` objects at the resource level. Produce `SnapshotDiff` with added/removed/changed. Test with fixture pairs.
4. **TDD: Auto-save integration** — hook snapshot persistence into the discovery engine's output path. Test that a discovery run produces a file.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-04 | | Initial creation |
