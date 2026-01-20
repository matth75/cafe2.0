# tests/test_api_status.py
def test_healthcheck(client):
    r = client.get("/api/status/healthcheck")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}
