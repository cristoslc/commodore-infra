---
title: "Plugin Development Guide"
artifact: SPEC-023
track: implementable
status: Complete
author: cristos
created: 2026-04-06
last-updated: 2026-04-06
priority-weight: medium
type: ""
parent-epic: EPIC-007
parent-initiative: ""
linked-artifacts:
  - ADR-001
depends-on-artifacts:
  - SPEC-020
  - SPEC-021
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Plugin Development Guide

## Problem Statement

Third-party developers have no documentation for creating Commodore adapter plugins. The entry point mechanism (ADR-001) and discovery system (SPEC-020) exist, but there's no guide showing how to build a plugin from scratch.

## Desired Outcomes

A developer can read a single `docs/examples/commodore-plugin-example/` directory and understand:
- How to structure a plugin package
- How to declare entry points in `pyproject.toml`
- How to implement a port protocol
- How to test a plugin locally
- How to publish to PyPI

## External Behavior

**Inputs:**
- Developer reads `docs/examples/commodore-plugin-example/`
- Developer has `commodore-core` installed or documented as dependency

**Outputs:**
- A working plugin package that installs and integrates with Commodore
- Documentation in `docs/docs/plugin-development.md`

**Preconditions:**
- SPEC-020 and SPEC-021 implemented

**Postconditions:**
- Example plugin successfully installs and registers
- Documentation covers all required steps

**Constraints:**
- Example must be minimal (one port, ~50 lines)
- Documentation must not assume advanced Python packaging knowledge

## Acceptance Criteria

**Given** the example plugin directory
**When** developer runs `pip install -e ./docs/examples/commodore-plugin-example`
**Then** plugin installs and `cdre validate --list-adapters` shows the example adapter

**Given** a developer reads `docs/docs/plugin-development.md`
**When** following the steps
**Then** they can create a new plugin package from scratch

**Given** the example plugin
**When** running its test suite
**Then** tests pass and demonstrate port protocol compliance

**Given** the documentation
**When** a developer wants to support multiple ports in one package
**Then** the guide explains how to declare multiple entry points

## Verification

<!-- Populated when entering Testing phase. -->

|| Criterion | Evidence | Result |
||-----------|----------|--------|
| Example installs | | |
| Example appears in list-adapters | | |
| Docs guide complete | | |
| Multiple entry points documented | | |
| Tests pass | | |

## Scope & Constraints

**In scope:**
- Example plugin in `docs/examples/commodore-plugin-example/`
- Plugin development guide in `docs/docs/plugin-development.md`
- README in example plugin directory
- Unit test for the example plugin
- Cross-link from main Commodore documentation

**Out of scope:**
- Plugin marketplace or registry (future)
- CI/CD automation (developer's responsibility)
- Automated plugin scaffolding tool (future)

## Implementation Approach

**Step 1: Create example plugin skeleton**
1. Create `docs/examples/commodore-plugin-example/`
2. Add minimal `pyproject.toml` with entry point declaration
3. Add `__init__.py` with `ExampleAdapter` implementing a port
4. Keep under 50 lines total

**Step 2: Write plugin guide**
1. Create `docs/docs/plugin-development.md`
2. Document: package structure, entry points, protocol implementation, testing, publishing
3. Include code snippets from example plugin

**Step 3: Add test fixture**
1. Create `tests/fixtures/plugin_example/` if needed for CI testing
2. Ensure example plugin can be installed in test environment
3. Write integration test: install plugin, run discovery, verify adapter appears

**Step 4: Integration test**
1. Write test: `test_example_plugin_discovers_and_loads()`
2. Run discovery with example plugin installed
3. Assert adapter in registry

## Lifecycle

|| Phase | Date | Commit | Notes |
||-------|------|--------|-------|
|| Proposed | 2026-04-06 | -- | Decomposed from EPIC-007 |