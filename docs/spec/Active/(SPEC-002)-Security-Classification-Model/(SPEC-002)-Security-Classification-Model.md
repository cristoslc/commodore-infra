---
title: "Security Classification Model"
artifact: SPEC-002
track: container
status: Active
author: cristos
created: 2026-04-04
last-updated: 2026-04-04
parent-epic: EPIC-001
parent-vision: VISION-001
priority-weight: high
depends-on-artifacts:
  - SPEC-001
---

# Security Classification Model

## Goal

Define the security classification system that enforces blast-radius boundaries between services and hosts. Custodial workloads must not run on operational hosts. Classification mismatches are caught at validation time, not deploy time.

## Acceptance Criteria

- `SecurityClassification` enum defines at least: `public`, `authenticated`, `internal`, `custodial`
- Classification has a strict ordering (public < authenticated < internal < custodial)
- A host declares its security domain (what classifications it can accept)
- A service declares its classification (what level of isolation it needs)
- `is_compatible(service_classification, host_classification) -> bool` works correctly for all combinations
- Error messages reference the operator's config (service name, host name) not internal paths

## Technical Approach

Enum with ordering. Compatibility is a simple comparison: a host can run services at its own classification level or below.

## Lifecycle

| Phase | Date | Notes |
|-------|------|-------|
| Active | 2026-04-04 | Decomposed from EPIC-001 |
