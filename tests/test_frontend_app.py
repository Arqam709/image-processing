"""Smoke tests for the Streamlit app (frontend/app.py), Stage 5A.

Streamlit's own testing tool (streamlit.testing.v1.AppTest) runs the app
script without a browser or web server, and lets us "upload" a file.
These tests only check that our page reacts correctly: they do not test
Streamlit itself. The upload logic is tested in detail in
test_frontend_image_processing.py.

Run from the project root:  python -m unittest tests.test_frontend_app -v
"""

import re
import unittest
from pathlib import Path

import cv2
import numpy as np
from streamlit.testing.v1 import AppTest

from frontend.image_processing import pixel_fingerprint
from src.noise import add_gaussian_noise, add_salt_and_pepper_noise, add_speckle_noise
from src.synthetic_image import create_synthetic_test_image

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


# --------------------------------------------------------------------------
# Stage 5B: noise controls
# --------------------------------------------------------------------------
SYNTHETIC = create_synthetic_test_image()  # 256 x 256, the Stage 3 test image
SYNTHETIC_PNG = encode(".png", SYNTHETIC)


def fingerprint_shown(app):
    """Read the pixel fingerprint of the noisy image from the page."""
    for caption in app.caption:
        match = re.search(r"Pixel fingerprint of the noisy image: `([0-9a-f]{12})`", caption.value)
        if match:
            return match.group(1)
    raise AssertionError("No pixel fingerprint shown on the page.")


def expected_fingerprint(function, strength, seed=42):
    return pixel_fingerprint(function(SYNTHETIC, strength, seed=seed))


def settings_text(app):
    return " ".join(m.value for m in app.markdown if m.value.startswith("**Settings:**"))


class TestNoiseControlsVisibility(unittest.TestCase):
    def test_no_noise_controls_before_upload(self):
        app = run_app()
        self.assertEqual(len(app.sidebar.radio), 0)
        self.assertEqual(len(app.number_input), 0)

    def test_no_noise_controls_after_invalid_upload(self):
        app = run_app(("broken.png", b"\x89PNG\r\n\x1a\n" + b"x" * 100))
        self.assertEqual(len(app.sidebar.radio), 0)
        self.assertEqual(len(app.exception), 0)

    def test_defaults_after_upload(self):
        app = run_app(("synthetic.png", SYNTHETIC_PNG))
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.error), 0)
        self.assertIn("2. Add Noise", [h.value for h in app.sidebar.header])
        self.assertEqual(app.radio(key="noise_type").value, "gaussian")
        self.assertEqual(app.radio(key="noise_type").options, ["Gaussian Noise", "Salt-and-Pepper Noise", "Speckle Noise"])
        self.assertEqual(app.slider(key="gaussian_sigma").value, 25)
        self.assertEqual(app.number_input(key="seed").value, 42)
        self.assertEqual(app.number_input(key="seed").label, "Random Seed")
        self.assertIn("Gaussian Noise — σ = 25", settings_text(app))
        self.assertIn("seed = 42", settings_text(app))

    def test_only_the_selected_strength_slider_is_shown(self):
        app = run_app(("synthetic.png", SYNTHETIC_PNG))
        strength_keys = {"gaussian_sigma", "salt_and_pepper_amount", "speckle_variance"}
        for noise_type, expected_key in [
            ("gaussian", "gaussian_sigma"),
            ("salt_and_pepper", "salt_and_pepper_amount"),
            ("speckle", "speckle_variance"),
        ]:
            with self.subTest(noise_type=noise_type):
                app.radio(key="noise_type").set_value(noise_type).run()
                shown = {s.key for s in app.sidebar.slider} & strength_keys
                self.assertEqual(shown, {expected_key})


class TestNoiseResults(unittest.TestCase):
    """The page must show exactly the pixels that src/noise.py produces."""

    def setUp(self):
        self.app = run_app(("synthetic.png", SYNTHETIC_PNG))

    def test_default_gaussian_matches_direct_call(self):
        self.assertEqual(fingerprint_shown(self.app), expected_fingerprint(add_gaussian_noise, 25))

    def test_switching_noise_type_updates_the_result(self):
        gaussian = fingerprint_shown(self.app)
        self.app.radio(key="noise_type").set_value("salt_and_pepper").run()
        self.assertEqual(fingerprint_shown(self.app), expected_fingerprint(add_salt_and_pepper_noise, 0.05))
        self.assertIn("Salt-and-Pepper Noise — 5% of pixels", settings_text(self.app))
        self.assertIn("3,277 of 65,536 pixels (1,638 white, 1,639 black)", all_text(self.app.sidebar.caption))
        self.app.radio(key="noise_type").set_value("speckle").run()
        self.assertEqual(fingerprint_shown(self.app), expected_fingerprint(add_speckle_noise, 0.04))
        self.assertIn("Speckle Noise — variance = 0.04", settings_text(self.app))
        self.assertNotEqual(fingerprint_shown(self.app), gaussian)
        self.assertEqual(len(self.app.exception), 0)

    def test_changing_strength_updates_the_result(self):
        before = fingerprint_shown(self.app)
        self.app.slider(key="gaussian_sigma").set_value(40).run()
        self.assertEqual(fingerprint_shown(self.app), expected_fingerprint(add_gaussian_noise, 40))
        self.assertNotEqual(fingerprint_shown(self.app), before)
        self.assertIn("σ = 40", settings_text(self.app))

    def test_changing_speckle_variance(self):
        self.app.radio(key="noise_type").set_value("speckle").run()
        self.app.slider(key="speckle_variance").set_value(0.1).run()
        self.assertEqual(fingerprint_shown(self.app), expected_fingerprint(add_speckle_noise, 0.1))

    def test_changing_salt_and_pepper_amount(self):
        self.app.radio(key="noise_type").set_value("salt_and_pepper").run()
        self.app.slider(key="salt_and_pepper_amount").set_value(0.1).run()
        self.assertEqual(fingerprint_shown(self.app), expected_fingerprint(add_salt_and_pepper_noise, 0.1))

    def test_seed_changes_pattern_and_is_reproducible(self):
        first = fingerprint_shown(self.app)
        self.app.number_input(key="seed").set_value(7).run()
        self.assertEqual(fingerprint_shown(self.app), expected_fingerprint(add_gaussian_noise, 25, seed=7))
        self.assertNotEqual(fingerprint_shown(self.app), first)
        self.app.number_input(key="seed").set_value(42).run()
        self.assertEqual(fingerprint_shown(self.app), first)

    def test_unrelated_controls_do_not_change_the_noise(self):
        first = fingerprint_shown(self.app)
        self.app.slider(key="zoom_x").set_value(10).run()
        self.assertEqual(fingerprint_shown(self.app), first)
        self.app.select_slider(key="zoom_size").set_value(16).run()
        self.assertEqual(fingerprint_shown(self.app), first)
        self.app.run()  # a plain rerun
        self.assertEqual(fingerprint_shown(self.app), first)

    def test_slider_value_is_remembered_when_switching_type(self):
        self.app.slider(key="gaussian_sigma").set_value(40).run()
        self.app.radio(key="noise_type").set_value("speckle").run()
        self.app.radio(key="noise_type").set_value("gaussian").run()
        self.assertEqual(self.app.slider(key="gaussian_sigma").value, 40)
        self.assertEqual(fingerprint_shown(self.app), expected_fingerprint(add_gaussian_noise, 40))

    def test_negative_seed_shows_safe_error(self):
        self.app.number_input(key="seed").set_value(-1).run()
        self.assertEqual(len(self.app.exception), 0)
        self.assertEqual(len(self.app.error), 1)
        self.assertIn("Noise could not be added", self.app.error[0].value)
        self.assertIn("non-negative", self.app.error[0].value)

    def test_noise_explanation_follows_selected_type(self):
        def explanation():
            [panel] = [e for e in self.app.expander if e.label == "How does this noise work?"]
            return all_text(panel.markdown)

        self.assertIn("standard deviation", explanation())
        self.app.radio(key="noise_type").set_value("salt_and_pepper").run()
        self.assertIn("salt", explanation())
        self.app.radio(key="noise_type").set_value("speckle").run()
        self.assertIn("times its own brightness", explanation())


if __name__ == "__main__":
    unittest.main()
