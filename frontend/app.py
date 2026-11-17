"""Image Noise Lab: the Streamlit web interface of the project.

Stage 5A: upload an image, convert it to grayscale and show it.
(Noise, filters, metrics and downloads are added in Stages 5B-5E.)

Launch from the project root folder (IP) with:

    python -m streamlit run frontend/app.py

This file contains only interface code. Checking and decoding the upload
is done by frontend/image_processing.py, and all image processing uses the
existing functions in src/.
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
    MAX_FILE_SIZE_MB,
    MAX_PIXELS,
    UPLOAD_TYPES,
    format_file_size,
    is_large_image,
    load_uploaded_image,
)
from src.image_io import format_image_info, get_image_info  # noqa: E402

APP_TITLE = "Image Noise Lab — Noise Addition and Removal"


def show_header():
    st.title(APP_TITLE)
    st.markdown(
        "A university Image Processing project. Upload a photo, add artificial noise, "
        "remove it with classic filters and measure the result with **MSE** and **PSNR**."
    )


def show_sidebar():
    """Draw the sidebar and return the uploaded file (or None)."""
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
        st.divider()
        st.caption("Noise and filter controls will appear here in the next stages.")
    return uploaded_file


def show_welcome():
    """Shown before any image is uploaded."""
    st.info("Upload a PNG or JPEG image in the sidebar to begin.", icon="⬅️")
    st.subheader("How the lab works")
    steps = [
        ("1. Upload", "Choose a photo. It is converted to a grayscale reference image.", "Available"),
        ("2. Add noise", "Gaussian, salt-and-pepper or speckle noise with a fixed seed.", "Next stage"),
        ("3. Remove noise", "Mean, Gaussian, median or bilateral filter.", "Later stage"),
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
            "processing will use the grayscale version shown on the right. "
            "Your original file is not changed.",
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
            "Processing in the next steps may take a few seconds.",
            icon="⏳",
        )


def show_images(image):
    st.subheader("Your image")
    st.text(f"File: {image.file_name}")
    left, right = st.columns(2)
    with left:
        # output_format="PNG" makes Streamlit send the exact pixels (no extra JPEG compression).
        st.image(image.preview_rgb, caption="Uploaded image (as decoded)", output_format="PNG", width="stretch")
    with right:
        st.image(
            image.grayscale,
            caption="Grayscale reference (used for all processing)",
            output_format="PNG",
            width="stretch",
        )


def show_dimensions(image):
    width_col, height_col, pixels_col, size_col = st.columns(4)
    width_col.metric("Width", f"{image.width} px")
    height_col.metric("Height", f"{image.height} px")
    pixels_col.metric("Pixels", f"{image.pixel_count:,}")
    size_col.metric("File size", format_file_size(image.file_size))


def show_details(image):
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
    uploaded_file = show_sidebar()

    if uploaded_file is None:
        show_welcome()
        return

    try:
        image = load_uploaded_image(uploaded_file.name, uploaded_file.getvalue())
    except (TypeError, ValueError) as error:
        st.error(f"**This file cannot be used.** {error}", icon="🚫")
        return

    show_image_notes(image)
    show_images(image)
    show_dimensions(image)
    show_details(image)


main()
