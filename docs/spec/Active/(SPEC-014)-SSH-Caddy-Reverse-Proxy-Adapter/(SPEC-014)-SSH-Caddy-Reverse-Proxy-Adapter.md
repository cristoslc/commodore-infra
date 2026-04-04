---
title: "SSH+Caddy Reverse Proxy Adapter"
artifact: SPEC-014
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

# SSH+Caddy Reverse Proxy Adapter

## Goal

Implement the ReverseProxyPort protocol using Caddy managed over SSH. Configures ingress routes and TLS.

## Acceptance Criteria

- Implements `ReverseProxyPort` protocol (current_state, diff, apply, validate)
- Generates Caddyfile blocks from service ingress rules
- Deploys Caddyfile updates via SSH + caddy reload
- Reads current config via SSH + caddy's admin API
- Config: SSH host, Caddyfile path, admin API endpoint injected at construction
- Passes the same port protocol test suite as InMemoryReverseProxy

## Lifecycle

| Phase | Date | Notes |
|-------|------|-------|
| Active | 2026-04-04 | Decomposed from EPIC-005 |
