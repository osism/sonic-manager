# SPDX-License-Identifier: Apache-2.0

"""Configuration management for SONiC Manager."""

import os
from typing import Optional


def read_secret(secret_name: str) -> str:
    """Read secret from file."""
    try:
        with open(f"/run/secrets/{secret_name}", "r", encoding="utf-8") as f:
            return f.readline().strip()
    except EnvironmentError:
        return ""


class Config:
    """Configuration class for SONiC Manager."""

    def __init__(self):
        # Redis configuration
        self.REDIS_HOST: str = os.getenv("REDIS_HOST", "redis")
        self.REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
        self.REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))

        # NetBox configuration
        self.NETBOX_URL: Optional[str] = os.getenv(
            "NETBOX_API", os.getenv("NETBOX_URL")
        )
        self.NETBOX_TOKEN: Optional[str] = os.getenv(
            "NETBOX_TOKEN", read_secret("NETBOX_TOKEN")
        )
        self.IGNORE_SSL_ERRORS: bool = os.getenv("IGNORE_SSL_ERRORS", "True") == "True"

        # SONiC specific configuration
        self.NETBOX_FILTER_CONDUCTOR_SONIC: str = os.getenv(
            "NETBOX_FILTER_CONDUCTOR_SONIC",
            "[{'state': 'active', 'tag': ['managed-by-metalbox']}]",
        )

        # SONiC export configuration
        self.SONIC_EXPORT_DIR: str = os.getenv("SONIC_EXPORT_DIR", "/etc/sonic/export")
        self.SONIC_EXPORT_PREFIX: str = os.getenv("SONIC_EXPORT_PREFIX", "osism_")
        self.SONIC_EXPORT_SUFFIX: str = os.getenv("SONIC_EXPORT_SUFFIX", ".json")
        self.SONIC_EXPORT_IDENTIFIER: str = os.getenv(
            "SONIC_EXPORT_IDENTIFIER", "hostname"
        )

        # API configuration
        self.OSISM_API_URL: Optional[str] = os.getenv("OSISM_API_URL", None)


# Global configuration instance
config = Config()
