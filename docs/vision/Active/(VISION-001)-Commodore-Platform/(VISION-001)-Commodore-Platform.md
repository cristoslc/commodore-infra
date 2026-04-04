---
title: "Commodore Platform"
artifact: VISION-001
track: standing
status: Active
product-type: personal
author: cristos
created: 2026-04-04
last-updated: 2026-04-04
priority-weight: high
depends-on-artifacts: []
evidence-pool: ""
---

# Commodore Platform

## Target Audience

A single homelab operator managing heterogeneous infrastructure -- Proxmox hypervisors, Docker VMs, NFS storage, cloud VPS, and edge nodes -- who wants a unified control surface that enforces security boundaries by construction rather than convention.

## Value Proposition

One domain model and one CLI (`cdre`) for defining, classifying, placing, and deploying services across any mix of container runtimes, bare metal hosts, and cloud resources. Security classification drives placement automatically -- custodial data can never land on an operational host, not because of ACLs, but because the topology makes it structurally impossible.

## Problem Statement

Managing personal infrastructure today requires juggling multiple tools (Docker Compose, DNS provider APIs, reverse proxy configs, load balancer configs, secret managers) with no shared model between them. Adding a new service means touching 4-5 systems manually. Security boundaries exist only in the operator's head -- nothing prevents a custodial workload from landing on the wrong host. The existing `lab` CLI in the Homelab repo reimplements functionality that existing tools handle (DNS management, credential lifecycle) while missing the higher-value layer: service composition and classified placement.

## Existing Landscape

- **Terraform/OpenTofu** -- infrastructure provisioning, but doesn't model service composition or security classification
- **Ansible** -- configuration management, but imperative playbooks don't capture the service-as-composition model
- **Kubernetes/k3s** -- container orchestration with scheduling, but assumes it IS the runtime (doesn't span Docker Compose, bare metal, VMs) and doesn't natively model blast-radius classification
- **OctoDNS/dnscontrol** -- declarative DNS, good at what they do but single-concern
- **Portainer/Dockge** -- container UIs, single-host, no classification or cross-concern composition
- **Coolify** -- self-hosted PaaS, too opinionated for heterogeneous infra

None of these provide: (1) a unified service model that composes DNS + ingress + workload + storage, (2) security-classified placement across heterogeneous runtimes, or (3) a hexagonal architecture where they themselves can serve as swappable adapters.

## Build vs. Buy

Tier 2 evolving toward Tier 3. The individual tools exist (OctoDNS, Ansible, Terraform, Docker Compose, k3s). What doesn't exist is the composition and classification layer above them. Commodore is that layer -- it owns the domain models, policy validation, and orchestration. Existing tools become driven adapters behind port interfaces. The core is new; the adapters wrap proven tools.

## Maintenance Budget

Low-to-moderate. Single developer, spare time. The architecture must support incremental development -- ship with 2-3 adapters (Cloudflare DNS, SSH+Caddy, SSH+HAProxy, Docker Compose), add more as needed. The hexagonal structure means adding an adapter doesn't touch the core. Returning after weeks away should be straightforward because the domain models are self-documenting and the port interfaces are explicit.

## Success Metrics

- A new service can be defined in one YAML file (workload + classification + DNS + ingress) and deployed with `cdre apply`
- `cdre validate` catches classification violations (custodial service on operational host) before deployment
- Migrating a service between runtimes (Docker Compose to k3s) requires changing only the host topology, not the service definition
- The existing Homelab repo's `lab` CLI functionality is fully replicated by `cdre` with Homelab-repo service/topology YAML as input
- Adding a new driven adapter (e.g., Route53 DNS, Ansible deploy) requires implementing one port interface with no core changes

## Non-Goals

- High availability, clustering, or multi-operator workflows (single operator)
- Replacing Kubernetes -- k3s is a valid adapter, not a competitor
- General-purpose IaC framework -- this is opinionated toward service composition and classified placement
- Dynamic scheduling in v1 -- static placement with operator pinning and core validation first
- Web UI or TUI in v1 -- CLI (`cdre`) is the only driving adapter initially

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-04 | -- | Created from architecture design session |
