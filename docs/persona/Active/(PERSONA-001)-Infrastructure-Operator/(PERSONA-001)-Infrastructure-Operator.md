---
title: "Infrastructure Operator"
artifact: PERSONA-001
track: standing
status: Active
author: cristos
created: 2026-04-04
last-updated: 2026-04-04
linked-artifacts:
  - VISION-001
depends-on-artifacts: []
---

# Infrastructure Operator

## Archetype Label

Solo Homelab Operator

## Demographic Summary

A technical professional who runs personal or small-team infrastructure across heterogeneous hosts. Comfortable with CLI tools, YAML configuration, and container runtimes. Manages infrastructure in spare time alongside a primary role. Linux-proficient, familiar with DNS, reverse proxies, and container orchestration at a practical level.

## Goals and Motivations

- Define a service once and deploy it anywhere -- Docker Compose today, k3s tomorrow -- without rewriting configuration
- Enforce security boundaries structurally so custodial data never lands on the wrong host, even when tired or rushing
- Reduce the number of systems touched when adding or moving a service (currently 4-5 manual touchpoints)
- Return to infrastructure work after weeks away and understand the current state without archaeology

## Frustrations and Pain Points

- Adding a new service means editing DNS configs, reverse proxy rules, container definitions, and secret stores separately with no shared model
- Security classification exists only in memory -- nothing prevents a misconfigured deployment from violating blast-radius boundaries
- Existing tools (Terraform, Ansible, Docker Compose) each solve one concern but don't compose into a unified service model
- Context-switching cost is high: after time away, reconstructing which services run where and why requires reading multiple config files across repos

## Behavioral Patterns

- Works in focused bursts -- an evening here, a weekend there -- not continuous operations
- Prefers declarative configuration over imperative scripts
- Tests changes locally or in staging before applying to production hosts
- Values explicit, self-documenting configuration over clever abstractions
- Maintains a small number of hosts (3-10) across 2-3 runtime types

## Context of Use

- Works from a single workstation via SSH to remote hosts
- Interacts with infrastructure through terminal-based CLI tools
- Manages DNS, ingress, workloads, and storage as related concerns that should move together
- Deploys to a mix of Proxmox VMs, Docker hosts, k3s clusters, and occasionally bare metal or cloud VPS

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-04 | -- | Seeded from README and VISION-001 |
