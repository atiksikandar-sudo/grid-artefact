"""Grid Artefact Removal demo (Flask).

Removes a simulated anti-scatter grid from chest X-rays with the U-Net / ResNet-34 model trained for the dissertation.

Run:   python app.py        (or double-click run.bat on Windows / ./run.sh on macOS and Linux)
Open:  http://127.0.0.1:5000
"""
import base64
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def fail(msg):
    print("\n" + "=" * 70 + "\nSETUP PROBLEM\n" + msg + "\n" + "=" * 70 + "\nSee README.md > Troubleshooting.\n")
    sys.exit(1)


try:
    import numpy as np
    import torch
    from flask import Flask, jsonify, render_template, request
    from PIL import Image
    import segmentation_models_pytorch as smp
except ImportError as e:
    fail(f"A required package is missing: {e}\nFix: run   pip install -r requirements.txt   (or use run.bat / run.sh).")

IMG_SIZE = 256  # size used in training
CKPT = os.environ.get("CKPT_PATH", os.path.join(HERE, "best_unet_resnet34.pth"))
SAMPLE_DIRS = [os.path.join(HERE, d) for d in ("test", "test-actual")]
IMG_EXT = (".png", ".jpg", ".jpeg")
MAX_SAMPLE_BYTES = 3 * 1024 * 1024  # keep the sample list light

if not os.path.isfile(CKPT):
    fail(f"Model file not found:\n  {CKPT}\nPlace best_unet_resnet34.pth next to app.py, or set the CKPT_PATH environment variable.")

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024  # 20 MB upload limit

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = smp.Unet(encoder_name="resnet34", encoder_weights=None, in_channels=1, classes=1, activation="sigmoid")
try:
    model.load_state_dict(torch.load(CKPT, map_location=device))
except Exception as e:
    fail(f"The model file could not be loaded: {e}")
model.to(device).eval()


def list_samples():
    out = {}
    for d in SAMPLE_DIRS:
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            p = os.path.join(d, f)
            if f.lower().endswith(IMG_EXT) and os.path.getsize(p) <= MAX_SAMPLE_BYTES:
                out[f] = p
    return out


def add_grid(clean, spacing, intensity):
    """Same degradation as training: darken every `spacing`-th row (rows 0, spacing, 2*spacing ...) by `intensity`."""
    mask = np.zeros_like(clean, dtype=np.float32)
    mask[::spacing, :] = 1.0
    return clean * (1.0 - intensity * mask)


def restore(dirty):
    x = torch.from_numpy(dirty).float().unsqueeze(0).unsqueeze(0).to(device)
    with torch.no_grad():
        return model(x)[0, 0].cpu().numpy()


def psnr(a, b):
    mse = float(np.mean((a - b) ** 2))
    return float("inf") if mse == 0 else 10 * np.log10(1.0 / mse)


def to_b64(arr):
    img = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8), mode="L")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/samples")
def samples():
    return jsonify(sorted(list_samples()))


@app.route("/sample-image/<name>")
def sample_image(name):
    p = list_samples().get(name)  # only names found in the sample folders are allowed
    if p is None:
        return ("Not found", 404)
    img = Image.open(p).convert("L").resize((IMG_SIZE, IMG_SIZE), Image.BILINEAR)
    return jsonify(src=to_b64(np.array(img).astype(np.float32) / 255.0))


@app.route("/restore", methods=["POST"])
def restore_route():
    sample = request.form.get("sample", "").strip()
    try:
        if sample:
            p = list_samples().get(sample)
            if p is None:
                return jsonify(error="Unknown sample image."), 400
            img = Image.open(p)
        else:
            f = request.files.get("image")
            if f is None or f.filename == "":
                return jsonify(error="Choose a sample image or upload a file first."), 400
            img = Image.open(f.stream)
        img = img.convert("L").resize((IMG_SIZE, IMG_SIZE), Image.BILINEAR)
    except Exception:
        return jsonify(error="Could not read that file as an image (use PNG or JPG)."), 400
    base = np.array(img).astype(np.float32) / 255.0

    simulate = request.form.get("mode", "simulate") == "simulate"
    try:
        intensity = float(request.form.get("intensity", 0.35))
        spacing = int(request.form.get("spacing", 8))
    except ValueError:
        return jsonify(error="Intensity and spacing must be numbers."), 400
    intensity = min(max(intensity, 0.0), 0.9)
    spacing = min(max(spacing, 2), 64)

    dirty = add_grid(base, spacing, intensity) if simulate else base
    restored = restore(dirty)

    out = {"dirty": to_b64(dirty), "restored": to_b64(restored), "simulated": simulate}
    if simulate:  # a clean reference exists, so the result can be scored
        out["clean"] = to_b64(base)
        out["psnr_dirty"] = round(psnr(dirty, base), 2)
        out["psnr_restored"] = round(psnr(restored, base), 2)
    return jsonify(out)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\nModel loaded on {device}. Open http://127.0.0.1:{port} in your browser. Press Ctrl+C to stop.\n")
    app.run(host="127.0.0.1", port=port, debug=False)
