---
title: "CLI Driving Adapter (cdre)"
artifact: EPIC-004
track: container
status: Active
author: cristos
created: 2026-04-04
last-updated: 2026-04-04
parent-vision: VISION-001
parent-initiative: INITIATIVE-001
priority-weight: medium
success-criteria:
  - "`cdre validate` loads service definitions and topology, runs placement validation, and reports actionable errors"
  - "`cdre plan` shows a human-readable diff of all changes across adapters"
  - "`cdre apply` executes the plan and reports per-adapter results"
  - "`cdre status` shows current service placement, health, and classification"
  - Error messages reference the operator's config files (path and field), not internal model types
depends-on-artifacts:
  - EPIC-003
addresses:
  - JOURNEY-001.PP-01
evidence-pool: ""
---

# CLI Driving Adapter (cdre)

## Goal / Objective

Build the `cdre` command-line interface -- the sole driving adapter for v1. The CLI is a thin layer that parses operator input, calls into the core's diff-plan-apply engine, and formats output for humans. It owns UX concerns (error formatting, progress display, output modes) but contains no domain logic.

## Desired Outcomes

The [Infrastructure Operator](../../../persona/Active/(PERSONA-001)-Infrastructure-Operator/(PERSONA-001)-Infrastructure-Operator.md) has four commands that cover the full deployment lifecycle. Error messages point to specific files and fields in their configuration, making issues immediately actionable.

## Progress

<!-- Auto-populated from session digests. See progress.md for full log. -->

## Scope Boundaries

**In scope:**
- `cdre validate` -- load and validate service definitions against topology
- `cdre plan` -- compute and display the deployment diff
- `cdre apply` -- execute the plan, display per-adapter results
- `cdre status` -- query current state and display service placement
- `cdre --help` and subcommand help
- Configuration file discovery (service YAML, topology YAML)
- Human-readable error formatting with file/field references
- Exit codes for scripting (0=success, 1=validation failure, 2=apply failure)

**Out of scope:**
- Interactive mode or TUI -- v1 is non-interactive
- `cdre init` scaffolding -- potential future enhancement
- JSON/machine-readable output -- v1 is human-only
- Shell completions

## Child Specs

None yet -- to be decomposed when implementation begins.

## Key Dependencies

- [EPIC-003](../../../epic/Active/(EPIC-003)-Diff-Plan-Apply-Engine/(EPIC-003)-Diff-Plan-Apply-Engine.md) -- the CLI calls the diff-plan-apply engine

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-04 | -- | v1 driving adapter for cdre |
