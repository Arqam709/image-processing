# Report Notes

_Last updated: 2026-11-16 (after Stage 2)_

These are **preparation notes**, not the report. Each section separates:

* **Confirmed:** facts from course material, verified sources, or our own code and tests.
* **Proposed:** planned methodology, not implemented yet.
* **Implemented:** working code that has been tested.
* **Not yet collected:** results that do not exist yet. Never fill these in without real program runs.

---

## 0. Professor's template: verified locally

`course_material/template.docx` was read on 2026-11-16 (text, tables, page setup and images extracted with a read-only script).

### Confirmed: structure and instructions in the template
| Section in template | Instruction text in the template |
|---|---|
| Abstract | Example paragraph only (about image processing in daily life) |
| Table of contents | A manually typed table: 1 Introduction, 2 Datasets, 3 Methods, 4 Results and discussion, 5 Conclusion, with page numbers |
| 1 Introduction | Example paragraph only |
| 2. Datasets (if applicable) | "If you use image data." |
| 3. Methods | "Please use draw.io for ploting", followed by an example figure with the caption "Figure1: Block diagram of the proposed work [1]." |
| 4. Results and discussion | "Simulation results should be here", followed by two example images |
| 5. Conclusion | "Summarized the whole project" |
| References | "Please put a least five Reference", followed by one example reference in IEEE style, numbered "[1]." in a two-column table |
| Index | "Please put your source code here if you it is applicable" |

### Confirmed: formatting facts read from the file
* Page size US Letter (8.5 × 11 in), all margins 1 inch.
* Theme body font **Aptos**, default size 12 pt. Some text uses 10 pt.
* Paragraph alignments used: justified and centred.
* Section titles are bold text in the Normal style, not Word heading styles. The table of contents is a typed table, not an automatic Word TOC.
* Figure caption pattern: "Figure1: <description> [ref]." placed with the figure.
* **The example reference is IEEE style** (authors, "title," venue, vol., pp., year, doi), so our provisional IEEE choice matches the template.

### Confirmed: template content that is NOT ours
* The abstract and introduction paragraphs are example text.
* The three images are examples: a block diagram for a speech-dataset pipeline (dashed rounded group boxes, icons, arrows), and two sampling demonstrations. They show the expected *style* only.
* Example reference [1] is a speech-detection paper and is not related to our topic.

### Not specified in the template
Page limit, deadline, number of figures, font requirements for the student's text, and heading numbering style (the template itself mixes "1 Introduction", "2.Datasets" and "3. Methods"). Do not invent rules for these. Ask the professor if needed.

> **Course context (lecture 1, PDF page 2):** Final exam 40%, Project 60%.
> The project part is Project work 15%, Written report 25%, Oral presentation 10%,
> Class contribution 10%.

---

## Abstract
* **Confirmed:** nothing yet.
* **Not yet collected:** main findings. Write the abstract only after the experiments (Stage 7).
* Material to collect: one-sentence problem, method (noise types, filters, metrics), key numerical finding, conclusion.

## Table of Contents
* The template uses a typed table (see section 0). Fill it in at the end.

---

## 1. Introduction

### Confirmed (lecture 1, "Simple Introduction to Digital Image Processing")
* A signal is a function that carries information. An image is a **2-D signal f(x, y)** (PDF p. 4).
* An image is a 2-D collection of **pixels**. Each pixel stores an intensity or colour value (PDF p. 5).
* **Pixel** = picture element, the smallest addressable element of a digital image (PDF p. 10).
* An 8-bit grayscale pixel uses 1 byte. The values range from **0 (black) to 255 (white)** (PDF pp. 6–8).
* Pixels in rows and columns form an **intensity matrix I(x, y)**. Example: a 512×512 image has 262,144 pixels, which is 256 KiB of raw 8-bit storage (PDF p. 9).
* "Spatial" refers to position (x, y) in the image (PDF p. 11).
* Image types: grayscale (1 value per pixel), RGB (3 values), RGBA (4 values, alpha = transparency) (PDF p. 13).
* Image processing changes an input image into a useful output image, for example by improving quality, **removing noise** or finding edges (PDF p. 14).
* Workflow: Acquire → Enhance → Analyze → Output (PDF p. 15).
* Sampling decides how many pixels represent the image. Quantization decides how many intensity levels are available (PDF pp. 17–18).
* **"Noise is unwanted variation in an image. Filtering can reduce noise and produce a cleaner image."** (PDF p. 20, "Noise Removal")
* Spatial filtering: "A small filter moves across the image. It uses neighboring pixels to smooth, sharpen, or detect patterns." The example uses a 3×3 neighbourhood (PDF p. 21).
* Applications listed: medical imaging, security, satellites, photography, industry, biology (PDF p. 27).

### Confirmed (verified literature, for the "how do we measure quality" part)
* Wang and Bovik [V5]: MSE "remains the standard criterion for the assessment of signal quality and fidelity" and is "the method of choice for comparing competing signal processing methods", even though it "has been widely criticized for serious shortcomings, especially when dealing with perceptually important signals such as speech and images."

### Proposed (needs verified references before use in the report)
* Why noise occurs: sensor noise, low light, transmission errors, and so on. Each claim needs a verified source.
* Real-world importance of denoising.
* Project objectives (from `project_overview.md`).

### Not yet collected
* Verified literature references for noise sources and applications.

---

## 2. Datasets
Template instruction: "If you use image data." We do, so this section is required.

### Confirmed / Implemented
**Image D1: `synthetic_test_image.png`**
| Field | Value |
|---|---|
| Source | Generated by our own code: `src/synthetic_image.py`, function `create_synthetic_test_image()` |
| Location | `data/input/synthetic_test_image.png` (created by the demo; it can always be regenerated) |
| Licence | Our own work, no restrictions |
| Dimensions | 256 × 256 pixels (measured by `demos/demo_image_loading.py` on 2026-11-16) |
| Colour format | 8-bit grayscale (`uint8`), PNG (lossless) |
| Pixel statistics (measured) | min 20, max 240, mean 120.59, std 66.64, 155 distinct intensity levels |
| Preprocessing | None. It is created directly as grayscale. |
| Why selected | We know every pixel exactly, and it contains the structures that make filters behave differently (listed below). |

Regions (positions are fractions of the image height/width):
* Background: horizontal gradient from 50 (left) to 200 (right), a smooth change.
* Dark square, value 20: rows 0.10–0.42, columns 0.08–0.40. It has straight sharp edges.
* Bright circle, value 235: centre (0.26 h, 0.70 w), radius 0.16 × size. It has curved edges.
* Flat patch, value 128: rows 0.55–0.90, columns 0.08–0.45. Constant intensity, so noise is easy to see.
* Fine detail: 1-pixel-wide lines (value 240) every 4 columns on a dark block (value 40), rows 0.55–0.90, columns 0.55–0.92.
* Values avoid exactly 0 and 255, so salt-and-pepper noise pixels can be identified later.

### Proposed
**Image D2: student's own photograph** (not yet provided). Record these fields:
| Field | Value |
|---|---|
| Filename | _TBD_ |
| Source | Taken by the student (record device and date) |
| Licence | Own work |
| Original dimensions / format | _TBD (measure with the demo)_ |
| Preprocessing | Conversion to grayscale during loading (Y = 0.299R + 0.587G + 0.114B [V1]). Whether to resize is _undecided_. |
| Why selected | Real-world content (textures, natural edges) to complement the synthetic image |

Notes for D2: avoid identifiable people (privacy). Check whether phone photos
appear rotated after loading (EXIF orientation); this is not tested yet.

**Possible D3:** a standard test image, used only with a verified source and licence.

---

## 3. Methods
Template instruction: "Please use draw.io for ploting" (block diagram, see 3.5).

### 3.1 Image loading and representation (Stage 1)
* **Implemented:** `src/image_io.py`
  * `load_grayscale_image(path)`: reads the file bytes (`numpy.fromfile` [V3]) and decodes them as grayscale (`cv2.imdecode` with `IMREAD_GRAYSCALE` [V2]). The result is a 2-D `uint8` NumPy array of shape (height, width), the intensity matrix I(x, y).
  * Colour conversion: OpenCV documents the luminance formula **Y = 0.299·R + 0.587·G + 0.114·B** [V1]. With `IMREAD_GRAYSCALE` the conversion happens inside the image codec [V2]. In our test, a pure green pixel gave 149 through decoding and 150 through `cv2.cvtColor`, so results can differ by 1 because of rounding.
  * Validation: clear errors for a wrong path type, a missing file, a folder, an unsupported extension, an empty file, or undecodable content.
  * `validate_grayscale_image(image)`: the image must be a non-empty 2-D `uint8` array.
  * `get_image_info(image)`: height, width, total pixels, dtype, bit depth, raw size in bytes, min, max, mean, standard deviation, and number of distinct intensity levels.
    * Mean: μ = (1/N) Σ I(x, y)
    * Standard deviation: σ = √[(1/N) Σ (I(x, y) − μ)²] (population form, NumPy default)
    * Computed in `float64` to avoid `uint8` overflow.
  * `save_grayscale_image(image, path, overwrite=False)`: refuses to overwrite existing files by default.
* **Implemented:** `src/synthetic_image.py`, which builds the D1 image with NumPy array slicing and a circle mask (y − cy)² + (x − cx)² ≤ r².
* **Design decisions:** see D1–D8 in `project_overview.md`.
* **Limitations:** grayscale only; 16-bit images are converted to 8-bit by the decoder; EXIF orientation is not yet tested.

### 3.2 Image quality metrics: MSE and PSNR (Stage 2)

**Implemented:** `src/metrics.py`. Tests: `tests/test_metrics.py` (31 tests).

**Mean Squared Error**

  MSE = (1 / (M·N)) · Σₓ Σᵧ [ I(x, y) − K(x, y) ]²

| Symbol | Meaning |
|---|---|
| I(x, y) | Pixel of the **original** (clean reference) image at row x, column y |
| K(x, y) | Pixel of the **processed** image (noisy or filtered) at the same position |
| M, N | Number of rows and columns; M·N = total number of pixels |
| Σ | Sum over all pixel positions |

* MSE = 0 means the images are identical. Larger MSE means larger average difference.
* The unit is "intensity levels squared". For 8-bit images the largest possible value is 255² = 65025.
* Squaring makes every difference positive and penalises large differences much more than small ones.

**Peak Signal-to-Noise Ratio**

  PSNR = 10 · log₁₀( MAX² / MSE )   [dB]

| Symbol | Meaning |
|---|---|
| MAX | Largest possible pixel value. For 8-bit images MAX = 2⁸ − 1 = **255** |
| MSE | Mean squared error from above |
| dB | Decibels, a logarithmic scale for ratios: every +10 dB means the error power is 10 times smaller |

* This is the same formula documented by OpenCV [V4] ("R is the maximum integer value of depth (e.g. 255 in the case of CV_8U data)") and by Wang and Bovik [V5] ("L is the dynamic range of allowable image pixel intensities").
* Higher PSNR means the processed image is closer to the original. Identical images have MSE = 0, so PSNR is infinite.
* PSNR is a rescaled MSE. Wang and Bovik [V5]: PSNR "is useful if images having different dynamic ranges are being compared, but otherwise contains no new information relative to the MSE." We report both because PSNR in dB is the common way to present results.

**Why float64 arithmetic**
* Images are `uint8` (0–255). In NumPy, uint8 array subtraction **wraps around silently**: 10 − 12 gives 254, not −2 (−2 + 256 = 254). We observed this, with no warning, in `demos/demo_metrics.py`. NumPy documents that "the fixed size of NumPy numeric types may cause overflow errors when a value requires more memory than available in the data type" [V6].
* Squared differences can reach 65025, and their sum over a 1000×1000 image reaches 6.5 × 10¹⁰. Both are far too large for uint8.
* Therefore both images are converted to `float64` **before** subtracting. A test proves that the uint8 version would give the wrong answer (a deliberately buggy uint8 version failed 6 of our tests).

**Implementation (how the code works)**
1. `_validate_image_pair`: both inputs must be valid 8-bit grayscale images (reusing Stage 1's `validate_grayscale_image`) with the **same shape**. Errors name the wrong argument ("original" or "processed").
2. `mse`: convert both to float64, subtract, square, average with `np.mean`, and return a Python `float`.
3. `psnr`: call `mse` (which also validates). If MSE is exactly 0.0, return `math.inf`; otherwise return 10·log₁₀(255² / MSE).
4. No new libraries: only NumPy and Python's `math`.

**Design decision: explicit infinity instead of cv2.PSNR**
* The OpenCV source code (`modules/core/src/norm.dispatch.cpp`, 4.x and 5.x branches) computes `20*log10(R/(diff+DBL_EPSILON))`, where diff = √MSE and DBL_EPSILON ≈ 2.22 × 10⁻¹⁶. Adding this tiny number avoids division by zero, but for identical images it gives 20·log₁₀(255 / 2.22×10⁻¹⁶) = **361.20 dB**, a finite number. We measured exactly this value.
* We return true infinity, so "identical" is never confused with "very good". It also prints clearly as "infinity" in tables.
* For non-identical images our PSNR equals `cv2.PSNR` to at least 6 decimal places (5 random image pairs and a modified synthetic image, tested).

**How the metrics will be used later (proposed, Stages 6–7)**
* For every noise setting: PSNR(original, noisy) is the **baseline**. Then PSNR(original, filtered) for each filter, always on the same noisy image.
* A filter helps if its PSNR is higher (MSE lower) than the noisy baseline. Filters are compared by their PSNR under identical conditions.

**Limitations**
* MSE/PSNR compare pixel by pixel. They ignore *where* the errors are and *what kind* they are. Wang and Bovik [V5] show that distorted versions of an image can have "nearly identical" MSE "even though the same images present dramatically (and obviously) different visual quality."
* Our own validation shows the same effect (section 4.0): a uniform +10 brightness shift (hard to notice) scored a much **lower** PSNR (28.13 dB) than 10 clearly visible white dots (52.32 dB).
* PSNR needs a clean reference image. This is fine for our controlled experiments, but not possible for real photos where no clean version exists.
* A possible extension is SSIM [C3, bibliographic data verified], which is designed to compare structure.

### 3.3 Noise models (Stage 3)
* **Proposed:** Gaussian (additive, σ on the 0–255 scale), salt-and-pepper (fraction p of pixels set to 0 or 255), speckle (multiplicative, I + I·n). Fixed random seed, calculation in float, clipping to [0, 255], then conversion to `uint8`.

### 3.4 Filters (Stage 4)
* **Proposed:** mean (`cv2.blur`), Gaussian (`cv2.GaussianBlur`), median (`cv2.medianBlur`), bilateral (`cv2.bilateralFilter`).

### 3.5 Block diagram workflow (for draw.io, Stage 8)
Status of each box: [I] = implemented, [P] = proposed. The template's example diagram uses dashed rounded group boxes, icons and arrows, with the caption "Figure1: Block diagram of the proposed work".
```
[I] Input image file (data/input)
      │  load_grayscale_image + validation
      ▼
[I] Clean grayscale image I (uint8 matrix)  ───────────────┐
      │  add noise (type, intensity, seed)        [P]        │ reference
      ▼                                                     │
[P] Noisy image  ──► [P] Filter (mean / Gaussian / median / bilateral, parameters)
      │                         │
      │ baseline                ▼
      │                  [P] Filtered image
      ▼                         ▼
[I] Metrics vs. clean image: MSE, PSNR  ◄───────────────────┘
      ▼
[P] Results table (CSV) + comparison figures (PNG)
```

---

## 4. Results and Discussion
Template instruction: "Simulation results should be here".

### 4.0 Preliminary metric validation (Stage 2): NOT noise removal results
These numbers only check that MSE and PSNR are calculated correctly. **No noise was added and no filter was applied.** Source: `python -m demos.demo_metrics`, run on 2026-11-16 (log IDs MV001–MV004 in `experiment_log.md`).

| ID | Comparison (original vs …) | Changed pixels | MSE | PSNR (ours) | cv2.PSNR | Hand check |
|---|---|---|---|---|---|---|
| MV001 | 2×2 example [[10,20],[30,40]] vs [[12,20],[30,36]] | 2 of 4 | 5.0 | 41.1411 dB | not run | 20/4 = 5; 10·log₁₀(13005) |
| MV002 | Synthetic image, case A: 10 pixels 128 → 178 | 10 of 65,536 | 0.3815 | 52.3162 dB | 52.3162 dB | 10·50²/65536 = 0.3815 |
| MV003 | Synthetic image, case B: every pixel +10 | 65,536 of 65,536 | 100.0000 | 28.1308 dB | 28.1308 dB | 10² = 100 |
| MV004 | Synthetic image vs identical copy | 0 | 0.0 | infinity | 361.2020 dB | MSE = 0 |

Figure (for report and presentation, if useful): `results/figures/stage2_metric_validation.png` (300 dpi, generated with `--save-figure`; regenerate any time).

Observations (from these real runs):
* Our MSE and PSNR match the hand calculations and `cv2.PSNR` (to 4 decimals here; to 6 decimals in the automated tests).
* Case B looks almost the same as the original to a human (slightly brighter), but scores far worse (28.13 dB) than case A (52.32 dB), where 10 bright dots are visible. This demonstrates the limitation described in [V5]: PSNR measures numerical difference, not visual importance.
* For identical images, our PSNR is infinity while OpenCV reports 361.20 dB.

### 4.1+ Noise removal experiments
* **Not yet collected.** Requires Stages 3–6. Every number must be traceable to an entry in `experiment_log.md`.
* Planned contents: experimental setup, images tested, noise and filter parameters, MSE/PSNR table, comparison figures, observations, explanations, limitations.

## 5. Conclusion
Template instruction: "Summarized the whole project".
* **Not yet collected.** Write it after Stage 7.
* Achievements so far (engineering, not results): reliable image loading with validation, Unicode path support, verified MSE/PSNR implementation, 63 passing unit tests.

## References
See `references.md`. Style: IEEE numbered (confirmed by the template's example reference). Template: "Please put a least five Reference". **6 sources are verified so far (V1–V6).** One of them (V5) is a peer-reviewed paper; the others are official documentation.

## Index (source code)
Template: "Please put your source code here if you it is applicable".
Current source files: `src/image_io.py`, `src/synthetic_image.py`, `src/metrics.py`, `demos/demo_image_loading.py`, `demos/demo_metrics.py`.
Final listing to be prepared at the end.
