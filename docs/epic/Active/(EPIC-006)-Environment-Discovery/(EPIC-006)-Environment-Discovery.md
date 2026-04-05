---
title: "Environment Discovery"
artifact: EPIC-006
track: container
status: Complete
author: cristos
created: 2026-04-04
last-updated: 2026-04-05
parent-vision: VISION-001
parent-initiative: ""
priority-weight: high
success-criteria:
  - "Running `cdre discover` with no arguments produces a useful inventory by probing available adapters and credentials"
  - "Running `cdre discover --host <name>` scans a single host and reports running containers, proxy routes, and DNS records that reference it"
  - "Running `cdre discover --segment <name>` scans all hosts in a network segment"
  - "Running `cdre discover --provider <name>` scans a provider across port types (e.g. Hetzner covers infrastructure + DNS, Cloudflare covers DNS + proxy)"
  - "Discovery output is structured (JSON and human-readable table) and can be piped into `cdre diff` to compare against declared state"
  - "Discovery respects security classification -- a custodial host's inventory is not mixed into public-facing output without explicit opt-in"
depends-on-artifacts:
  - EPIC-001
  - EPIC-002
  - EPIC-005
addresses:
  - JOURNEY-001.PP-01
evidence-pool: ""
---

# Environment Discovery

## Goal / Objective

Give the operator an on-the-ground snapshot of what is actually running across their infrastructure. Today, `cdre` can only work forward from declared YAML to desired state. It has no way to answer "what's already out there?" Discovery closes this gap by querying real adapters and assembling a unified inventory -- the same domain model used for planning, but populated from live infrastructure instead of config files.

## Desired Outcomes

The infrastructure operator ([PERSONA-001](../../../persona/Active/(PERSONA-001)-Infrastructure-Operator/(PERSONA-001)-Infrastructure-Operator.md)) gains the ability to audit what exists before declaring what should exist. This serves three use cases:

1. **Onboarding** -- point `cdre discover` at existing infrastructure and get a starting inventory. No need to hand-write YAML for services that are already running.
2. **Drift detection** -- compare discovered state against declared state to find unmanaged resources, missing services, or configuration drift.
3. **Exploration** -- answer "what's on this host?" or "what DNS records does Cloudflare have?" without logging into each system separately.

## Progress

| Date | Activity | Status |
|------|----------|--------|
| 2026-04-04 | EPIC-006 activation | Active |
| 2026-04-05 | SPEC-015 Provider Model complete | ✅ Complete |
| 2026-04-05 | SPEC-016 Discovery Engine complete | ✅ Complete |
| 2026-04-05 | SPEC-017 Snapshot Store complete | ✅ Complete |
| 2026-04-05 | SPEC-018 CLI Discover Command complete | ✅ Complete |
| 2026-04-05 | SPEC-019 Drift Comparison complete | ✅ Complete |
| 2026-04-05 | EPIC-006 terminal transition | Complete |

## Scope Boundaries

**In scope:**
- A `cdre discover` CLI command with scope selectors (no args, `--host`, `--segment`, `--provider`)
- A discovery engine that coordinates `current_state()` calls across adapters and merges results
- Scope resolution: mapping `--provider hetzner` to the right set of port adapters
- Output formatters: human-readable table, JSON, and a "draft YAML" mode that generates service definitions from discovered state
- Credential probing: when no scope is given, check which adapters have valid credentials and scan those
- Classification-aware output grouping

**Out of scope:**
- Continuous monitoring or polling (discovery is point-in-time)
- Auto-remediation based on discovered drift (that's `cdre apply`)
- New adapter implementations -- this epic uses the existing port `current_state()` protocol
- Agent discovery (finding hosts that aren't already in the topology)

## Scope Model

Discovery operates at four levels, from broadest to narrowest:

```
no scope          scan everything reachable (probe credentials)
  |
--provider X      scan all ports backed by provider X
  |
--segment X       scan all hosts on network segment X
  |
--host X          scan one host
```

A **provider** can span multiple port types. Hetzner provides both infrastructure (VMs) and DNS. Cloudflare provides DNS and reverse proxy. The discovery engine needs a provider-to-ports mapping so that `--provider cloudflare` queries both DNS and proxy adapters backed by Cloudflare.

A **segment** maps to a set of hosts via the existing `Topology.hosts_on_segment()` method. Discovery iterates those hosts and queries each adapter that applies.

A **host** is the narrowest scope. Discovery queries container, proxy, and infrastructure adapters for that specific host, plus any DNS records that resolve to it.

**No scope** is the most interesting case. The engine checks which adapters are configured and have valid credentials (a new `health()` or `probe()` method on the port protocol), then scans all of them. This is the "just show me what you can see" mode.

## Child Specs

| Spec | Title | Priority | Dependencies | Status |
|------|-------|----------|-------------|--------|
| SPEC-015 | Provider Model and Adapter Wiring | high | SPEC-004, SPEC-005 | ✅ Complete |
| SPEC-016 | Discovery Engine | high | SPEC-015, SPEC-007 | ✅ Complete |
| SPEC-017 | Snapshot Store | medium | SPEC-016 | ✅ Complete |
| SPEC-018 | CLI Discover Command | high | SPEC-016, SPEC-017 | ✅ Complete |
| SPEC-019 | Drift Comparison | medium | SPEC-016, SPEC-017 | ✅ Complete |

**Dependency chain:** SPEC-015 (provider model) → SPEC-016 (engine) → SPEC-017 (snapshots) + SPEC-018 (CLI) + SPEC-019 (drift).

## Key Dependencies

- **[EPIC-001](../../Complete/(EPIC-001)-Core-Domain-Models/(EPIC-001)-Core-Domain-Models.md)** (Core Domain Models) -- discovery produces the same `Service`, `Host`, `Topology` types
- **[EPIC-002](../../Complete/(EPIC-002)-Hexagonal-Port-Framework/(EPIC-002)-Hexagonal-Port-Framework.md)** (Hexagonal Port Framework) -- discovery calls `current_state()` on port adapters
- **[EPIC-005](../../Complete/(EPIC-005)-Initial-Driven-Adapters/(EPIC-005)-Initial-Driven-Adapters.md)** (Initial Driven Adapters) -- real adapters (Cloudflare, Docker Compose, Caddy) must implement `current_state()` against live infrastructure

The existing `current_state()` protocol returns typed state objects per port. Discovery wraps these into a unified view. No changes to the port protocol are needed -- but a `health()` method on `PortBase` would help credential probing (SPEC-016).

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-04 | | Initial creation |
| Complete | 2026-04-05 | 976ae92 | All 5 child SPECs complete |

## Retrospective

**Terminal state:** Complete
**Period:** 2026-04-04 — 2026-04-05
**Related artifacts:** SPEC-015, SPEC-016, SPEC-017, SPEC-018, SPEC-019

### Summary

The EPIC-006 Environment Discovery epic delivered the complete discovery pipeline. Starting from the provider model (SPEC-015), we built:

1. **Provider Model and Adapter Wiring (SPEC-015)**: Established the foundation for provider-adapter relationship mapping, credential resolution, and `health()` methods on all 6 port protocols. Real adapters (Cloudflare DNS, Caddy reverse proxy, Docker Compose containers) now implement health checks to validate credentials before discovery runs.

2. **Discovery Engine (SPEC-016)**: Orchestrates `current_state()` calls across adapters and merges results into a unified inventory. Supports scope filtering by host, segment, or provider. Output formatted as JSON, table, or draft YAML for review.

3. **Snapshot Store (SPEC-017)**: Persists discovery snapshots to `.snapshots/` directory as JSON files with metadata. Enables persisting discovered state for comparison against declared state.

4. **CLI Discover Command (SPEC-018)**: Implemented `cdre discover` with scope flags (`--host`, `--segment`, `--provider`) and output formatters (`--format json|table|draft-yaml`).

5. **Drift Comparison (SPEC-019)**: Compares discovered state against declared state, identifying added, removed, and modified resources. Reports structured drift with status (clean/dirty) and human-readable formatting.

### Reflection

#### What went well
- The provider model design (Name + credential_ref + port_types) proved robust and extensible
- Using existing `current_state()` protocol meant no adapter changes were needed beyond implementing the `health()` method
- The snapshot/persistance layer enabled drift detection without tightly coupling to storage
- CLI interface aligned well with existing `cdre` commands (validate, plan, apply, status)
- All 6 port protocols now have consistent `health()` behavior for credential probing

#### What was surprising
- The `--provider` scope required significant refactoring to `AdapterRegistry` to track which provider backs which adapters
- SSH-based health checks (for Caddy/Docker Compose) needed careful error handling to avoid blocking discovery when a host is unavailable
- The draft-yaml output format was simpler than anticipated and provides immediate value for onboarding

#### What would change
- Could add a `--dry-run` flag for `cdre discover` to show what would be scanned without actually running each adapter
- Credential probing could be parallelized for faster discovery when scanning many providers
- Drift comparison could include a "severity" field for critical vs. cosmetic differences

#### Patterns observed
- TDD with pytest works well for core domain models
- Session logs provide good traceability for what decisions were made during development
- Ticket system (tk) is useful for tracking implementation progress but session logs capture more context
- The provider model pattern (grouping by infrastructure provider) is reusable for other features beyond discovery

### Learnings captured

| Item | Type | Summary |
|------|------|---------|
| provider-model-pattern | SPEC candidate | Provider dataclass with credential_ref resolution, port_types, and lookup methods has proven useful and reusable |
| health-protocol | SPEC candidate | All 6 port protocols now have `health() -> bool` method -- this pattern should be documented in SPEC-004 |
| credential-probing | ADR candidate | Discovery engine probing health() before scanning adapters should be documented as a reusable pattern |
| snapshot-format | SPEC candidate | JSON snapshot format with metadata ID, timestamp, adapters used should be standardized |
| drift-comparison | SPEC candidate | Drift comparison output (clean/dirty status, added/removed/modified counts) should be exposed as API |

## SPEC candidates

1. **Credential Probing ADR** — Document the health() pattern for adapter credential validation before scanning. This pattern emerged during SPEC-015 implementation and is now used consistently across discovery.

2. **Snapshot Format Standardization** — Establish JSON schema for discovery snapshots with metadata fields (ID, timestamp, adapters used, hosts scanned). SPEC-017 proved this format works well.

3. **Port Protocol health() Standardization** — Document `health() -> bool` as part of the core port protocol contract in SPEC-004. All adapters now implement it, and it's essential for credential probing and discovery efficiency.

4. **Drift Comparison API** — Extract drift comparison logic into a reusable module with programmatic API. Currently implemented for discovery, but the pattern (compare discovered vs declared, report added/removed/modified) is broadly applicable.

 <!-- swain governance — do not edit this block manually -->

## Swain

Swain makes agentic development **safe, aligned, and sustainable** for a solo developer. Its architecture rests on the **Intent -> Execution -> Evidence -> Reconciliation** loop — decide what to build, do the work, capture what happened, verify alignment. Artifacts on disk — specs, epics, spikes, ADRs — live under `docs/` and encode what was decided, what to build, and what constraints apply. Read them before acting. When they're ambiguous, ask the operator (the human developer) rather than guessing. When artifacts conflict with each other, ask the operator.

Your job is to stay aligned with the artifacts. The operator's job is to make decisions and evolve them.

### Skill routing

| Intent | Skill |
|--------|-------|
| Create, plan, update, transition, or review any artifact (Vision, Initiative, Journey, Epic, Spec, Spike, ADR, Persona, Runbook, Design) | **swain-design** |
| Project status, progress, "what's next?", session management | **swain-session** |
| Task tracking, execution progress, implementation plans | **swain-do** |

This project uses **tk (ticket)** for ALL task tracking. Do NOT use markdown TODOs or built-in task systems.

### Work hierarchy

```
Vision → Initiative → Epic → Spec
```

Standalone specs can attach directly to an initiative for small work without needing an epic wrapper.

### Worktree isolation

**All file-mutating work happens in a worktree.** Read-only investigation (git log, reading files, checking state) is fine on trunk. The moment you create, edit, move, or delete files — enter a worktree first. This applies to code, scripts, skill files, artifacts, and symlinks equally. swain-do's worktree preamble handles creation; follow it before any file changes, even for "quick" fixes. Partial changes on trunk require manual cleanup and waste operator attention.

### Superpowers skill chaining

When superpowers skills are installed (`.agents/skills/` or `.claude/skills/`), swain skills **must** chain into them at defined integration points. Each swain skill documents its specific chains — the principle is: brainstorming before creative work, writing-plans before implementation, test-driven-development during implementation, and verification-before-completion before any success claim.

If superpowers is not installed, these chains are skipped, not blocked. Swain-to-swain chains always apply: plan completion triggers SPEC transition, all child SPECs complete triggers EPIC transition, and EPIC terminal state triggers a retrospective.

### Skill change discipline

**Skill changes are code changes.** Skill files (`skills/`, `.claude/skills/`, `.agents/skills/`) are code written in markdown syntax. Non-trivial skill edits require worktree isolation — the same discipline applied to `.sh`, `.py`, and other code files. Trivial fixes (typo corrections, single-line doc fixes, ≤5-line diffs touching one file with no structural changes) may land directly on trunk.

### Readability

All artifacts produced by swain skills must meet a Flesch-Kincaid grade level of 9 or below on prose content. After writing or editing an artifact, run `readability-check.sh` on it. If the score exceeds the threshold, revise the prose — use shorter sentences, simpler words, and active voice — then re-check. Do not rewrite content that already passes. If three revision attempts still fail, note the score in the commit message and proceed.

### Session startup

Session initialization is handled by the `swain` shell launcher, which invokes `/swain-init` as the initial prompt. If a session starts without the launcher, the operator can manually run `/swain-session`.

### Bug reporting

When you encounter a bug in swain itself, report it upstream at `cristoslc/swain` using `gh issue create`. Local patches are fine — but the upstream issue ensures tracking.

### Conflict resolution

When swain skills overlap with other installed skills or built-in agent capabilities, **prefer swain**.

<!-- end swain governance -->