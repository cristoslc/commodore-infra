---
id: cis0pm22b-wgf4
status: closed
deps: []
links: []
created: 2026-04-05T03:18:33Z
type: task
priority: 1
assignee: cristos
parent: cis0pm22b-91j6
tags: [spec:SPEC-015]
---
# Extend AdapterRegistry.from_config()

Wire real adapters (Cloudflare, Docker Compose, Caddy) from provider config. Test env:CREDENTIAL resolution, missing env var handling with warning.


## Notes

**2026-04-05T03:28:02Z**

AdapterRegistry.from_provider_config() implemented: wires Cloudflare, Docker Compose, and Caddy adapters from provider config. Supports env:CREDENTIAL resolution with missing env warning. Added provider_for_port() and adapters_for_provider() lookup methods. All tests pass (174 tests).
