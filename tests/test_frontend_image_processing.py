"""Unit tests for frontend/image_processing.py (Stage 5A: image upload).

Uploaded files are simulated with bytes created in memory by cv2.imencode.
Nothing here starts Streamlit or touches data/input.

Run from the project root:  python -m unittest tests.test_frontend_image_processing -v
"""

import struct
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import cv2
import numpy as np

from frontend.image_processing import (
    LARGE_IMAGE_PIXELS,
    MAX_FILE_SIZE_BYTES,
    UploadedImage,
    check_file_name,
    detect_image_format,
    format_file_size,
    is_large_image,
    load_uploaded_image,
    png_has_alpha,
)
from src.image_io import load_grayscale_image


def encode(extension, array, *params):
    """Encode an array as image-file bytes, like a file a user would upload."""
    ok, encoded = cv2.imencode(extension, array, list(params))
    assert ok
    return encoded.tobytes()


def random_gray(height=40, width=60, seed=0):
    return np.random.default_rng(seed).integers(0, 256, (height, width), dtype=np.uint8)


def random_bgr(height=40, width=60, seed=1):
    return np.random.default_rng(seed).integers(0, 256, (height, width, 3), dtype=np.uint8)


def add_exif_orientation(jpeg_bytes, orientation):
    """Insert a minimal EXIF block with the given orientation tag into a JPEG.

    Phone cameras store photos sideways and record the rotation in this tag.
    Orientation 6 means "rotate 90 degrees clockwise to display".
    """
    tiff = (
        b"II*\x00"  # little-endian TIFF header
        + struct.pack("<I", 8)  # first directory starts at byte 8
        + struct.pack("<H", 1)  # one entry
        + struct.pack("<HHII", 0x0112, 3, 1, orientation)  # Orientation, SHORT, count 1
        + struct.pack("<I", 0)  # no next directory
    )
    app1 = b"Exif\x00\x00" + tiff
    segment = b"\xff\xe1" + struct.pack(">H", len(app1) + 2) + app1
    return jpeg_bytes[:2] + segment + jpeg_bytes[2:]


class TestValidUploads(unittest.TestCase):
    def test_grayscale_png_is_loaded_exactly(self):
        gray = random_gray()
        result = load_uploaded_image("photo.png", encode(".png", gray))
        self.assertIsInstance(result, UploadedImage)
        self.assertEqual(result.file_format, "PNG")
        self.assertEqual(result.grayscale.dtype, np.uint8)
        self.assertEqual(result.grayscale.ndim, 2)
        np.testing.assert_array_equal(result.grayscale, gray)  # PNG is lossless
        self.assertFalse(result.is_colour)
        self.assertFalse(result.has_alpha)

    def test_dimensions(self):
        result = load_uploaded_image("wide.png", encode(".png", random_gray(height=30, width=70)))
        self.assertEqual((result.height, result.width), (30, 70))
        self.assertEqual(result.grayscale.shape, (30, 70))
        self.assertEqual(result.preview_rgb.shape, (30, 70, 3))
        self.assertEqual(result.pixel_count, 2100)

    def test_colour_png(self):
        bgr = random_bgr()
        result = load_uploaded_image("colour.png", encode(".png", bgr))
        self.assertTrue(result.is_colour)
        self.assertEqual(result.grayscale.shape, (40, 60))
        self.assertEqual(result.preview_rgb.dtype, np.uint8)
        # The preview must be in RGB order (what browsers expect), not OpenCV's BGR.
        np.testing.assert_array_equal(result.preview_rgb, bgr[:, :, ::-1])

    def test_pure_red_pixel_order(self):
        red_bgr = np.zeros((4, 4, 3), dtype=np.uint8)
        red_bgr[:, :, 2] = 255
        result = load_uploaded_image("red.png", encode(".png", red_bgr))
        np.testing.assert_array_equal(result.preview_rgb[0, 0], [255, 0, 0])

    def test_gray_image_stored_as_rgb_is_not_colour(self):
        gray = random_gray()
        result = load_uploaded_image("gray_rgb.png", encode(".png", cv2.merge([gray, gray, gray])))
        self.assertFalse(result.is_colour)
        np.testing.assert_array_equal(result.grayscale, gray)

    def test_colour_jpeg(self):
        data = encode(".jpg", random_bgr(), cv2.IMWRITE_JPEG_QUALITY, 90)
        for name in ("photo.jpg", "photo.jpeg", "PHOTO.JPG", "Photo.JpEg"):
            with self.subTest(name=name):
                result = load_uploaded_image(name, data)
                self.assertEqual(result.file_format, "JPEG")
                self.assertEqual(result.grayscale.shape, (40, 60))
                self.assertEqual(result.grayscale.dtype, np.uint8)
                self.assertTrue(result.is_colour)

    def test_grayscale_jpeg_is_not_colour(self):
        result = load_uploaded_image("gray.jpg", encode(".jpg", random_gray()))
        self.assertFalse(result.is_colour)
        self.assertEqual(result.file_format, "JPEG")

    def test_same_grayscale_as_stage1_loader(self):
        """The app and the Stage 1 demos must see exactly the same pixels."""
        cases = {
            "colour.png": encode(".png", random_bgr()),
            "colour.jpg": encode(".jpg", random_bgr(), cv2.IMWRITE_JPEG_QUALITY, 85),
            "gray.png": encode(".png", random_gray()),
            "phone_rotated.jpg": add_exif_orientation(encode(".jpg", random_bgr(height=16, width=32)), 6),
        }
        with tempfile.TemporaryDirectory() as folder:
            for name, data in cases.items():
                with self.subTest(name=name):
                    path = Path(folder) / name
                    path.write_bytes(data)
                    np.testing.assert_array_equal(
                        load_uploaded_image(name, data).grayscale, load_grayscale_image(path)
                    )

    def test_sixteen_bit_png_becomes_uint8(self):
        values = np.random.default_rng(2).integers(0, 65536, (20, 20)).astype(np.uint16)
        result = load_uploaded_image("deep.png", encode(".png", values))
        self.assertEqual(result.grayscale.dtype, np.uint8)
        np.testing.assert_array_equal(result.grayscale, (values >> 8).astype(np.uint8))

    def test_transparent_png_is_flagged(self):
        rgba = np.dstack([random_bgr(), np.zeros((40, 60), dtype=np.uint8)])
        result = load_uploaded_image("logo.png", encode(".png", rgba))
        self.assertTrue(result.has_alpha)
        self.assertEqual(result.grayscale.shape, (40, 60))
        self.assertEqual(result.preview_rgb.shape, (40, 60, 3))

    def test_exif_orientation_is_applied_to_both_images(self):
        data = add_exif_orientation(encode(".jpg", random_bgr(height=16, width=32)), orientation=6)
        result = load_uploaded_image("phone.jpg", data)
        self.assertEqual(result.grayscale.shape, (32, 16))  # rotated: height and width swap
        self.assertEqual(result.preview_rgb.shape, (32, 16, 3))

    def test_extension_and_contents_may_differ(self):
        """The contents decide the format: a PNG saved as '.jpg' is still a PNG."""
        result = load_uploaded_image("renamed.jpg", encode(".png", random_gray()))
        self.assertEqual(result.file_format, "PNG")

    def test_tiny_image(self):
        result = load_uploaded_image("one.png", encode(".png", np.array([[7]], dtype=np.uint8)))
        self.assertEqual(result.grayscale.shape, (1, 1))
        self.assertEqual(int(result.grayscale[0, 0]), 7)

    def test_bytearray_and_memoryview_accepted(self):
        data = encode(".png", random_gray())
        for wrapped in (bytearray(data), memoryview(data)):
            with self.subTest(kind=type(wrapped).__name__):
                self.assertEqual(load_uploaded_image("a.png", wrapped).file_bytes, data)

    def test_deterministic(self):
        data = encode(".jpg", random_bgr())
        first = load_uploaded_image("a.jpg", data)
        second = load_uploaded_image("a.jpg", data)
        np.testing.assert_array_equal(first.grayscale, second.grayscale)
        np.testing.assert_array_equal(first.preview_rgb, second.preview_rgb)


class TestOriginalIsPreserved(unittest.TestCase):
    def setUp(self):
        self.data = encode(".png", random_bgr())
        self.result = load_uploaded_image("photo.png", self.data)

    def test_original_bytes_kept_exactly(self):
        self.assertIsInstance(self.result.file_bytes, bytes)
        self.assertEqual(self.result.file_bytes, self.data)
        self.assertEqual(self.result.file_size, len(self.data))
        self.assertEqual(self.result.file_name, "photo.png")

    def test_later_changes_to_the_input_buffer_do_not_matter(self):
        buffer = bytearray(self.data)
        result = load_uploaded_image("photo.png", buffer)
        buffer[:] = b"\x00" * len(buffer)
        self.assertEqual(result.file_bytes, self.data)

    def test_grayscale_reference_is_read_only(self):
        self.assertFalse(self.result.grayscale.flags.writeable)
        with self.assertRaises(ValueError):
            self.result.grayscale[0, 0] = 0

    def test_preview_is_read_only(self):
        self.assertFalse(self.result.preview_rgb.flags.writeable)
        with self.assertRaises(ValueError):
            self.result.preview_rgb[0, 0, 0] = 0

    def test_preview_and_grayscale_do_not_share_memory(self):
        self.assertFalse(np.shares_memory(self.result.preview_rgb, self.result.grayscale))

    def test_record_cannot_be_reassigned(self):
        with self.assertRaises(AttributeError):
            self.result.grayscale = np.zeros((2, 2), dtype=np.uint8)


class TestInvalidUploads(unittest.TestCase):
    def test_empty_file(self):
        with self.assertRaisesRegex(ValueError, "empty"):
            load_uploaded_image("empty.png", b"")

    def test_wrong_data_type(self):
        for bad in (None, "not bytes", 123, [1, 2, 3], np.zeros(10, dtype=np.uint8)):
            with self.subTest(bad=type(bad).__name__):
                with self.assertRaises(TypeError):
                    load_uploaded_image("a.png", bad)

    def test_wrong_file_name_type(self):
        for bad in (None, 5, Path("a.png"), b"a.png"):
            with self.subTest(bad=bad):
                with self.assertRaises(TypeError):
                    load_uploaded_image(bad, encode(".png", random_gray()))

    def test_unsupported_extensions(self):
        data = encode(".png", random_gray())
        for name in ("a.bmp", "a.gif", "a.tif", "a.txt", "a", "a.png.exe", "", "   "):
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    load_uploaded_image(name, data)

    def test_other_image_formats_rejected_even_with_png_name(self):
        for extension in (".bmp", ".tif"):
            with self.subTest(extension=extension):
                with self.assertRaisesRegex(ValueError, "not a PNG or JPEG"):
                    load_uploaded_image("disguised.png", encode(extension, random_gray()))

    def test_text_file_renamed_to_png(self):
        with self.assertRaisesRegex(ValueError, "not a PNG or JPEG"):
            load_uploaded_image("notes.png", b"This is a text file, not an image.")

    def test_corrupted_png(self):
        data = b"\x89PNG\r\n\x1a\n" + b"x" * 200  # correct signature, garbage after it
        with self.assertRaisesRegex(ValueError, "could not be decoded"):
            load_uploaded_image("broken.png", data)

    def test_truncated_files(self):
        cases = {
            "cut.png": encode(".png", random_bgr()),
            "cut.jpg": encode(".jpg", random_bgr()),
        }
        for name, data in cases.items():
            for fraction in (0.5, 0.9):
                with self.subTest(name=name, fraction=fraction):
                    with self.assertRaisesRegex(ValueError, "could not be decoded"):
                        load_uploaded_image(name, data[: int(len(data) * fraction)])

    def test_file_too_large(self):
        data = encode(".png", random_gray())
        with self.assertRaisesRegex(ValueError, "too large"):
            load_uploaded_image("big.png", data, max_file_bytes=len(data) - 1)
        # exactly at the limit is allowed
        load_uploaded_image("ok.png", data, max_file_bytes=len(data))

    def test_default_file_limit_is_20_mb(self):
        self.assertEqual(MAX_FILE_SIZE_BYTES, 20 * 1024 * 1024)

    def test_decoder_result_is_validated(self):
        """OpenCV always returns 2-D uint8 here, so we fake a wrong result to check
        that validate_grayscale_image (from src/image_io.py) is really called."""
        data = encode(".png", random_gray())
        wrong_result = np.zeros((4, 4), dtype=np.float64)
        with mock.patch("frontend.image_processing._decode", return_value=wrong_result):
            with self.assertRaisesRegex(ValueError, "uint8"):
                load_uploaded_image("a.png", data)

    def test_too_many_pixels(self):
        data = encode(".png", random_gray(height=40, width=60))  # 2400 pixels
        with self.assertRaisesRegex(ValueError, "too large"):
            load_uploaded_image("big.png", data, max_pixels=2399)
        load_uploaded_image("ok.png", data, max_pixels=2400)


class TestSmallHelpers(unittest.TestCase):
    def test_check_file_name_returns_lower_case_extension(self):
        self.assertEqual(check_file_name("My Photo.JPEG"), ".jpeg")
        self.assertEqual(check_file_name("görüntü_İ.png"), ".png")  # Turkish letters are fine

    def test_detect_image_format(self):
        self.assertEqual(detect_image_format(encode(".png", random_gray())), "PNG")
        self.assertEqual(detect_image_format(encode(".jpg", random_gray())), "JPEG")
        with self.assertRaises(ValueError):
            detect_image_format(b"GIF89a....")

    def test_png_has_alpha(self):
        gray_png = encode(".png", random_gray())
        self.assertFalse(png_has_alpha(gray_png))
        self.assertFalse(png_has_alpha(encode(".png", random_bgr())))
        self.assertTrue(png_has_alpha(encode(".png", np.dstack([random_bgr(), random_gray()]))))
        # Colour type 4 (gray + alpha): change only the colour-type byte of the header.
        gray_alpha_header = gray_png[:25] + bytes([4]) + gray_png[26:]
        self.assertTrue(png_has_alpha(gray_alpha_header))
        self.assertFalse(png_has_alpha(encode(".jpg", random_bgr())))
        self.assertFalse(png_has_alpha(b"\x89PNG"))  # too short to contain a header

    def test_is_large_image(self):
        result = load_uploaded_image("a.png", encode(".png", random_gray(height=10, width=10)))
        self.assertFalse(is_large_image(result))
        self.assertTrue(is_large_image(result, threshold=99))
        self.assertFalse(is_large_image(result, threshold=100))
        self.assertEqual(LARGE_IMAGE_PIXELS, 4_000_000)

    def test_format_file_size(self):
        self.assertEqual(format_file_size(0), "0 bytes")
        self.assertEqual(format_file_size(1023), "1023 bytes")
        self.assertEqual(format_file_size(2048), "2.0 KB")
        self.assertEqual(format_file_size(5 * 1024 * 1024), "5.0 MB")


if __name__ == "__main__":
    unittest.main()
