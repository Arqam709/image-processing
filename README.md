# Image Noise Addition and Removal

University Image Processing course project. The goal is to add controlled
noise (Gaussian, salt-and-pepper, speckle) to clean grayscale images, remove it
with classic filters (mean, Gaussian, median, bilateral), and compare the
filters fairly using MSE and PSNR.

**Current status: Stages 1–4 are complete.** They cover image loading,
validation, pixel statistics, the image quality metrics MSE and PSNR,
three reproducible noise models (Gaussian, salt-and-pepper, speckle), and
four noise-removal filters (mean, Gaussian, median, bilateral).

**Stage 5 (in progress): Image Noise Lab, a Streamlit web interface.**
Stages 5A and 5B are complete. You can upload a PNG/JPEG photo, see its grayscale version, and
add Gaussian, salt-and-pepper or speckle noise with a reproducible seed. Filters (5C),
metrics (5D) and downloads (5E) come next.
The full experiment runner comes in a later stage.

## Setup (Windows PowerShell)

```powershell
cd C:\Users\ahsan\OneDrive\Desktop\IP
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt   # only needed on a new machine
```

All commands below are run from the project root folder (`IP`).

## Run the Stage 1 demonstration

```powershell
python -m demos.demo_image_loading                         # synthetic test image
python -m demos.demo_image_loading data\input\my_photo.jpg  # your own image
python -m demos.demo_image_loading --show                  # also show image + histogram
```

## Run the Stage 2 demonstration (MSE and PSNR)

```powershell
python -m demos.demo_metrics                # print a step-by-step example and results
python -m demos.demo_metrics --show         # also show original vs modified images
python -m demos.demo_metrics --save-figure  # save results\figures\stage2_metric_validation.png
```

## Run the Stage 3 demonstration (adding noise)

```powershell
python -m demos.demo_noise                  # print the MSE/PSNR table for 9 noisy images
python -m demos.demo_noise --show           # also show the comparison figure
python -m demos.demo_noise --save-figure    # save results\figures\stage3_noise_examples.png
python -m demos.demo_noise --save-outputs   # save noisy PNGs (results\noisy) + CSV (results\tables)
```

All noise uses the fixed seed 42, so every run gives exactly the same images.

## Run the Stage 4 demonstration (removing noise with filters)

```powershell
python -m demos.demo_filters                  # print the comparison tables
python -m demos.demo_filters --show           # also show the comparison figure
python -m demos.demo_filters --save-figure    # save results\figures\stage4_filter_comparison.png
python -m demos.demo_filters --save-outputs   # save filtered PNGs (results\filtered) + CSV (results\tables)
```

The demo recreates two Stage 3 noisy images (Gaussian σ = 25 and
salt-and-pepper 5%, seed 42), applies all four filters to the **same** noisy
image, and prints MSE and PSNR for each one. It never changes the Stage 3 files.

## Run the Image Noise Lab web app (Stage 5)

The app needs Streamlit, which is listed in `requirements.txt`. On a new
machine, `pip install -r requirements.txt` installs it into the existing `.venv`.
No other virtual environment is needed.

```powershell
cd C:\Users\ahsan\OneDrive\Desktop\IP
.\.venv\Scripts\Activate.ps1
python -m streamlit run frontend/app.py
```

Streamlit prints a local address (normally http://localhost:8501) and opens it in your
browser. Press `Ctrl+C` in PowerShell to stop the app.

**First launch:** Streamlit may ask for an email address. You can leave it empty and press Enter.

**Using it:**
1. **Upload (sidebar, section 1):** choose a PNG or JPEG file (at most 20 MB and 25 megapixels).
   Colour photos are converted to grayscale, because our algorithms work on grayscale images.
2. **Add noise (sidebar, section 2, appears after a valid upload):**
   * Choose **Gaussian**, **Salt-and-Pepper** or **Speckle** noise. Only the slider for the chosen type is shown.
   * Set its strength:

     | Noise | Slider | Range (step) | Default |
     |---|---|---|---|
     | Gaussian | σ (sigma) | 0–100 (1) | 25 |
     | Salt-and-Pepper | amount, shown as % of pixels | 0–50% (1%) | 5% |
     | Speckle | variance | 0.00–0.25 (0.01) | 0.04 |

     The defaults are the Stage 3 baselines E002, E005 and E008.
   * Set the **Random Seed** (default 42). The same image, settings and seed always give
     exactly the same noisy image.
3. **Main page:**
   * "Original Grayscale" and the noisy image are shown side by side at the same compact size.
   * Below them are the settings and a short **pixel fingerprint**. The fingerprint changes when
     any pixel changes, so you can check that returning to the same settings gives the identical image.
4. **Expandable panels:**
   * "Inspect details": zoom into the real pixels of both images at the same position.
   * "How does this noise work?": a simple explanation and formula for the selected noise.
   * "Uploaded photo (original colours)", plus the grayscale statistics.

Damaged, empty, oversized or non-PNG/JPEG files show a clear error message instead of crashing.
An invalid seed (for example a negative number) shows an error message too.
Images are processed in memory only. Nothing is saved to disk when you change a control.

**How it connects to the project code:**
* `frontend/app.py` contains only the interface.
* `frontend/image_processing.py` holds two kinds of helpers:
  * **Upload:** it checks the file and decodes it in the same way as
    `src/image_io.load_grayscale_image`, then validates it with `src/image_io.validate_grayscale_image`.
  * **Noise:** `make_noisy_image()` picks and calls the existing function in `src/noise.py`
    (`add_gaussian_noise`, `add_salt_and_pepper_noise` or `add_speckle_noise`). It passes the
    strength and seed on unchanged.
* No algorithm is copied into `frontend/`. Later stages will call `src/filters.py` and
  `src/metrics.py` in the same way.
* `.streamlit/config.toml` keeps the app on this computer only (localhost) and turns off
  Streamlit's anonymous usage statistics.

## Run the tests

```powershell
python -m unittest -v
```

## Folder structure

| Folder | Purpose |
|---|---|
| `src/` | Image processing code (no interface code) |
| `frontend/` | Streamlit web interface (Image Noise Lab) and its small helper module |
| `.streamlit/` | Streamlit settings (no usage statistics) |
| `demos/` | Small scripts that demonstrate one feature |
| `tests/` | Unit tests (Python's built-in `unittest`) |
| `experiments/` | Experiment runner (later stage) |
| `data/input/` | Original input images, which are never modified |
| `results/` | Generated outputs (ignored by Git) |
| `docs/` | Report notes, experiment log, references, presentation notes |
| `course_material/` | Professor's template and lecture slides |
