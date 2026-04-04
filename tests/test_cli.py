"""Tests for CLI commands (SPEC-010)."""

from __future__ import annotations

from click.testing import CliRunner
from commodore.cli import app


def _write_project(tmp_path):
    """Write a minimal project with one service and topology."""
    cdre = tmp_path / "cdre.yaml"
    cdre.write_text("topology: topology.yaml\nservices:\n  - services/*.yaml\n")

    topo = tmp_path / "topology.yaml"
    topo.write_text(
        "hosts:\n"
        "  nas:\n"
        "    address: 10.0.0.10\n"
        "    roles:\n"
        "      - container\n"
        "    classification: internal\n"
    )

    svc_dir = tmp_path / "services"
    svc_dir.mkdir()
    svc = svc_dir / "test.yaml"
    svc.write_text(
        "name: test-svc\n"
        "classification: public\n"
        "container:\n"
        "  image: test:latest\n"
        "  ports:\n"
        "    - 80\n"
    )
    return str(cdre)


class TestValidateCommand:
    def test_validate_valid_project(self, tmp_path):
        path = _write_project(tmp_path)
        runner = CliRunner()
        result = runner.invoke(app, ["validate", path])
        assert result.exit_code == 0
        assert "valid" in result.output.lower() or "ok" in result.output.lower()

    def test_validate_missing_file(self):
        runner = CliRunner()
        result = runner.invoke(app, ["validate", "/nonexistent/cdre.yaml"])
        assert result.exit_code != 0

    def test_validate_classification_violation(self, tmp_path):
        cdre = tmp_path / "cdre.yaml"
        cdre.write_text("topology: topology.yaml\nservices:\n  - services/*.yaml\n")
        topo = tmp_path / "topology.yaml"
        topo.write_text(
            "hosts:\n"
            "  edge:\n"
            "    address: 10.0.0.1\n"
            "    roles:\n"
            "      - container\n"
            "    classification: public\n"
        )
        svc_dir = tmp_path / "services"
        svc_dir.mkdir()
        svc = svc_dir / "secret.yaml"
        svc.write_text(
            "name: secret-svc\n"
            "classification: custodial\n"
            "container:\n"
            "  image: secret:latest\n"
            "  ports:\n"
            "    - 443\n"
        )
        runner = CliRunner()
        result = runner.invoke(app, ["validate", str(cdre)])
        assert result.exit_code == 1
        assert "custodial" in result.output.lower() or "classification" in result.output.lower()


class TestPlanCommand:
    def test_plan_shows_changes(self, tmp_path):
        path = _write_project(tmp_path)
        runner = CliRunner()
        result = runner.invoke(app, ["plan", path])
        assert result.exit_code == 0
        assert "plan" in result.output.lower() or "create" in result.output.lower()

    def test_plan_missing_file(self):
        runner = CliRunner()
        result = runner.invoke(app, ["plan", "/nonexistent/cdre.yaml"])
        assert result.exit_code != 0


class TestApplyCommand:
    def test_apply_succeeds(self, tmp_path):
        path = _write_project(tmp_path)
        runner = CliRunner()
        result = runner.invoke(app, ["apply", path])
        assert result.exit_code == 0

    def test_apply_missing_file(self):
        runner = CliRunner()
        result = runner.invoke(app, ["apply", "/nonexistent/cdre.yaml"])
        assert result.exit_code != 0


class TestStatusCommand:
    def test_status_runs(self):
        runner = CliRunner()
        result = runner.invoke(app, ["status"])
        assert result.exit_code == 0


class TestHelp:
    def test_main_help(self):
        runner = CliRunner()
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "validate" in result.output
        assert "plan" in result.output
        assert "apply" in result.output

    def test_validate_help(self):
        runner = CliRunner()
        result = runner.invoke(app, ["validate", "--help"])
        assert result.exit_code == 0
