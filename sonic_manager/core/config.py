# SPDX-License-Identifier: Apache-2.0

"""Configuration management for SONiC Manager using Dynaconf."""

import os
from pathlib import Path
from typing import Optional
from dynaconf import Dynaconf


def read_secret(secret_name: str) -> str:
    """Read secret from file."""
    try:
        with open(f"/run/secrets/{secret_name}", "r", encoding="utf-8") as f:
            return f.readline().strip()
    except EnvironmentError:
        return ""


# Get the settings file path relative to this module
settings_path = Path(__file__).parent.parent / "settings.toml"

# Initialize Dynaconf
settings = Dynaconf(
    environments=True,
    envvar_prefix="SONIC_MANAGER",
    settings_files=[str(settings_path)],
    env_switcher="SONIC_MANAGER_ENV",
    load_dotenv=True,
)


class Config:
    """Configuration class for SONiC Manager using Dynaconf."""

    def __init__(self) -> None:
        # NetBox configuration
        self.NETBOX_URL: Optional[str] = (
            os.getenv("NETBOX_API")
            or os.getenv("NETBOX_URL")
            or settings.netbox.url
            or None
        )

        self.NETBOX_TOKEN: Optional[str] = (
            os.getenv("NETBOX_TOKEN")
            or read_secret("NETBOX_TOKEN")
            or settings.netbox.token
            or None
        )

        self.IGNORE_SSL_ERRORS: bool = (
            os.getenv("IGNORE_SSL_ERRORS", "").lower() == "true"
            if os.getenv("IGNORE_SSL_ERRORS")
            else settings.netbox.ignore_ssl_errors
        )

        # SONiC specific configuration
        self.NETBOX_FILTER_CONDUCTOR_SONIC: str = (
            os.getenv("NETBOX_FILTER_CONDUCTOR_SONIC")
            or settings.netbox.filter_conductor_sonic
        )

        # SONiC export configuration
        self.SONIC_EXPORT_DIR: str = (
            os.getenv("SONIC_EXPORT_DIR") or settings.sonic.export_dir
        )

        self.SONIC_EXPORT_PREFIX: str = (
            os.getenv("SONIC_EXPORT_PREFIX") or settings.sonic.export_prefix
        )

        self.SONIC_EXPORT_SUFFIX: str = (
            os.getenv("SONIC_EXPORT_SUFFIX") or settings.sonic.export_suffix
        )

        self.SONIC_EXPORT_IDENTIFIER: str = (
            os.getenv("SONIC_EXPORT_IDENTIFIER") or settings.sonic.export_identifier
        )

        # API configuration
        self.OSISM_API_URL: Optional[str] = (
            os.getenv("OSISM_API_URL") or settings.osism.api_url or None
        )


# Global configuration instance
config = Config()
