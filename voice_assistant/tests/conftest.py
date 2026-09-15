import pytest


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("LENTSWE_DATA_DIR", str(tmp_path))
    from app import create_app

    flask_app = create_app()
    flask_app.config["TESTING"] = True
    return flask_app.test_client()
