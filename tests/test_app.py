import sys
sys.path.insert(0, "/app")

from app import app


def test_home():
    app.config["TESTING"] = True

    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
