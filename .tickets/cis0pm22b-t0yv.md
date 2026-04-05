---
id: cis0pm22b-t0yv
status: closed
deps: []
links: []
created: 2026-04-05T03:18:34Z
type: task
priority: 1
assignee: cristos
parent: cis0pm22b-91j6
tags: [spec:SPEC-015]
---
# Add provider lookup methods

Add provider_for_port(port_name) and adapters_for_provider(provider_name) methods. Test cross-port grouping (e.g., cloudflare->[dns, reverse_proxy]).


## Notes

**2026-04-05T03:28:13Z**

provider_for_port() and adapters_for_provider() methods were implemented in task 3. Tests already verify: test_provider_for_port, test_provider_for_port_not_found, test_adapters_for_provider, test_adapters_for_provider_not_found.
