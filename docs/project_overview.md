# Project Overview: Image Noise Addition and Removal

_Last updated: 2026-11-16 (after Stage 3)_

## Objective
Build a Python system that takes a clean digital image, adds controlled noise,
removes the noise with classic spatial filters, and measures how well each
filter restores the image.

## Problem statement
Real images are often corrupted by noise, which is unwanted variation in pixel
intensity (lecture 1, PDF page 20). Different kinds of noise need different filters.
A filter that removes one noise type well may blur edges or fail on another type.
We want to show, with measured results, which filter works best for which noise
and why.

## Proposed solution
1. Load a clean grayscale image (the reference).
2. Add noise of a known type and strength, using a fixed random seed.
3. Apply several filters to the **same** noisy image.
4. Compare each result with the clean reference using MSE and PSNR.
5. Save the images, a results table, and labeled comparison figures.

## Technologies (versions verified in `.venv` on 2026-11-16)
| Tool | Version | Used for |
|---|---|---|
| Python | 3.12.10 | Programming language |
| opencv-python | 5.0.0.93 | Image decoding/encoding, filters |
| numpy | 2.5.5 | Pixel arrays, noise generation, statistics |
| matplotlib | 3.11.2 | Figures and histograms |
| unittest | built in | Automated tests |
| Git | 2.49.0 | Local version history (no commits yet) |

## Scope
* **In scope:** 8-bit grayscale images; Gaussian, salt-and-pepper and speckle
  noise (implemented); mean, Gaussian, median and bilateral filters; MSE and PSNR (implemented).
* **Possible later:** SSIM, colour (RGB) images, a simple Tkinter interface.
* **Out of scope:** deep-learning denoising, real camera noise modelling.

## Implementation stages
| Stage | Content | Status |
|---|---|---|
| 1 | Folder structure, docs, image loading and validation, pixel statistics, synthetic test image | ✅ Done |
| 2 | MSE and PSNR metrics (`src/metrics.py`, 31 tests, demo) | ✅ Done (63/63 tests pass) |
| 3 | Noise functions (`src/noise.py`, 38 tests, demo, 9 baseline experiments E001–E009) | ✅ Done (101/101 tests pass) |
| 4 | Filters (mean, Gaussian, median, bilateral) | Not started |
| 5 | Visualization (comparison figures) | Not started |
| 6 | Experiment runner (CSV table + saved images) | Not started |
| 7 | Analysis of real results | Not started |
| 8 | draw.io block diagram | Not started |
| 9 | Optional: SSIM, RGB | Not decided |
| 10 | Optional: interactive interface (Tkinter proposed) | Needs approval |
| 11 | Report and presentation preparation | Not started |

## Important design decisions
| ID | Decision | Reason |
|---|---|---|
| D1 | Read files with `numpy.fromfile` + `cv2.imdecode` instead of `cv2.imread` | We tested `cv2.imread` on Windows and it returned `None` for a path with Turkish characters (`görüntü_İ.png`). The fromfile + imdecode approach worked. |
| D2 | Work with 8-bit grayscale (`uint8`, 0–255) first | One value per pixel keeps the algorithms easy to understand and explain. |
| D3 | `save_grayscale_image` refuses to overwrite files unless `overwrite=True` | Protects original input images. |
| D4 | Statistics are computed in `float64` | Summing many `uint8` values would overflow. A test checks a 100×100 white image. |
| D5 | Check for empty (0-byte) files before decoding | OpenCV crashes with an assertion error on an empty buffer (we observed this). |
| D6 | Synthetic test image avoids exactly 0 and 255 (range 20–240) | Salt-and-pepper noise pixels are exactly 0 or 255, so they stay easy to identify. |
| D7 | Use Python's built-in `unittest` | No extra dependency (pytest is not installed). |
| D8 | Image processing code (`src/`) never imports interface code | Logic can be tested on its own, and the GUI can be added later without changes. |
| D9 | IEEE numbered citations | Chosen by the student; the template's example reference is also IEEE style. |
| D10 | Our own `psnr()` returns `math.inf` for identical images instead of using `cv2.PSNR` | OpenCV adds DBL_EPSILON and returns 361.20 dB for identical images (verified in its source code and measured). Infinity is mathematically correct and cannot be mistaken for "very good". |
| D11 | MSE subtracts in float64, never uint8 | NumPy uint8 subtraction wraps around silently (10 − 12 = 254). A deliberately buggy uint8 version failed 6 tests. |
| D12 | Metrics accept only same-shape, 2-D uint8 images, and errors name the bad argument | Prevents silent broadcasting or comparing wrong images. A version without validation failed 7 tests. |
| D13 | MAX = 255 is a fixed constant (no parameter) | All our images are 8-bit, so a parameter would only add a way to make mistakes. |
| D14 | Every noise call creates its own `np.random.default_rng(seed)`; the global `np.random` state is never used | NumPy's recommended generator; reproducible; one call cannot affect another. A version using the global state failed our test. |
| D15 | Seeds must be `None` or non-negative integers; booleans are rejected | NumPy itself rejects negative seeds but accepts `True` (observed), which would silently act as seed 1. |
| D16 | Gaussian/speckle: calculate in float64, then **round** (`np.rint`), **clip** to [0, 255], convert to uint8 | Rounding avoids the downward bias of truncation; clipping avoids uint8 wrap-around. Both bugs were caught by tests in mutation checks. |
| D17 | Salt-and-pepper selects an **exact** number of pixels without replacement: selected = ⌊amount·N + 0.5⌋, salt = ⌊selected/2⌋, pepper = rest | Every run with the same amount corrupts exactly the same number of pixels, which can be checked by hand. This deliberately differs from scikit-image, which decides per pixel. |
| D18 | Salt = 255, pepper = 0 (the extreme values of 8-bit images) | Matches the definition "maximum or minimum gray level" [V9]. |
| D19 | Speckle uses g = f + f·n with Gaussian n (γ = 1) | The same form as scikit-image's 'speckle' mode; simple and clearly brightness-dependent. Documented as a simplified model. |
| D20 | Strength 0 returns a copy; invalid strengths (negative, NaN, ±∞, bool, non-numbers) raise errors | Predictable behaviour; a copy means callers can never accidentally modify the original. |
| D21 | Demo seed = 42 for every experiment; outputs are named `<image>__<noise>_<param><value>__seed<seed>.png` | The file name alone tells you how to reproduce the image. |
| D22 | Generated results (noisy PNGs, CSV, figures) may be overwritten by the demo, but inputs never | Results are deterministic and can be regenerated; `save_grayscale_image(..., overwrite=True)` is used only for `results/`. |

## Open items
* `course_material/template.docx` was read on 2026-11-16. Findings are in `report_notes.md` §0.
* The student's own photograph is not yet in `data/input/`.
* OpenCV documentation URLs (V1, V2, V4 in `references.md`) should be opened once in a browser, because the site blocks automated checks.
