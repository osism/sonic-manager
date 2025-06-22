# SPDX-License-Identifier: Apache-2.0

"""NetBox client for SONiC Manager."""

from typing import Optional, Any, Dict, List
import json
import urllib3
import pynetbox
from loguru import logger

from .config import config


def get_netbox_connection(
    netbox_url: Optional[str],
    netbox_token: Optional[str],
    ignore_ssl_errors: bool = False,
) -> Optional[pynetbox.api]:
    """Create NetBox API connection."""
    if netbox_url and netbox_token:
        nb = pynetbox.api(netbox_url, token=netbox_token)

        if ignore_ssl_errors and nb:
            import requests

            urllib3.disable_warnings()
            session = requests.Session()
            session.verify = False
            nb.http_session = session

        return nb

    return None


class NetBoxClient:
    """NetBox client wrapper."""

    def __init__(self) -> None:
        self.nb = get_netbox_connection(
            config.NETBOX_URL, config.NETBOX_TOKEN, config.IGNORE_SSL_ERRORS
        )

    def get_nb_device_query_list_sonic(self) -> List[Dict[str, Any]]:
        """Get NetBox device query list for SONiC devices."""
        try:
            result = json.loads(config.NETBOX_FILTER_CONDUCTOR_SONIC)
            return result
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing NETBOX_FILTER_CONDUCTOR_SONIC: {e}")
            return [{"state": "active", "tag": ["managed-by-metalbox"]}]

    def get_device_loopbacks(self, device: Any) -> List[Any]:
        """Get loopback interfaces for a device."""
        if not self.nb:
            return []

        try:
            return list(
                self.nb.dcim.interfaces.filter(device_id=device.id, name__ic="loopback")
            )
        except Exception as e:
            logger.error(f"Error getting loopbacks for device {device.name}: {e}")
            return []

    def get_device_oob_ip(self, device: Any) -> Optional[str]:
        """Get out-of-band IP address for a device."""
        if not self.nb:
            return None

        try:
            # Look for management interface IP
            interfaces = self.nb.dcim.interfaces.filter(
                device_id=device.id, mgmt_only=True
            )
            for interface in interfaces:
                ip_addresses = self.nb.ipam.ip_addresses.filter(
                    assigned_object_id=interface.id
                )
                for ip in ip_addresses:
                    return str(ip.address).split("/")[0]
        except Exception as e:
            logger.error(f"Error getting OOB IP for device {device.name}: {e}")

        return None

    def get_device_vlans(self, device: Any) -> List[Any]:
        """Get VLANs associated with a device."""
        if not self.nb:
            return []

        try:
            # Get interfaces for the device
            interfaces = self.nb.dcim.interfaces.filter(device_id=device.id)
            vlans = []

            for interface in interfaces:
                if interface.untagged_vlan:
                    vlans.append(interface.untagged_vlan)
                if interface.tagged_vlans:
                    vlans.extend(interface.tagged_vlans)

            return list(set(vlans))  # Remove duplicates
        except Exception as e:
            logger.error(f"Error getting VLANs for device {device.name}: {e}")
            return []


# Global NetBox client instance
netbox_client = NetBoxClient()
