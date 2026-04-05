---
title: "Config Discovery and YAML Loading"
artifact: SPEC-011
track: container
status: Complete
author: cristos
created: 2026-04-04
last-updated: 2026-04-04
parent-epic: EPIC-004
parent-vision: VISION-001
priority-weight: medium
depends-on-artifacts:
  - SPEC-001
---

# Config Discovery and YAML Loading

## Goal

Load service definitions, topology, and project config from YAML files. Discover the cdre.yaml project file and resolve relative paths to service and topology files.

## Acceptance Criteria

- `load_project(path) -> ProjectConfig` finds and parses cdre.yaml
- `load_services(project) -> list[Service]` loads all referenced service YAML files into domain models
- `load_topology(project) -> Topology` loads topology YAML into domain model
- Glob patterns work in service paths (e.g., `services/*.yaml`)
- Missing files produce clear errors with the path that was tried
- Invalid YAML produces errors with file path and line number
- Round-trip: domain models serialize back to valid YAML

## Lifecycle

| Phase | Date | Notes |
|-------|------|-------|
| Active | 2026-04-04 | Decomposed from EPIC-004 |
