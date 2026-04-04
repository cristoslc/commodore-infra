---
title: "Plan Generation"
artifact: SPEC-008
track: container
status: Active
author: cristos
created: 2026-04-04
last-updated: 2026-04-04
parent-epic: EPIC-003
parent-vision: VISION-001
priority-weight: high
depends-on-artifacts:
  - SPEC-003
  - SPEC-007
---

# Plan Generation

## Goal

Turn a diff into an ordered execution plan that can be reviewed before applying. The plan shows exactly what each adapter will do.

## Acceptance Criteria

- `generate_plan(changes, topology) -> Plan` creates an ordered plan from a diff
- Plan includes placement resolution (which host runs each service)
- Plan validates placements before generating steps (reuses SPEC-003 validation)
- Plan steps are ordered: DNS before ingress, container before proxy
- Plan has a human-readable `format()` method for CLI output
- Plan with no changes produces an empty plan (not an error)

## Lifecycle

| Phase | Date | Notes |
|-------|------|-------|
| Active | 2026-04-04 | Decomposed from EPIC-003 |
