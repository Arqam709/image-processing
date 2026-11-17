"""Smoke tests for the Streamlit app (frontend/app.py), Stage 5A.

Streamlit's own testing tool (streamlit.testing.v1.AppTest) runs the app
script without a browser or web server, and lets us "upload" a file.
These tests only check that our page reacts correctly: they do not test
Streamlit itself. The upload logic is tested in detail in
test_frontend_image_processing.py.

Run from the project root:  python -m unittest tests.test_frontend_app -v
"""

import unittest
from pathlib import Path

import cv2
import numpy as np
from streamlit.testing.v1 import AppTest

APP_PATH = str(Path(__file__).resolve().parent.parent / "frontend" / "app.py")
TIMEOUT_SECONDS = 60


def encode(extension, array):
    ok, encoded = cv2.imencode(extension, array)
    assert ok
    return encoded.tobytes()


def run_app(upload=None):
    """Run the app once; optionally upload (file_name, bytes) and run again."""
    app = AppTest.from_file(APP_PATH, default_timeout=TIMEOUT_SECONDS)
    app.run()
    if upload is not None:
        file_name, data = upload
        app.sidebar.file_uploader[0].upload(file_name, data).run()
    return app


def all_text(elements):
    return " ".join(str(element.value) for element in elements)


class TestAppWithoutUpload(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = run_app()

    def test_runs_without_exception(self):
        self.assertEqual(len(self.app.exception), 0)
        self.assertEqual(len(self.app.error), 0)

    def test_title(self):
        self.assertEqual(self.app.title[0].value, "Image Noise Lab — Noise Addition and Removal")

    def test_uploader_accepts_only_png_and_jpeg(self):
        uploader = self.app.sidebar.file_uploader[0]
        self.assertEqual(sorted(t.lstrip(".") for t in uploader.allowed_type), ["jpeg", "jpg", "png"])

    def test_asks_user_to_upload(self):
        self.assertIn("Upload a PNG or JPEG image", all_text(self.app.info))


class TestAppWithValidUploads(unittest.TestCase):
    def test_colour_png(self):
        image = np.random.default_rng(0).integers(0, 256, (40, 60, 3), dtype=np.uint8)
        app = run_app(("colour photo.png", encode(".png", image)))
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.error), 0)
        self.assertIn("colour", all_text(app.info))
        metrics = {metric.label: metric.value for metric in app.metric}
        self.assertEqual(metrics["Width"], "60 px")
        self.assertEqual(metrics["Height"], "40 px")
        self.assertEqual(metrics["Pixels"], "2,400")

    def test_grayscale_jpeg(self):
        image = np.random.default_rng(1).integers(0, 256, (30, 20), dtype=np.uint8)
        app = run_app(("gray.jpg", encode(".jpg", image)))
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.error), 0)
        self.assertIn("already grayscale", all_text(app.info))

    def test_transparent_png_shows_warning(self):
        rgba = np.zeros((10, 10, 4), dtype=np.uint8)
        app = run_app(("logo.png", encode(".png", rgba)))
        self.assertEqual(len(app.exception), 0)
        self.assertIn("transparent", all_text(app.warning))

    def test_large_image_shows_warning(self):
        large = np.zeros((2000, 2100), dtype=np.uint8)  # 4.2 megapixels (compresses to a tiny PNG)
        app = run_app(("large.png", encode(".png", large)))
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.error), 0)
        self.assertIn("large image", all_text(app.warning))


class TestAppWithInvalidUploads(unittest.TestCase):
    def check_rejected(self, file_name, data, expected_text):
        app = run_app((file_name, data))
        self.assertEqual(len(app.exception), 0, "the app must not crash")
        self.assertEqual(len(app.error), 1)
        self.assertIn("cannot be used", app.error[0].value)
        self.assertIn(expected_text, app.error[0].value)
        self.assertEqual(len(app.metric), 0, "no image information for a rejected file")

    def test_corrupted_png(self):
        self.check_rejected("broken.png", b"\x89PNG\r\n\x1a\n" + b"x" * 100, "could not be decoded")

    def test_empty_file(self):
        self.check_rejected("empty.png", b"", "empty")

    def test_text_file_renamed_to_png(self):
        self.check_rejected("notes.png", b"hello, this is not an image", "not a PNG or JPEG")

    def test_bmp_file_renamed_to_png(self):
        # A file named "picture.bmp" never reaches our code: Streamlit itself
        # refuses extensions not listed in `type=` (observed with AppTest).
        # A BMP renamed to .png passes that check, so our content check must catch it.
        bmp = encode(".bmp", np.zeros((5, 5), dtype=np.uint8))
        self.check_rejected("picture.png", bmp, "not a PNG or JPEG")


if __name__ == "__main__":
    unittest.main()
