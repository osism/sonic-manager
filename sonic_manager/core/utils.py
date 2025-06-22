# SPDX-License-Identifier: Apache-2.0

"""Utility functions for SONiC Manager."""

from typing import Callable, Iterable, TypeVar
from .netbox_client import netbox_client

T = TypeVar("T")


def first(iterable: Iterable[T], condition: Callable[[T], bool] = lambda x: True) -> T:
    """
    Returns the first item in the `iterable` that satisfies the `condition`.

    If the condition is not given, returns the first item of the iterable.
    Raises `StopIteration` if no item satisfying the condition is found.

    >>> first((1,2,3), condition=lambda x: x % 2 == 0)
    2
    >>> first(range(3, 100))
    3
    >>> first(())
    Traceback (most recent call last):
    ...
    StopIteration
    """
    return next(x for x in iterable if condition(x))


# Compatibility layer for OSISM utils
class Utils:
    """Compatibility layer for OSISM utils."""

    @property
    def nb(self):
        """NetBox client."""
        return netbox_client.nb

    def push_task_output(self, task_id: str, line: str) -> None:
        """Push task output."""
        netbox_client.push_task_output(task_id, line)

    def finish_task_output(self, task_id: str, rc: int = 0) -> None:
        """Finish task output."""
        netbox_client.finish_task_output(task_id, rc)

    def fetch_task_output(
        self, task_id: str, timeout: int = 300, enable_play_recap: bool = False
    ) -> int:
        """Fetch task output."""
        return netbox_client.fetch_task_output(task_id, timeout, enable_play_recap)


# Global utils instance for compatibility
utils = Utils()
