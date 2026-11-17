# Presentation Notes (simple English)

_Last updated: 2026-11-17 (after Stage 5A)_

## What the project does (planned, in one breath)
"We take a clean picture, add a known amount of noise to it on purpose, try
four different filters to clean it, and measure with numbers which filter
brings the picture closest to the original."

## Why it matters
Real images get noise from cameras, low light and transmission. Before a
computer can analyse an image, we often need to clean it. But every filter has
a cost: it may remove noise **and** blur important details. Our project measures
that trade-off.

---

## Stage 1: what I can explain now

**What is a digital image?**
A grid of numbers. Each number is a pixel. In an 8-bit grayscale image each
pixel is between 0 (black) and 255 (white). Our program prints a 5×5 block of
these numbers, which shows the image is really a matrix I(x, y).

**What is the shape (256, 256)?**
NumPy stores the image as (rows, columns), which is (height, width).
256 × 256 = 65,536 pixels. At 1 byte per pixel, that is 65,536 bytes of raw data.

**How do you turn a colour photo into grayscale?**
OpenCV combines the three colour channels with weights:
Gray = 0.299·Red + 0.587·Green + 0.114·Blue. Green gets the biggest weight
because human eyes are most sensitive to green.
_(The formula is verified [V1]. The "eyes most sensitive to green" explanation
still needs a verified reference before it goes into the written report.)_

**Why did you make a synthetic image?**
Because we know every pixel exactly, it is a perfect clean reference. It has a
smooth gradient, flat areas, sharp edges and 1-pixel-thin lines. Later these
will show the differences between filters: some filters keep edges, some blur
them, and some erase thin lines.

**Why does the synthetic image use 20–240 instead of 0–255?**
Salt-and-pepper noise sets pixels to exactly 0 or 255. Keeping the clean image
away from those values makes the noise pixels easy to identify.

**Why not just use `cv2.imread`?**
We tested it: on Windows, `cv2.imread` could not open a file whose name had
Turkish letters (ü, İ). So we read the raw bytes with NumPy and decode them with
`cv2.imdecode`. That works for any filename.

**Why compute the mean in float64?**
`uint8` can only hold 0–255. Adding up thousands of pixel values in `uint8`
would overflow and wrap around. `float64` avoids that.

**How do you protect the original image?**
The loading function only reads the file. The saving function refuses to
overwrite an existing file unless you explicitly allow it. We have tests that
check the file's fingerprint (SHA-256 hash) is unchanged after loading.

**How do you know the code works?**
32 automated unit tests for Stage 1 (Python `unittest`), run on 2026-11-16, all passing
(63 in total after Stage 2, 101 after Stage 3, 144 after Stage 4, 194 after Stage 5A).
They check correct pixel values, colour-to-gray conversion, and every error
case: missing file, empty file, corrupted file, wrong type, and so on.

---

## Stage 2: MSE and PSNR (how we measure quality)

**What does MSE measure?**
"How different, on average, two images are, pixel by pixel." For every pixel we
subtract the processed value from the original value, square it, and take the
average over all pixels.

**Tiny example (do it on the board):**
original = [10, 20, 30, 40], processed = [12, 20, 30, 36]
differences = −2, 0, 0, 4 → squares = 4, 0, 0, 16 → sum = 20 → MSE = 20 / 4 = **5**

**Why square the differences?**
1. So that +4 and −4 count the same, because both are errors.
2. So that big errors count much more than small ones (an error of 10 counts 100, an error of 1 counts 1).

**What does PSNR measure?**
The same information as MSE, but on a "higher is better" decibel scale:
PSNR = 10 × log₁₀(255² / MSE). 255 is the brightest possible pixel, so PSNR
compares the biggest possible signal with the average error.

**Numbers worth remembering (all checked by our tests):**
| Situation | MSE | PSNR |
|---|---|---|
| Identical images | 0 | infinity |
| Every pixel off by 1 | 1 | 48.13 dB |
| Our 2×2 example | 5 | 41.14 dB |
| Every pixel off by 10 | 100 | 28.13 dB |
| 1 of 100 pixels completely wrong (off by 255) | 650.25 | 20 dB |
| Black image vs white image | 65025 | 0 dB |

**What does "decibel" mean here?**
It is a logarithmic ratio scale. +10 dB means the error is 10 times smaller,
and +20 dB means 100 times smaller. That is why one wrong pixel in 100 gives 20 dB,
while one wrong pixel in 10,000 gives 40 dB.

**Why lower MSE / higher PSNR = better?**
Lower MSE means the processed image's pixels are closer to the original's.
PSNR divides by MSE, so less error means a bigger ratio and a higher PSNR.

**Why do we need the original image?**
Both metrics compare against the clean original ("full-reference" metrics).
Without the original there is nothing to compare with. That is why we add noise
ourselves to a clean image: we always know the correct answer.

**Why float64? (a likely question!)**
Images are stored as uint8 (0–255). With uint8, 10 − 12 does not give −2: it
wraps around to 254, with no warning. Squaring 254 instead of −2 would make the
error enormous. So we convert to float64 first. A test proves the uint8 version
is wrong.

**What happens with identical images?**
MSE = 0, so PSNR = 255²/0, which is a division by zero, i.e. infinity. Our function
returns infinity. OpenCV's `cv2.PSNR` returns 361.20 dB instead, because its
source code adds a tiny number (2.2 × 10⁻¹⁶) to avoid dividing by zero. We
return true infinity so "identical" can never be confused with "very good".

**Why can't PSNR fully describe what a human sees?**
It treats every pixel error the same, wherever it is and whatever kind it is.
Our demo shows this: making the whole image 10 levels brighter (barely
noticeable) gives 28.13 dB, but 10 clearly visible white dots give 52.32 dB,
a much "better" score. Wang and Bovik (2009) show the same with images that
have nearly identical MSE but very different visual quality.

**Did you check your PSNR against OpenCV?**
Yes. For non-identical images, our result equals `cv2.PSNR` to at least 6 decimal
places (automated tests on random image pairs and on the synthetic image).

---

## Stage 3: adding noise

**One-sentence summary:** "We damage a clean image on purpose, in three
different ways and at three strengths, so we know exactly what the correct
image is and can later measure how well each filter repairs it."

**Gaussian noise (the standard "additive white Gaussian noise" model in denoising research [V8])**
* Every pixel gets a small random number added: noisy = original + n.
* n comes from a bell-shaped (normal) distribution with mean 0. σ (sigma) says how wide the bell is.
* σ = 10 means most pixels move by less than about ±10 levels (about 68% within ±σ).
* **σ is not a percentage of pixels.** Almost every pixel changes (95.8% at σ = 10); σ controls *how much*.
* Our results: σ = 10 → 28.15 dB, σ = 25 → 20.51 dB, σ = 50 → 15.00 dB.

**Salt-and-pepper noise (impulse noise, e.g. caused by bit errors during acquisition and transmission [V9])**
* A chosen fraction of pixels becomes pure white (salt, 255) or pure black (pepper, 0). All other pixels stay exactly the same.
* amount = 0.05 means 5% of the pixels are *selected*: 0.05 × 65,536 = 3276.8 → 3,277 pixels (1,638 white + 1,639 black).
* **Selected vs. changed:** a white pixel that gets salt stays white, so it was selected but did not change. Our test image has no pure black or white pixels, so there every selected pixel changed.
* Few pixels, but huge errors per pixel. That is why 2% salt-and-pepper (MSE 413) has a bigger MSE than Gaussian σ = 10 (MSE 100).

**Speckle noise (granular, brightness-dependent noise, e.g. in ultrasound images [V10])**
* noisy = original + original × n. The noise is *multiplied* by the brightness.
* Bright pixels get big changes, dark pixels small ones, and black pixels none at all.
* Example with variance 0.01 (standard deviation 0.1, i.e. about ±10%): a pixel of 40 moves about ±4, and a pixel of 160 moves about ±16 (our test measured exactly this).
* In our figure, speckle is clearly visible on the bright circle but hardly on the dark square.
* Honest limitation: this is a simplified model. Real ultrasound/radar speckle is more complex (other distributions, correlated between neighbouring pixels).

**Random seeds (reproducibility)**
* A computer's "random" numbers come from a formula started by a *seed*. Same seed → same numbers → same noisy image, every time.
* We use seed 42 for every experiment and write it in the file name, e.g. `..._gaussian_sigma25__seed42.png`.
* We ran the demo twice: the output files were byte-for-byte identical.
* Each call creates its own generator (`default_rng(seed)`), so experiments cannot influence each other.

**What is clipping and why does it matter?**
* Pixels must stay between 0 and 255. If noise pushes a value to 270, we set it to 255; if to −5, we set it to 0.
* Without clipping, uint8 would "wrap around": 270 would become 14, so a bright pixel would turn almost black. That is a bug, and we have tests that catch it.
* Side effect: clipping cuts off some noise, so the measured MSE is lower than the theory predicts. At σ = 50 we measured only 82% of the expected σ² = 2500.

**Comparing noise types with PSNR**
* Within one noise type: stronger noise → lower PSNR, always (our 9 results).
* Across noise types: careful! Gaussian σ = 50 (15.00 dB) and salt-and-pepper 10% (14.94 dB) have nearly the same PSNR, but in the salt-and-pepper image 90% of the pixels are still perfect and the shapes are clearly visible. Same number, different damage.

**Likely questions about Stage 3**
* *Why add noise artificially instead of using real noisy photos?* Because we need the clean original to compute MSE/PSNR. With artificial noise we know the exact ground truth and can control the strength.
* *Why these strengths?* Three levels (low/medium/high) per type, to see the trend. They are our own choices, not standard values.
* *Why does Gaussian noise change almost all pixels but salt-and-pepper only some?* Gaussian adds a random value to every pixel; salt-and-pepper replaces only the selected pixels.
* *Why is the speckle noise invisible on the dark square?* Because the noise is multiplied by the pixel value: 20 × 0.1 = ±2 levels, too small to see.
* *Why round instead of just converting to integers?* Converting cuts off the decimals (2.9 → 2), which would make every pixel slightly too dark on average. Rounding (2.9 → 3) has no such bias.
* *Is your salt-and-pepper the same as in other libraries?* The idea is the same, but scikit-image decides each pixel by "coin flip", so the count varies. We select an exact number, so the result is easier to check and compare.

---

## Stage 4: removing noise with filters

**One-sentence summary:** "We take one noisy image, clean it with four
different filters, and measure which result is closest to the original, both
for the whole image and for separate regions."

**What is a filter here?** A small window (3×3 = 9 pixels) slides over the image.
For every position, the filter looks at the 9 pixels and computes one new
value for the centre pixel (lecture 1, PDF p. 21).

**The four filters in one line each**
* **Mean:** take the average of the 9 pixels. Simple; it smooths noise but also smooths edges.
* **Gaussian:** a weighted average; the centre pixel counts most (1/4), its 4 direct neighbours 1/8 each, the 4 corners 1/16 each.
* **Median:** sort the 9 values and take the middle one. An extreme value (0 or 255) is never in the middle, so it just disappears.
* **Bilateral:** average only the neighbours that are close **and** have a similar brightness. Pixels on the other side of an edge are ignored, so edges stay sharp.

**Board example for the median (easy to show):**
window = 100, 100, 100, 100, **255**, 100, 100, 100, 100
* sorted: 100 100 100 100 **100** 100 100 100 255, so the median is **100**. The salt pixel is gone.
* the mean of the same window is (8·100 + 255)/9 = 117.2. The salt pixel was only spread out.

**Our settings and why**
* Kernel size 3 for mean, Gaussian and median: the smallest window that smooths, and the same for all three, so the comparison is fair.
* Gaussian sigma = 0: OpenCV picks it from the kernel size. For size 3 it uses the weights 1/4, 1/2, 1/4 (we checked OpenCV's source code and wrote a test).
* Bilateral d = 5, sigmaColor = sigmaSpace = 50. OpenCV's documentation suggests d = 5 for fast filtering and equal sigmas, and says values below 10 do little while values above 150 look "cartoonish". 50 is in between. **We did not tune it.**

**What is "border handling"?** At the image edge, part of the window is outside the image.
* Mean, Gaussian and bilateral **mirror** the image (OpenCV's default; we set it explicitly).
* The median always **repeats** the edge pixel (fixed inside OpenCV).
* We have tests for both.

**Our actual results (seed 42, synthetic image)**
| Noise | Noisy | Mean | Gaussian | Median | Bilateral |
|---|---|---|---|---|---|
| Gaussian σ = 25 | 20.51 dB | 18.37 | 20.43 | 17.28 | **28.69** |
| Salt-and-pepper 5% | 17.89 dB | 18.10 | **19.86** | 17.09 | 18.78 |

**The surprise, and how to explain it (important!)**
* Several filters made the whole-image PSNR **worse** than the noisy image. Even the median, the textbook filter for salt-and-pepper, scored −0.80 dB.
* Reason: our test image has a block of 1-pixel-wide lines. A 3×3 window sees a line as only 3 of 9 pixels.
  * The median throws the lines away completely.
  * Mean and Gaussian smear them.
* Proof: applied to the **clean** image, almost all of the median's error (≈ 100%) comes from that one block, which is only 12.9% of the image.
* In the flat region (no detail), the median removed **99.7%** of the salt-and-pepper error (830.67 → 2.66), the best of all filters.
* Lesson: **noise removal and detail preservation pull in opposite directions.** A single PSNR number for the whole image mixes them up. That is why we also measure regions.

**What each filter is good and bad at (our measurements)**
* Mean and Gaussian: reduce Gaussian noise in flat areas to about 13–15% of the error, but blur lines and spread impulses into gray blobs.
* Median: perfect against isolated salt-and-pepper pixels, keeps straight edges sharp, but erases thin lines.
* Bilateral: best for Gaussian noise (+8.18 dB) and keeps the lines, but leaves most salt-and-pepper pixels. A white dot looks to the filter like a tiny "edge", so it keeps it.

**Likely questions about Stage 4**
* *Why did you use OpenCV instead of writing the filters yourself?* OpenCV's versions are tested, fast and standard. Our code validates the inputs, chooses explicit settings, and a test checks that our result equals the direct OpenCV call. Writing our own would add bugs without teaching more about the results.
* *Why must the kernel size be odd?* So the window has a centre pixel: 3 = 1 left + centre + 1 right.
* *Why is the median filter non-linear?* Sorting is not a weighted sum. For example, median(a + b) is not median(a) + median(b).
* *Why does the mean filter not remove salt-and-pepper?* It averages the 255 with its neighbours, so the error is spread over 9 pixels instead of removed.
* *Why apply all filters to the same noisy image?* Otherwise the random noise would differ between filters, and we could not tell whether a difference comes from the filter or from the noise. The program checks that no filter changed the noisy image.
* *Is the bilateral filter always the best?* No. It was the worst of the four in the flat region with salt-and-pepper (458.25 vs 2.66 for the median).
* *Would bigger kernels be better?* More noise removal but more blur. We have not measured that yet; it is planned for the experiment runner (Stage 6).
* *Would the results be the same on a real photo?* Probably not exactly, because our image has an unusually hard line pattern. We will test the student's own photo later.

---

## Stage 5A: the web app "Image Noise Lab" (upload only, so far)

**What is it?** A web page that runs on my own computer. You upload a photo and see it next to
its grayscale version. Later sub-stages add noise, filters, metrics and downloads.
Launch it with `python -m streamlit run frontend/app.py` and open http://localhost:8501.

**Why Streamlit?** It builds a web page from a short Python script: no HTML, JavaScript or
separate server code. So the whole project stays in one language, and I can explain every line.

**How is it organised? (three layers)**
1. `frontend/app.py` is only the page: layout, messages and pictures.
2. `frontend/image_processing.py` checks and decodes the upload. It does not import Streamlit,
   so it is tested like the rest of the project.
3. `src/` is the image processing from Stages 1–4, unchanged. The app only *calls* it.
   No formula is copied.

**What happens when I upload a photo?**
1. Check the name: .png, .jpg or .jpeg. Check the file is not empty and at most 20 MB.
2. Check the first bytes. Every PNG starts with the same 8 bytes and every JPEG with `FF D8 FF`.
   So a text file renamed to `.png` is refused.
3. Decode it in memory to grayscale with OpenCV. This is exactly the same method as Stage 1,
   so the app and my demos see the same pixel values. Then check: 2-D, `uint8`, not empty,
   at most 25 megapixels.
4. Show the colour original and the grayscale reference side by side, with width, height,
   pixels and file size.

**Why grayscale?** All our algorithms work on one brightness value per pixel (0–255).
For colour photos OpenCV uses Y = 0.299·R + 0.587·G + 0.114·B. Green counts most because our
eyes are most sensitive to green. The page tells the user when a colour photo was converted.

**How is the original protected?**
* The uploaded bytes are kept exactly as they were.
* The grayscale image is **read-only**: any attempt to change it in place raises an error.
* Nothing is saved to disk.

**What can go wrong, and what does the user see?** Each case gives a red message instead of a crash:
* an empty file
* a damaged or cut-off file
* a non-image file
* a BMP file renamed to .png
* a file that is too big

Transparent PNGs and very large photos get a yellow warning.

**How was it tested?**
* 38 tests for the upload helper and 12 tests that run the real page with Streamlit's test tool
  (no browser needed).
* 14 deliberately broken versions of the helper were all caught by the tests.

### Likely questions about the web app
* *Why not write the algorithms again inside the app?* Then there would be two versions that could
  disagree. The app calls the same tested functions as the demos.
* *Why is the app only on localhost?* It is a local demo. By default Streamlit would also accept
  connections from other devices on the same Wi-Fi, so we turned that off.
* *Why PNG for display and not JPEG?* JPEG compression changes pixel values. When we later show
  noise, that would hide or add noise. Streamlit would use JPEG by default, so we force PNG.
* *Does the uploaded photo leave my computer?* No. The browser sends it to the local server on
  the same computer. We also switched off Streamlit's anonymous usage statistics.
* *Why is a big photo shown smaller?* Streamlit shrinks images wider than 1460 px for the screen
  only. The processing always uses the full-size grayscale image.

---

## Questions the professor might ask (answers grow with each stage)
* *What is a "full-reference" metric?* One that needs the original clean image, like MSE and PSNR.
* *If PSNR is just a rescaled MSE, why report both?* PSNR in dB is the common convention in image processing papers and is easier to read. MSE is easier to understand and calculate by hand.
* *Can PSNR be negative?* Not for 8-bit images: the largest possible MSE is 255², which gives exactly 0 dB.
* *Is a PSNR of 30 dB good?* It depends on the image and the task. We will only compare PSNR values measured under identical conditions (same image, same noise), not judge single numbers.
* *What is noise?* Unwanted variation in pixel intensity (lecture 1).
* *What is a pixel?* The smallest addressable element of a digital image (lecture 1).
* *What is the difference between sampling and quantization?* Sampling is how many pixels; quantization is how many intensity levels (8-bit gives 256 levels).
* *Why grayscale first?* One value per pixel makes the algorithms easier to understand and compare. Colour may come later.
* *What is a linear filter?* One where the output is a fixed weighted sum of the inputs (mean, Gaussian). Median and bilateral are non-linear [V8].
* _(To add in later stages: full results with several settings, comparison figures, the photo.)_
