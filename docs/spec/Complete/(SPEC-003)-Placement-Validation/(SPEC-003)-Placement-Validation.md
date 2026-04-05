---
title: "Placement Validation"
artifact: SPEC-003
track: container
status: Complete
author: cristos
created: 2026-04-04
last-updated: 2026-04-04
parent-epic: EPIC-001
parent-vision: VISION-001
priority-weight: high
depends-on-artifacts:
  - SPEC-001
  - SPEC-002
---

# Placement Validation

## Goal

Build the rules engine that checks whether a service can run on a given host. This is validation only (can it go here?) not resolution (where should it go?). Resolution is EPIC-003 scope.

## Acceptance Criteria

- `validate_placement(service, host, topology) -> list[ValidationError]` returns all violations, not just the first
- Checks classification compatibility (from SPEC-002)
- Checks role compatibility (service needs `container` role, host must have it)
- Checks resource constraints if declared (service requests X memory, host has Y available)
- Returns empty list when placement is valid
- Each `ValidationError` includes: severity, rule name, human-readable message referencing service and host names
- Batch validation: `validate_all_placements(services, topology) -> dict[str, list[ValidationError]]`

## Technical Approach

Rule-based validator. Each rule is a callable that takes (service, host, topology) and returns a list of errors. Rules are composed, not inherited. Easy to add new rules without modifying existing ones.

## Lifecycle

| Phase | Date | Notes |
|-------|------|-------|
| Active | 2026-04-04 | Decomposed from EPIC-001 |
