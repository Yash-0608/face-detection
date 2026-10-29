from __future__ import annotations

from pathlib import Path
from threading import Lock

import cv2
from ultralytics import YOLO

# Resolve paths relative to the repository, not the shell's current directory.
BASE_DIR = Path(__file__).resolve().parents[2]
MODEL_PATH = BASE_DIR / "model" / "best.pt"
CONFIDENCE_THRESHOLD = 0.35

if not MODEL_PATH.is_file():
    raise FileNotFoundError(
        f"YOLO model was not found at {MODEL_PATH}. "
        "Make sure model/best.pt exists in the repository."
    )

model = YOLO(str(MODEL_PATH))
_inference_lock = Lock()


def detect_faces(image_path: str | Path, output_path: str | Path) -> dict:
    """Run face detection, save an annotated JPEG, and return detection details."""
    image_path = Path(image_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not image_path.is_file():
        raise FileNotFoundError(f"Input image does not exist: {image_path}")

    # Ultralytics model instances are shared by requests; serialize inference.
    with _inference_lock:
        results = model.predict(
            source=str(image_path),
            conf=CONFIDENCE_THRESHOLD,
            verbose=False,
        )

    if not results:
        raise RuntimeError("The model did not return a prediction result.")

    result = results[0]
    annotated = result.plot()
    if not cv2.imwrite(str(output_path), annotated):
        raise OSError(f"Could not save annotated image to {output_path}")

    confidences = []
    if result.boxes is not None and result.boxes.conf is not None:
        confidences = [round(float(value), 4) for value in result.boxes.conf.tolist()]

    return {
        "output_path": str(output_path),
        "faces_detected": len(confidences),
        "confidences": confidences,
    }
