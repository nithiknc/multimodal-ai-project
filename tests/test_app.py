
import io
from app import app


def setup_function():
    app.config["TESTING"] = True


def test_home_page():
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200


def test_health_endpoint():
    client = app.test_client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json["status"] == "running"


def test_missing_image():
    client = app.test_client()
    response = client.post("/ask", data={})
    assert response.status_code == 400


def test_missing_question():
    client = app.test_client()
    response = client.post(
        "/ask",
        data={
            "image": (io.BytesIO(b"fake image"), "test.jpg"),
            "question": ""
        },
        content_type="multipart/form-data"
    )
    assert response.status_code == 400
