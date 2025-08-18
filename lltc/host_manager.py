"""Simple in-memory host manager."""

from __future__ import annotations

from typing import Dict

from .host import Host


class HostManager:
    def __init__(self) -> None:
        self._hosts: Dict[str, Host] = {}

    def add_host(self, host: Host) -> None:
        self._hosts[host.name] = host

    def get_host(self, name: str) -> Host | None:
        return self._hosts.get(name)

    def list_hosts(self) -> list[Host]:
        return list(self._hosts.values())

    def remove_host(self, name: str) -> None:
        self._hosts.pop(name, None)
