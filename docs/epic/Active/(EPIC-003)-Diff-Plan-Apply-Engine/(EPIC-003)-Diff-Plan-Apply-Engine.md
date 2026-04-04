---
title: "Diff-Plan-Apply Engine"
artifact: EPIC-003
track: container
status: Active
author: cristos
created: 2026-04-04
last-updated: 2026-04-04
parent-vision: VISION-001
parent-initiative: INITIATIVE-001
priority-weight: high
success-criteria:
  - Diff engine computes the delta between current infrastructure state and desired service definitions
  - Plan output shows exactly what each adapter will do before any changes are made
  - Apply executes the plan through port interfaces with per-adapter error isolation
  - Apply is idempotent -- safe to re-run after partial failure
  - Failed adapter operations report which adapter failed and what was attempted, without exposing adapter internals
depends-on-artifacts:
  - EPIC-001
  - EPIC-002
addresses:
  - JOURNEY-001.PP-02
evidence-pool: ""
---

# Diff-Plan-Apply Engine

## Goal / Objective

Build the orchestration engine that turns service definitions and topology into executable infrastructure changes. The engine diffs current state against desired state, produces a reviewable plan, and applies changes through port interfaces. This is the operational heart of `cdre` -- the layer that composes calls across multiple ports for a single service deployment.

## Desired Outcomes

The [Infrastructure Operator](../../../persona/Active/(PERSONA-001)-Infrastructure-Operator/(PERSONA-001)-Infrastructure-Operator.md) runs `cdre plan` and sees a clear diff of what will change. After `cdre apply`, partial failures are recoverable by re-running apply -- idempotent port methods ensure convergence. The operator never sees adapter internals in error messages.

## Progress

<!-- Auto-populated from session digests. See progress.md for full log. -->

## Scope Boundaries

**In scope:**
- State collection: gather current state from each driven port
- Diff computation: compare current state against desired service definitions
- Placement resolution: choose valid hosts for services based on classification and topology constraints
- Plan generation: ordered list of adapter operations with dry-run output
- Apply execution: run plan steps through port interfaces with error isolation
- Idempotent semantics: port methods express desired state, re-running converges
- Operation result tracking: record which steps succeeded/failed for retry

**Out of scope:**
- Rollback orchestration -- v1 tracks success/failure for retry, not automatic rollback
- Parallel adapter execution -- v1 executes sequentially for simplicity
- State persistence/caching -- v1 queries live state on each run

## Child Specs

None yet -- to be decomposed when implementation begins.

## Key Dependencies

- [EPIC-001](../../../epic/Active/(EPIC-001)-Core-Domain-Models/(EPIC-001)-Core-Domain-Models.md) -- domain models for services, hosts, topology
- [EPIC-002](../../../epic/Active/(EPIC-002)-Hexagonal-Port-Framework/(EPIC-002)-Hexagonal-Port-Framework.md) -- port interfaces for state collection and apply

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-04 | -- | Core orchestration epic for cdre v1 |
