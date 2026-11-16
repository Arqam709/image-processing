"""Image quality metrics: Mean Squared Error (MSE) and Peak Signal-to-Noise Ratio (PSNR).

Both metrics compare a *processed* image (for example noisy or filtered)
with the clean *original* image, pixel by pixel. See docs/report_notes.md,
section 3.2, for the formulas and their limitations.

Why we convert to float64 before subtracting
--------------------------------------------
Our images are uint8 (unsigned 8-bit integers, 0..255). uint8 arithmetic
"wraps around" instead of going negative or above 255:

    np.uint8(10) - np.uint8(20)  ->  246   (not -10)

because -10 is stored modulo 256. Squaring 246 instead of -10 would give a
completely wrong error. Squares can also be far larger than 255
(255**2 = 65025). Converting to float64 first gives correct negative
differences and enough room for large sums.
"""

import math

import numpy as np

from src.image_io import validate_grayscale_image

# Largest possible pixel value for 8-bit images (2**8 - 1).
MAX_PIXEL_VALUE = 255


def _validate_image_pair(original, processed):
    """Check that both inputs are valid 8-bit grayscale images of the same size."""
    for name, image in (("original", original), ("processed", processed)):
        try:
            validate_grayscale_image(image)
        except (TypeError, ValueError) as error:
            # Re-raise the same error type, but say which argument was wrong.
            raise type(error)(f"{name} image: {error}") from error

    if original.shape != processed.shape:
        raise ValueError(
            f"Images must have the same dimensions: original {original.shape} "
            f"vs processed {processed.shape}."
        )


def mse(original, processed):
    """Return the Mean Squared Error between two grayscale images.

        MSE = (1 / N) * sum( (original - processed)^2 )

    where N is the number of pixels. 0.0 means the images are identical.
    Larger values mean larger differences. Inputs are not modified.
    """
    _validate_image_pair(original, processed)

    difference = original.astype(np.float64) - processed.astype(np.float64)
    squared_difference = difference ** 2
    return float(np.mean(squared_difference))


def psnr(original, processed):
    """Return the Peak Signal-to-Noise Ratio in decibels (dB).

        PSNR = 10 * log10( MAX^2 / MSE ),   MAX = 255 for 8-bit images

    Higher values mean the processed image is closer to the original.
    For identical images MSE = 0, so the ratio is a division by zero and
    PSNR is mathematically infinite: we return math.inf explicitly.
    (cv2.PSNR instead returns a large finite number, about 361.2 dB.)
    """
    error = mse(original, processed)  # validates the inputs too
    if error == 0.0:
        return math.inf
    return 10.0 * math.log10(MAX_PIXEL_VALUE ** 2 / error)
