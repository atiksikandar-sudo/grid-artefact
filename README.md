# Grid Artefact Removal: demo app

A small web app that runs the trained U-Net (ResNet-34 encoder) from the dissertation
*Deep Learning-Based Removal of Synthetic Grid Artifacts in Paediatric Chest X-ray Using U-Net*.

## Quick start (about 5 minutes the first time)
download the ai model and place it next to app.py https://drive.google.com/file/d/133ya7VA8bqaAmMTOj49TTE8iPv_CMyfK/view?usp=sharing

**Windows:** double-click **`run.bat`**.
**macOS / Linux:** open a terminal in this folder and run `bash run.sh`.

The script creates a private environment (in your user folder, `GridAppEnv`), installs the packages once, starts the
app and opens your browser at http://127.0.0.1:5000. Later runs start in a few seconds. Nothing is installed globally.

Requirements: **Python 3.9 or newer** and an internet connection for the first run only.
No GPU is needed, and nothing is downloaded when the app runs (the model file is included).

### Manual start (if you prefer)
```
python -m venv C:\gridenv                 (macOS/Linux: python3 -m venv ~/gridenv)
C:\gridenv\Scripts\activate               (macOS/Linux: source ~/gridenv/bin/activate)
pip install -r requirements.txt
python app.py
```

## How to use it
1. **Choose an X-ray**: pick a built-in sample from the list, or upload/drag a PNG or JPG.
2. **Choose what to do**
   - *Add a simulated grid, then remove it* (default): real clean X-rays have no grid, so the app draws the
     same stripe pattern used in training, removes it with the model, and shows the PSNR before and after,
     measured against the clean image.
   - *My image already has a grid, just remove it*: upload the gridded file saved from the first option
     (download link under the result). No clean reference exists, so no score is shown.
3. Press **Remove grid**.

## Why a simulated grid?
Paired real images (the same patient with and without a grid) do not exist and cannot ethically be collected,
so the dissertation trains and evaluates on simulated grids. The model was trained only on a fixed horizontal
one-pixel grid (spacing 8 at 256x256), so it is **not expected to work on real grid images**. See Sections 5.6 and
6.4 of the dissertation for this limitation. Research demo only; not for clinical use.

## Files
| File | Purpose |
|---|---|
| `app.py` | Flask server and model code |
| `templates/index.html` | The web page |
| `best_unet_resnet34.pth` | Trained model weights (about 98 MB) |
| `test-actual/` | Sample X-rays shown in the sample list (public Wikimedia Commons images; check each file's licence page before redistributing). Any PNG/JPG under 3 MB put in this folder, or in a `test/` folder, appears in the list. |
| `run.bat`, `run.sh` | One-step launchers |
| `requirements.txt` | Python packages |

## Troubleshooting
| Problem | Fix |
|---|---|
| "Python was not found" | Install Python 3.9+ from python.org and tick "Add python.exe to PATH". |
| Install fails or is very slow | PyTorch is a large download (a few hundred MB). Retry on a stable connection. If it still fails: `pip install torch --index-url https://download.pytorch.org/whl/cpu`, then run `run.bat` again. |
| "Port 5000 already in use" | Set another port: `set PORT=5050` (Windows) or `PORT=5050 bash run.sh`, then open that port. |
| "Model file not found" | `best_unet_resnet34.pth` must sit next to `app.py` (or set `CKPT_PATH`). |
| Page does not open | Open http://127.0.0.1:5000 yourself while the window is still running. |
| Install fails with "No such file or directory ... path too long" | Windows limits paths to 260 characters. The launcher already puts its environment in a short path (`%USERPROFILE%\GridAppEnv`), so do not move it into a deep folder. If you install manually, create the environment close to the drive root, e.g. `python -m venv C:\gridenv`, or enable Windows long paths (https://pip.pypa.io/warnings/enable-long-paths). |
| Want a clean reinstall | Delete the `GridAppEnv` folder in your user folder (macOS/Linux: `~/.gridapp_env`) and run the launcher again. |

Tested with Python 3.14, Flask 3.0, PyTorch 2.14 (CPU) and segmentation-models-pytorch 0.5.
