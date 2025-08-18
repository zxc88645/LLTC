from lltc.host import Host
from lltc.host_manager import HostManager


def test_add_and_get_host():
    manager = HostManager()
    host = Host(name="server", ip="127.0.0.1")
    manager.add_host(host)
    assert manager.get_host("server") == host
    assert manager.list_hosts() == [host]
    manager.remove_host("server")
    assert manager.get_host("server") is None
