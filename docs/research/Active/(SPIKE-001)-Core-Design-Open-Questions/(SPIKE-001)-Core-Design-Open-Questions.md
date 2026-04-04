---
title: "Core Design Open Questions"
artifact: SPIKE-001
track: container
status: Active
author: cristos
created: 2026-04-04
last-updated: 2026-04-04
question: "What are the right port interfaces, v1 scope, instance format, and migration path from the existing lab CLI?"
gate: Pre-MVP
parent-vision: VISION-001
risks-addressed:
  - Over-engineering ports before real adapter implementations validate them
  - Shipping too much or too little in v1
  - Breaking existing lab CLI workflows during migration
evidence-pool: ""
---

# Core Design Open Questions

## Summary

<!-- Final-pass section: populated when transitioning to Complete. -->

## Question

Four interconnected design questions that must be resolved before implementation begins:

1. **Port interface signatures** — What methods does each driven port expose? How granular are the operations? Do we use a generic `ResourcePort[T]` protocol or keep each port type-specific?

2. **v1 scope** — Which adapters ship first? What's the minimum useful `cdre`? Is it `cdre validate` (policy engine only), `cdre diff/apply` (full lifecycle for one resource type), or `cdre service apply` (full composition)?

3. **Instance format** — What does the YAML look like that a consumer repo (like Homelab) contains for Commodore to consume? How much of the current `routing/dns/zones/*.yaml`, `routing/caddy/sites.yaml`, `routing/haproxy/routes.yaml` format survives vs gets replaced by service-centric definitions?

4. **Migration path** — Which existing `lab` CLI code becomes Commodore adapter code? Which stays in the Homelab repo as instance config? What's the transition plan so the homelab doesn't go dark during migration?

## Go / No-Go Criteria

- Each port interface has at least two candidate adapter implementations sketched (even if only one is built in v1) to validate the abstraction isn't over-fitted
- v1 scope is defined as a concrete list of commands with expected inputs/outputs
- Instance format has a worked example: Jellyseerr (or Seerr) service defined end-to-end (workload + classification + DNS + ingress + LB)
- Migration path has a file-by-file mapping: each `lab` CLI source file -> Commodore adapter or Homelab instance config or deleted

## Pivot Recommendation

If port interfaces can't stabilize across two adapter sketches, the abstraction layer is premature — fall back to building `cdre` as a monolith CLI first (like `lab` is today, but with the service composition model) and extract ports later once the real boundaries emerge from working code.

## Findings

### Thread 1: Port Interface Signatures

**Status:** Not started

Key sub-questions:
- `DNSPort`: current lab CLI passes zone_id and token to every method. Should the port own its config (injected at construction) or receive it per-call?
- `ReverseProxyPort` and `LoadBalancerPort` have identical shapes (fetch/deploy/validate/rollback). Generic or separate?
- `ContainerPort`: how does it handle the Docker Compose "stack as a single unit" vs k3s "individual pod" difference?
- `SecretPort`: is `get(key) -> str` sufficient, or does it need batch operations and session lifecycle?

### Thread 2: v1 Scope

**Status:** Not started

Candidates for minimum viable `cdre`:
- **Option A (validator only):** `cdre validate` reads service + topology YAML and reports classification violations. No deployment. Proves the domain model works.
- **Option B (single-resource lifecycle):** `cdre dns diff/apply` — reimplements current `lab dns` through the port interface. Proves the hexagonal architecture works end-to-end.
- **Option C (service composition):** `cdre service diff/apply` for one service type. Proves the composition model works. Highest value but biggest scope.

### Thread 3: Instance Format

**Status:** Not started

Key sub-questions:
- Does the instance repo have a single `cdre.yaml` project config pointing to service/topology/routing dirs?
- Do current zone files, sites.yaml, routes.yaml survive as-is (Commodore learns to read them) or do they get replaced by service-centric YAML?
- Can both formats coexist during migration (resource-centric files for things not yet modeled as services, service-centric for things that are)?

### Thread 4: Migration Path

**Status:** Not started

Known file disposition from the lab CLI:
- `lab/dns_cloudflare.py`, `lab/dns_digitalocean.py`, `lab/dns_provider.py` -> Commodore DNS adapters
- `lab/caddy_generator.py`, `lab/caddy_parser.py`, `lab/caddy_diff.py` -> Commodore reverse proxy adapter
- `lab/haproxy_generator.py`, `lab/haproxy_parser.py` -> Commodore load balancer adapter
- `lab/credentials.py` -> Commodore secrets adapter (1Password)
- `lab/ssh.py` -> Commodore shared utility (used by multiple adapters)
- `lab/config.py` -> split: YAML loading stays in Commodore, repo-root detection becomes instance concern
- `routing/dns/zones/*.yaml` -> stays in Homelab as instance config
- `routing/caddy/sites.yaml` -> stays in Homelab as instance config
- `routing/haproxy/routes.yaml` -> stays in Homelab as instance config
- `routing/caddy/Caddyfile.j2`, `routing/haproxy/haproxy.cfg.j2` -> Commodore adapter templates

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-04 | — | Created from architecture design session |
