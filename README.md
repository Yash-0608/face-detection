# FaceVision AI — Face Detection

A local face-detection web app powered by your custom Ultralytics YOLO model, Flask, and OpenCV. It supports image uploads and browser webcam detection.

## Requirements
- Windows 10/11, macOS, or Linux
- Python 3.10–3.12 recommended
- The model file at `model/best.pt` (included in this repository)
- Webcam access is optional and requires browser permission

## Run on Windows (PowerShell)

Clone the repository and enter its folder:

```powershell
git clone https://github.com/Yash-0608/face-detection.git
cd face-detection
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python backend/app.py
```

If PowerShell blocks virtual-environment activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that terminal, then activate again. Alternatively use Command Prompt: `.venv\Scripts\activate.bat`.

Open **http://127.0.0.1:5000**. Do not open the HTML file directly; the browser must use the Flask server so the API requests reach the backend.

## Use
1. Wait for the header to show **Model ready**.
2. Select or drag an image into the upload area.
3. Click **Detect faces** and wait for the annotated result.
4. For webcam detection, choose **Camera mode**, click **Start camera**, and allow camera access. Click **Stop** when finished.

The webcam sends resized frames to your local Flask server approximately once every 1.3 seconds. It is intentionally not a high-frame-rate video stream so inference remains manageable on a laptop.

## Troubleshooting
- **Backend unavailable / Failed to fetch:** keep the terminal running and open `http://127.0.0.1:5000`; check the terminal for Python errors. Refresh the page after the server starts.
- **Model file missing:** confirm `model/best.pt` exists. The backend resolves the model path relative to the repository, so you can start it from the repository root or another working directory.
- **No faces detected:** try a sharp, well-lit image with faces clearly visible. The confidence threshold is set to 0.35 in `backend/services/face_detector.py`; raise it to reduce false positives or lower it to make detection more sensitive.
- **Camera permission denied:** allow camera access for localhost in browser site settings. Use Chrome or Edge and ensure no other application is exclusively using the camera.
- **Port 5000 already in use:** stop the other process or change the port at the bottom of `backend/app.py`.

## API
- `GET /` and `GET /workspace` — web interface
- `GET /api/health` — backend health check
- `POST /detect` — multipart form upload with field `image`; returns the result image URL, number of detected faces, and confidence values
- `GET /results/<filename>` — serves an annotated result image

Example response:

```json
{
  "message": "Detection completed",
  "result": "/results/abc123.jpg",
  "faces_detected": 2,
  "confidences": [0.97, 0.94]
}
```

## Privacy and limitations
Images are processed by the local application. Uploaded input files are deleted after processing and old output files are cleaned periodically; result images are retained temporarily. This is face **detection**, not face recognition or identity matching. The development server is intended for local use, not public production deployment.
