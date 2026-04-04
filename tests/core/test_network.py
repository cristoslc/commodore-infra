"""Tests for network segment model and reachability."""

from __future__ import annotations

import pytest
from commodore.core.models.segment import NetworkSegment
from commodore.core.models.host import Host
from commodore.core.models.topology import Topology
from commodore.core.models.classification import SecurityClassification
from commodore.core.models.service import Service, ContainerSpec, IngressRule
from commodore.core.validation import validate_placement


def _host(name: str, segments: frozenset[str] = frozenset({"default"}), roles: frozenset[str] = frozenset({"container"})) -> Host:
    return Host(name=name, address="10.0.0.1", roles=roles, classification=SecurityClassification.INTERNAL, segments=segments)


def _svc(name: str = "test-svc", upstream: str | None = None) -> Service:
    ingress = [IngressRule(type="reverse_proxy", upstream=upstream, tls="auto")] if upstream else []
    return Service(
        name=name,
        classification=SecurityClassification.INTERNAL,
        container=ContainerSpec(image="test:latest", ports=[80]),
        ingress=ingress,
    )


class TestNetworkSegment:
    def test_create_segment(self):
        seg = NetworkSegment(name="services", cidr="10.0.10.0/24")
        assert seg.name == "services"
        assert seg.cidr == "10.0.10.0/24"
        assert seg.reachable_from == frozenset()

    def test_segment_with_reachability(self):
        seg = NetworkSegment(name="dmz", cidr="10.0.30.0/24", reachable_from=frozenset({"services"}))
        assert "services" in seg.reachable_from

    def test_segment_is_frozen(self):
        seg = NetworkSegment(name="test")
        with pytest.raises(AttributeError):
            seg.name = "changed"

    def test_segment_name_required(self):
        with pytest.raises(ValueError):
            NetworkSegment(name="")


class TestHostSegments:
    def test_host_default_segment(self):
        host = Host(name="h", address="10.0.0.1", roles=frozenset({"container"}), classification=SecurityClassification.INTERNAL)
        assert host.segments == frozenset({"default"})

    def test_host_explicit_segments(self):
        host = _host("nas", segments=frozenset({"services", "management"}))
        assert "services" in host.segments
        assert "management" in host.segments

    def test_host_multi_segment(self):
        host = _host("proxy", segments=frozenset({"dmz", "services"}))
        assert len(host.segments) == 2


class TestCanReach:
    def test_same_segment_reachable(self):
        h1 = _host("a", segments=frozenset({"services"}))
        h2 = _host("b", segments=frozenset({"services"}))
        topo = Topology(hosts=(h1, h2), segments=(NetworkSegment(name="services"),))
        assert topo.can_reach(h1, h2)

    def test_different_segment_unreachable(self):
        h1 = _host("a", segments=frozenset({"services"}))
        h2 = _host("b", segments=frozenset({"iot"}))
        topo = Topology(
            hosts=(h1, h2),
            segments=(NetworkSegment(name="services"), NetworkSegment(name="iot")),
        )
        assert not topo.can_reach(h1, h2)

    def test_directed_reachability(self):
        """DMZ can reach services (reachable_from), but not the reverse."""
        h_dmz = _host("proxy", segments=frozenset({"dmz"}))
        h_svc = _host("nas", segments=frozenset({"services"}))
        topo = Topology(
            hosts=(h_dmz, h_svc),
            segments=(
                NetworkSegment(name="dmz"),
                NetworkSegment(name="services", reachable_from=frozenset({"dmz"})),
            ),
        )
        # DMZ host can reach services host (dmz is in services.reachable_from)
        assert topo.can_reach(h_dmz, h_svc)
        # Services host cannot reach DMZ host (services is NOT in dmz.reachable_from)
        assert not topo.can_reach(h_svc, h_dmz)

    def test_multi_homed_host_reachable(self):
        """A host on both services and management can reach both segments."""
        h_multi = _host("nas", segments=frozenset({"services", "management"}))
        h_mgmt = _host("admin", segments=frozenset({"management"}))
        h_svc = _host("app", segments=frozenset({"services"}))
        topo = Topology(
            hosts=(h_multi, h_mgmt, h_svc),
            segments=(NetworkSegment(name="services"), NetworkSegment(name="management")),
        )
        assert topo.can_reach(h_multi, h_mgmt)
        assert topo.can_reach(h_multi, h_svc)
        assert topo.can_reach(h_mgmt, h_multi)

    def test_self_always_reachable(self):
        h = _host("a", segments=frozenset({"services"}))
        topo = Topology(hosts=(h,), segments=(NetworkSegment(name="services"),))
        assert topo.can_reach(h, h)

    def test_default_segment_all_reachable(self):
        """Backward compat: hosts on 'default' segment can reach each other."""
        h1 = _host("a")
        h2 = _host("b")
        topo = Topology(hosts=(h1, h2))
        assert topo.can_reach(h1, h2)


class TestHostsOnSegment:
    def test_filter_by_segment(self):
        h1 = _host("a", segments=frozenset({"services"}))
        h2 = _host("b", segments=frozenset({"iot"}))
        h3 = _host("c", segments=frozenset({"services", "management"}))
        topo = Topology(hosts=(h1, h2, h3))
        svc_hosts = topo.hosts_on_segment("services")
        assert len(svc_hosts) == 2
        names = {h.name for h in svc_hosts}
        assert names == {"a", "c"}


class TestNetworkReachabilityValidation:
    def test_reachable_upstream_passes(self):
        proxy = _host("proxy", segments=frozenset({"dmz"}), roles=frozenset({"container"}))
        nas = _host("nas", segments=frozenset({"services"}))
        svc = _svc(upstream="http://nas:5055")
        topo = Topology(
            hosts=(proxy, nas),
            segments=(
                NetworkSegment(name="dmz"),
                NetworkSegment(name="services", reachable_from=frozenset({"dmz"})),
            ),
        )
        errors = validate_placement(svc, proxy, topo)
        assert not any(e.rule == "network_reachability" for e in errors)

    def test_unreachable_upstream_fails(self):
        iot_host = _host("camera", segments=frozenset({"iot"}), roles=frozenset({"container"}))
        nas = _host("nas", segments=frozenset({"services"}))
        svc = _svc(upstream="http://nas:5055")
        topo = Topology(
            hosts=(iot_host, nas),
            segments=(NetworkSegment(name="iot"), NetworkSegment(name="services")),
        )
        errors = validate_placement(svc, iot_host, topo)
        assert any(e.rule == "network_reachability" for e in errors)

    def test_no_ingress_skips_check(self):
        """Services without ingress rules skip reachability check."""
        h = _host("nas", segments=frozenset({"services"}))
        svc = _svc()  # no upstream
        topo = Topology(hosts=(h,), segments=(NetworkSegment(name="services"),))
        errors = validate_placement(svc, h, topo)
        assert not any(e.rule == "network_reachability" for e in errors)

    def test_upstream_host_not_in_topology_warns(self):
        """Upstream references a hostname not in topology."""
        h = _host("proxy", segments=frozenset({"dmz"}))
        svc = _svc(upstream="http://unknown-host:8080")
        topo = Topology(hosts=(h,), segments=(NetworkSegment(name="dmz"),))
        errors = validate_placement(svc, h, topo)
        assert any(e.rule == "network_reachability" for e in errors)
