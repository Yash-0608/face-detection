from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from pathlib import Path
import uuid

from services.face_detector import detect_faces


app = Flask(
    __name__,
    static_folder="../frontend",
    static_url_path=""
)

CORS(app)

BASE_DIR = Path(__file__).resolve().parent.parent


UPLOAD_FOLDER = BASE_DIR / "backend" / "uploads"

RESULT_FOLDER = BASE_DIR / "backend" / "results"


UPLOAD_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)

RESULT_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)


# Serve frontend
@app.route("/")
def home():

    return app.send_static_file(
        "index.html"
    )


# Detection API
@app.route("/detect", methods=["POST"])
def detect():

    if "image" not in request.files:

        return jsonify({
            "error": "No image uploaded"
        }), 400


    image = request.files["image"]


    file_id = str(uuid.uuid4())


    extension = Path(
        image.filename
    ).suffix


    input_path = (
        UPLOAD_FOLDER /
        f"{file_id}{extension}"
    )


    output_path = (
        RESULT_FOLDER /
        f"{file_id}.jpg"
    )


    # Save uploaded image
    image.save(input_path)


    # Run YOLO detection
    detect_faces(
        input_path,
        output_path
    )


    return jsonify({

        "message":
        "Detection completed",

        "result":
        f"/results/{output_path.name}"

    })



# Serve result images
@app.route("/results/<filename>")
def results(filename):

    return send_from_directory(
        RESULT_FOLDER,
        filename
    )



if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )