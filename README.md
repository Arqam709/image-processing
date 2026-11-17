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
Stage 5A is complete. You can upload a PNG/JPEG photo and see it, its grayscale version and its
dimensions. Noise controls (5B), filters (5C), metrics (5D) and downloads (5E) come next.
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

**Using it (Stage 5A):**
1. In the sidebar, choose a PNG or JPEG file (at most 20 MB and 25 megapixels).
2. The page shows the uploaded image and the grayscale reference image side by side.
   Colour photos are converted to grayscale, because our algorithms work on grayscale images.
3. The page shows the width, height, number of pixels and file size. Below them,
   "Grayscale image details" shows the pixel statistics.

Damaged, empty, oversized or non-PNG/JPEG files show a clear error message instead of crashing.
The uploaded file is processed in memory only. It is never changed or saved to disk.

**How it connects to the project code:**
* `frontend/app.py` contains only the interface.
* `frontend/image_processing.py` checks the upload and decodes it in the same way as
  `src/image_io.load_grayscale_image`, then validates it with
  `src/image_io.validate_grayscale_image`.
* No algorithm is copied into `frontend/`. Later stages will call `src/noise.py`,
  `src/filters.py` and `src/metrics.py` directly.
* `.streamlit/config.toml` turns off Streamlit's anonymous usage statistics.

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
