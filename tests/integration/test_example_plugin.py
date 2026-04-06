"""Tests for Example Plugin Integration (SPEC-023).

Verifies the example plugin can be installed and discovered.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest


class TestExamplePluginDiscovery:
    """Example plugin appears in discovery after installation."""

    @pytest.mark.skip(reason="Requires package installation - run manually")
    def test_example_plugin_discovers_and_loads(self):
        """After install, example plugin appears in discover_adapters()."""
        from commodore.core.plugin_discovery import discover_adapters

        result = discover_adapters()

        # Entry point name from pyproject.toml
        assert "example_dns" in result.adapters
        assert result.errors == []

    @pytest.mark.skip(reason="Requires package installation - run manually")
    def test_example_plugin_adapter_loads(self):
        """Example plugin entry point can be loaded."""
        from commodore.core.plugin_discovery import discover_adapters, load_adapter
        from commodore.ports.driven.dns import DNSPort

        result = discover_adapters()

        if "example_dns" in result.adapters:
            entry_point = result.adapters["example_dns"]
            adapter_class, error = load_adapter(entry_point, DNSPort)

            assert error is None, f"Failed to load: {error}"
            assert adapter_class is not None

            # Can instantiate
            adapter = adapter_class(api_endpoint="https://test.com")
            assert hasattr(adapter, "current_state")
            assert hasattr(adapter, "diff")
            assert hasattr(adapter, "apply")
            assert hasattr(adapter, "health")


class TestExamplePluginStructure:
    """Example plugin has correct structure without installation."""

    def test_pyproject_toml_exists(self):
        """pyproject.toml exists in example directory."""
        example_dir = Path(__file__).parent.parent.parent / "docs" / "examples" / "commodore-plugin-example"
        pyproject_path = example_dir / "pyproject.toml"

        assert pyproject_path.exists()

    def test_pyproject_has_entry_points(self):
        """pyproject.toml declares entry points for commodore.adapters."""
        import tomllib

        example_dir = Path(__file__).parent.parent.parent / "docs" / "examples" / "commodore-plugin-example"
        pyproject_path = example_dir / "pyproject.toml"

        with open(pyproject_path, "rb") as f:
            pyproject = tomllib.load(f)

        assert "project" in pyproject
        assert "entry-points" in pyproject["project"]
        assert "commodore.adapters" in pyproject["project"]["entry-points"]

        entry_points = pyproject["project"]["entry-points"]["commodore.adapters"]
        assert "example_dns" in entry_points

    def test_adapter_module_exists(self):
        """Adapter module exists in src directory."""
        example_dir = Path(__file__).parent.parent.parent / "docs" / "examples" / "commodore-plugin-example"
        init_path = example_dir / "src" / "commodore_plugin_example" / "__init__.py"

        assert init_path.exists()

    def test_adapter_module_exports_class(self):
        """Adapter module exports ExampleDNSAdapter."""
        example_dir = Path(__file__).parent.parent.parent / "docs" / "examples" / "commodore-plugin-example"
        init_path = example_dir / "src" / "commodore_plugin_example" / "__init__.py"

        content = init_path.read_text()
        assert "ExampleDNSAdapter" in content
        assert "class ExampleDNSAdapter" in content

    def test_adapter_implements_dns_port(self):
        """Adapter implements DNSPort protocol methods."""
        example_dir = Path(__file__).parent.parent.parent / "docs" / "examples" / "commodore-plugin-example"
        init_path = example_dir / "src" / "commodore_plugin_example" / "__init__.py"

        content = init_path.read_text()

        # Check for protocol methods
        assert "def current_state" in content
        assert "def diff" in content
        assert "def apply" in content
        assert "def health" in content


class TestPluginDevelopmentGuide:
    """Plugin development guide exists and is complete."""

    def test_guide_exists(self):
        """Plugin development guide exists."""
        guide_path = Path(__file__).parent.parent.parent / "docs" / "docs" / "plugin-development.md"

        assert guide_path.exists()

    def test_guide_covers_entry_points(self):
        """Guide documents entry point declaration."""
        guide_path = Path(__file__).parent.parent.parent / "docs" / "docs" / "plugin-development.md"
        content = guide_path.read_text()

        assert "entry-points" in content.lower()
        assert "commodore.adapters" in content

    def test_guide_covers_port_protocols(self):
        """Guide documents port protocols."""
        guide_path = Path(__file__).parent.parent.parent / "docs" / "docs" / "plugin-development.md"
        content = guide_path.read_text()

        assert "DNSPort" in content
        assert "ReverseProxyPort" in content
        assert "ContainerPort" in content

    def test_guide_covers_testing(self):
        """Guide documents plugin testing."""
        guide_path = Path(__file__).parent.parent.parent / "docs" / "docs" / "plugin-development.md"
        content = guide_path.read_text()

        assert "test" in content.lower()
        assert "pytest" in content.lower() or "test_adapter" in content