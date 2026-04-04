---
title: "Cloudflare DNS Adapter"
artifact: SPEC-012
track: container
status: Active
author: cristos
created: 2026-04-04
last-updated: 2026-04-04
parent-epic: EPIC-005
parent-vision: VISION-001
priority-weight: medium
depends-on-artifacts:
  - SPEC-004
---

# Cloudflare DNS Adapter

## Goal

Implement the DNSPort protocol against the Cloudflare API. Manages DNS records for zones configured in the adapter.

## Acceptance Criteria

- Implements `DNSPort` protocol (current_state, diff, apply)
- Creates, updates, and deletes DNS records via Cloudflare API
- Config: API token, zone ID injected at construction
- Passes the same port protocol test suite as InMemoryDNS
- API errors surface as PortError with actionable messages

## Lifecycle

| Phase | Date | Notes |
|-------|------|-------|
| Active | 2026-04-04 | Decomposed from EPIC-005 |
