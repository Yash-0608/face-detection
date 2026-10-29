# FaceVision AI — Face Detection

A local face-detection web app powered by a custom Ultralytics YOLO model, Flask, and OpenCV. It supports image uploads and browser webcam detection.

## Requirements
- Windows 10/11, macOS, or Linux
- Python 3.10–3.12 recommended
- The trained model file at `model/best.pt` (included in this repository)
- Webcam access is optional and requires browser permission

## Run on Windows — recommended

1. Download or clone this repository.
2. Open the repository root folder (the folder containing `backend`, `frontend`, `model`, and `requirements.txt`).
3. Double-click `run_windows.bat`. It creates the virtual environment if needed, installs dependencies, and starts Flask from the correct project directory.
4. Keep the terminal open and open **http://127.0.0.1:5000/workspace**.

**Important:** stop any older FaceVision server first by selecting its terminal and pressing `Ctrl+C`. If the browser still shows the old interface, the old Python process or a different project folder is being used. The current app prints its version and project directory when it starts.

## Run manually (PowerShell)

From the repository root:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python backend/app.py
```

If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that terminal, then activate again. You can also run `.venv\Scripts\python.exe backend\app.py` without activating the environment.

Do not open the HTML file directly; use the Flask URL so browser requests reach the API.

## Confirm the correct server is running

Open **http://127.0.0.1:5000/api/health**. The JSON response should contain `"app_version": "2026.10.29.2"`, `"status": "ok"`, and `"model_file_exists": true`. If the version is missing or different, an older server is still responding or you started another copy of the project.

## Use
1. Wait for the header to show **Model ready**.
2. Select or drag an image into the upload area.
3. Click **Detect faces** and wait for the annotated result.
4. For webcam detection, choose **Camera mode**, click **Start camera**, and allow camera access. Click **Stop** when finished.

The webcam sends resized frames to the local Flask server about once every 1.3 seconds. This is intentionally not a high-frame-rate stream so inference remains manageable on a laptop.

## Tests

Install the test dependency and run the Flask route tests:

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

## Troubleshooting
- **Backend unavailable / Failed to fetch:** keep the terminal open; inspect its Python traceback and open the health URL above.
- **Old page / tiny dot / no image preview:** check the health response version, stop old Python servers, then launch `run_windows.bat` from this repository root and press `Ctrl+F5`.
- **Model file missing:** confirm `model/best.pt` exists. Model paths are resolved relative to the repository, not the terminal's working directory.
- **No faces detected:** try a sharp, well-lit photo. The confidence threshold is 0.35 in `backend/services/face_detector.py`.
- **Camera permission denied:** allow camera access for localhost in Chrome/Edge site settings.
- **Port 5000 already in use:** stop the older process before launching this app. Do not run two versions on the same port.

## API
- `GET /` and `GET /workspace` — web interface
- `GET /api/health` — runtime version, project root, and model-file diagnostics
- `POST /detect` — multipart form upload with field `image`; returns the result URL, face count, and confidence values
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
Images are processed by the local application. Uploaded input files are deleted after processing; old result files are cleaned periodically. This is face **detection**, not face recognition or identity matching. The Flask development server is intended for local use, not public production deployment.
