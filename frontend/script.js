(() => {
  const $ = (id) => document.getElementById(id);
  const input = $("imageInput");
  const detectButton = $("detectButton");
  const preview = $("preview");
  const resultImage = $("result");
  const imageMessage = $("imageMessage");
  const resultStats = $("resultStats");
  let selectedFile = null;
  let previewUrl = null;
  let cameraStream = null;
  let cameraTimer = null;
  let cameraBusy = false;
  let cameraStopped = true;

  async function checkHealth() {
    const status = $("apiStatus");
    try {
      const response = await fetch("/api/health", { cache: "no-store" });
      if (!response.ok) throw new Error("API is not ready");
      const data = await response.json();
      status.className = "status status-online";
      status.innerHTML = '<span class="status-dot"></span> Model ready';
      status.title = data.model || "Detection API ready";
    } catch {
      status.className = "status status-offline";
      status.innerHTML = '<span class="status-dot"></span> Backend unavailable';
      status.title = "Start the app with: python backend/app.py";
    }
  }

  function setMessage(element, message, kind = "") {
    element.textContent = message;
    element.className = "message" + (kind ? " " + kind : "");
  }

  function formatError(data, response) {
    return data && data.error ? data.error : `Request failed (HTTP ${response.status}). Check the Flask terminal.`;
  }

  input.addEventListener("change", () => {
    selectedFile = input.files && input.files[0] ? input.files[0] : null;
    resultImage.hidden = true;
    $("resultPlaceholder").hidden = false;
    resultStats.hidden = true;

    if (previewUrl) URL.revokeObjectURL(previewUrl);
    previewUrl = null;

    if (!selectedFile) {
      preview.hidden = true;
      $("previewPlaceholder").hidden = false;
      detectButton.disabled = true;
      setMessage(imageMessage, "Select an image to get started.");
      return;
    }

    if (!selectedFile.type.startsWith("image/")) {
      selectedFile = null;
      input.value = "";
      detectButton.disabled = true;
      setMessage(imageMessage, "Please choose a valid image file.", "error");
      return;
    }
    if (selectedFile.size > 12 * 1024 * 1024) {
      selectedFile = null;
      input.value = "";
      detectButton.disabled = true;
      setMessage(imageMessage, "This image is over 12 MB. Choose a smaller image.", "error");
      return;
    }

    previewUrl = URL.createObjectURL(selectedFile);
    preview.src = previewUrl;
    preview.hidden = false;
    $("previewPlaceholder").hidden = true;
    detectButton.disabled = false;
    setMessage(imageMessage, `${selectedFile.name} ready for detection.`);
  });

  detectButton.addEventListener("click", async () => {
    if (!selectedFile) return;
    detectButton.disabled = true;
    detectButton.classList.add("loading");
    setMessage(imageMessage, "Running face detection…");
    resultImage.hidden = true;
    $("resultPlaceholder").hidden = false;
    resultStats.hidden = true;

    try {
      const formData = new FormData();
      formData.append("image", selectedFile);
      const response = await fetch("/detect", { method: "POST", body: formData });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(formatError(data, response));
      if (!data.result) throw new Error("The server did not return a result image.");

      resultImage.onload = () => {
        resultImage.hidden = false;
        $("resultPlaceholder").hidden = true;
      };
      resultImage.onerror = () => setMessage(imageMessage, "Detection finished, but the result image could not be loaded. Try again.", "error");
      resultImage.src = data.result + "?t=" + Date.now();
      $("faceCount").textContent = Number.isFinite(data.faces_detected) ? data.faces_detected : "—";
      const confidences = Array.isArray(data.confidences) ? data.confidences : [];
      $("confidenceText").textContent = confidences.length ? Math.round(Math.max(...confidences) * 100) + "% max" : "No faces found";
      resultStats.hidden = false;
      setMessage(imageMessage, data.faces_detected === 0 ? "No faces detected. Try a clearer, front-facing image." : `Detection complete — ${data.faces_detected} face(s) found.`, "success");
    } catch (error) {
      setMessage(imageMessage, error instanceof TypeError ? "Could not reach the backend. Confirm the Flask server is running at http://127.0.0.1:5000." : error.message, "error");
    } finally {
      detectButton.disabled = !selectedFile;
      detectButton.classList.remove("loading");
    }
  });

  const dropZone = $("dropZone");
  ["dragenter", "dragover"].forEach((eventName) => dropZone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropZone.classList.add("drag-over");
  }));
  ["dragleave", "drop"].forEach((eventName) => dropZone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropZone.classList.remove("drag-over");
  }));
  dropZone.addEventListener("drop", (event) => {
    const file = event.dataTransfer && event.dataTransfer.files && event.dataTransfer.files[0];
    if (!file) return;
    const transfer = new DataTransfer();
    transfer.items.add(file);
    input.files = transfer.files;
    input.dispatchEvent(new Event("change", { bubbles: true }));
  });

  document.querySelectorAll(".mode-tab").forEach((button) => button.addEventListener("click", () => {
    document.querySelectorAll(".mode-tab").forEach((tab) => tab.classList.toggle("active", tab === button));
    const cameraMode = button.dataset.mode === "camera";
    $("imagePanel").hidden = cameraMode;
    $("cameraPanel").hidden = !cameraMode;
    if (!cameraMode) stopCamera();
  }));

  async function sendFrame() {
    if (cameraStopped || cameraBusy || !cameraStream) return;
    const video = $("cameraVideo");
    if (video.readyState < 2 || !video.videoWidth) return;
    cameraBusy = true;
    try {
      const canvas = $("cameraCanvas");
      const scale = Math.min(1, 720 / video.videoWidth);
      canvas.width = Math.round(video.videoWidth * scale);
      canvas.height = Math.round(video.videoHeight * scale);
      canvas.getContext("2d").drawImage(video, 0, 0, canvas.width, canvas.height);
      const blob = await new Promise((resolve) => canvas.toBlob(resolve, "image/jpeg", 0.82));
      if (!blob || cameraStopped) return;
      const formData = new FormData();
      formData.append("image", blob, "camera-frame.jpg");
      const response = await fetch("/detect", { method: "POST", body: formData });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(formatError(data, response));
      if (data.result && !cameraStopped) {
        $("cameraResult").src = data.result + "?t=" + Date.now();
        $("cameraResult").hidden = false;
        $("cameraPlaceholder").hidden = true;
        setMessage($("cameraMessage"), `${data.faces_detected || 0} face(s) detected in latest frame.`, "success");
      }
    } catch (error) {
      if (!cameraStopped) {
        setMessage($("cameraMessage"), error instanceof TypeError ? "Could not reach the detection API. Check that Flask is running." : error.message, "error");
        stopCamera();
      }
    } finally {
      cameraBusy = false;
    }
  }

  async function startCamera() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      setMessage($("cameraMessage"), "Camera access is unavailable. Open the app on localhost in a supported browser.", "error");
      return;
    }
    $("startCamera").disabled = true;
    setMessage($("cameraMessage"), "Requesting camera permission…");
    try {
      cameraStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "user", width: { ideal: 640 }, height: { ideal: 480 } }, audio: false });
      cameraStopped = false;
      const video = $("cameraVideo");
      video.srcObject = cameraStream;
      video.hidden = false;
      $("cameraPlaceholder").hidden = true;
      $("cameraResult").hidden = true;
      await video.play();
      $("stopCamera").disabled = false;
      setMessage($("cameraMessage"), "Camera running. Processing frames…");
      cameraTimer = window.setInterval(sendFrame, 1300);
      sendFrame();
    } catch (error) {
      stopCamera();
      setMessage($("cameraMessage"), error.name === "NotAllowedError" ? "Camera permission was denied. Allow camera access in your browser settings." : "Could not start camera: " + error.message, "error");
    } finally {
      $("startCamera").disabled = false;
    }
  }

  function stopCamera() {
    cameraStopped = true;
    if (cameraTimer !== null) window.clearInterval(cameraTimer);
    cameraTimer = null;
    if (cameraStream) cameraStream.getTracks().forEach((track) => track.stop());
    cameraStream = null;
    const video = $("cameraVideo");
    video.pause();
    video.srcObject = null;
    video.hidden = true;
    $("stopCamera").disabled = true;
    if ($("cameraPanel") && !$("cameraPanel").hidden) {
      $("cameraPlaceholder").hidden = false;
      $("cameraResult").hidden = true;
      setMessage($("cameraMessage"), "Camera is stopped.");
    }
  }

  $("startCamera").addEventListener("click", startCamera);
  $("stopCamera").addEventListener("click", stopCamera);
  window.addEventListener("beforeunload", () => {
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    stopCamera();
  });

  checkHealth();
})();
