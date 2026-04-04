---
title: "State Collection and Diff Engine"
artifact: SPEC-007
track: container
status: Active
author: cristos
created: 2026-04-04
last-updated: 2026-04-04
parent-epic: EPIC-003
parent-vision: VISION-001
priority-weight: high
depends-on-artifacts:
  - SPEC-004
  - SPEC-006
---

# State Collection and Diff Engine

## Goal

Gather current infrastructure state from each port and compute the delta between current and desired state. This is the "diff" in diff-plan-apply.

## Acceptance Criteria

- `collect_state(registry) -> InfraState` gathers current state from all configured ports
- `compute_diff(current, desired) -> list[Change]` returns typed change objects
- Changes are tagged with which port they belong to (dns, proxy, container, etc.)
- Each Change has: action (create/update/delete), resource identifier, before state, after state
- Empty diff when current matches desired
- Diff works against in-memory stubs for testing

## Lifecycle

| Phase | Date | Notes |
|-------|------|-------|
| Active | 2026-04-04 | Decomposed from EPIC-003 |
