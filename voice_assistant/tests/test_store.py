from src.store import add_task, load, open_tasks


def test_add_task_persists(tmp_path, monkeypatch):
    monkeypatch.setenv("LENTSWE_DATA_DIR", str(tmp_path))
    item = add_task("buy bread")
    assert item["description"] == "buy bread"
    data = load()
    assert any(t["description"] == "buy bread" for t in data["tasks"])
    assert open_tasks()
