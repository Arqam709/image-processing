# Report Notes

_Last updated: 2026-11-16 (after Stage 3)_

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

### Confirmed (verified literature): why image noise matters
* **Where noise comes from.** Fan et al. [V8]: "Owing to the influence of environment, transmission channel, and other factors, images are inevitably contaminated by noise during acquisition, compression, and transmission, leading to distortion and loss of image information." Also: "the images captured by modern cameras are inevitably degraded by noise, which leads to deteriorated visual image quality."
* **Why it is a problem for later processing.** Fan et al. [V8]: "With the presence of noise, possible subsequent image processing tasks, such as video processing, image analysis, and tracking, are adversely affected. Therefore, image denoising plays an important role in modern image processing systems."
* **Impulse (salt-and-pepper) noise.** Ma and Nie [V9]: "Digital images can be corrupted by impulse noise due to bit errors in the process of image acquisition and transmission." It "can not only significantly deteriorate the quality of an image, but also bring some difficulty to the subsequent image analysis such as image segmentation, edge detection and classification."
* **Speckle noise.** Yu et al. [V10]: "ultrasound images are inevitably corrupted by speckle noise due to the coherent imaging mechanism", which "reduces the sharpness of image details and complicates the diagnosis". Denoising as "a pre-processing step … will also benefit image post-processing tasks such as image segmentation, classification and registration."
* **The core difficulty of denoising.** Fan et al. [V8]: "since noise, edge, and texture are high frequency components, it is difficult to distinguish them in the process of denoising and the denoised images could inevitably lose some details." Our noisy images will let us test this trade-off in Stage 4.

### Proposed (still to write)
* Project objectives (from `project_overview.md`).
* Optional: more real-world examples, each needing its own verified source.

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

How D1 is used in Stage 3 (confirmed by the actual runs):
* D1 is the **clean reference** for every noise experiment (E001–E009). All MSE/PSNR values are measured against it.
* Because D1 contains no 0 or 255, every salt-and-pepper pixel that is *selected* is also *visibly changed* (measured: 1,311 / 3,277 / 6,554 selected = changed).
* The dark square (value 20) next to the bright circle (value 235) makes the brightness dependence of speckle noise easy to see.
* The values 20 and 240 lie close to the limits 0 and 255, so strong Gaussian/speckle noise is clipped there. This is visible in the results (see §4.1).
* Derived noisy images are stored in `results/noisy/` with names like `synthetic_test_image__gaussian_sigma25__seed42.png`. They can be regenerated exactly, so Git ignores them.

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

**Implemented:** `src/noise.py`. Tests: `tests/test_noise.py` (38 tests). Demo: `demos/demo_noise.py`.

#### 3.3.0 Rules shared by all three noise functions
* **Input:** a valid 2-D `uint8` image (checked with Stage 1's `validate_grayscale_image`), a strength parameter, and an optional `seed`.
* **Output:** a **new** 2-D `uint8` array. The input is never modified (tested, including that the result shares no memory with the input).
* **Strength validation:** it must be a real number (int or float), finite (not NaN or ±∞) and ≥ 0. Booleans are rejected (`True` would otherwise count as 1). Salt-and-pepper `amount` must also be ≤ 1. Strength 0 returns an unchanged copy.
* **Random numbers:** `numpy.random.default_rng(seed)` creates a private Generator for each call [V7]. NumPy documents that "Our RNGs are deterministic sequences and can be reproduced by specifying a seed integer" [V7], and that the old `np.random.*` functions use "a single global RandomState instance" [V7]. We never touch that global state (tested).
  * Same image + strength + seed always gives exactly the same output (tested; reruns of the demo produced byte-identical PNG files).
  * The seed must be `None` or a non-negative integer, as NumPy requires [V7]. We reject booleans ourselves, because NumPy would accept `True` as a seed (we observed this).
* **Back to uint8 (Gaussian and speckle):** the noisy values are calculated in `float64`, then (1) rounded to the nearest whole number with `np.rint` (exact halves go to the even number, e.g. 2.5 → 2), (2) clipped to [0, 255], and (3) converted to `uint8`.
  * Without clipping, `uint8` conversion would wrap around (270 → 14). A deliberately buggy wrap-around version failed our clipping tests.
  * Without rounding, `astype` would *truncate* (cut off the decimals), which biases every value downwards. A buggy truncating version failed our mean/standard-deviation test.
  * **Consequence of clipping:** the noise near 0 and 255 is cut off, so the real error is *smaller* than the noise model predicts (measured in §4.1).

#### 3.3.1 Gaussian noise: `add_gaussian_noise(image, sigma, seed=None)`
* **Definition:** additive noise. An independent random value from a normal (bell-shaped) distribution is added to every pixel. This is the standard additive white Gaussian noise (AWGN) model of the denoising literature: "y = x + n, where y is the observed noisy image, x is the unknown clean image, and n represents additive white Gaussian noise (AWGN) with standard deviation σ" [V8].
* **Model:** g(x, y) = f(x, y) + n(x, y),  n(x, y) ~ N(0, σ²), then rounded and clipped to [0, 255].

| Symbol | Meaning |
|---|---|
| f(x, y) | original (clean) pixel |
| g(x, y) | noisy pixel |
| n(x, y) | random noise value for this pixel, independent of all other pixels |
| N(0, σ²) | normal distribution with mean 0 and variance σ² |
| σ (sigma) | standard deviation in intensity levels (0–255 scale) |

* **Parameter σ:** controls **how much** pixels change, **not how many**. Almost every pixel changes (E001: 62,782 of 65,536 = 95.8%; the rest received noise that rounded to 0). About 68% of noise values lie within ±σ and about 95% within ±2σ (property of the normal distribution). Values used: σ = 10, 25, 50.
* **Implementation:** `rng.normal(loc=0.0, scale=sigma, size=image.shape)` [V7, documented as "Draw random samples from a normal (Gaussian) distribution", with `scale` = "Standard deviation"], added to the float64 image, then rounded, clipped and converted.
* **Verified by tests:** on a flat 400×400 image of 128 with σ = 10, the measured noise mean is ≈ 0 and its standard deviation ≈ 10. MSE ≈ σ² when there is no clipping. The output exactly matches the formula.
* **Limitations:** a simplified model. Real camera noise also depends on brightness and can be correlated between neighbouring pixels. Clipping makes the effective noise smaller than σ near black and white.

#### 3.3.2 Salt-and-pepper (impulse) noise: `add_salt_and_pepper_noise(image, amount, seed=None)`
* **Definition:** a kind of impulse noise where "each corrupted pixel takes either the maximum or minimum gray level" [V9]: 255 = salt (white), 0 = pepper (black). All other pixels stay **exactly** unchanged.
* **Model:**
  g(x, y) = 255 if (x, y) ∈ S_salt;  0 if (x, y) ∈ S_pepper;  f(x, y) otherwise,
  where S_salt and S_pepper are disjoint random sets of pixel positions.
* **Parameter `amount`:** the fraction of pixels **selected** (0.02 = 2%). Values used: 0.02, 0.05, 0.10.
* **Rounding rule (our design, tested):**
  * selected = round-half-up(amount × N) = ⌊amount × N + 0.5⌋, where N is the number of pixels
  * salt = ⌊selected / 2⌋; pepper = selected − salt (pepper gets the extra pixel when the count is odd)
  * Our 256×256 image: 0.02 → 1310.72 → **1,311** (655 + 656); 0.05 → 3276.8 → **3,277** (1,638 + 1,639); 0.10 → 6553.6 → **6,554** (3,277 + 3,277).
* **Implementation:** `rng.choice(N, size=selected, replace=False)` picks `selected` *different* flat positions [V7: `replace` = "Whether the sample is with or without replacement"]. `np.unravel_index` converts them to (row, column). The positions come in random order, so the first `salt` become 255 and the rest 0.
* **Selected vs. visibly changed:** a selected pixel that already had the value it is given does not change (255 + salt stays 255; 0 + pepper stays 0). So changed ≤ selected. In a test with an all-white image and amount 0.5: 5,000 selected, but only the 2,500 pepper pixels changed. In our synthetic image (no 0 or 255) the two counts are equal.
* **Design choice vs. other libraries:** scikit-image decides for **each pixel independently** whether it is corrupted (a Bernoulli trial with probability `amount`) [V11], so the number of noisy pixels is only *approximately* amount × N. We select an **exact** number without replacement, so every run with the same amount corrupts exactly the same number of pixels. That makes the experiments easier to compare and to check by hand.
* **Limitations:** real impulse noise can also take random values (not only 0/255). Ma and Nie call this "random-valued noise" [V9]. That type is not modelled here.

#### 3.3.3 Speckle (multiplicative) noise: `add_speckle_noise(image, variance, seed=None)`
* **Definition:** noise whose size is proportional to the pixel's own brightness ("signal-dependent" [V10]).
* **Model:** g(x, y) = f(x, y) + f(x, y) · n(x, y),  n ~ N(0, variance), then rounded and clipped.
  * This is the same form scikit-image calls 'speckle': "out = image + n * image, where n is Gaussian noise with specified mean & variance" [V11].
  * Yu et al. [V10] write the more general form u = v + v^γ · η, with η zero-mean Gaussian with variance σ². Our model is the case **γ = 1**. They note that γ = 0.5 is often used for ultrasound images.
* **Parameter `variance`:** the variance of n, with no unit (it is relative to brightness). The standard deviation of n is √variance: 0.01 → 0.1 (±10% of the pixel value), 0.04 → 0.2, 0.10 → 0.316. Values used: 0.01, 0.04, 0.10.
* **Why brightness matters:** the change f·n has standard deviation f·√variance. With variance 0.01, a pixel of 40 changes by about ±4 levels and a pixel of 160 by about ±16 (tested: measured 4.0 and 16.0). A pixel of 0 never changes (tested).
* **Implementation:** `rng.normal(0, sqrt(variance), shape)`, multiplied by the float64 original, added to it, then rounded, clipped and converted.
* **Limitations:** this is a *simplified* multiplicative model, **not** a complete physical model of radar or ultrasound speckle. Real speckle comes from coherent imaging and is described by other distributions (e.g. Fisher–Tippett or Gamma, as noted in [V10]), may use γ ≠ 1 [V10], and is spatially correlated. Our noise is independent from pixel to pixel.

### 3.4 Filters (Stage 4)
* **Proposed:** mean (`cv2.blur`), Gaussian (`cv2.GaussianBlur`), median (`cv2.medianBlur`), bilateral (`cv2.bilateralFilter`).

### 3.5 Block diagram workflow (for draw.io, Stage 8)
Status of each box: [I] = implemented, [P] = proposed. The template's example diagram uses dashed rounded group boxes, icons and arrows, with the caption "Figure1: Block diagram of the proposed work".
```
[I] Input image file (data/input)
      │  load_grayscale_image + validation
      ▼
[I] Clean grayscale image I (uint8 matrix)  ───────────────┐
      │  add noise (Gaussian σ / salt-and-pepper amount /    │ reference
      │  speckle variance, fixed seed)            [I]        │
      ▼                                                     │
[I] Noisy image  ──► [P] Filter (mean / Gaussian / median / bilateral, parameters)
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

### 4.1 Noise addition results (Stage 3): noisy baselines, NO filtering yet
These are the first real noise experiments. **No filter has been applied**, so
nothing here says anything about noise removal. These values are the
**baselines** that Stage 4 filters must beat.

**Setup:** image D1 (`synthetic_test_image.png`, 256 × 256 = 65,536 pixels, uint8). Seed 42 for every experiment. Command: `python -m demos.demo_noise --save-figure --save-outputs`, run on 2026-11-16 with Python 3.12.10, NumPy 2.5.5 and OpenCV 5.0.0. Source of every number: `results/tables/stage3_noise_results.csv` (log IDs E001–E009).

| ID | Noise | Strength | MSE | PSNR (dB) | Changed pixels | Pixels at 0 or 255 |
|---|---|---|---|---|---|---|
| E001 | Gaussian | σ = 10 | 99.60 | 28.15 | 62,782 | 456 |
| E002 | Gaussian | σ = 25 | 577.99 | 20.51 | 64,457 | 3,713 |
| E003 | Gaussian | σ = 50 | 2053.92 | 15.00 | 64,984 | 8,693 |
| E004 | Salt-and-pepper | amount = 0.02 | 413.36 | 21.97 | 1,311 | 1,311 |
| E005 | Salt-and-pepper | amount = 0.05 | 1058.04 | 17.89 | 3,277 | 3,277 |
| E006 | Salt-and-pepper | amount = 0.10 | 2083.03 | 14.94 | 6,554 | 6,554 |
| E007 | Speckle | variance = 0.01 | 171.46 | 25.79 | 61,713 | 1,680 |
| E008 | Speckle | variance = 0.04 | 636.43 | 20.09 | 63,627 | 3,086 |
| E009 | Speckle | variance = 0.10 | 1483.11 | 16.42 | 64,330 | 4,468 |

**Model check: measured MSE vs. the value predicted without clipping** (printed by the same demo run)
| ID | Predicted MSE | Formula | Measured | Measured / predicted |
|---|---|---|---|---|
| E001 | 100.00 | σ² | 99.60 | 0.996 |
| E002 | 625.00 | σ² | 577.99 | 0.925 |
| E003 | 2500.00 | σ² | 2053.92 | 0.822 |
| E007 | 189.84 | variance × mean(I²) = 0.01 × 18983.8 | 171.46 | 0.903 |
| E008 | 759.35 | 0.04 × 18983.8 | 636.43 | 0.838 |
| E009 | 1898.38 | 0.10 × 18983.8 | 1483.11 | 0.781 |

**Figure:** `results/figures/stage3_noise_examples.png` (300 dpi; rows = Gaussian / salt-and-pepper / speckle; columns = original + three strengths; MSE and PSNR in each title). A good candidate for the report.

**Observations (based only on these runs):**
1. **Stronger noise → higher MSE, lower PSNR, for all three types.** Every step up in strength lowered PSNR (Gaussian 28.15 → 20.51 → 15.00 dB; salt-and-pepper 21.97 → 17.89 → 14.94 dB; speckle 25.79 → 20.09 → 16.42 dB). Visually the shapes become harder to see: at σ = 50 the edges of the square and the 1-pixel lines are still visible but much less clear.
2. **Gaussian and speckle change almost every pixel; salt-and-pepper changes only the selected few.** Gaussian σ = 10 changed 95.8% of pixels (the rest got noise smaller than ±0.5, which rounds to no change; checked: exactly those 2,754 pixels). Salt-and-pepper 10% changed exactly 6,554 pixels (10.0%).
3. **Salt-and-pepper creates a large error with few pixels.** Each corrupted pixel jumps to 0 or 255, an error of up to 240 levels in our image (a pixel of 240 set to pepper 0). So 2% salt-and-pepper (MSE 413.36) gives a larger MSE than Gaussian σ = 10 applied to almost every pixel (MSE 99.60).
4. **Same PSNR, different appearance.** E003 (Gaussian σ = 50, 15.00 dB) and E006 (salt-and-pepper 10%, 14.94 dB) have almost the same PSNR. In the figure, however, E006 keeps 90% of the pixels exactly correct and the shapes and lines stay clearly recognisable, while E003 looks uniformly grainy. This is another example of the PSNR limitation in [V5] and §3.2.
5. **Speckle depends on brightness, as the model predicts.** In the figure, speckle is strong on the bright circle (235) and the bright right side, and barely visible on the dark square (20) and dark left side. Gaussian noise looks the same everywhere.
6. **Clipping reduces the measured error.** For Gaussian σ = 10 the measured MSE is 99.6% of σ², so almost no clipping. At σ = 50 it is only 82.2%, because values pushed below 0 or above 255 are cut off. The number of pixels at exactly 0 or 255 grows from 456 to 8,693. Speckle shows the effect more strongly (90.3% → 78.1%) because its largest changes happen at the brightest pixels, which are closest to 255.
7. **Reproducibility confirmed:** running the demo a second time produced byte-identical PNG and CSV files (SHA-256 compared), and a saved noisy PNG reloads to exactly the array the noise function produces.

**Limitations of these results:** one synthetic image only, one seed (42), and no real photograph yet. The numbers describe this image and seed. Other images or seeds will give somewhat different values. PSNR comparisons across noise types should be read together with the images (observation 4).

### 4.2 Noise removal experiments
* **Not yet collected.** Requires Stage 4 (filters) and Stage 6 (experiment runner). Each filter will be applied to the saved noisy baselines (groups G001–G009), and its PSNR compared with the baseline PSNR above.

## 5. Conclusion
Template instruction: "Summarized the whole project".
* **Not yet collected.** Write it after Stage 7.
* Achievements so far (engineering, not final conclusions): reliable image loading with validation, Unicode path support, verified MSE/PSNR implementation, three reproducible noise models, 101 passing unit tests.
* Findings so far that may feed the conclusion (from §4.0–4.1, not about filters): PSNR does not capture the *type* of degradation (salt-and-pepper 10% and Gaussian σ = 50 have equal PSNR but look very different); clipping makes strong noise measure lower than its model predicts.

## References
See `references.md`. Style: IEEE numbered (confirmed by the template's example reference). Template: "Please put a least five Reference". **11 sources are verified so far (V1–V11): 4 peer-reviewed papers (V5, V8, V9, V10) and 7 official technical documentation / source-code references.**

## Index (source code)
Template: "Please put your source code here if you it is applicable".
Current source files: `src/image_io.py`, `src/synthetic_image.py`, `src/metrics.py`, `src/noise.py`, `demos/demo_image_loading.py`, `demos/demo_metrics.py`, `demos/demo_noise.py`.
Final listing to be prepared at the end.
