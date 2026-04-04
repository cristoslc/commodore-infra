---
title: "Initial Driven Adapters"
artifact: EPIC-005
track: container
status: Active
author: cristos
created: 2026-04-04
last-updated: 2026-04-04
parent-vision: VISION-001
parent-initiative: INITIATIVE-001
priority-weight: medium
success-criteria:
  - Cloudflare DNS adapter creates, updates, and deletes DNS records via the Cloudflare API
  - Docker Compose adapter deploys, stops, and inspects containers via SSH + docker compose commands
  - SSH+Caddy reverse proxy adapter configures ingress routes and TLS via Caddyfile management over SSH
  - All three adapters pass the port protocol test suite (same tests as in-memory stubs)
  - Each adapter is independently deployable -- removing one doesn't affect the others
depends-on-artifacts:
  - EPIC-002
addresses: []
evidence-pool: ""
---

# Initial Driven Adapters

## Goal / Objective

Implement the minimum viable set of driven adapters that makes `cdre apply` functional against real infrastructure. Three adapters cover the most common homelab topology: Cloudflare for DNS, Docker Compose for container workloads, and Caddy (via SSH) for reverse proxy/ingress.

## Desired Outcomes

The [Infrastructure Operator](../../../persona/Active/(PERSONA-001)-Infrastructure-Operator/(PERSONA-001)-Infrastructure-Operator.md) can deploy a containerized service with DNS and HTTPS ingress using `cdre apply` against their existing Cloudflare + Docker + Caddy stack. Each adapter is self-contained and tested against the same port protocol test suite as the in-memory stubs.

## Progress

<!-- Auto-populated from session digests. See progress.md for full log. -->

## Scope Boundaries

**In scope:**
- `CloudflareDNS` adapter: implements `DNSProvider` port via Cloudflare API
- `DockerCompose` adapter: implements `ContainerRuntime` port via SSH + docker compose CLI
- `SSHCaddy` adapter: implements `ReverseProxy` port via Caddyfile management over SSH
- Port protocol compliance tests shared between stubs and real adapters
- Configuration schema for each adapter (API keys, SSH credentials, paths)

**Out of scope:**
- `LoadBalancer` adapter (HAProxy) -- deferred to post-v1; the port protocol exists but no real adapter yet
- `SecretStore` adapter (Vault, SOPS) -- deferred; v1 reads secrets from environment or plain config
- `Infrastructure` adapter (Proxmox API) -- deferred; v1 assumes hosts are pre-provisioned
- Route53, Nginx, k3s, or other alternative adapters

## Child Specs

None yet -- to be decomposed when implementation begins.

## Key Dependencies

- [EPIC-002](../../../epic/Active/(EPIC-002)-Hexagonal-Port-Framework/(EPIC-002)-Hexagonal-Port-Framework.md) -- port protocols that adapters implement

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-04 | -- | Minimum viable adapter set for cdre v1 |
