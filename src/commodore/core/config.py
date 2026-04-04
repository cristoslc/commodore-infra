"""Config discovery and YAML loading (SPEC-011)."""

from __future__ import annotations

import glob
import os
from dataclasses import dataclass, field
from typing import Any

from ruamel.yaml import YAML

from commodore.core.models.classification import SecurityClassification
from commodore.core.models.host import Host
from commodore.core.models.segment import NetworkSegment
from commodore.core.models.service import ContainerSpec, DNSRecord, IngressRule, Service, StorageMount
from commodore.core.models.topology import Topology

yaml = YAML()


@dataclass(frozen=True)
class ProjectConfig:
    root: str
    topology_path: str
    service_patterns: list[str] = field(default_factory=list)


def load_project(path: str) -> ProjectConfig:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Project file not found: {path}")

    with open(path) as f:
        data = yaml.load(f)

    root = os.path.dirname(os.path.abspath(path))
    topology_path = os.path.join(root, data["topology"])
    service_patterns = [os.path.join(root, p) for p in data.get("services", [])]

    return ProjectConfig(root=root, topology_path=topology_path, service_patterns=service_patterns)


def load_topology(path: str) -> Topology:
    with open(path) as f:
        data = yaml.load(f)

    # Parse segments
    segments = []
    if "segments" in data:
        for name, info in data["segments"].items():
            segments.append(
                NetworkSegment(
                    name=name,
                    cidr=info.get("cidr", ""),
                    reachable_from=frozenset(info.get("reachable_from", [])),
                )
            )

    # Parse hosts
    hosts = []
    for name, info in data["hosts"].items():
        host_segments = frozenset(info["segments"]) if "segments" in info else frozenset({"default"})
        hosts.append(
            Host(
                name=name,
                address=info["address"],
                roles=frozenset(info.get("roles", [])),
                classification=SecurityClassification(info["classification"]),
                segments=host_segments,
            )
        )
    return Topology(hosts=tuple(hosts), segments=tuple(segments))


def _parse_service(data: dict[str, Any]) -> Service:
    container_data = data["container"]
    container = ContainerSpec(
        image=container_data["image"],
        ports=container_data.get("ports", []),
        volumes=container_data.get("volumes", {}),
    )

    dns_records = []
    if "dns" in data and "records" in data["dns"]:
        for rec in data["dns"]["records"]:
            dns_records.append(DNSRecord(name=rec["name"], type=rec["type"], target=rec["target"]))

    ingress_rules = []
    if "ingress" in data:
        for ingress_type, ingress_config in data["ingress"].items():
            ingress_rules.append(
                IngressRule(
                    type=ingress_type,
                    upstream=ingress_config.get("upstream", ""),
                    tls=ingress_config.get("tls", "auto"),
                )
            )

    storage_mounts = []
    if "storage" in data:
        for mount in data["storage"]:
            storage_mounts.append(
                StorageMount(name=mount["name"], path=mount["path"], size=mount.get("size", ""))
            )

    return Service(
        name=data["name"],
        classification=SecurityClassification(data["classification"]),
        container=container,
        dns=dns_records,
        ingress=ingress_rules,
        storage=storage_mounts,
    )


def load_services(config: ProjectConfig) -> list[Service]:
    services = []
    for pattern in config.service_patterns:
        for filepath in sorted(glob.glob(pattern)):
            with open(filepath) as f:
                data = yaml.load(f)
            services.append(_parse_service(data))
    return services
