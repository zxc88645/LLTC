from dataclasses import dataclass


@dataclass
class Host:
    """Represents SSH host connection information."""

    name: str
    ip: str
    port: int = 22
    username: str = "root"
    password: str | None = None
    key: str | None = None
