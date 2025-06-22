# SPDX-License-Identifier: Apache-2.0

"""NetBox compatibility functions for SONiC Manager."""

from typing import Any, List, Optional
from .netbox_client import netbox_client


def get_nb_device_query_list_sonic() -> List[dict]:
    """Get NetBox device query list for SONiC devices."""
    return netbox_client.get_nb_device_query_list_sonic()


def get_device_loopbacks(device: Any) -> List[Any]:
    """Get loopback interfaces for a device."""
    return netbox_client.get_device_loopbacks(device)


def get_device_oob_ip(device: Any) -> Optional[str]:
    """Get out-of-band IP address for a device."""
    return netbox_client.get_device_oob_ip(device)


def get_device_vlans(device: Any) -> List[Any]:
    """Get VLANs associated with a device."""
    return netbox_client.get_device_vlans(device)
