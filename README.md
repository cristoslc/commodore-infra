# Commodore

> **WARNING: This project is experimental and completely untested.** The code is provided solely for research interest. It is not intended for production use, and there are no guarantees of correctness, stability, or completeness. Use at your own risk.

**CLI:** `cdre`

Commodore is a hexagonal architecture infrastructure platform that separates service definitions from runtime concerns. Services declare what they need and their security classification; the platform resolves placement across heterogeneous hosts (Docker Compose, k3s, bare metal, Proxmox VMs). The CLI is `cdre`.

## Status

Experimental -- not tested, not production-ready.

## Key Concepts

- **Hexagonal architecture (ports & adapters)** -- core domain logic is isolated from all external systems through explicit port interfaces and swappable adapters
- **Security-classified placement** -- blast-radius classes and taint domains determine where services can run; violations are structural, not policy-based
- **Service composition** -- DNS, ingress, workload, and storage are declared as one unit per service
- **Runtime-agnostic workloads** -- a service definition is valid whether it runs as a Docker container, k3s pod, Proxmox VM, or bare metal process
- **Topology-aware scheduling** -- placement respects host locality, storage bus reachability, and network peer constraints

## Architecture

See `docs/vision/Active/(VISION-001)-Commodore-Platform/` for the full product vision and architecture overview.

## Project Structure

```
src/commodore/
  core/           -- domain models and operations (diff, plan, apply, validate)
  ports/          -- port interfaces (driven and driving)
  adapters/       -- adapter implementations (DNS, reverse proxy, LB, container, secrets, frontends)
tests/
docs/vision/      -- product vision and architecture artifacts
```

## Development

```bash
cd cli && uv run cdre --help
```

Managed with `uv`. Python 3.11+.
