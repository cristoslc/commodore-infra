---
title: "Drift Comparison"
artifact: SPEC-019
track: implementable
status: Active
author: cristos
created: 2026-04-04
last-updated: 2026-04-04
priority-weight: medium
type: ""
parent-epic: EPIC-006
parent-initiative: ""
linked-artifacts:
  - SPEC-007
depends-on-artifacts:
  - SPEC-016
  - SPEC-017
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Drift Comparison

## Problem Statement

The operator can discover what's running (SPEC-016) and declare what should be running (cdre.yaml). But there is no way to compare the two. The existing `compute_diff()` in the engine works from desired state forward — it assumes the declared state is correct and produces changes to reach it. Drift comparison works the other direction: what exists that isn't declared? What's declared but missing? What changed between two points in time?

## Desired Outcomes

The operator can detect configuration drift, unmanaged resources, and missing deployments. This serves three comparison modes:

1. **Discovered vs. declared** — "what's running that I haven't defined?" and "what have I defined that isn't running?" This is the onboarding gap analysis.
2. **Snapshot vs. snapshot** — "what changed between Tuesday and today?" This is the temporal drift view.
3. **Discovered vs. planned** — "if I run `cdre apply`, what will change relative to what's actually there?" This is the pre-apply safety check.

## External Behavior

**Inputs:**
- Two `DiscoveredState` objects (snapshot-vs-snapshot), or
- One `DiscoveredState` and one declared state from config (discovered-vs-declared), or
- One `DiscoveredState` and one `Plan` (discovered-vs-planned).

**Outputs:**
- `DriftReport` containing:
  - `unmanaged: list[DriftEntry]` — resources found in discovered state but not in declared state.
  - `missing: list[DriftEntry]` — resources in declared state but not found in discovered state.
  - `diverged: list[DriftEntry]` — resources that exist in both but differ (e.g., different image tag, different DNS target).
  - `matched: int` — count of resources that match exactly.
  - `scope` — what was compared.
  - `timestamp` — when the comparison was made.

- `DriftEntry`:
  - `resource_id`, `port`, `host`
  - `declared_value` (if applicable), `discovered_value` (if applicable)
  - `drift_type`: `unmanaged | missing | diverged`

**Preconditions:**
- At least one side of the comparison is a `DiscoveredState`.

**Postconditions:**
- Every resource in both inputs is accounted for — either matched, unmanaged, missing, or diverged.
- The report is deterministic (same inputs produce same output regardless of ordering).

## Acceptance Criteria

- Given a discovered container `app-v2` on host `nas` and no declared service named `app-v2`, then the drift report lists it as `unmanaged`.
- Given a declared service `monitoring` and no discovered container matching it, then the drift report lists it as `missing`.
- Given a declared service with `image: app:1.0` and a discovered container running `app:2.0`, then the drift report lists it as `diverged` with both values.
- Given identical declared and discovered state, then `unmanaged`, `missing`, and `diverged` are all empty and `matched` equals the total resource count.
- Given two snapshots where a container was added between them, then the snapshot diff reports it as `added`.
- Given two snapshots where a DNS record was removed between them, then the snapshot diff reports it as `removed`.
- Given `cdre discover diff --latest` when declared state has 5 services and discovered state has 7 resources, then the report categorizes all 7+5 entries correctly (with deduplication for matches).
- Given a drift report, when formatted as a table, then unmanaged resources are visually distinct from missing and diverged entries.

## Scope & Constraints

- Resource matching uses name + host + port type as the identity key. If the operator names containers differently than their service definitions, those are reported as unmanaged + missing (not diverged). Fuzzy matching is out of scope.
- Drift comparison does not trigger remediation. It informs; the operator decides what to do.
- The comparison engine is reused by both the CLI (`cdre discover diff`) and the snapshot store's `diff()` method.
- Comparison of secret values is explicitly out of scope — secrets are not included in discovery state.

## Implementation Approach

1. **TDD: Resource identity** — define the identity key (name + host + port type) and matching function. Test exact match, partial match, and no match.
2. **TDD: Declared state extraction** — convert `cdre.yaml` services into a comparable format (same structure as `DiscoveredResource`). Test against fixture configs.
3. **TDD: DriftReport generation** — given two resource sets, classify each as unmanaged/missing/diverged/matched. Test all four categories.
4. **TDD: Snapshot-vs-snapshot** — reuse the same comparison engine but with two `DiscoveredState` inputs. Test temporal changes (added, removed, changed).
5. **TDD: CLI integration** — wire `cdre discover diff` to the comparison engine. Test output formatting.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-04 | | Initial creation |
