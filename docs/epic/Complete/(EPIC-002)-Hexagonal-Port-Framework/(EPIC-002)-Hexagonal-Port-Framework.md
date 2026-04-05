---
title: "Hexagonal Port Framework"
artifact: EPIC-002
track: container
status: Complete
author: cristos
created: 2026-04-04
last-updated: 2026-04-04
parent-vision: VISION-001
parent-initiative: INITIATIVE-001
priority-weight: high
success-criteria:
  - Six driven port protocols defined as Python Protocol classes (DNS, ReverseProxy, LoadBalancer, ContainerRuntime, SecretStore, Infrastructure)
  - Adapter registry resolves port implementations from topology configuration at startup
  - In-memory stub adapters exist for all ports, enabling full core testing without external systems
  - No direct import from any adapter module into core code
depends-on-artifacts:
  - EPIC-001
addresses: []
evidence-pool: ""
---

# Hexagonal Port Framework

## Goal / Objective

Establish the hexagonal boundary between core domain logic and external systems. Define the six driven port protocols, build the adapter registry, and create in-memory stubs for testing. This epic makes the architecture described in [DESIGN-001](../../../design/Active/(DESIGN-001)-Hexagonal-Port-Architecture/(DESIGN-001)-Hexagonal-Port-Architecture.md) concrete.

## Desired Outcomes

Adding a new adapter requires implementing one port protocol with zero core changes. The core can be developed and tested entirely against in-memory stubs. Port interfaces are self-documenting -- reading the protocol tells you exactly what an adapter must do.

## Progress

<!-- Auto-populated from session digests. See progress.md for full log. -->

## Scope Boundaries

**In scope:**
- `DNSProvider` protocol: create, update, delete DNS records
- `ReverseProxy` protocol: configure ingress routes and TLS
- `LoadBalancer` protocol: manage targets and health checks
- `ContainerRuntime` protocol: deploy, stop, inspect workloads
- `SecretStore` protocol: read and write secrets
- `Infrastructure` protocol: provision and query host resources
- Adapter registry with configuration-time binding
- In-memory stub implementations for all six ports
- Port-level error types (domain exceptions, not adapter internals)

**Out of scope:**
- Concrete adapters (Cloudflare, Docker Compose, etc.) -- covered by [EPIC-005](../../../epic/Active/(EPIC-005)-Initial-Driven-Adapters/(EPIC-005)-Initial-Driven-Adapters.md)
- Driving port interfaces (CLI, MCP) -- covered by [EPIC-004](../../../epic/Active/(EPIC-004)-CLI-Driving-Adapter/(EPIC-004)-CLI-Driving-Adapter.md)
- Core domain models -- covered by [EPIC-001](../../../epic/Active/(EPIC-001)-Core-Domain-Models/(EPIC-001)-Core-Domain-Models.md)

## Child Specs

- [SPEC-004: Port Protocol Definitions](../../../spec/Active/(SPEC-004)-Port-Protocol-Definitions/(SPEC-004)-Port-Protocol-Definitions.md)
- [SPEC-005: Adapter Registry](../../../spec/Active/(SPEC-005)-Adapter-Registry/(SPEC-005)-Adapter-Registry.md)
- [SPEC-006: In-Memory Stub Adapters](../../../spec/Active/(SPEC-006)-In-Memory-Stub-Adapters/(SPEC-006)-In-Memory-Stub-Adapters.md)

## Key Dependencies

- [EPIC-001](../../../epic/Active/(EPIC-001)-Core-Domain-Models/(EPIC-001)-Core-Domain-Models.md) -- port protocols reference core domain types (Service, Host, etc.)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-04 | -- | Foundational epic for cdre v1 |
