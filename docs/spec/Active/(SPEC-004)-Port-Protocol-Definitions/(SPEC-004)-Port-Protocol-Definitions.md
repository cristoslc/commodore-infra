---
title: "Port Protocol Definitions"
artifact: SPEC-004
track: container
status: Active
author: cristos
created: 2026-04-04
last-updated: 2026-04-04
parent-epic: EPIC-002
parent-vision: VISION-001
priority-weight: high
depends-on-artifacts:
  - SPEC-001
---

# Port Protocol Definitions

## Goal

Define the 6 driven port protocols as Python Protocol classes. Each protocol specifies the contract an adapter must satisfy. Protocols use structural typing — no base class inheritance required.

## Acceptance Criteria

- `DNSPort` protocol with `current_state()`, `diff(desired)`, `apply(changes)` methods
- `ReverseProxyPort` protocol with `current_state()`, `diff(desired)`, `apply(changes)`, `validate(config)` methods
- `LoadBalancerPort` protocol with `current_state()`, `diff(desired)`, `apply(changes)` methods
- `ContainerPort` protocol with `current_state()`, `diff(desired)`, `apply(changes)` methods
- `SecretPort` protocol with `get(ref)`, `get_batch(refs)`, `health()` methods
- `InfrastructurePort` protocol with `current_state()`, `diff(desired)`, `apply(changes)` methods
- Port-level domain exceptions defined (PortError, AdapterError, etc.)
- All protocols reference core domain types (Service, Host) — not adapter-specific types
- Change and Result types defined for diff/apply operations

## Lifecycle

| Phase | Date | Notes |
|-------|------|-------|
| Active | 2026-04-04 | Decomposed from EPIC-002 |
