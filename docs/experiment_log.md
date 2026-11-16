# Experiment Log

_Last updated: 2026-11-16 (after Stage 3)_

Rules:
* Every entry must come from an actual program run. Never type results in by hand.
* Every number in the report's Results section must be traceable to an entry here.
* Filters compared in one experiment group must use the **same** noisy image (same image, noise type, intensity and seed).
* The noisy image itself is always recorded as the **baseline** (filter = "none").

## Entry format

| Field | Meaning |
|---|---|
| Experiment ID | `E###`, for example E001. One ID per (image, noise, intensity, seed, filter, parameters). |
| Group ID | `G###`. All filters applied to the same noisy image share a group. |
| Date | YYYY-MM-DD of the run |
| Input image | Filename in `data/input/` |
| Noise type | gaussian / salt_and_pepper / speckle |
| Noise intensity | For example σ = 25, p = 0.05, variance = 0.04 |
| Random seed | Integer used for noise generation |
| Filter | none (baseline) / mean / gaussian / median / bilateral |
| Filter parameters | For example ksize = 3; or d = 9, sigmaColor = 75, sigmaSpace = 75 |
| MSE | Compared with the clean original |
| PSNR (dB) | Compared with the clean original |
| Saved image paths | Paths in `results/noisy/` and `results/filtered/` |
| Source of numbers | Script and command that produced the values, plus the CSV file |
| Observations | What we saw (visual and numerical) |

## Table template

| ID | Group | Date | Image | Noise | Intensity | Seed | Filter | Params | MSE | PSNR (dB) | Output | Observations |
|---|---|---|---|---|---|---|---|---|---|---|---|---|

## Entries: noise experiments (E###)

### Stage 3: noise addition, noisy baselines (filter = none)
These are real noise experiments, but **no filter was applied**. Each one creates
one noisy image (group G###) that Stage 4 filters will later be applied to.

* **Date:** 2026-11-16
* **Command:** `python -m demos.demo_noise --save-figure --save-outputs` (project root)
* **Code:** `src/noise.py` (`add_gaussian_noise`, `add_salt_and_pepper_noise`, `add_speckle_noise`); metrics from `src/metrics.py`
* **Environment:** Python 3.12.10, NumPy 2.5.5 (Generator `default_rng`, PCG64), OpenCV 5.0.0, Windows 11
* **Input image:** `data/input/synthetic_test_image.png` (256 × 256 = 65,536 pixels, uint8, values 20–240). The program confirmed "Original image unchanged: True".
* **Random seed:** 42 for every experiment (each call creates its own generator from seed 42).
* **Machine-readable copy:** `results/tables/stage3_noise_results.csv` (also contains the dates and salt/pepper counts)
* **Reproducibility check:** a second run produced byte-identical PNG and CSV files (SHA-256), and a saved PNG reloads to exactly the array the function returns.

| ID | Group | Image | Noise | Strength | Seed | Filter | MSE | PSNR (dB) | Changed px | At 0/255 | Output (`results/noisy/`) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| E001 | G001 | synthetic_test_image.png (256×256) | gaussian | σ = 10 | 42 | none | 99.5965 | 28.1484 | 62,782 | 456 | synthetic_test_image__gaussian_sigma10__seed42.png |
| E002 | G002 | synthetic_test_image.png (256×256) | gaussian | σ = 25 | 42 | none | 577.9914 | 20.5116 | 64,457 | 3,713 | synthetic_test_image__gaussian_sigma25__seed42.png |
| E003 | G003 | synthetic_test_image.png (256×256) | gaussian | σ = 50 | 42 | none | 2053.9173 | 15.0050 | 64,984 | 8,693 | synthetic_test_image__gaussian_sigma50__seed42.png |
| E004 | G004 | synthetic_test_image.png (256×256) | salt_and_pepper | amount = 0.02 | 42 | none | 413.3608 | 21.9675 | 1,311 | 1,311 | synthetic_test_image__salt_and_pepper_amount0.02__seed42.png |
| E005 | G005 | synthetic_test_image.png (256×256) | salt_and_pepper | amount = 0.05 | 42 | none | 1058.0422 | 17.8858 | 3,277 | 3,277 | synthetic_test_image__salt_and_pepper_amount0.05__seed42.png |
| E006 | G006 | synthetic_test_image.png (256×256) | salt_and_pepper | amount = 0.10 | 42 | none | 2083.0331 | 14.9438 | 6,554 | 6,554 | synthetic_test_image__salt_and_pepper_amount0.1__seed42.png |
| E007 | G007 | synthetic_test_image.png (256×256) | speckle | variance = 0.01 | 42 | none | 171.4604 | 25.7892 | 61,713 | 1,680 | synthetic_test_image__speckle_variance0.01__seed42.png |
| E008 | G008 | synthetic_test_image.png (256×256) | speckle | variance = 0.04 | 42 | none | 636.4267 | 20.0933 | 63,627 | 3,086 | synthetic_test_image__speckle_variance0.04__seed42.png |
| E009 | G009 | synthetic_test_image.png (256×256) | speckle | variance = 0.10 | 42 | none | 1483.1099 | 16.4191 | 64,330 | 4,468 | synthetic_test_image__speckle_variance0.1__seed42.png |

Salt-and-pepper counts (rounding rule: selected = ⌊amount × N + 0.5⌋; salt = ⌊selected/2⌋; pepper = rest):
* E004: 0.02 × 65,536 = 1310.72 → 1,311 selected = 655 salt + 656 pepper; changed 1,311
* E005: 0.05 × 65,536 = 3276.80 → 3,277 selected = 1,638 salt + 1,639 pepper; changed 3,277
* E006: 0.10 × 65,536 = 6553.60 → 6,554 selected = 3,277 salt + 3,277 pepper; changed 6,554

**Figure:** `results/figures/stage3_noise_examples.png` (300 dpi, all nine experiments plus the original).

**Observations:**
* E001–E003: PSNR falls 28.15 → 20.51 → 15.00 dB as σ grows. Measured MSE / σ² = 0.996, 0.925, 0.822, so clipping at 0/255 increasingly cuts off the noise (pixels at 0/255: 456 → 8,693). The unchanged pixels in E001 (2,754) are exactly those whose noise was smaller than ±0.5.
* E004–E006: only the selected pixels change, but each by a large amount, so MSE is high for few pixels. E006 (14.94 dB) ≈ E003 (15.00 dB) in PSNR, but E006 looks far less degraded overall: the shapes and lines stay recognisable.
* E007–E009: noise is visibly stronger on bright regions (circle, right side) than on dark ones (dark square, left side). Measured MSE / predicted (variance × mean(I²) = variance × 18983.8) = 0.903, 0.838, 0.781, an even stronger clipping effect than Gaussian, because the largest changes occur at the brightest pixels.

### Later: noise removal experiments
_None yet. Filters come in Stage 4 and the experiment runner in Stage 6. Filtered results will reuse groups G001–G009, so every filter is compared on the same noisy image._

---

## Separate section: metric validation runs (MV###), Stage 2

These are **not** noise removal experiments. They are controlled, hand-checkable
changes used only to check that MSE and PSNR are calculated correctly.
No noise model and no filter were involved.

* **Date:** 2026-11-16
* **Command:** `python -m demos.demo_metrics --save-figure` (run from the project root; the same numbers were also printed by a run without `--save-figure`)
* **Code:** `src/metrics.py` (`mse`, `psnr`), compared with `cv2.PSNR` (OpenCV 5.0.0)
* **Input image:** `data/input/synthetic_test_image.png` (256 × 256, uint8; see report_notes §2). The original array was checked to be unchanged after the run ("Original image unchanged: True").
* **Random seed:** not applicable (all changes are deterministic)

| ID | Original | Processed (controlled change) | Changed pixels | MSE | PSNR (ours) | cv2.PSNR | Hand calculation | Observation |
|---|---|---|---|---|---|---|---|---|
| MV001 | 2×2 array [[10,20],[30,40]] | [[12,20],[30,36]] | 2 / 4 | 5.0 | 41.1411 dB | not run | (4+0+0+16)/4 = 5; 10·log₁₀(65025/5) = 41.1411 | Direct uint8 subtraction gave [[254,0],[0,4]] (silent wrap-around) |
| MV002 | synthetic_test_image.png | Case A: row 185, columns 30, 39, …, 111 (10 pixels), 128 → 178 | 10 / 65,536 | 0.3815 | 52.3162 dB | 52.3162 dB | 10·50²/65536 = 0.3815 | Dots clearly visible, yet PSNR is high |
| MV003 | synthetic_test_image.png | Case B: every pixel +10 (0 pixels clipped) | 65,536 / 65,536 | 100.0000 | 28.1308 dB | 28.1308 dB | 10² = 100; 10·log₁₀(650.25) = 28.1308 | Looks almost unchanged, yet PSNR is much lower than case A |
| MV004 | synthetic_test_image.png | Identical copy | 0 / 65,536 | 0.0 | infinity | 361.2020 dB | MSE = 0 → PSNR = ∞ | OpenCV's epsilon gives a finite value |

**Saved output:** `results/figures/stage2_metric_validation.png` (300 dpi; original, case A, case B with MSE/PSNR in the titles). Git ignores it, so regenerate it with the command above.
