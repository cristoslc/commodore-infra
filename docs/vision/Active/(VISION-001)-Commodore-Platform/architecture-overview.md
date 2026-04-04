# Commodore -- Architecture Overview

## Hexagonal Architecture

Commodore follows hexagonal (ports & adapters) architecture. The core owns domain models and business logic. All external interactions happen through port interfaces, implemented by swappable adapters.

```
                    ┌─────────────────────────┐
                    │      Domain Core         │
                    │                          │
                    │  Models:                 │
                    │    Service, Workload,     │
                    │    Classification,        │
                    │    Host, Topology,        │
                    │    Volume, Zone,          │
                    │    Site, Route, Stack     │
                    │                          │
                    │  Operations:             │
                    │    diff, plan, apply      │
                    │    validate, compose      │
                    │                          │
                    └──────────┬───────────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
          ╔═════════╗   ╔═════════╗   ╔═════════╗
          ║ Driving ║   ║ Driven  ║   ║ Driven  ║
          ║ Ports   ║   ║ Ports   ║   ║ Ports   ║
          ╚════╤════╝   ╚════╤════╝   ╚════╤════╝
               │              │              │
      ┌────────┴───┐   ┌─────┴─────┐  ┌─────┴─────┐
      │ Driving    │   │ Infra     │  │ Runtime   │
      │ Adapters   │   │ Adapters  │  │ Adapters  │
      │            │   │           │  │           │
      │ • CLI      │   │ • CF DNS  │  │ • Docker  │
      │   (cdre)   │   │ • DO DNS  │  │   Compose │
      │ • MCP      │   │ • SSH     │  │ • k3s     │
      │   server   │   │   Caddy   │  │ • Proxmox │
      │ • Pulumi   │   │ • SSH     │  │   VM      │
      │   provider │   │   HAProxy │  │ • Bare    │
      │ • TUI      │   │ • 1Pass   │  │   metal   │
      └────────────┘   └───────────┘  └───────────┘
```

## Domain Models

### Service (the unit of deployment)

A service declares what it needs without knowing how or where it runs:

- **Workload** -- image or binary, env vars, port requirements, storage requirements, resource requirements, network peers
- **Classification** -- blast-radius class, taint domain, audience, persistence, replaceability
- **Composition** -- optional DNS record, ingress (reverse proxy site), load balancer route

Services are runtime-agnostic. A service definition is valid whether the workload runs as a Docker container, k3s pod, Proxmox VM, or bare metal process.

### Classification (security by topology)

Drawn from the data-classification-tenancy model (2026-04-01). Three layers:

1. **Blast-radius class** -- determines security posture:
   - Custodial: third parties harmed who can't self-remediate
   - Identity: enables impersonation or financial theft
   - Strategic: destroys optionality, positional damage
   - Operational: annoying, not harmful

2. **Taint domain** -- determines agent/data boundary (one per stakeholder group within a class)

3. **Room type** -- determines per-artifact persistence and storage location

Classification is applied to services, volumes, and hosts. The core validates that placements respect classification boundaries -- a custodial service cannot be placed on an operational host, and a service cannot mount a volume with an incompatible classification.

### Host & Topology

Hosts exist in a topology with physical and network relationships:

- **Host** -- a compute target with a placement zone (blast-radius + taint domain), available runtimes, locality (site, network, storage bus), and resource capacity
- **Locality** -- encodes which hosts can share storage, reach each other over fast networks, or must communicate over WAN/VPN
- **Storage bus** -- determines which volumes a host can mount (NFS server must be on the same LAN as NFS clients)

### Stack (deployment group)

A stack groups services that must deploy together with an affinity constraint (same-host, same-site, or any). Used for services that share network namespaces (e.g., Gluetun VPN + download clients) or have tight coupling.

## Driven Ports

| Port | Responsibility | v1 Adapters |
|------|---------------|-------------|
| DNSPort | CRUD DNS records in a zone | Cloudflare API, DigitalOcean API |
| ReverseProxyPort | Deploy/fetch/validate proxy config | SSH + Caddy (docker exec) |
| LoadBalancerPort | Deploy/fetch/validate LB routes | SSH + HAProxy (systemctl) |
| ContainerPort | Deploy/manage workloads | Docker Compose (SSH), k3s (future) |
| SecretPort | Fetch secrets by key | 1Password (op read + session cache) |
| InfrastructurePort | Provision hosts, networks, storage | Terraform/OpenTofu (future) |

## Driving Ports

The core exposes use cases that any frontend can call:

- `dns_diff`, `dns_apply`, `dns_import`
- `proxy_diff`, `proxy_apply`
- `lb_diff`, `lb_apply`
- `service_diff`, `service_apply`, `service_expose`, `service_teardown`
- `validate` -- check all placements against classification policy
- `topology_status` -- show hosts, capacity, current placements

v1 driving adapter: CLI (`cdre`). Future: MCP server, Pulumi provider, TUI.

## Placement & Validation

### v1: Static placement with policy validation

Services are pinned to hosts by the operator in configuration. The core validates:

1. Classification match -- host zone compatible with service classification
2. Runtime available -- host supports a runtime for the workload
3. Storage reachable -- host's storage bus can reach required volumes
4. Network peers reachable -- host can reach the service's declared network peers
5. Resource capacity -- host has sufficient CPU/memory (advisory, not blocking in v1)

### v2: Dynamic scheduling

Same constraint solver, but the core picks hosts instead of validating operator-pinned assignments. Adds migration planning and rebalancing. The scheduler is the same; the new complexity is in migration and rebalancing, not in the matching logic.

## Instance Model

Commodore is the tool. A specific infrastructure deployment is an instance. The relationship:

| Concept | Commodore (tool) | Homelab (instance) |
|---------|-----------------|-------------------|
| Service definitions | Schema + validation | `services/jellyseerr.yaml` |
| Topology | Host + locality model | `infrastructure/topology.yaml` |
| DNS zones | DNSPort interface | `routing/dns/zones/*.yaml` |
| Proxy config | ReverseProxyPort interface | `routing/caddy/sites.yaml` |
| LB config | LoadBalancerPort interface | `routing/haproxy/routes.yaml` |
| Classification policy | BlastRadius + TaintDomain models | Zone assignments per host |
