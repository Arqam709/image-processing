# Project Overview: Image Noise Addition and Removal

_Last updated: 2026-11-17 (after Stage 5B)_

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
| streamlit | 1.67.0 | Web interface "Image Noise Lab" (installed 2026-11-17 for Stage 5) |
| unittest | built in | Automated tests |
| Git | 2.49.0 | Local version history (no commits yet) |

## Scope
* **In scope:** 8-bit grayscale images; Gaussian, salt-and-pepper and speckle
  noise (implemented); mean, Gaussian, median and bilateral filters (implemented); MSE and PSNR (implemented).
* **In scope (Stage 5):** a local Streamlit web interface where a user uploads a photo, adds noise,
  applies a filter and compares the results. The interface calls the existing `src/` functions only.
* **Possible later:** SSIM, colour (RGB) images.
* **Out of scope:** deep-learning denoising, real camera noise modelling.

## Implementation stages
| Stage | Content | Status |
|---|---|---|
| 1 | Folder structure, docs, image loading and validation, pixel statistics, synthetic test image | ✅ Done |
| 2 | MSE and PSNR metrics (`src/metrics.py`, 31 tests, demo) | ✅ Done (63/63 tests pass) |
| 3 | Noise functions (`src/noise.py`, 38 tests, demo, 9 baseline experiments E001–E009) | ✅ Done (101/101 tests pass) |
| 4 | Filters (`src/filters.py`, 43 tests, demo, 8 filter experiments E010–E017 on baselines G002 and G005) | ✅ Done (144/144 tests pass) |
| 5 | Interactive web interface "Image Noise Lab" (Streamlit, `frontend/`), built in five sub-stages: | In progress |
| 5A | Upload, grayscale conversion, preview, dimensions, invalid-file handling (`frontend/`, 38 + 12 tests) | ✅ Done (194/194 tests pass) |
| 5B | Noise controls (three noise models, strength sliders, seed), original vs noisy display, 1:1 zoom, noise explanations (74 + 26 frontend tests in total) | ✅ Done (244/244 tests pass) |
| 5C | Filter controls (four filters), original / noisy / filtered display | Not started |
| 5D | MSE/PSNR, PSNR change, all-four-filter comparison and table | Not started |
| 5E | Downloads (noisy, filtered, CSV), final polish and checks | Not started |
| 6 | Experiment runner (CSV table + saved images) and static comparison figures for the report | Not started |
| 7 | Analysis of real results | Not started |
| 8 | draw.io block diagram | Not started |
| 9 | Optional: SSIM, RGB | Not decided |
| 10 | Optional: interactive interface | Replaced by Stage 5 (Streamlit chosen by the student on 2026-11-17 instead of the earlier Tkinter proposal) |
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
| D23 | Filters are thin wrappers around OpenCV (`cv2.blur`, `cv2.GaussianBlur`, `cv2.medianBlur`, `cv2.bilateralFilter`); we do not reimplement the algorithms | Tested, fast, standard implementations. Our code only validates inputs and fixes the settings. |
| D24 | Border handling is passed explicitly: `BORDER_REFLECT_101` for mean, Gaussian and bilateral; median always uses `BORDER_REPLICATE` inside OpenCV (no parameter) | `BORDER_REFLECT_101` is OpenCV's default, so behaviour is unchanged, but now visible in the code. Both border behaviours are checked by known-answer tests. |
| D25 | Kernel sizes must be odd integers ≥ 1 (all three kernel filters); booleans and floats are rejected | An odd window has a centre pixel. OpenCV rejects even sizes for Gaussian and median, but `cv2.blur` silently accepts them (observed), so we check ourselves for consistency. Size 1 = no change, as documented by OpenCV 5.x for the median filter and observed for all three. |
| D26 | Gaussian `sigma` ≥ 0, where 0 means "computed by OpenCV from the kernel size"; the same sigma is passed for x and y | OpenCV recommends specifying sigmaX and sigmaY explicitly. With kernel 3 and sigma 0 OpenCV uses fixed weights [1/4, 1/2, 1/4] (read in the OpenCV source, confirmed by a test). |
| D27 | Bilateral `diameter` must be odd and ≥ 3; `sigma_color` and `sigma_space` must be > 0 | OpenCV computes radius = d // 2 (at least 1), so d = 1, 2, 3 all behave the same and an even d acts like d + 1 (observed); sigmas ≤ 0 are silently replaced by 1 (observed). Rejecting these avoids misleading parameter labels. |
| D28 | Demo default settings: kernel 3 for mean/Gaussian/median; bilateral d = 5, sigmaColor = sigmaSpace = 50 | Kernel 3 is the smallest smoothing window and is the same for the three kernel filters. The bilateral values follow OpenCV's documented guidance (d = 5; equal sigmas; < 10 little effect, > 150 "cartoonish"). Not tuned for best PSNR. |
| D29 | Stage 4 demo recreates the Stage 3 noisy images G002 and G005 with seed 42 instead of reading them, and checks they equal the saved PNGs (read-only) | Works even when `results/` is empty; proves the filters see exactly the Stage 3 baselines; never overwrites Stage 3 files. New experiment IDs continue at E010. |
| D30 | The demo also reports MSE inside two regions (flat patch, 1-pixel line block) and the effect of each filter on the clean image | The first run showed that the line block dominates the whole-image MSE. Without the breakdown the whole-image numbers alone would be misleading (see report_notes §4.2). |
| D31 | The web interface is a separate `frontend/` folder. `frontend/app.py` is interface code only. `frontend/image_processing.py` holds small helpers and does **not** import Streamlit | The helpers can be tested with `unittest` without a web server. D8 still holds: `src/` never imports `frontend/`. No noise, filter or metric formula is copied into `frontend/`. |
| D32 | Uploads are decoded **in memory** with `cv2.imdecode(..., IMREAD_GRAYSCALE)`, exactly like Stage 1's `load_grayscale_image`, then checked with `validate_grayscale_image`. A second, colour decode is used only for display | The app and the Stage 1–4 demos see identical pixels (a test compares them for PNG and JPEG). We observed that a separate colour decode followed by `cvtColor` can differ by up to 11 levels on a random-noise JPEG, so we use one method everywhere. Nothing is written to disk. |
| D33 | Only PNG and JPEG are accepted. The extension must be .png/.jpg/.jpeg, **and** the file contents must start with the PNG or JPEG signature | OpenCV would also decode BMP or TIFF data hidden behind a .png name (observed), so the contents decide. Streamlit separately refuses other extensions before our code runs (observed with AppTest). |
| D34 | Limits: 20 MB per file (set on the upload widget and checked again in the helper), 25 megapixels maximum, and a "may be slow" warning above 4 megapixels | Keeps memory use and processing time reasonable while still accepting normal phone (12 MP) and camera (24 MP) photos. Larger images get a clear message asking the user to resize. |
| D35 | The original upload is kept as unchangeable `bytes`; the grayscale reference and the colour preview are **read-only** NumPy arrays inside a frozen record (`UploadedImage`) | Any accidental in-place change raises an error instead of silently corrupting the clean reference. Tests check this. |
| D36 | Every `st.image` call uses `output_format="PNG"` | Streamlit's default re-encodes NumPy arrays as JPEG with quality 90 (read in Streamlit 1.67's `image_utils.py`), which would change pixel values and hide or add noise. |
| D37 | `frontend/app.py` adds the project root, found from the file's own location (`__file__`), to `sys.path` once | Streamlit runs `app.py` as a script and adds only `frontend/` to the path. Using `__file__` (not the current folder) makes `import src...` work from any folder. We verified this from an unrelated folder. |
| D38 | `.streamlit/config.toml`: `server.address = "localhost"` and `browser.gatherUsageStats = false` | Observed: by default Streamlit listens on all network connections (other devices on the same Wi-Fi could open the app) and looks up the computer's public IP address. A local demo needs neither. |
| D39 | No caching: on each page rerun the upload is decoded again and the noise is generated again | Without a cache there can be no stale results. Re-checked in 5B: a full page rerun for a 12-megapixel photo took about 0.8 s (measured with AppTest). Noise generation took 0.07–0.46 s of that. To be reconsidered when four filters run per rerun (5C–5D). |
| D40 | `make_noisy_image(reference, noise_type, strength, seed)` only **selects** the function from `src/noise.py` (a table `NOISE_OPTIONS`) and passes strength and seed on **unchanged**. All strength and seed checks are those of `src/noise.py` | No noise formula exists twice. Tests compare the result pixel by pixel with direct calls (3 types × several strengths × 3 seeds) and reproduce the Stage 3 logged MSE values of E002, E005 and E008. |
| D41 | The app **requires** a seed: `None` is refused, although `src/noise.py` accepts it | Without a seed, every rerun (any click) would create new random noise. With a seed, the same settings always give identical pixels. |
| D42 | Slider ranges and defaults: σ 0–100 (step 1, default 25); amount 0–0.50 (step 0.01, shown as %, default 0.05); variance 0.00–0.25 (step 0.01, default 0.04); seed default 42 | The defaults are the Stage 3 baselines E002/E005/E008. The ranges include every Stage 3 value exactly and stay inside the `src/noise.py` rules (≥ 0; amount ≤ 1). Strength 0 is allowed and gives an unchanged copy, as documented in D20. The salt-and-pepper value stays a fraction (0.05); only its display is a percentage. |
| D43 | The seed box has no minimum; an invalid seed (e.g. −1) reaches `src/noise.py`, which raises an error that the page shows | The seed is checked by the existing rules, not by a second copy of them in the interface. |
| D44 | Each strength slider has its own key and `persist_state="page"` (a built-in Streamlit option) | Switching Gaussian → Speckle → Gaussian keeps the chosen σ instead of resetting it. No extra session-state code is needed. Checked by a test. |
| D45 | The noisy image is returned **read-only** | 5C/5D will give the same noisy image to every filter; read-only guarantees that none of them can change it. Stage 4 showed that the OpenCV filters accept read-only input. |
| D46 | The page shows a **pixel fingerprint**: the first 12 hex characters of SHA-256 over the image shape and pixel bytes | The user can *see* reproducibility: same settings → same code; a different seed → a different code. The tests read it to prove that the page shows exactly the `src/noise.py` result, and that unrelated controls (zoom) do not change the noise. |
| D47 | Display: both images are shrunk with `cv2.INTER_AREA` to fit 560 × 420 px (never enlarged, aspect ratio kept). A zoom panel shows the same square of both images (16–128 px), enlarged by repeating each pixel | This keeps portrait photos compact on a laptop screen and keeps both images the same size. Shrinking averages pixels and makes noise look weaker, so the zoom shows the real, unsmoothed pixel values. Display copies are never used for processing. |

## Architecture (Stages 5A–5B)
```
Browser ──upload──► frontend/app.py (Streamlit page: layout, messages, display)
                          │ file name + bytes
                          ▼
                    frontend/image_processing.py
                      load_uploaded_image():
                        check name, size, PNG/JPEG signature
                        cv2.imdecode(IMREAD_GRAYSCALE)  ── same as src/image_io.load_grayscale_image
                        src.image_io.validate_grayscale_image
                        pixel limit, colour preview, read-only arrays
                          │ UploadedImage (bytes, preview, grayscale reference)
                          ▼
Sidebar controls (noise type, strength, seed)
                          │ UploadedImage.grayscale (read-only clean reference)
                          ▼
                    make_noisy_image(reference, noise_type, strength, seed)
                      NOISE_OPTIONS table ──► src/noise.py
                        add_gaussian_noise / add_salt_and_pepper_noise / add_speckle_noise
                          │ noisy image (new, read-only uint8)
                          ▼
                    frontend/app.py shows Original Grayscale | Noisy (fit_for_display),
                    zoom (crop_square + enlarge_pixels), pixel fingerprint,
                    dimensions, src.image_io.get_image_info / format_image_info
```
Later sub-stages will add calls to `src/filters.py` (5C) and `src/metrics.py` (5D).

## Current limitations of the web interface (Stage 5B)
* Upload and noise work. There are no filter, metric or download features yet.
* The side-by-side view is shrunk for large photos, which makes noise look weaker than it is. The zoom panel shows the real pixels; its position is chosen with two sliders, not by clicking on the image.
* Switching noise type keeps each slider's value only while the user stays on the page. A browser reload resets all controls to their defaults.
* Transparency is ignored. Only PNG colour types 4 and 6 are detected; palette PNGs with a transparency chunk are not flagged.
* The pixel limit is checked after decoding. Extremely large images are still limited by OpenCV's own decoder limit.
* Verified automatically: the helper (74 tests), the page logic (26 Streamlit `AppTest` tests), and that the real server starts and answers on localhost. **Not yet verified:** how the page looks in a real browser, including the slider layout and the zoom panel. The student should check this manually.

## Open items
* `course_material/template.docx` was read on 2026-11-16. Findings are in `report_notes.md` §0.
* The student's own photograph is not yet in `data/input/`.
* OpenCV documentation URLs (V1, V2, V4, V12 in `references.md`) should be opened once in a browser, because the site blocks automated checks.
* Browser check by the student for Stages 5A and 5B: launch the app and follow the manual steps in the stage summaries.
* Filter results so far cover only one setting per filter, two noise cases, one image and one seed. Comparing several kernel sizes and all nine noise baselines is planned for the experiment runner (Stage 6).
