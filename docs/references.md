# References

_Last updated: 2026-11-16 (after Stage 2)_

Citation style: **IEEE numbered**. The template's own example reference is
in IEEE style (authors, "title," venue, vol., pp., year, doi), so this is consistent.
Template requirement: "Please put a least five Reference".
Final numbers [1], [2], ... are assigned in order of first citation when the
report is written. Until then, verified sources use IDs V1, V2, ...

**Status: 6 verified sources (V1–V6).** Of these, 1 is a peer-reviewed paper
(V5) and 5 are official technical documentation. More academic sources (for
example a textbook for noise models and filters) should be verified in
Stages 3–4, because the report will be stronger with several academic references.

---

## A. Verified sources

Verification means we opened an official source and confirmed that the content
we rely on is really there.

### [V1] OpenCV: colour conversions (RGB → Gray formula)
* **IEEE draft:** OpenCV, "Color conversions," *OpenCV Documentation*. [Online]. Available: https://docs.opencv.org/4.x/de/d25/imgproc_color_conversions.html
* **Author/organization:** OpenCV team · **Year:** documentation for the 4.x branch (no single publication year)
* **What we verified:** the formula "RGB[A] to Gray: Y ← 0.299·R + 0.587·G + 0.114·B".
* **How verified (2026-11-16):** the docs.opencv.org page blocked automated access (HTTP 403, bot check), so we read the same text in OpenCV's official source file `modules/imgproc/doc/colors.markdown` (4.x branch, https://github.com/opencv/opencv), which the documentation page is generated from. **Action for the student:** open the docs URL in a browser once to confirm it displays the formula.
* **Note:** our installed version is OpenCV 5.0.0; the text was checked on the 4.x branch. Our own tests confirm the behaviour in our environment.
* **Supports:** grayscale conversion during image loading.
* **Cite in:** 2 Datasets (preprocessing), 3 Methods (3.1).

### [V2] OpenCV: image file reading and writing (imgcodecs)
* **IEEE draft:** OpenCV, "Image file reading and writing," *OpenCV Documentation*. [Online]. Available: https://docs.opencv.org/4.x/d4/da8/group__imgcodecs.html
* **Author/organization:** OpenCV team · **Year:** 4.x documentation
* **What we verified:** `IMREAD_GRAYSCALE`: "always convert image to the single channel grayscale image (codec internal conversion)". `imdecode`: "Reads an image from a buffer in memory"; if decoding fails, it "returns an empty matrix". `imread`: "If the image cannot be read, the function returns an empty matrix."
* **How verified (2026-11-16):** same situation as V1. We read the official header `modules/imgcodecs/include/opencv2/imgcodecs.hpp` (4.x branch), which the documentation is generated from. Please confirm in a browser.
* **Supports:** image loading, error handling, and why grayscale values can differ by 1 from `cvtColor`.
* **Cite in:** 3 Methods (3.1).

### [V3] NumPy: numpy.fromfile
* **IEEE draft:** NumPy Developers, "numpy.fromfile," *NumPy v2.5 Manual*. [Online]. Available: https://numpy.org/doc/stable/reference/generated/numpy.fromfile.html
* **Author/organization:** NumPy Developers · **Year:** v2.5 manual
* **What we verified (2026-11-16):** the page loads (title "numpy.fromfile — NumPy v2.5 Manual") and describes the function as "Construct an array from data in a text or binary file."
* **Supports:** reading image bytes so that non-ASCII Windows paths work.
* **Cite in:** 3 Methods (3.1).

### [V4] OpenCV: cv::PSNR (core module, operations on arrays)
* **IEEE draft:** OpenCV, "Operations on arrays: PSNR," *OpenCV Documentation*. [Online]. Available: https://docs.opencv.org/4.x/d2/de8/group__core__array.html
* **Author/organization:** OpenCV team · **Year:** 4.x documentation
* **What we verified (2026-11-16):**
  * Documentation text in the official header `modules/core/include/opencv2/core.hpp` (4.x): "PSNR = 10 · log10(R² / MSE) where R is the maximum integer value of depth (e.g. 255 in the case of CV_8U data) and MSE is the mean squared error between the two arrays."
  * Implementation in `modules/core/src/norm.dispatch.cpp` (identical in the 4.x and 5.x branches): `return 20*log10(R/(diff+DBL_EPSILON));` with `diff = sqrt(MSE)`. This explains the finite 361.20 dB for identical images.
* **How verified:** docs.opencv.org blocks automated access, so the text was read in the official GitHub repository. The exact docs page URL above (group "core_array") was **not** opened. **Action for the student:** open it in a browser and confirm that it shows PSNR. If not, cite the GitHub source file instead.
* **Supports:** PSNR formula with MAX = 255; why `cv2.PSNR` is finite for identical images; validating our implementation against OpenCV.
* **Cite in:** 3 Methods (3.2).

### [V5] Wang & Bovik (2009): MSE and its limitations (peer-reviewed)
* **IEEE:** Z. Wang and A. C. Bovik, "Mean squared error: Love it or leave it? A new look at signal fidelity measures," *IEEE Signal Processing Magazine*, vol. 26, no. 1, pp. 98–117, Jan. 2009, doi: 10.1109/MSP.2008.930649.
* **How verified (2026-11-16):** bibliographic data from the Crossref DOI registry (api.crossref.org). Content checked in the author-hosted PDF (https://ece.uwaterloo.ca/~z70wang/publications/SPM09.pdf).
* **Quotes we rely on (from the PDF):**
  * "PSNR = 10 log10 (L² / MSE), where L is the dynamic range of allowable image pixel intensities."
  * PSNR "is useful if images having different dynamic ranges are being compared, but otherwise contains no new information relative to the MSE."
  * "The MSE has many attractive features: 1) It is simple. It is parameter free and inexpensive to compute…"
  * MSE "remains the standard criterion for the assessment of signal quality and fidelity" and "is the method of choice for comparing competing signal processing methods".
  * "the MSE values … of several of the distorted images are nearly identical …, even though the same images present dramatically (and obviously) different visual quality."
* **Supports:** definitions of MSE and PSNR, why they are widely used, and their main limitation.
* **Cite in:** 1 Introduction, 3 Methods (3.2), 4 Results (discussion of metric limits).

### [V6] NumPy: data types and overflow
* **IEEE draft:** NumPy Developers, "Data types," *NumPy v2.5 Manual*. [Online]. Available: https://numpy.org/doc/stable/user/basics.types.html
* **What we verified (2026-11-16):** page title "Data types — NumPy v2.5 Manual". Section "Overflow errors": "The fixed size of NumPy numeric types may cause overflow errors when a value requires more memory than available in the data type."
* **Supports:** why uint8 arithmetic is unsafe and why we convert to float64.
* **Cite in:** 3 Methods (3.1, 3.2).

---

## B. Course material (cite only if the professor allows lecture slides)

### [C-L1] Lecture 1 slides
* **Draft:** K. Zaman, "Simple Introduction to Digital Image Processing," lecture slides, course 1400002073 Image Processing.
* **File:** `course_material/İP lecture 1.pdf`
* **Supports:** basic definitions (pixel, f(x, y), 8-bit grayscale, noise, spatial filtering).
* **Note:** this does **not** count toward the five references unless the professor confirms it does. The year is not printed on the extracted slide text.

---

## C. Bibliographic data verified, content NOT yet checked

The DOI and details were confirmed in Crossref on 2026-11-16, but we have not read
the paper text, so we must not cite these for any specific claim yet.

| ID | IEEE reference | Possible use | What is still needed |
|---|---|---|---|
| C1 | Q. Huynh-Thu and M. Ghanbari, "Scope of validity of PSNR in image/video quality assessment," *Electronics Letters*, vol. 44, no. 13, pp. 800–801, Jun. 2008, doi: 10.1049/el:20080522. | When PSNR comparisons are valid | Read the paper (closed access; try the university library) |
| C2 | A. Hore and D. Ziou, "Image quality metrics: PSNR vs. SSIM," in *Proc. 20th Int. Conf. Pattern Recognition (ICPR)*, 2010, pp. 2366–2369, doi: 10.1109/ICPR.2010.579. | Relation between PSNR and SSIM | Read the paper (closed access) |
| C3 | Z. Wang, A. C. Bovik, H. R. Sheikh, and E. P. Simoncelli, "Image quality assessment: From error visibility to structural similarity," *IEEE Trans. Image Processing*, vol. 13, no. 4, pp. 600–612, Apr. 2004, doi: 10.1109/TIP.2003.819861. | SSIM (only if we add it) | Read the paper if SSIM is added |

---

## D. Candidates: NOT yet verified (do not cite)

| Candidate | Would support | Report section | When |
|---|---|---|---|
| R. C. Gonzalez and R. E. Woods, *Digital Image Processing*, Pearson (4th ed.) | Noise models, spatial filters | 1, 3 | Stage 3 |
| C. Tomasi and R. Manduchi, bilateral filtering paper, ICCV 1998 | Bilateral filter | 3 | Stage 4 |
| OpenCV documentation: `blur`, `GaussianBlur`, `medianBlur`, `bilateralFilter` | Filter implementation and parameters | 3 | Stage 4 |
| NumPy documentation: `numpy.random.default_rng` / `Generator` | Reproducible noise with seeds | 3 | Stage 3 |
