# Example Commodore Plugin

This is a minimal example plugin demonstrating how to create a Commodore adapter.

## Installation

```bash
pip install ./docs/examples/commodore-plugin-example
# or
uv pip install ./docs/examples/commodore-plugin-example
```

## Usage

After installation, the plugin is automatically discovered by Commodore:

```yaml
# topology.yaml
providers:
  example:
    api_endpoint: https://api.example.com
    api_token: env:EXAMPLE_API_TOKEN
    ports: [dns]

hosts:
  webserver:
    dns_provider: example
```

## What This Demonstrates

1. **Entry Point Registration**: `pyproject.toml` declares `example_dns` under `[project.entry-points."commodore.adapters"]`

2. **Port Protocol Implementation**: `ExampleDNSAdapter` implements `DNSPort` from `commodore.ports.driven.dns`

3. **Configuration Handling**: The adapter accepts `api_endpoint` and `api_token` parameters

4. **Discovery**: After installation, `commodore.core.plugin_discovery.discover_adapters()` will find this adapter

## Testing the Plugin

```bash
cd docs/examples/commodore-plugin-example
uv run pytest tests/
```

## Creating Your Own Plugin

1. Copy this directory as a template
2. Rename the package (e.g., `commodore_vultr`)
3. Update `pyproject.toml` with your provider details
4. Implement the port protocols you need
5. Add entry points for each adapter
6. Test with `cdre validate`

See the [Plugin Development Guide](../../docs/plugin-development.md) for full documentation.