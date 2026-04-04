"""Tests for config discovery and YAML loading (SPEC-011)."""

from __future__ import annotations

import os
import tempfile

import pytest
from commodore.core.models.classification import SecurityClassification
from commodore.core.config import load_project, load_services, load_topology, ProjectConfig


class TestProjectConfig:
    def test_load_project(self, tmp_path):
        cdre_yaml = tmp_path / "cdre.yaml"
        cdre_yaml.write_text("topology: topology.yaml\nservices:\n  - services/*.yaml\n")
        config = load_project(str(cdre_yaml))
        assert config.topology_path == str(tmp_path / "topology.yaml")
        assert len(config.service_patterns) == 1

    def test_missing_project_file(self):
        with pytest.raises(FileNotFoundError):
            load_project("/nonexistent/cdre.yaml")


class TestLoadTopology:
    def test_load_topology(self, tmp_path):
        topo_yaml = tmp_path / "topology.yaml"
        topo_yaml.write_text(
            "hosts:\n"
            "  nas:\n"
            "    address: 10.0.0.10\n"
            "    roles:\n"
            "      - container\n"
            "      - storage\n"
            "    classification: internal\n"
            "  proxy:\n"
            "    address: 10.0.0.1\n"
            "    roles:\n"
            "      - reverse-proxy\n"
            "    classification: internal\n"
        )
        topo = load_topology(str(topo_yaml))
        assert topo.get_host("nas") is not None
        assert topo.get_host("proxy") is not None
        assert topo.get_host("nas").classification == SecurityClassification.INTERNAL


class TestLoadServices:
    def test_load_service(self, tmp_path):
        svc_dir = tmp_path / "services"
        svc_dir.mkdir()
        svc_file = svc_dir / "jellyseerr.yaml"
        svc_file.write_text(
            "name: jellyseerr\n"
            "classification: authenticated\n"
            "container:\n"
            "  image: fallenbagel/jellyseerr:latest\n"
            "  ports:\n"
            "    - 5055\n"
        )
        config = ProjectConfig(
            root=str(tmp_path),
            topology_path=str(tmp_path / "topology.yaml"),
            service_patterns=[str(svc_dir / "*.yaml")],
        )
        services = load_services(config)
        assert len(services) == 1
        assert services[0].name == "jellyseerr"
        assert services[0].classification == SecurityClassification.AUTHENTICATED

    def test_load_service_with_dns_and_ingress(self, tmp_path):
        svc_dir = tmp_path / "services"
        svc_dir.mkdir()
        svc_file = svc_dir / "jellyseerr.yaml"
        svc_file.write_text(
            "name: jellyseerr\n"
            "classification: authenticated\n"
            "container:\n"
            "  image: fallenbagel/jellyseerr:latest\n"
            "  ports:\n"
            "    - 5055\n"
            "  volumes:\n"
            "    config: /app/config\n"
            "dns:\n"
            "  records:\n"
            "    - name: requests.example.com\n"
            "      type: CNAME\n"
            "      target: proxy.example.com\n"
            "ingress:\n"
            "  reverse_proxy:\n"
            "    upstream: http://nas:5055\n"
            "    tls: auto\n"
        )
        config = ProjectConfig(
            root=str(tmp_path),
            topology_path=str(tmp_path / "topology.yaml"),
            service_patterns=[str(svc_dir / "*.yaml")],
        )
        services = load_services(config)
        svc = services[0]
        assert len(svc.dns) == 1
        assert svc.dns[0].name == "requests.example.com"
        assert len(svc.ingress) == 1

    def test_glob_pattern_matches_multiple(self, tmp_path):
        svc_dir = tmp_path / "services"
        svc_dir.mkdir()
        for name in ["alpha", "beta"]:
            f = svc_dir / f"{name}.yaml"
            f.write_text(f"name: {name}\nclassification: public\ncontainer:\n  image: {name}:latest\n  ports:\n    - 80\n")
        config = ProjectConfig(
            root=str(tmp_path),
            topology_path=str(tmp_path / "topology.yaml"),
            service_patterns=[str(svc_dir / "*.yaml")],
        )
        services = load_services(config)
        assert len(services) == 2
