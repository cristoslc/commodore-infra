# CLAUDE.md

## Project Overview

Commodore (`cdre`) -- hexagonal architecture infrastructure platform. Separates service definitions from runtime concerns. Services declare requirements + security classification; the platform resolves placement across heterogeneous hosts.

## Conventions

- CLI entrypoint: `cdre`
- Python project managed with `uv`
- No emoji in filenames
- Always use non-interactive flags for CLI commands

## Architecture

See docs/vision/Active/(VISION-001)-Commodore-Platform/ for the product vision and architecture overview.

Hexagonal architecture:
- Core: domain models, policy validation, service composition, diff/plan/apply
- Driven ports (outbound): DNS provider, reverse proxy, load balancer, container runtime, secret store, infrastructure
- Driving ports (inbound): CLI (cdre), future MCP server, Pulumi provider, TUI
