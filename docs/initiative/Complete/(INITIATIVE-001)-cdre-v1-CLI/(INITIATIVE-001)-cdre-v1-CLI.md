---
title: "cdre v1 CLI"
artifact: INITIATIVE-001
track: container
status: Complete
author: cristos
created: 2026-04-04
last-updated: 2026-04-04
parent-vision:
  - VISION-001
priority-weight: high
success-criteria:
  - A new service can be defined in one YAML file and deployed with `cdre apply`
  - "`cdre validate` catches classification violations before deployment"
  - Adding a new driven adapter requires implementing one port interface with no core changes
  - The CLI covers the full lifecycle: validate, plan, apply, status
depends-on-artifacts: []
addresses:
  - JOURNEY-001.PP-01
  - JOURNEY-001.PP-02
evidence-pool: ""
---

# cdre v1 CLI

## Strategic Focus

Ship the first usable version of the Commodore CLI. v1 delivers the core value proposition: one domain model and one CLI (`cdre`) for defining, classifying, placing, and deploying services across heterogeneous hosts. The hexagonal architecture is established from day one so that adapter growth never requires core changes.

v1 is CLI-only -- no MCP server, Pulumi provider, or TUI. The driving adapter is `cdre`; the driven adapters are a minimum viable set (Cloudflare DNS, Docker Compose, SSH+Caddy).

## Desired Outcomes

The [Infrastructure Operator](../../../persona/Active/(PERSONA-001)-Infrastructure-Operator/(PERSONA-001)-Infrastructure-Operator.md) can define a service in a single YAML file, validate it against their topology, review a plan, and apply it -- replacing the current 4-5 system manual workflow. Security classification violations are caught structurally at validation time, not discovered after deployment.

## Progress

<!-- Auto-populated from session digests. See progress.md for full log. -->

## Scope Boundaries

**In scope:**
- Core domain models (service, host, topology, security classification)
- Hexagonal port framework with protocol-based contracts
- Diff-plan-apply engine with idempotent apply semantics
- `cdre` CLI with validate, plan, apply, and status commands
- Initial driven adapters: Cloudflare DNS, Docker Compose, SSH+Caddy reverse proxy

**Out of scope:**
- Additional driving adapters (MCP server, Pulumi provider, TUI)
- Additional driven adapters beyond the initial set (Route53, k3s, Nginx, Vault)
- Dynamic scheduling -- v1 uses static placement with operator pinning
- High availability or multi-operator workflows

## Child Epics

- [EPIC-001](../../../epic/Complete/(EPIC-001)-Core-Domain-Models/(EPIC-001)-Core-Domain-Models.md) -- Core Domain Models
- [EPIC-002](../../../epic/Complete/(EPIC-002)-Hexagonal-Port-Framework/(EPIC-002)-Hexagonal-Port-Framework.md) -- Hexagonal Port Framework
- [EPIC-003](../../../epic/Complete/(EPIC-003)-Diff-Plan-Apply-Engine/(EPIC-003)-Diff-Plan-Apply-Engine.md) -- Diff-Plan-Apply Engine
- [EPIC-004](../../../epic/Complete/(EPIC-004)-CLI-Driving-Adapter/(EPIC-004)-CLI-Driving-Adapter.md) -- CLI Driving Adapter (`cdre`)
- [EPIC-005](../../../epic/Complete/(EPIC-005)-Initial-Driven-Adapters/(EPIC-005)-Initial-Driven-Adapters.md) -- Initial Driven Adapters

## Small Work (Epic-less Specs)

None yet.

## Key Dependencies

None -- this is the foundational initiative.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-04 | -- | Created to deliver cdre v1 CLI |
