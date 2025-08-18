from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .host import Host
from .host_manager import HostManager
from .command_parser import parse_command

app = FastAPI(title="LLTC")

_manager = HostManager()


class HostCreate(BaseModel):
    name: str
    ip: str
    port: int = 22
    username: str = "root"
    password: str | None = None
    key: str | None = None


@app.post("/hosts")
def add_host(host: HostCreate) -> dict[str, str]:
    _manager.add_host(Host(**host.dict()))
    return {"status": "ok"}


@app.get("/hosts")
def list_hosts() -> list[Host]:
    return _manager.list_hosts()


class CommandRequest(BaseModel):
    host: str
    text: str


@app.post("/command")
def run_command(req: CommandRequest) -> dict[str, str]:
    host = _manager.get_host(req.host)
    if host is None:
        raise HTTPException(status_code=404, detail="Host not found")
    command = parse_command(req.text)
    if command is None:
        raise HTTPException(status_code=400, detail="Could not parse command")
    # Real implementation would execute `command` on `host` via SSH.
    return {"command": command}
