# SPDX-License-Identifier: Apache-2.0

"""CLI interface for SONiC Manager."""

import click
import sys
from loguru import logger
from typing import Optional

from ..sonic.sync import run
from ..core.config import config


@click.group()
@click.option("--debug", is_flag=True, help="Enable debug logging")
def cli(debug: bool) -> None:
    """SONiC Manager - Standalone SONiC configuration management."""
    if debug:
        logger.remove()
        logger.add(sys.stderr, level="DEBUG")
    else:
        logger.remove()
        logger.add(sys.stderr, level="INFO")


@cli.command()
@click.option("--device", help="Name of specific device to sync")
@click.option("--no-diff", is_flag=True, help="Disable diff output")
def sync(device: Optional[str], no_diff: bool) -> None:
    """Sync SONiC configurations for eligible devices."""
    try:
        show_diff = not no_diff
        result = run(device_name=device, show_diff=show_diff)

        if result:
            click.echo(f"Successfully synced {len(result)} device(s)")
            for device_name, config_data in result.items():
                ports_count = len(config_data.get("PORT", {}))
                click.echo(f"  - {device_name}: {ports_count} ports configured")
        else:
            click.echo("No devices were synced")

    except Exception as e:
        logger.error(f"Sync failed: {e}")
        sys.exit(1)


@cli.command()
@click.option("--output-dir", help="Output directory for config files")
@click.option("--device", help="Name of specific device to export")
def export(output_dir: Optional[str], device: Optional[str]) -> None:
    """Export SONiC configurations to files."""
    try:
        if output_dir:
            # Temporarily override export directory
            original_dir = config.SONIC_EXPORT_DIR
            config.SONIC_EXPORT_DIR = output_dir

        result = run(device_name=device, show_diff=False)

        if output_dir:
            # Restore original directory
            config.SONIC_EXPORT_DIR = original_dir

        if result:
            click.echo(f"Successfully exported {len(result)} device(s)")
            export_dir = output_dir or config.SONIC_EXPORT_DIR
            click.echo(f"Files saved to: {export_dir}")
        else:
            click.echo("No devices were exported")

    except Exception as e:
        logger.error(f"Export failed: {e}")
        sys.exit(1)


@cli.command()
def config_info() -> None:
    """Show current configuration."""
    click.echo("SONiC Manager Configuration:")
    click.echo(f"  NetBox URL: {config.NETBOX_URL}")
    click.echo(f"  NetBox Token: {'***' if config.NETBOX_TOKEN else 'Not set'}")
    click.echo(f"  Export Directory: {config.SONIC_EXPORT_DIR}")
    click.echo(f"  Export Prefix: {config.SONIC_EXPORT_PREFIX}")
    click.echo(f"  Export Suffix: {config.SONIC_EXPORT_SUFFIX}")
    click.echo(f"  Export Identifier: {config.SONIC_EXPORT_IDENTIFIER}")


def main() -> None:
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
