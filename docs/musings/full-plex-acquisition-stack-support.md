# Musing: Supporting the full Plex/acquisition stack vs. just Plex

**Date:** 2026-08-13
**Status:** Idea — not yet a plan
**Trigger:** Diagnosed a multi-hour Plex outage. Root cause: Kometa (`KOMETA_RUN=true` + `restart: unless-stopped`) crash-looped and re-ran a 1050-show scan every few minutes, starving Plex. The fix was a one-line edit to a compose file that lives only on the Thor server — untracked, unreviewable, no audit trail. The Homelab repo's VISION-002 reframes this repo as Commodore instance config, but the media stack is nowhere near being Commodore-declared. This musing maps the gap between "one service (Plex)" and "the whole acquisition stack."

## The two shapes to compare

**Shape A — a single Plex service.** One `Service` in Commodore: workload (linuxserver/plex image, /config volume, /media mount), a reverse-proxy site, maybe a DNS record. This is the easy, well-covered case — it's basically what SPEC-010/EPIC-001 assumed ("ingest Plex as proof").

**Shape B — the full acquisition stack.** The live stack on Thor's Docker VM:

| Container | Role | Lab CLI today? |
|---|---|---|
| plex | Media server | no |
| sonarr | TV acquisition | no |
| radarr | Movie acquisition | no |
| prowlarr | Indexer aggregator | no |
| bazarr | Subtitle management | no |
| nzbget | Usenet downloader | no |
| qbittorrent | Torrent downloader | no |
| gluetun | VPN gateway (WireGuard) | no |
| seerr (jellyseerr) | Discovery/request UI | no |
| tautulli | Plex monitoring | no |
| unpackerr | Post-download extraction | no |
| kometa | Metadata manager | no |
| caddy-reverse-proxy | Ingress | **yes — `lab caddy`** |

None of the acquisition services are lab-managed today (no compose in the Homelab repo). The only overlap with lab CLI is **Caddy** (`lab caddy apply/diff/import`), which per VISION-002 migrates to Commodore as the SSH+Caddy ReverseProxyPort adapter — so its instance config (sites.yaml) moves over but stays as-is.

## Why Shape B is materially harder than Shape A

### 1. Shared network namespace (Gluetun) — the Stack concept

gluetun is the VPN gateway; nzbget/qbittorrent route through it via the same Docker network. This is exactly what Commodore's **Stack** model is for (same-host affinity + shared network namespace). But it means the acquisition services are *not independent units* — they have a hard placement coupling (all on the Docker VM, all sharing gluetun's network). Shape A (Plex alone) never exercises Stack.

### 2. Service-to-service dependencies, not just placement

sonarr/radarr → prowlarr → indexers; sonarr/radarr → download clients (nzbget/qbittorrent) → unpackerr → post-processing → Plex scan. Commodore's Service model has "network peers" but the current design doesn't model the *orchestrated data flow* (who calls whom, in what order, with what backpressure). The acquisition stack is a pipeline, not a set of peers.

### 3. Shared volumes + NFS storage bus

All services mount from the NFS share (`lab2_media`, `lab2_downloads`). Commodore's storage-bus locality model (NFS server on same LAN as clients) handles *reachability*, but the acquisition stack has **shared write paths** — sonarr/radarr write to the same downloads tree, unpackerr extracts into it, plex reads from it. The current volume model is per-service; the pipeline shares volumes across services with cross-service contention (the kind of thing that actually caused this outage: NFS read/write contention during Kometa's scan).

### 4. The VPN/routing concern

gluetun is a *network provider* for other services, not a typical workload. Commodore has no concept of "a service that provides the network for peers." Whether that's a Stack-level property or a new port (a VPNProviderPort?) is an open design question. The Homelab routing chain (Cloudflare → bastion HAProxy → Thor Caddy → service) also has the LB/ingress adapters, but the *VPN egress* layer is new territory.

### 5. Secrets density

Every service has API keys/tokens: sonarr/radarr API keys, prowlarr indexer creds, trakt (kometa), downloader passwords. The Homelab repo's `lab creds` (1Password) handles credential lifecycle today and migrates to Commodore as the SecretPort. But the acquisition stack needs *many* per-service secrets wired into each workload's env — the SecretPort must be able to resolve a full set, not one credential. This is the config-dirs-as-code blocker from the Homelab media-stack musing.

### 6. Job-shaped services (Kometa)

Kometa is a one-shot job (runs at 03:00, exits) — not a long-running daemon. Commodore's Service model assumes long-running workloads. A job/cron workload type (or a `schedule:` field) is missing. This is exactly the shape whose misconfiguration caused the outage.

## What "supporting the full stack" concretely requires

Against Commodore's current v1 adapters (DNS, SSH+Caddy, SSH+HAProxy, Docker Compose, 1Password):

- **ContainerPort (Docker Compose) is the crux.** Compose must deploy *the whole stack as one project* (`lab2`) with shared volumes and the gluetun network, not one service at a time. The SPEC-013 compose adapter needs a **stack-level deploy** that handles: shared networks, shared volumes, depends_on ordering, and the gluetun network namespace.
- **A job/scheduled workload type** for Kometa (and any cron-shaped service), so a run-once-then-exit container isn't mis-scheduled as a daemon.
- **Volume/shared-write modeling** — volumes shared across services with write contention, on top of the existing storage-bus reachability.
- **A service-to-service dependency/ordering model** for the pipeline (sonarr→prowlarr→client→unpackerr→plex).
- **VPN/egress as a first-class concern** (gluetun as a network provider for peers), distinct from public ingress.
- **Batch secret resolution** through SecretPort for the many per-service credentials.
- **Classification policy for the whole stack** — Plex+acquisition is Operational-class, but the pipeline has shared write access and a VPN egress that raises the taint surface. The classified-placement model should force "all acquisition services co-located on the Docker VM, never on a Custodial host" structurally.

## The honest sizing

Supporting just Plex (Shape A) is a well-scoped first slice and exercises ContainerPort, ReverseProxyPort, SecretPort, and a single classification. The full acquisition stack (Shape B) is a much larger surface: it forces Stack (shared network), job workloads, shared-volume modeling, dependency ordering, and VPN egress — roughly 5 new domain-model capabilities, several of which (job workloads, VPN provider, pipeline deps) aren't even sketched in the current architecture docs.

The pragmatic path is probably Shape A first (proves the compose adapter + instance-config loop end-to-end with one service), then Shape B as a follow-on that explicitly adds the Stack + job + shared-volume + VPN pieces — rather than trying to model the whole pipeline on day one.

## Open questions

- Is the gluetun network namespace a Stack property, or a new "network provider service" concept?
- Should Kometa be a job workload type, or a scheduled daemon that sleeps (the `KOMETA_RUN=false` fix)? The latter sidesteps the model gap but keeps a "job" mis-shaped as a daemon.
- Does shared-write volume contention belong in the domain model, or is it out of scope for placement (operator-managed)?
- How much of the pipeline ordering is Commodore's job vs. the compose file's `depends_on`? If compose already expresses it, Commodore just needs to deploy the stack as-is (SPEC-013 stack-level deploy), not re-model the pipeline.
