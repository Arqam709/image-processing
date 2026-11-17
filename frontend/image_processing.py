"""Small helpers that connect the Streamlit app (frontend/app.py) to src/.

This module does NOT import Streamlit, so it can be tested with unittest
without starting a web server. It also contains NO image-processing
algorithms of its own:

* Decoding uses OpenCV exactly like src.image_io.load_grayscale_image
  (cv2.imdecode with cv2.IMREAD_GRAYSCALE), but works on the uploaded bytes
  in memory instead of on a file path. Nothing is written to disk.
* Validation of the result uses src.image_io.validate_grayscale_image.

Stage 5A covers only the upload step. Noise, filters and metrics will be
connected in Stages 5B-5D by calling the existing functions in src/.
"""

from dataclasses import dataclass
from pathlib import PurePath

import cv2
import numpy as np

from src.image_io import validate_grayscale_image

# --------------------------------------------------------------------------
# Upload rules
# --------------------------------------------------------------------------
ALLOWED_EXTENSIONS = (".png", ".jpg", ".jpeg")
UPLOAD_TYPES = ("png", "jpg", "jpeg")  # the same list, in the form st.file_uploader wants

# Limits that keep the app responsive and memory use reasonable.
# 20 MB is far more than a normal phone photo (a 12-megapixel JPEG is usually 2-6 MB).
MAX_FILE_SIZE_MB = 20
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
# 25 megapixels covers typical phone (12 MP) and camera (24 MP) photos.
MAX_PIXELS = 25_000_000
# Above 4 megapixels (about 2300 x 1700) the app shows a "may be slow" note.
LARGE_IMAGE_PIXELS = 4_000_000

# The first bytes of a file tell us its real format, whatever its name says.
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
JPEG_SIGNATURE = b"\xff\xd8\xff"
# In a PNG, byte 25 (inside the IHDR header) is the "colour type".
# Types 4 (gray + alpha) and 6 (RGB + alpha) contain transparency.
PNG_COLOUR_TYPE_OFFSET = 25
PNG_ALPHA_COLOUR_TYPES = (4, 6)


@dataclass(frozen=True)
class UploadedImage:
    """Everything the app needs to know about one uploaded image.

    file_bytes  : the uploaded file, byte for byte (never changed).
    file_format : "PNG" or "JPEG", detected from the file contents.
    preview_rgb : the image as decoded in colour (height x width x 3, RGB),
                  used ONLY for display. Read-only.
    grayscale   : the clean grayscale reference (height x width, uint8)
                  that all processing will use. Read-only.
    is_colour   : True if the red, green and blue channels are not all equal.
    has_alpha   : True if a PNG stores transparency (it is ignored).
    """

    file_name: str
    file_bytes: bytes
    file_format: str
    preview_rgb: np.ndarray
    grayscale: np.ndarray
    is_colour: bool
    has_alpha: bool

    @property
    def height(self):
        return self.grayscale.shape[0]

    @property
    def width(self):
        return self.grayscale.shape[1]

    @property
    def pixel_count(self):
        return self.grayscale.size

    @property
    def file_size(self):
        return len(self.file_bytes)


# --------------------------------------------------------------------------
# Checks
# --------------------------------------------------------------------------
def check_file_name(file_name):
    """Check the file name and return its extension in lower case (e.g. '.jpg')."""
    if not isinstance(file_name, str):
        raise TypeError(f"File name must be a string, got {type(file_name).__name__}.")
    if not file_name.strip():
        raise ValueError("File name is empty.")
    extension = PurePath(file_name).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        allowed = ", ".join(ALLOWED_EXTENSIONS)
        shown = extension if extension else "no extension"
        raise ValueError(f"Unsupported file type ({shown}). Please upload one of: {allowed}.")
    return extension


def detect_image_format(data):
    """Return "PNG" or "JPEG" by looking at the first bytes of the file.

    The file name can be wrong, so the contents decide. Any other format
    (for example BMP or GIF, or a text file renamed to .png) is rejected.
    """
    if data.startswith(PNG_SIGNATURE):
        return "PNG"
    if data.startswith(JPEG_SIGNATURE):
        return "JPEG"
    raise ValueError("The file is not a PNG or JPEG image (its contents do not match either format).")


def png_has_alpha(data):
    """True if a PNG file's header says it stores transparency (colour type 4 or 6)."""
    return (
        data.startswith(PNG_SIGNATURE)
        and len(data) > PNG_COLOUR_TYPE_OFFSET
        and data[PNG_COLOUR_TYPE_OFFSET] in PNG_ALPHA_COLOUR_TYPES
    )


def _decode(data, flag):
    """Decode image bytes with OpenCV; return None if they cannot be decoded."""
    try:
        return cv2.imdecode(np.frombuffer(data, dtype=np.uint8), flag)
    except cv2.error:
        return None


def _read_only(array):
    """Mark an array as read-only, so no later step can change it by accident."""
    array.setflags(write=False)
    return array


# --------------------------------------------------------------------------
# Main function
# --------------------------------------------------------------------------
def load_uploaded_image(file_name, data, max_file_bytes=MAX_FILE_SIZE_BYTES, max_pixels=MAX_PIXELS):
    """Check and decode an uploaded PNG/JPEG file, entirely in memory.

    Steps:
      1. Check the file name (.png, .jpg or .jpeg) and the data type.
      2. Reject empty files and files larger than `max_file_bytes`.
      3. Check that the contents really are PNG or JPEG.
      4. Decode to grayscale with cv2.IMREAD_GRAYSCALE, exactly like
         src.image_io.load_grayscale_image (Stage 1), and validate the
         result with validate_grayscale_image (2-D, uint8, not empty).
      5. Reject images with more than `max_pixels` pixels.
      6. Decode again in colour, only for displaying the original.

    Both decodes apply the EXIF orientation of phone photos, so the colour
    preview and the grayscale image always have the same shape.

    Returns an UploadedImage. Raises TypeError or ValueError with a message
    that can be shown to the user.
    """
    check_file_name(file_name)
    if not isinstance(data, (bytes, bytearray, memoryview)):
        raise TypeError(f"File contents must be bytes, got {type(data).__name__}.")
    data = bytes(data)  # an unchangeable copy of exactly what was uploaded

    if len(data) == 0:
        raise ValueError("The file is empty (0 bytes).")
    if len(data) > max_file_bytes:
        raise ValueError(
            f"The file is too large ({format_file_size(len(data))}). "
            f"The limit is {format_file_size(max_file_bytes)}."
        )

    file_format = detect_image_format(data)

    grayscale = _decode(data, cv2.IMREAD_GRAYSCALE)
    if grayscale is None:
        raise ValueError(f"The {file_format} file could not be decoded. It may be damaged or incomplete.")
    validate_grayscale_image(grayscale)

    if grayscale.size > max_pixels:
        height, width = grayscale.shape
        raise ValueError(
            f"The image is too large ({width} x {height} = {grayscale.size:,} pixels). "
            f"The limit is {max_pixels:,} pixels. Please resize it and upload it again."
        )

    preview_bgr = _decode(data, cv2.IMREAD_COLOR)
    if preview_bgr is None or preview_bgr.shape[:2] != grayscale.shape:
        raise ValueError("The colour version of the image could not be decoded consistently.")

    # OpenCV stores colour as Blue-Green-Red; browsers expect Red-Green-Blue.
    preview_rgb = cv2.cvtColor(preview_bgr, cv2.COLOR_BGR2RGB)
    blue, green, red = cv2.split(preview_bgr)
    is_colour = not (np.array_equal(blue, green) and np.array_equal(green, red))

    return UploadedImage(
        file_name=file_name,
        file_bytes=data,
        file_format=file_format,
        preview_rgb=_read_only(preview_rgb),
        grayscale=_read_only(grayscale),
        is_colour=is_colour,
        has_alpha=png_has_alpha(data),
    )


# --------------------------------------------------------------------------
# Small display helpers
# --------------------------------------------------------------------------
def is_large_image(uploaded, threshold=LARGE_IMAGE_PIXELS):
    """True if the image has more pixels than `threshold` (processing may be slow)."""
    return uploaded.pixel_count > threshold


def format_file_size(num_bytes):
    """Turn a number of bytes into readable text, e.g. 2048 -> '2.0 KB'."""
    if num_bytes < 1024:
        return f"{num_bytes} bytes"
    if num_bytes < 1024 * 1024:
        return f"{num_bytes / 1024:.1f} KB"
    return f"{num_bytes / (1024 * 1024):.1f} MB"
