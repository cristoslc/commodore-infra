---
title: "CLI Commands"
artifact: SPEC-010
track: container
status: Active
author: cristos
created: 2026-04-04
last-updated: 2026-04-04
parent-epic: EPIC-004
parent-vision: VISION-001
priority-weight: medium
depends-on-artifacts:
  - SPEC-009
  - SPEC-011
---

# CLI Commands

## Goal

Implement the four cdre commands: validate, plan, apply, status. The CLI is a thin driving adapter — it parses input, calls the core engine, and formats output.

## Acceptance Criteria

- `cdre validate <path>` loads service defs + topology and reports validation errors
- `cdre plan <path>` shows the diff of what would change
- `cdre apply <path>` executes the plan and reports per-adapter results
- `cdre status` shows current service placement and health
- Exit codes: 0=success, 1=validation failure, 2=apply failure
- Error messages reference operator config files (file path, field name)
- `--help` works for all commands

## Lifecycle

| Phase | Date | Notes |
|-------|------|-------|
| Active | 2026-04-04 | Decomposed from EPIC-004 |
