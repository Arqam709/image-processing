# Experiment Log

_Last updated: 2026-11-16 (after Stage 2)_

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

## Entries: noise removal experiments (E###)

_None yet. Noise is implemented in Stage 3, filters in Stage 4, and the experiment runner in Stage 6._

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
