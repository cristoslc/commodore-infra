---
title: "Plugin Missing Error Handling"
artifact: SPEC-022
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
  - SPEC-021
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Plugin Missing Error Handling

## Problem Statement

When a topology references a provider that isn't installed (e.g., `dns_provider: route53` when no Route53 adapter exists), the error is cryptic. Users see import errors or `KeyError` traces instead of actionable guidance like "Install commodore-route53 to use the route53 provider."

## Desired Outcomes

Users receive clear, actionable error messages when a required plugin is missing. The error includes:
- Provider name and port type
- Expected package name(s)
- Install command (pip/uv)

No stack traces from import failures reach the user.

## External Behavior

**Inputs:**
- Topology configuration referencing provider X
- Discovered adapters (may not include X)

**Outputs:**
- Actionable error message for `cdre validate` and `cdre apply`

**Preconditions:**
- Discovery (SPEC-020) and registry (SPEC-021) have run

**Postconditions:**
- User sees error with install instructions
- Exit code is non-zero
- No unhandled exception stack trace

**Constraints:**
- Error message must fit on a single terminal screen (no 100-line traces)
- Must suggest at least one package name (built-in or known plugin)
- If package name is unknown, suggest checking PyPI or docs

## Acceptance Criteria

**Given** topology with `proxy_provider: envoy` and no Envoy adapter installed
**When** `cdre validate` runs
**Then** output includes: `Missing plugin for provider 'envoy' (port: ReverseProxy). Install: pip install commodore-envoy`

**Given** topology with `infrastructure_provider: hetzner` (built-in)
**When** `cdre validate` runs
**Then** validation passes (no error)

**Given** a custom provider `mycompany-dns`
**When** `cdre validate` fails to find it
**Then** error includes: `Missing plugin for provider 'mycompany-dns' (port: DNSProvider). Check https://commodore.dev/plugins or implement your own adapter.`

**Given** validation runs in CI
**When** plugin is missing
**Then** exit code is 1 (non-zero) and error message is machine-parseable

## Verification

<!-- Populated when entering Testing phase. -->

|| Criterion | Evidence | Result |
||-----------|----------|--------|
| Missing plugin error clear | | |
| Install hint provided | | |
| Built-in works | | |
| Unknown provider hint | | |
| Exit code non-zero | | |

## Scope & Constraints

**In scope:**
- `ProviderNotFoundError` exception with structured fields
- Error formatting for CLI commands
- Suggestion logic for known vs. unknown providers

**Out of scope:**
- Auto-installation of plugins (user must run pip/uv)
- Plugin marketplace or search command (future)
- Network connectivity checks for install verification

## Implementation Approach

**TDD Cycle 1: Exception definition**
1. Write test: `test_provider_not_found_error_contains_fields()`
2. Implement: `ProviderNotFoundError(provider="envoy", port=ReverseProxy)`
3. Assert: Exception message includes all required fields

**TDD Cycle 2: Error formatting**
1. Write test: `test_format_missing_plugin_error_includes_install_hint()`
2. Implement: Lookup known providers → suggest package name
3. Assert: Message ends with `pip install <package>`

**TDD Cycle 3: Unknown providers**
1. Write test: `test_unknown_provider_suggests_docs()`
2. Implement: Fallback message with docs URL
3. Assert: Message includes "Check https://commodore.dev/plugins"

**TDD Cycle 4: CLI integration**
1. Write test: `test_cdre_validate_exits_nonzero_on_missing_plugin()`
2. Implement: Catch ProviderNotFoundError, format and exit(1)
3. Assert: Exit code and stderr content

## Lifecycle

|| Phase | Date | Commit | Notes |
||-------|------|--------|-------|
|| Proposed | 2026-04-06 | -- | Decomposed from EPIC-007 |