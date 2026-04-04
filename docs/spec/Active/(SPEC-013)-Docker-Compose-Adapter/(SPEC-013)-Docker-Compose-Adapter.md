---
title: "Docker Compose Adapter"
artifact: SPEC-013
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

# Docker Compose Adapter

## Goal

Implement the ContainerPort protocol using Docker Compose over SSH. Manages container stacks on remote hosts.

## Acceptance Criteria

- Implements `ContainerPort` protocol (current_state, diff, apply)
- Generates docker-compose.yml from service container specs
- Deploys via SSH + `docker compose up -d`
- Stops via SSH + `docker compose down`
- Inspects running state via `docker compose ps --format json`
- Config: SSH host, compose project directory injected at construction
- Passes the same port protocol test suite as InMemoryContainer

## Lifecycle

| Phase | Date | Notes |
|-------|------|-------|
| Active | 2026-04-04 | Decomposed from EPIC-005 |
