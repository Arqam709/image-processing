# Image Noise Addition and Removal

University Image Processing course project. The goal is to add controlled
noise (Gaussian, salt-and-pepper, speckle) to clean grayscale images, remove it
with classic filters (mean, Gaussian, median, bilateral), and compare the
filters fairly using MSE and PSNR.

**Current status: Stages 1–4 are complete.** They cover image loading,
validation, pixel statistics, the image quality metrics MSE and PSNR,
three reproducible noise models (Gaussian, salt-and-pepper, speckle), and
four noise-removal filters (mean, Gaussian, median, bilateral).
Comparison figures for all settings and the full experiment runner come in later stages.

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

## Run the tests

```powershell
python -m unittest -v
```

## Folder structure

| Folder | Purpose |
|---|---|
| `src/` | Image processing code (no interface code) |
| `demos/` | Small scripts that demonstrate one feature |
| `tests/` | Unit tests (Python's built-in `unittest`) |
| `experiments/` | Experiment runner (later stage) |
| `data/input/` | Original input images, which are never modified |
| `results/` | Generated outputs (ignored by Git) |
| `docs/` | Report notes, experiment log, references, presentation notes |
| `course_material/` | Professor's template and lecture slides |
