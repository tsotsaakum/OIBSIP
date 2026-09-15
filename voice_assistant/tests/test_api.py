def test_health_ok(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    body = res.get_json()
    assert body["status"] == "ok"
    assert body["service"] == "lentswe"


def test_ready_ok(client):
    res = client.get("/api/ready")
    assert res.status_code == 200
    assert res.get_json()["status"] == "ready"


def test_chat_requires_text(client):
    res = client.post("/api/chat", json={"text": "", "language": "english"})
    assert res.status_code == 400


def test_chat_time(client):
    res = client.post(
        "/api/chat",
        json={"text": "what time is it", "language": "english", "history": []},
    )
    assert res.status_code == 200
    reply = res.get_json()["reply"]
    assert "time" in reply.lower()


def test_languages(client):
    res = client.get("/api/languages")
    assert res.status_code == 200
    langs = res.get_json()["languages"]
    assert any(item["id"] == "english" for item in langs)
