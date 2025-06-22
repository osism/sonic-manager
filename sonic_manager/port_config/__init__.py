# SPDX-License-Identifier: Apache-2.0

"""Port configuration files for SONiC devices."""

from pathlib import Path
from typing import Optional, List


def get_port_config_path(hwsku: str) -> Optional[Path]:
    """Get the path to a port configuration file for a specific HWSKU.

    Args:
        hwsku: Hardware SKU name (e.g., 'Accton-AS7326-56X')

    Returns:
        Path to the port config file, or None if not found
    """
    port_config_dir = Path(__file__).parent

    # Try different possible filename formats
    possible_names = [
        f"{hwsku}.ini",
        f"{hwsku.lower()}.ini",
        f"{hwsku.replace('-', '_')}.ini",
        f"{hwsku.lower().replace('-', '_')}.ini",
    ]

    for name in possible_names:
        config_file = port_config_dir / name
        if config_file.exists():
            return config_file

    return None


def list_available_hwskus() -> List[str]:
    """List all available HWSKUs based on port config files.

    Returns:
        List of HWSKU names that have port config files
    """
    port_config_dir = Path(__file__).parent
    hwskus = []

    for config_file in port_config_dir.glob("*.ini"):
        # Extract HWSKU name from filename (remove .ini extension)
        hwsku = config_file.stem
        hwskus.append(hwsku)

    return sorted(hwskus)
