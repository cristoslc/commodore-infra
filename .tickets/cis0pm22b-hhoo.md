---
id: cis0pm22b-hhoo
status: closed
deps: []
links: []
created: 2026-04-05T03:18:26Z
type: task
priority: 1
assignee: cristos
parent: cis0pm22b-91j6
tags: [spec:SPEC-015]
---
# Define Provider dataclass

TDD: Provider dataclass with name, credential_ref, port_types. Test round-trip construction and lookup.


## Notes

**2026-04-05T03:20:39Z**

Provider dataclass implemented with name, credential_ref, port_types. Tests pass: creation, immutability, credential resolution (env:, direct, None), port type checking.
