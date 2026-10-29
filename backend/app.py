from __future__ import annotations

import uuid
from pathlib import Path
import time

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

try:
    from .services.face_detector import detect_faces
except ImportError:
    from services.face_detector import detect_faces


BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
UPLOAD_FOLDER = BASE_DIR / "backend" / "uploads"
RESULT_FOLDER = BASE_DIR / "backend" / "results"
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "bmp"}
MAX_IMAGE_BYTES = 12 * 1024 * 1024

UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
RESULT_FOLDER.mkdir(parents=True, exist_ok=True)

# Serve /style.css and /script.js to match the paths in frontend/index.html.
app = Flask(
    __name__,
    static_folder=str(FRONTEND_DIR),
    static_url_path="",
)
app.config["MAX_CONTENT_LENGTH"] = MAX_IMAGE_BYTES
CORS(app)


def json_error(message: str, status: int):
    return jsonify({"error": message}), status


def cleanup_old_files(folder: Path, max_age_seconds: int = 1800) -> None:
    """Delete temporary files older than 30 minutes."""
    cutoff = time.time() - max_age_seconds
    try:
        for item in folder.iterdir():
            if item.is_file() and item.stat().st_mtime < cutoff:
                item.unlink(missing_ok=True)
    except OSError:
        app.logger.warning("Could not clean old files in %s", folder, exc_info=True)


@app.get("/")
@app.get("/workspace")
def workspace():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "model": "model/best.pt"})


@app.post("/detect")
def detect():
    image = request.files.get("image")
    if image is None or not image.filename:
        return json_error("Choose an image before clicking Detect.", 400)

    extension = Path(image.filename).suffix.lower().lstrip(".")
    if extension not in ALLOWED_EXTENSIONS:
        return json_error(
            "Unsupported image format. Use JPG, JPEG, PNG, WEBP, or BMP.", 415
        )

    file_id = uuid.uuid4().hex
    input_path = UPLOAD_FOLDER / f"{file_id}.{extension}"
    output_path = RESULT_FOLDER / f"{file_id}.jpg"

    try:
        cleanup_old_files(UPLOAD_FOLDER)
        cleanup_old_files(RESULT_FOLDER)
        image.save(input_path)
        detection = detect_faces(input_path, output_path)
        return jsonify({
            "message": "Detection completed",
            "result": f"/results/{output_path.name}",
            "faces_detected": detection["faces_detected"],
            "confidences": detection["confidences"],
        })
    except Exception:
        app.logger.exception("Face detection failed")
        output_path.unlink(missing_ok=True)
        return json_error(
            "Face detection failed. Check the Flask terminal for the detailed error.",
            500,
        )
    finally:
        input_path.unlink(missing_ok=True)


@app.get("/results/<path:filename>")
def results(filename: str):
    return send_from_directory(RESULT_FOLDER, filename)


@app.errorhandler(413)
def request_too_large(_error):
    return json_error("Image is too large. Maximum upload size is 12 MB.", 413)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
