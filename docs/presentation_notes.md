# Presentation Notes (simple English)

_Last updated: 2026-11-16 (after Stage 2)_

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
(63 in total after Stage 2).
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

## Questions the professor might ask (answers grow with each stage)
* *What is a "full-reference" metric?* One that needs the original clean image, like MSE and PSNR.
* *If PSNR is just a rescaled MSE, why report both?* PSNR in dB is the common convention in image processing papers and is easier to read. MSE is easier to understand and calculate by hand.
* *Can PSNR be negative?* Not for 8-bit images: the largest possible MSE is 255², which gives exactly 0 dB.
* *Is a PSNR of 30 dB good?* It depends on the image and the task. We will only compare PSNR values measured under identical conditions (same image, same noise), not judge single numbers.
* *What is noise?* Unwanted variation in pixel intensity (lecture 1).
* *What is a pixel?* The smallest addressable element of a digital image (lecture 1).
* *What is the difference between sampling and quantization?* Sampling is how many pixels; quantization is how many intensity levels (8-bit gives 256 levels).
* *Why grayscale first?* One value per pixel makes the algorithms easier to understand and compare. Colour may come later.
* _(To add in later stages: noise types, filters, MSE/PSNR, results.)_
