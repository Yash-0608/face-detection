from io import BytesIO

from backend.app import APP_VERSION, app


def setup_function():
    app.config.update(TESTING=True)


def test_health_reports_version_and_model():
    response = app.test_client().get("/api/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"
    assert data["app_version"] == APP_VERSION
    assert data["model_file_exists"] is True


def test_root_and_workspace_serve_same_frontend():
    client = app.test_client()
    root = client.get("/")
    workspace = client.get("/workspace")
    assert root.status_code == 200
    assert workspace.status_code == 200
    assert b"Face detection," in root.data
    assert b"Face detection," in workspace.data
    assert root.headers.get("X-FaceVision-Version") == APP_VERSION


def test_missing_upload_returns_helpful_error():
    response = app.test_client().post("/detect", data={})
    assert response.status_code == 400
    assert "Choose an image" in response.get_json()["error"]


def test_unsupported_file_type_returns_415():
    response = app.test_client().post(
        "/detect",
        data={"image": (BytesIO(b"not an image"), "document.txt")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 415
    assert "Unsupported image format" in response.get_json()["error"]
