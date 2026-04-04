---
title: "Service, Host, and Topology Models"
artifact: SPEC-001
track: container
status: Active
author: cristos
created: 2026-04-04
last-updated: 2026-04-04
parent-epic: EPIC-001
parent-vision: VISION-001
priority-weight: high
depends-on-artifacts: []
---

# Service, Host, and Topology Models

## Goal

Define the core data models that represent what the operator wants (Service) and what infrastructure exists (Host, Topology). These are pure domain objects with no I/O dependencies.

## Acceptance Criteria

- `Service` dataclass captures: name, classification, container spec, DNS records, ingress rules, storage mounts
- `Host` dataclass captures: name, address, roles, classification, resource constraints
- `Topology` dataclass holds a collection of hosts with lookup by name and role
- All models round-trip through YAML (load from file, serialize back identically)
- Models are immutable after construction (frozen dataclasses)
- A worked example: Jellyseerr service definition parses and validates

## Technical Approach

Python dataclasses with `__post_init__` validation. YAML via `ruamel.yaml` for round-trip fidelity. Service schema matches the format defined in SPIKE-001 Thread 3.

## Lifecycle

| Phase | Date | Notes |
|-------|------|-------|
| Active | 2026-04-04 | Decomposed from EPIC-001 |
