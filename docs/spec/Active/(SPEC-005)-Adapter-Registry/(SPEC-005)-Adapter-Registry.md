---
title: "Adapter Registry"
artifact: SPEC-005
track: container
status: Active
author: cristos
created: 2026-04-04
last-updated: 2026-04-04
parent-epic: EPIC-002
parent-vision: VISION-001
priority-weight: high
depends-on-artifacts:
  - SPEC-004
---

# Adapter Registry

## Goal

Build the adapter registry that resolves port implementations from topology configuration. At startup, the registry reads which adapters are configured for each port and wires them up.

## Acceptance Criteria

- `AdapterRegistry` class holds one adapter per port type
- `registry.dns`, `registry.reverse_proxy`, etc. return the configured adapter
- Registry is constructed from a configuration dict (parsed from YAML)
- Missing adapter for a required port raises a clear error at construction time
- Registry is immutable after construction
- Works with both real adapters and in-memory stubs (same interface)

## Lifecycle

| Phase | Date | Notes |
|-------|------|-------|
| Active | 2026-04-04 | Decomposed from EPIC-002 |
