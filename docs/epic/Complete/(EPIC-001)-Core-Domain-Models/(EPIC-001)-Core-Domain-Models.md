---
title: "Core Domain Models"
artifact: EPIC-001
track: container
status: Complete
author: cristos
created: 2026-04-04
last-updated: 2026-04-04
parent-vision: VISION-001
parent-initiative: INITIATIVE-001
priority-weight: high
success-criteria:
  - Service definition schema captures workload, DNS, ingress, storage, and security classification in one structure
  - Host topology model represents heterogeneous hosts with runtime capabilities and security domains
  - Security classification model enforces blast-radius boundaries -- custodial workloads structurally cannot target operational hosts
  - Placement validation rejects invalid service-to-host assignments before any adapter is called
depends-on-artifacts: []
addresses:
  - JOURNEY-001.PP-01
evidence-pool: ""
---

# Core Domain Models

## Goal / Objective

Define the foundational domain models that every other component depends on: service definitions, host topology, security classification, and placement validation. These models are the core of the hexagonal architecture -- they have no external dependencies and are testable in isolation.

## Desired Outcomes

The [Infrastructure Operator](../../../persona/Active/(PERSONA-001)-Infrastructure-Operator/(PERSONA-001)-Infrastructure-Operator.md) can express a complete service definition in one YAML file. The classification system catches violations at validation time with actionable error messages that reference the operator's config files, not internal model paths.

## Progress

<!-- Auto-populated from session digests. See progress.md for full log. -->

## Scope Boundaries

**In scope:**
- `Service` model: workload spec, DNS records, ingress rules, storage mounts, security classification
- `Host` model: address, runtime capabilities, security domain, resource constraints
- `Topology` model: collection of hosts with their relationships and network reachability
- `SecurityClassification` model: blast-radius classes, taint domains, placement constraints
- `PlacementValidation`: rules engine that checks service-to-host compatibility
- YAML serialization/deserialization for all models

**Out of scope:**
- Placement *resolution* (choosing optimal hosts) -- that's part of the plan engine (EPIC-003)
- Port interfaces and adapters -- covered by [EPIC-002](../(EPIC-002)-Hexagonal-Port-Framework/(EPIC-002)-Hexagonal-Port-Framework.md)
- CLI parsing and commands -- covered by [EPIC-004](../(EPIC-004)-CLI-Driving-Adapter/(EPIC-004)-CLI-Driving-Adapter.md)

## Child Specs

- [SPEC-001: Service, Host, and Topology Models](../../../spec/Complete/(SPEC-001)-Service-Host-Topology-Models/(SPEC-001)-Service-Host-Topology-Models.md)
- [SPEC-002: Security Classification Model](../../../spec/Complete/(SPEC-002)-Security-Classification-Model/(SPEC-002)-Security-Classification-Model.md)
- [SPEC-003: Placement Validation](../../../spec/Complete/(SPEC-003)-Placement-Validation/(SPEC-003)-Placement-Validation.md)

## Key Dependencies

None -- this is foundational.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-04 | -- | Foundational epic for cdre v1 |
