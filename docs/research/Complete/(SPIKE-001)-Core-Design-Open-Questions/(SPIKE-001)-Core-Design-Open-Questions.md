---
title: "Core Design Open Questions"
artifact: SPIKE-001
track: container
status: Complete
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

All four threads resolved. Port interfaces use type-specific protocols with config injected at construction. v1 scope is full service composition (`cdre service diff/apply`). Instance format is a clean-break service-centric YAML schema. No migration from lab CLI — Commodore starts fresh, using the lab CLI only as a reference for which adapter categories are needed (DNS, reverse proxy, load balancer, container, secrets, infrastructure).

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

**Status:** Complete — type-specific protocols, config at construction

**Decision:** Each port gets its own Protocol class. Config is injected at construction (not per-call). Ports with similar shapes (ReverseProxy, LoadBalancer) stay separate — the domain semantics differ even if the method signatures overlap today. This avoids premature abstraction while keeping each port testable in isolation.

**Port catalog (6 driven ports):**

1. **`DNSPort`** — `diff(desired) -> list[Change]`, `apply(changes) -> Result`, `current_state() -> DNSState`. Provider credentials and zone config injected at init.

2. **`ReverseProxyPort`** — `diff(desired) -> list[Change]`, `apply(changes) -> Result`, `current_state() -> ProxyState`, `validate(config) -> list[Error]`. Separate from LoadBalancer because reverse proxy is L7 (TLS termination, path routing) while LB is L4 (TCP/UDP distribution).

3. **`LoadBalancerPort`** — `diff(desired) -> list[Change]`, `apply(changes) -> Result`, `current_state() -> LBState`. Handles backend health, weight distribution, protocol-level routing.

4. **`ContainerPort`** — `diff(desired) -> list[Change]`, `apply(changes) -> Result`, `current_state() -> ContainerState`. Operates on "stacks" as the unit of deployment. A stack maps to a Docker Compose file or a set of k3s manifests — the port abstracts the unit boundary.

5. **`SecretPort`** — `get(ref) -> str`, `get_batch(refs) -> dict[str, str]`, `health() -> bool`. Stateless reads only — Commodore does not write secrets. Batch support avoids N+1 lookups during service composition.

6. **`InfrastructurePort`** — `diff(desired) -> list[Change]`, `apply(changes) -> Result`, `current_state() -> InfraState`. Host provisioning and topology. v1 adapter: static topology from YAML (no actual provisioning).

**Validation of abstraction:** Each port can name at least two plausible adapters:
- DNS: Cloudflare, DigitalOcean (both existed in lab CLI)
- ReverseProxy: Caddy, nginx
- LoadBalancer: HAProxy, nginx-stream
- Container: Docker Compose, k3s
- Secret: 1Password CLI, environment variables
- Infrastructure: Proxmox API, static YAML

### Thread 2: v1 Scope

**Status:** Complete — Option C, full service composition

**Decision:** `cdre service diff/apply` — full composition for a single service. This is the highest-value option and proves the entire architecture end-to-end: domain models, policy validation, composition engine, and at least one adapter per port category.

**v1 commands:**
- `cdre validate <service.yaml>` — parse and validate a service definition against topology and policy
- `cdre diff <service.yaml>` — show what would change across all ports
- `cdre apply <service.yaml>` — execute the changes
- `cdre status` — show current state of deployed services

### Thread 3: Instance Format

**Status:** Complete — clean-break service-centric YAML

**Decision:** From-scratch definitions. No backward compatibility with the old `routing/` YAML format. A consumer repo provides:

```yaml
# cdre.yaml — project root
topology: topology.yaml
services:
  - services/*.yaml

# topology.yaml — host inventory
hosts:
  nas:
    address: 10.0.0.10
    roles: [container, storage]
    classification: internal
  proxy:
    address: 10.0.0.1
    roles: [reverse-proxy, load-balancer]
    classification: edge

# services/jellyseerr.yaml — single service definition
name: jellyseerr
classification: authenticated
container:
  image: fallenbagel/jellyseerr:latest
  ports: [5055]
  volumes:
    config: /app/config
dns:
  records:
    - name: requests.example.com
      type: CNAME
      target: proxy.example.com
ingress:
  reverse_proxy:
    upstream: "http://nas:5055"
    tls: auto
  load_balancer:
    backend: jellyseerr
    port: 5055
    health_check: /api/v1/health
```

### Thread 4: Migration Path

**Status:** Complete — no migration, fresh start

**Decision:** Commodore starts from scratch. The existing lab CLI code is reference material only — it informs which adapter categories are needed and what real-world adapter behavior looks like, but no code is ported. The lab CLI continues to operate the homelab until Commodore reaches feature parity for at least one service.

**Adapter categories derived from lab CLI reference:**
- DNS management (Cloudflare, DigitalOcean) → `DNSPort`
- Caddy config generation → `ReverseProxyPort`
- HAProxy config generation → `LoadBalancerPort`
- Docker Compose stack management → `ContainerPort`
- 1Password credential reads → `SecretPort`
- Host SSH access → `InfrastructurePort`

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-04 | — | Created from architecture design session |
| Complete | 2026-04-04 | — | All threads resolved. Operator decisions + agent design for port interfaces. |
