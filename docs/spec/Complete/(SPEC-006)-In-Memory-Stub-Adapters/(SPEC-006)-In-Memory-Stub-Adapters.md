---
title: "In-Memory Stub Adapters"
artifact: SPEC-006
track: container
status: Complete
author: cristos
created: 2026-04-04
last-updated: 2026-04-04
parent-epic: EPIC-002
parent-vision: VISION-001
priority-weight: high
depends-on-artifacts:
  - SPEC-004
---

# In-Memory Stub Adapters

## Goal

Create in-memory stub implementations for all 6 port protocols. These stubs enable full core testing without external systems and serve as reference implementations for adapter authors.

## Acceptance Criteria

- One stub class per port protocol (InMemoryDNS, InMemoryReverseProxy, etc.)
- Each stub satisfies its port protocol (type-checks as Protocol implementor)
- Stubs maintain in-memory state that can be inspected in tests
- Stubs support pre-loading state (simulating existing infrastructure)
- Each stub has a `reset()` method for test isolation

## Lifecycle

| Phase | Date | Notes |
|-------|------|-------|
| Active | 2026-04-04 | Decomposed from EPIC-002 |
