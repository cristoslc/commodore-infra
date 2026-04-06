---
title: "Entry Point Discovery Mechanism"
artifact: SPEC-020
track: implementable
status: Proposed
author: cristos
created: 2026-04-06
last-updated: 2026-04-06
priority-weight: high
type: ""
parent-epic: EPIC-007
parent-initiative: ""
linked-artifacts:
  - ADR-001
depends-on-artifacts:
  - SPEC-005
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Entry Point Discovery Mechanism

## Problem Statement

Commodore needs a standard mechanism to discover adapter plugins at runtime. The current `AdapterRegistry` (SPEC-005) only knows about built-in adapters. Third-party adapters have no way to register themselves without modifying core code.

## Desired Outcomes

Plugin authors can distribute adapters as standard Python packages. Users install them via pip/uv and Commodore discovers them automatically at startup. The discovery mechanism uses Python's `importlib.metadata.entry_points()` — a well-established pattern that requires no custom plugin loader.

## External Behavior

**Inputs:**
- Python environment with installed packages (some may declare `commodore.adapters` entry points)

**Outputs:**
- A mapping of entry point names to adapter classes: `Dict[str, Type[PortProtocol]]`

**Preconditions:**
- Packages declaring adapters have `commodore-core` (or port protocols) as a dependency

**Postconditions:**
- All declared entry points are loadable and type-checked against port protocols
- Invalid or unloadable adapters raise an informative error

**Constraints:**
- Discovery must complete before any adapter is instantiated
- Discovery should be idempotent (calling twice returns same result)
- Built-in adapters use the same entry point mechanism (parity with plugins)

## Acceptance Criteria

**Given** a Python environment with packages installed
**When** `discover_adapters()` is called
**Then** all packages declaring `[project.entry-points."commodore.adapters"]` are discovered

**Given** a package declares an adapter entry point
**When** the entry point is loaded
**Then** the adapter class implements its declared port protocol (type-checked)

**Given** an entry point fails to load (missing dependency, import error)
**When** discovery proceeds
**Then** an informative error is raised listing the entry point name, expected port, and underlying exception

**Given** Commodore's built-in adapters
**When** discovery runs
**Then** built-in adapters appear alongside plugin adapters in the same registry

## Verification

<!-- Populated when entering Testing phase. -->

|| Criterion | Evidence | Result |
||-----------|----------|--------|
| Entry points discovered | | |
| Type checking works | | |
| Error messages clear | | |
| Built-in parity | | |

## Scope & Constraints

**In scope:**
- `discover_adapters()` function in `commodore.discovery`
- Entry point group name: `commodore.adapters`
- Mapping structure: `{entry_point_name: (port_protocol, adapter_class)}`
- Basic validation (class exists, implements protocol)

**Out of scope:**
- Adapter instantiation (handled by SPEC-021)
- Configuration binding (handled by SPEC-021)
- Plugin installation/package management (user responsibility via pip/uv)

## Implementation Approach

**TDD Cycle 1: Discovery**
1. Write test: `test_discover_adapters_finds_entry_points()`
2. Implement: Scan `importlib.metadata.entry_points(group="commodore.adapters")`
3. Assert: Returns mapping of names to entry points

**TDD Cycle 2: Type checking**
1. Write test: `test_load_adapter_validates_port_protocol()`
2. Implement: Load entry point, check `issubclass(adapter_class, port_protocol)`
3. Assert: Invalid adapters raise clear error

**TDD Cycle 3: Built-in parity**
1. Write test: `test_builtin_adapters_registered_via_entry_points()`
2. Implement: Register built-in adapters via same mechanism
3. Assert: Discovery returns both built-in and plugin adapters uniformly

## Lifecycle

|| Phase | Date | Commit | Notes |
||-------|------|--------|-------|
|| Proposed | 2026-04-06 | -- | Decomposed from EPIC-007 |