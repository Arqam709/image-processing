"""Image Noise Lab: the Streamlit web interface of the project.

Stage 5A: upload an image, convert it to grayscale and show it.
Stage 5B: add Gaussian, salt-and-pepper or speckle noise with a fixed seed.
(Filters, metrics and downloads are added in Stages 5C-5E.)

Launch from the project root folder (IP) with:

    python -m streamlit run frontend/app.py

This file contains only interface code. Checking and decoding the upload
and choosing the noise function is done by frontend/image_processing.py,
and all image processing uses the existing functions in src/.

How Streamlit works: every time the user changes a control, this whole
script runs again from the top. Because the noise always uses the chosen
seed, running again with the same settings gives exactly the same pixels.
"""

import sys
from pathlib import Path

# Streamlit runs this file as a script, so Python does not know where the
# project root is. We add the root folder (the parent of frontend/) once,
# so that "import src..." and "import frontend..." work no matter which
# folder the command is started from.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st  # noqa: E402  (must come after the path line above)

from frontend.image_processing import (  # noqa: E402
    DEFAULT_SEED,
    MAX_FILE_SIZE_MB,
    MAX_PIXELS,
    NOISE_OPTIONS,
    NOISE_TYPES,
    UPLOAD_TYPES,
    ZOOM_DISPLAY_SIZE,
    crop_square,
    describe_noise,
    enlarge_pixels,
    fit_for_display,
    format_file_size,
    is_large_image,
    load_uploaded_image,
    make_noisy_image,
    pixel_fingerprint,
)
from src.image_io import format_image_info, get_image_info  # noqa: E402
from src.noise import salt_and_pepper_counts  # noqa: E402

APP_TITLE = "Image Noise Lab — Noise Addition and Removal"
ZOOM_SIZES = (16, 32, 64, 128)  # side length of the zoom window in image pixels

# Shown in "How does this noise work?". Each text describes what src/noise.py does.
NOISE_DETAILS = {
    "gaussian": (
        "Every pixel gets its own random number from a bell-shaped (normal) distribution "
        "with average 0 and standard deviation **σ**. The number is added to the pixel's "
        "brightness, the result is rounded to a whole number and kept inside 0–255.\n\n"
        "**σ (sigma)** sets the typical size of the change: for a normal distribution about "
        "two out of three random numbers lie between −σ and +σ. Dark and bright areas get "
        "the same amount of noise.",
        r"g = \mathrm{clip}_{[0,255]}\big(\mathrm{round}(f + n)\big), \quad n \sim \mathcal{N}(0,\ \sigma^2)",
    ),
    "salt_and_pepper": (
        "A fixed number of different pixels is chosen at random: the **amount** times the "
        "number of pixels, rounded. Half of them become white (255, *salt*) and the rest "
        "become black (0, *pepper*). All other pixels stay exactly the same.\n\n"
        "**Amount** is the share of pixels that are changed: 0.05 means 5% of the pixels.",
        r"\text{selected} = \lfloor \text{amount} \cdot N + 0.5 \rfloor, \quad "
        r"\text{salt} = \lfloor \text{selected} / 2 \rfloor, \quad \text{pepper} = \text{selected} - \text{salt}",
    ),
    "speckle": (
        "Every pixel gets a random number n from a normal distribution with average 0 and "
        "variance **v**. The pixel's change is n **times its own brightness**, so bright "
        "areas get stronger noise and pure black pixels (0) never change. The result is "
        "rounded and kept inside 0–255.\n\n"
        "**Variance** sets the size of the random factor: its standard deviation is √v, "
        "so v = 0.04 gives √0.04 = 0.2, meaning typical changes of about 20% of the "
        "pixel's brightness.",
        r"g = \mathrm{clip}_{[0,255]}\big(\mathrm{round}(f + f \cdot n)\big), \quad n \sim \mathcal{N}(0,\ v)",
    ),
}


# --------------------------------------------------------------------------
# Header and sidebar
# --------------------------------------------------------------------------
def show_header():
    st.title(APP_TITLE)
    st.markdown(
        "A university Image Processing project. Upload a photo, add artificial noise, "
        "remove it with classic filters and measure the result with **MSE** and **PSNR**."
    )


def show_upload_control():
    """Draw section 1 of the sidebar and return the uploaded file (or None)."""
    with st.sidebar:
        st.header("1. Upload an image")
        uploaded_file = st.file_uploader(
            "Choose a PNG or JPEG file",
            type=list(UPLOAD_TYPES),
            max_upload_size=MAX_FILE_SIZE_MB,  # in megabytes; checked again by load_uploaded_image
            help=(
                f"Up to {MAX_FILE_SIZE_MB} MB and {MAX_PIXELS // 1_000_000} megapixels. "
                "The file is processed in memory only. It is never changed or saved."
            ),
        )
        st.caption(
            "Our algorithms work on **grayscale** images: one brightness value "
            "from 0 (black) to 255 (white) for every pixel. Colour photos are "
            "converted to grayscale automatically."
        )
    return uploaded_file


def show_noise_controls(image):
    """Draw section 2 of the sidebar and return (noise_type, strength, seed).

    Only the slider for the selected noise type is shown. Each slider has
    its own key and persist_state="page", so its value is remembered while
    another noise type is selected.
    """
    with st.sidebar:
        st.divider()
        st.header("2. Add Noise")
        noise_type = st.radio(
            "Noise type",
            NOISE_TYPES,
            format_func=lambda key: NOISE_OPTIONS[key].label,
            key="noise_type",
        )
        option = NOISE_OPTIONS[noise_type]
        st.caption(option.explanation)

        if noise_type == "gaussian":
            strength = st.slider(
                "Standard deviation (σ, sigma)",
                min_value=option.minimum,
                max_value=option.maximum,
                value=option.default,
                step=option.step,
                key="gaussian_sigma",
                persist_state="page",
                help="Typical size of the random brightness change, in gray levels (0–255 scale).",
            )
        elif noise_type == "salt_and_pepper":
            strength = st.slider(
                "Amount (share of pixels changed)",
                min_value=option.minimum,
                max_value=option.maximum,
                value=option.default,
                step=option.step,
                format="percent",  # shows 0.05 as "5%"; the value itself stays 0.05
                key="salt_and_pepper_amount",
                persist_state="page",
                help="0.05 (5%) means that 5 out of every 100 pixels become black or white.",
            )
            selected, salt, pepper = salt_and_pepper_counts(image.pixel_count, strength)
            st.caption(
                f"{strength * 100:g}% of pixels = {selected:,} of {image.pixel_count:,} pixels "
                f"({salt:,} white, {pepper:,} black)."
            )
        else:
            strength = st.slider(
                "Variance (v)",
                min_value=option.minimum,
                max_value=option.maximum,
                value=option.default,
                step=option.step,
                format="%.2f",
                key="speckle_variance",
                persist_state="page",
                help="Size of the random factor that multiplies each pixel's brightness.",
            )

        seed = st.number_input(
            "Random Seed",
            value=DEFAULT_SEED,
            step=1,
            format="%d",
            key="seed",
            help="Any whole number from 0 upwards. Our experiments use 42.",
        )
        st.caption(
            "The seed makes the random noise reproducible. The same image, noise settings "
            "and seed produce the same result."
        )
        st.divider()
        st.caption("Filter controls will appear here in the next stage.")
    return noise_type, strength, seed


# --------------------------------------------------------------------------
# Main area
# --------------------------------------------------------------------------
def show_welcome():
    """Shown before any image is uploaded."""
    st.info("Upload a PNG or JPEG image in the sidebar to begin.", icon="⬅️")
    st.subheader("How the lab works")
    steps = [
        ("1. Upload", "Choose a photo. It is converted to a grayscale reference image.", "Available"),
        ("2. Add noise", "Gaussian, salt-and-pepper or speckle noise with a fixed seed.", "Available"),
        ("3. Remove noise", "Mean, Gaussian, median or bilateral filter.", "Next stage"),
        ("4. Compare", "MSE and PSNR against the clean grayscale reference.", "Later stage"),
    ]
    for column, (title, text, status) in zip(st.columns(len(steps)), steps):
        with column.container(border=True):
            st.markdown(f"**{title}**")
            st.write(text)
            st.caption(status)


def show_image_notes(image):
    """Explain colour conversion, transparency and size to the user."""
    if image.is_colour:
        st.info(
            "This is a **colour** image. Our algorithms process grayscale images, so all "
            "processing uses its grayscale version. The colour photo is in "
            "\"Uploaded photo (original colours)\" below. Your original file is not changed.",
            icon="ℹ️",
        )
    else:
        st.info("This image is already grayscale (its red, green and blue values are equal).", icon="ℹ️")
    if image.has_alpha:
        st.warning(
            "This PNG has transparent areas. Transparency is ignored: those pixels use the "
            "colour stored underneath them, which is often black.",
            icon="⚠️",
        )
    if is_large_image(image):
        st.warning(
            f"This is a large image ({image.pixel_count / 1_000_000:.1f} megapixels). "
            "Each change of a control may take a moment.",
            icon="⏳",
        )


def show_comparison(image, noisy, noise_label, seed):
    """Original grayscale and noisy image side by side, at the same compact size."""
    st.subheader("Original grayscale vs noisy image")
    left, right = st.columns(2)
    shown_original = fit_for_display(image.grayscale)
    # output_format="PNG" makes Streamlit send the exact pixels (no extra JPEG compression).
    left.image(shown_original, caption="Original Grayscale", output_format="PNG")
    right.image(fit_for_display(noisy), caption=noise_label, output_format="PNG")

    st.markdown(f"**Settings:** {noise_label} · seed = {seed} · {image.width} × {image.height} pixels")
    st.caption(
        f"Pixel fingerprint of the noisy image: `{pixel_fingerprint(noisy)}`. "
        "It is calculated from every pixel value: the same image, settings and seed always "
        "give the same fingerprint."
    )
    if shown_original.shape != image.grayscale.shape:
        st.caption(
            f"Both images are shown smaller than their real size ({image.width} × {image.height}). "
            "Shrinking averages neighbouring pixels and makes noise look weaker. "
            "Use \"Inspect details\" below to see the real pixels."
        )


def show_zoom(image, noisy, noise_label):
    """Show the same small square of both images, enlarged so single pixels are visible."""
    with st.expander("🔍 Inspect details (zoom into the real pixels)"):
        size_col, x_col, y_col = st.columns(3)
        size = size_col.select_slider(
            "Zoom window",
            options=ZOOM_SIZES,
            value=64,
            format_func=lambda s: f"{s} × {s} pixels",
            key="zoom_size",
        )
        x_percent = x_col.slider("Horizontal position (%)", 0, 100, 50, key="zoom_x")
        y_percent = y_col.slider("Vertical position (%)", 0, 100, 50, key="zoom_y")

        original_crop, (top, left) = crop_square(image.grayscale, x_percent, y_percent, size)
        noisy_crop, _ = crop_square(noisy, x_percent, y_percent, size)
        side = original_crop.shape[0]
        factor = max(1, ZOOM_DISPLAY_SIZE // side)

        where = f"rows {top}–{top + side - 1}, columns {left}–{left + side - 1}"
        left_col, right_col = st.columns(2)
        left_col.image(enlarge_pixels(original_crop, factor), caption=f"Original Grayscale ({where})", output_format="PNG")
        right_col.image(enlarge_pixels(noisy_crop, factor), caption=f"{noise_label} ({where})", output_format="PNG")
        st.caption(f"Each image pixel is drawn as a {factor} × {factor} block. Nothing is smoothed or changed.")


def show_noise_explanation(noise_type):
    with st.expander("How does this noise work?"):
        text, formula = NOISE_DETAILS[noise_type]
        st.markdown(text)
        st.caption("Formula used by src/noise.py (f = clean pixel, g = noisy pixel, N = number of pixels):")
        st.latex(formula)


def show_dimensions(image):
    width_col, height_col, pixels_col, size_col = st.columns(4)
    width_col.metric("Width", f"{image.width} px")
    height_col.metric("Height", f"{image.height} px")
    pixels_col.metric("Pixels", f"{image.pixel_count:,}")
    size_col.metric("File size", format_file_size(image.file_size))


def show_details(image):
    st.text(f"File: {image.file_name}")
    with st.expander("Uploaded photo (original colours)"):
        st.image(fit_for_display(image.preview_rgb), caption="Uploaded image (as decoded)", output_format="PNG")
    with st.expander("Grayscale image details"):
        st.caption(f"Detected file format: {image.file_format}. Statistics from src.image_io.get_image_info.")
        st.code(format_image_info(get_image_info(image.grayscale)), language=None)
    with st.expander("How is the grayscale image made?"):
        st.markdown(
            "OpenCV decodes the uploaded file directly to grayscale (`cv2.imdecode` with "
            "`cv2.IMREAD_GRAYSCALE`), exactly like `load_grayscale_image` in Stage 1. "
            "For colour pixels OpenCV documents the brightness formula\n\n"
            "**Y = 0.299·R + 0.587·G + 0.114·B**\n\n"
            "Green counts most because our eyes are most sensitive to it. The decoder does "
            "this conversion itself, so some values can differ slightly from a separate "
            "colour-to-gray conversion, especially for JPEG files. We always use the same "
            "method, so the app and the Stage 1-4 demos see exactly the same pixels. "
            "Phone photos are rotated using their EXIF orientation tag."
        )


def main():
    st.set_page_config(page_title="Image Noise Lab", page_icon="🔬", layout="wide")
    show_header()
    uploaded_file = show_upload_control()

    if uploaded_file is None:
        show_welcome()
        return

    try:
        image = load_uploaded_image(uploaded_file.name, uploaded_file.getvalue())
    except (TypeError, ValueError) as error:
        st.error(f"**This file cannot be used.** {error}", icon="🚫")
        return

    noise_type, strength, seed = show_noise_controls(image)
    show_image_notes(image)

    try:
        noisy = make_noisy_image(image.grayscale, noise_type, strength, seed)
    except (TypeError, ValueError) as error:
        st.error(f"**Noise could not be added.** {error}", icon="🚫")
        return

    noise_label = describe_noise(noise_type, strength)
    show_comparison(image, noisy, noise_label, seed)
    show_zoom(image, noisy, noise_label)
    show_noise_explanation(noise_type)
    show_dimensions(image)
    show_details(image)


main()
