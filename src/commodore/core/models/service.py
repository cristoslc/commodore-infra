"""Service domain model (SPEC-001)."""

from __future__ import annotations

from dataclasses import dataclass, field

from commodore.core.models.classification import SecurityClassification


@dataclass(frozen=True)
class ContainerSpec:
    image: str
    ports: tuple[int, ...]
    volumes: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.image:
            raise ValueError("ContainerSpec requires a non-empty image")
        # Coerce list to tuple for immutability
        if isinstance(self.ports, list):
            object.__setattr__(self, "ports", tuple(self.ports))


@dataclass(frozen=True)
class DNSRecord:
    name: str
    type: str
    target: str


@dataclass(frozen=True)
class IngressRule:
    type: str
    upstream: str
    tls: str = "auto"


@dataclass(frozen=True)
class StorageMount:
    name: str
    path: str
    size: str = ""


@dataclass(frozen=True)
class Service:
    name: str
    classification: SecurityClassification
    container: ContainerSpec
    dns: tuple[DNSRecord, ...] = ()
    ingress: tuple[IngressRule, ...] = ()
    storage: tuple[StorageMount, ...] = ()

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("Service requires a non-empty name")
        # Coerce lists to tuples for immutability
        for attr in ("dns", "ingress", "storage"):
            val = getattr(self, attr)
            if isinstance(val, list):
                object.__setattr__(self, attr, tuple(val))
