"""CLI driving adapter — cdre commands (SPEC-010)."""

from __future__ import annotations

import sys

import click

from commodore.core.config import load_project, load_services, load_topology
from commodore.core.engine import apply_plan, collect_state, compute_diff, generate_plan
from commodore.core.validation import validate_all_placements
from commodore.ports.registry import AdapterRegistry


def _load_and_validate(path: str):
    """Shared loading logic for validate/plan/apply."""
    config = load_project(path)
    topology = load_topology(config.topology_path)
    services = load_services(config)
    return config, topology, services


@click.group()
def app():
    """cdre — Commodore infrastructure platform."""
    pass


@app.command()
@click.argument("path")
def validate(path: str):
    """Validate service definitions against topology."""
    try:
        config, topology, services = _load_and_validate(path)
    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    results = validate_all_placements(services, topology)
    has_errors = False
    for svc_name, errors in results.items():
        if errors:
            has_errors = True
            for err in errors:
                click.echo(f"  {err.severity}: {err.message}")

    if has_errors:
        sys.exit(1)
    else:
        click.echo("Validation OK — all placements valid.")


@app.command()
@click.argument("path")
def plan(path: str):
    """Show what would change."""
    try:
        config, topology, services = _load_and_validate(path)
    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    registry = AdapterRegistry.from_config({"dns": {"type": "in_memory"}, "container": {"type": "in_memory"}, "reverse_proxy": {"type": "in_memory"}})
    state = collect_state(registry)
    changes = compute_diff(state, services, registry)
    p = generate_plan(changes, topology)
    click.echo(p.format())


@app.command()
@click.argument("path")
def apply(path: str):
    """Apply changes to infrastructure."""
    try:
        config, topology, services = _load_and_validate(path)
    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    registry = AdapterRegistry.from_config({"dns": {"type": "in_memory"}, "container": {"type": "in_memory"}, "reverse_proxy": {"type": "in_memory"}})
    state = collect_state(registry)
    changes = compute_diff(state, services, registry)
    p = generate_plan(changes, topology)
    result = apply_plan(p, registry)

    if result.success:
        click.echo(f"Apply complete: {result.steps_succeeded} changes applied.")
    else:
        click.echo(f"Apply failed: {result.steps_succeeded} succeeded, {result.steps_failed} failed.", err=True)
        for err in result.errors:
            click.echo(f"  {err}", err=True)
        sys.exit(2)


@app.command()
def status():
    """Show current service placement and health."""
    click.echo("Status: no services deployed (in-memory adapters).")
