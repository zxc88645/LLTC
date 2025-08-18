from fastapi.testclient import TestClient

from lltc.web import app


client = TestClient(app)


def test_add_and_list_hosts():
    payload = {
        "name": "test",
        "ip": "127.0.0.1",
        "username": "root",
    }
    r = client.post("/hosts", json=payload)
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

    r = client.get("/hosts")
    hosts = r.json()
    assert hosts and hosts[0]["name"] == "test"


def test_run_command():
    client.post(
        "/hosts",
        json={"name": "os", "ip": "127.0.0.1", "username": "root"},
    )
    r = client.post(
        "/command",
        json={"host": "os", "text": "幫我查看這台作業系統版本"},
    )
    assert r.status_code == 200
    assert r.json()["command"] == "uname -a"
