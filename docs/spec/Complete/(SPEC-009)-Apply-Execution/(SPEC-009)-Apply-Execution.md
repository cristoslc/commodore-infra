---
title: "Apply Execution"
artifact: SPEC-009
track: container
status: Complete
author: cristos
created: 2026-04-04
last-updated: 2026-04-04
parent-epic: EPIC-003
parent-vision: VISION-001
priority-weight: high
depends-on-artifacts:
  - SPEC-008
---

# Apply Execution

## Goal

Execute a plan through port interfaces with per-adapter error isolation. Apply is idempotent — safe to re-run after partial failure.

## Acceptance Criteria

- `apply_plan(plan, registry) -> ApplyResult` executes each step through the appropriate port
- Per-step success/failure tracking in `ApplyResult`
- Failed step does not prevent other independent steps from executing
- `ApplyResult` reports which steps succeeded, which failed, and error details
- Re-running apply after partial failure converges to desired state
- Error messages reference adapter and operation, not internal types

## Lifecycle

| Phase | Date | Notes |
|-------|------|-------|
| Active | 2026-04-04 | Decomposed from EPIC-003 |
