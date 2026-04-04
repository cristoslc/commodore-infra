"""Tests for core domain models (SPEC-001): Service, Host, Topology."""

from __future__ import annotations

import pytest
from commodore.core.models.service import Service, ContainerSpec, DNSRecord, IngressRule, StorageMount
from commodore.core.models.host import Host
from commodore.core.models.topology import Topology
from commodore.core.models.classification import SecurityClassification


class TestService:
    def test_create_minimal_service(self):
        svc = Service(
            name="jellyseerr",
            classification=SecurityClassification.AUTHENTICATED,
            container=ContainerSpec(
                image="fallenbagel/jellyseerr:latest",
                ports=[5055],
            ),
        )
        assert svc.name == "jellyseerr"
        assert svc.classification == SecurityClassification.AUTHENTICATED
        assert svc.container.image == "fallenbagel/jellyseerr:latest"

    def test_create_full_service(self):
        svc = Service(
            name="jellyseerr",
            classification=SecurityClassification.AUTHENTICATED,
            container=ContainerSpec(
                image="fallenbagel/jellyseerr:latest",
                ports=[5055],
                volumes={"config": "/app/config"},
            ),
            dns=[
                DNSRecord(name="requests.example.com", type="CNAME", target="proxy.example.com"),
            ],
            ingress=[
                IngressRule(
                    type="reverse_proxy",
                    upstream="http://nas:5055",
                    tls="auto",
                ),
            ],
            storage=[
                StorageMount(name="config", path="/app/config", size="1Gi"),
            ],
        )
        assert len(svc.dns) == 1
        assert len(svc.ingress) == 1
        assert len(svc.storage) == 1
        assert svc.dns[0].name == "requests.example.com"

    def test_service_is_frozen(self):
        svc = Service(
            name="test",
            classification=SecurityClassification.PUBLIC,
            container=ContainerSpec(image="test:latest", ports=[80]),
        )
        with pytest.raises(AttributeError):
            svc.name = "changed"

    def test_service_name_required(self):
        with pytest.raises((TypeError, ValueError)):
            Service(
                name="",
                classification=SecurityClassification.PUBLIC,
                container=ContainerSpec(image="test:latest", ports=[80]),
            )

    def test_container_spec_requires_image(self):
        with pytest.raises((TypeError, ValueError)):
            ContainerSpec(image="", ports=[80])


class TestHost:
    def test_create_host(self):
        host = Host(
            name="nas",
            address="10.0.0.10",
            roles=frozenset({"container", "storage"}),
            classification=SecurityClassification.INTERNAL,
        )
        assert host.name == "nas"
        assert "container" in host.roles
        assert host.classification == SecurityClassification.INTERNAL

    def test_host_is_frozen(self):
        host = Host(
            name="proxy",
            address="10.0.0.1",
            roles=frozenset({"reverse-proxy"}),
            classification=SecurityClassification.INTERNAL,
        )
        with pytest.raises(AttributeError):
            host.name = "changed"

    def test_host_name_required(self):
        with pytest.raises((TypeError, ValueError)):
            Host(
                name="",
                address="10.0.0.1",
                roles=frozenset({"container"}),
                classification=SecurityClassification.INTERNAL,
            )


class TestTopology:
    def _make_topology(self) -> Topology:
        hosts = [
            Host(
                name="nas",
                address="10.0.0.10",
                roles=frozenset({"container", "storage"}),
                classification=SecurityClassification.INTERNAL,
            ),
            Host(
                name="proxy",
                address="10.0.0.1",
                roles=frozenset({"reverse-proxy", "load-balancer"}),
                classification=SecurityClassification.INTERNAL,
            ),
        ]
        return Topology(hosts=tuple(hosts))

    def test_lookup_by_name(self):
        topo = self._make_topology()
        host = topo.get_host("nas")
        assert host is not None
        assert host.address == "10.0.0.10"

    def test_lookup_missing_host(self):
        topo = self._make_topology()
        assert topo.get_host("nonexistent") is None

    def test_lookup_by_role(self):
        topo = self._make_topology()
        container_hosts = topo.hosts_with_role("container")
        assert len(container_hosts) == 1
        assert container_hosts[0].name == "nas"

    def test_topology_is_frozen(self):
        topo = self._make_topology()
        with pytest.raises(AttributeError):
            topo.hosts = ()

    def test_duplicate_host_names_rejected(self):
        host = Host(
            name="dup",
            address="10.0.0.1",
            roles=frozenset({"container"}),
            classification=SecurityClassification.INTERNAL,
        )
        with pytest.raises(ValueError, match="Duplicate host name"):
            Topology(hosts=(host, host))
