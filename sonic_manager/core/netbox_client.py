# SPDX-License-Identifier: Apache-2.0

"""NetBox client for SONiC Manager."""

import time
from typing import Optional, Any, Dict, List
import json
import urllib3
import pynetbox
from loguru import logger
from redis import Redis

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

    def __init__(self):
        self.nb = get_netbox_connection(
            config.NETBOX_URL, config.NETBOX_TOKEN, config.IGNORE_SSL_ERRORS
        )

        # Redis client for task management
        try:
            self.redis = Redis(
                host=config.REDIS_HOST,
                port=config.REDIS_PORT,
                db=config.REDIS_DB,
                socket_keepalive=True,
            )
            self.redis.ping()
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")
            self.redis = None

    def get_nb_device_query_list_sonic(self) -> List[Dict[str, Any]]:
        """Get NetBox device query list for SONiC devices."""
        try:
            return json.loads(config.NETBOX_FILTER_CONDUCTOR_SONIC)
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

    def push_task_output(self, task_id: str, line: str) -> None:
        """Push task output to Redis stream."""
        if self.redis:
            try:
                self.redis.xadd(task_id, {"type": "stdout", "content": line})
            except Exception as e:
                logger.error(f"Error pushing task output: {e}")

    def finish_task_output(self, task_id: str, rc: int = 0) -> None:
        """Finish task output in Redis stream."""
        if self.redis:
            try:
                self.redis.xadd(task_id, {"type": "rc", "content": str(rc)})
                self.redis.xadd(task_id, {"type": "action", "content": "quit"})
            except Exception as e:
                logger.error(f"Error finishing task output: {e}")

    def fetch_task_output(
        self, task_id: str, timeout: int = 300, enable_play_recap: bool = False
    ) -> int:
        """Fetch task output from Redis stream."""
        if not self.redis:
            return 0

        rc = 0
        stoptime = time.time() + timeout
        last_id = 0

        while time.time() < stoptime:
            try:
                data = self.redis.xread(
                    {str(task_id): last_id}, count=1, block=(timeout * 1000)
                )
                if data:
                    stoptime = time.time() + timeout
                    messages = data[0]
                    for message_id, message in messages[1]:
                        last_id = message_id.decode()
                        message_type = message[b"type"].decode()
                        message_content = message[b"content"].decode()

                        logger.debug(
                            f"Processing message {last_id} of type {message_type}"
                        )
                        self.redis.xdel(str(task_id), last_id)

                        if message_type == "stdout":
                            print(message_content, end="")
                            if enable_play_recap and "PLAY RECAP" in message_content:
                                logger.info(
                                    "Play has been completed. There may now be a delay until all logs have been written."
                                )
                                logger.info("Please wait and do not abort execution.")
                        elif message_type == "rc":
                            rc = int(message_content)
                        elif message_type == "action" and message_content == "quit":
                            return rc
            except Exception as e:
                logger.error(f"Error fetching task output: {e}")
                break

        return rc


# Global NetBox client instance
netbox_client = NetBoxClient()
