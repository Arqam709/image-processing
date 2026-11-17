"""Image Noise Lab: the Streamlit web interface of the project.

Stage 5A: upload an image, convert it to grayscale and show it.
Stage 5B: add Gaussian, salt-and-pepper or speckle noise with a fixed seed.
Stage 5C: remove noise with the mean, Gaussian, median or bilateral filter.
(Metrics and downloads are added in Stages 5D-5E.)

Launch from the project root folder (IP) with:

    python -m streamlit run frontend/app.py

This file contains only interface code. Checking and decoding the upload
and choosing the noise and filter functions is done by
frontend/image_processing.py, and all image processing uses the existing
functions in src/.

Processing flow on every run:
    uploaded file -> grayscale reference -> noisy image -> filtered image
The filter is always applied to the noisy image, never to the reference.

How Streamlit works: every time the user changes a control, this whole
script runs again from the top. Because the noise always uses the chosen
seed, running again with the same settings gives exactly the same pixels,
so changing only the filter never changes the noisy image.
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
    BILATERAL_DIAMETERS,
    BILATERAL_SIGMA_RANGE,
    DEFAULT_SEED,
    FILTER_OPTIONS,
    FILTER_TYPES,
    GAUSSIAN_FILTER_SIGMA_RANGE,
    KERNEL_SIZES,
    MAX_FILE_SIZE_MB,
    MAX_PIXELS,
    NOISE_OPTIONS,
    NOISE_TYPES,
    UPLOAD_TYPES,
    ZOOM_DISPLAY_SIZE,
    apply_selected_filter,
    crop_square,
    describe_filter,
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


# Shown in "How does this filter work?". Each text describes what src/filters.py
# (that is, OpenCV) does. p = the pixel being filtered, q = a neighbour in the window.
FILTER_DETAILS = {
    "mean": (
        "Every pixel is replaced by the plain average of the k × k window around it "
        "(k = kernel size). All pixels in the window count equally. A bigger window "
        "averages more pixels: more smoothing, but also more blur.",
        r"g(p) = \frac{1}{k^2} \sum_{q \in \text{window}(p)} f(q)",
    ),
    "gaussian": (
        "Like the mean filter, but each neighbour gets a weight from a bell-shaped "
        "(Gaussian) curve: the centre pixel counts most and far pixels count less.\n\n"
        "**Filter σ** is the width of that bell in pixels. A larger σ gives a flatter bell "
        "and stronger smoothing; the kernel size limits how far the bell reaches. "
        "**σ = 0** means OpenCV chooses σ from the kernel size. For a 3 × 3 kernel it then "
        "uses the fixed weights ¼, ½, ¼ in each direction.\n\n"
        "This filter σ is about *smoothing* and has nothing to do with the σ of Gaussian *noise*.",
        r"g(p) = \frac{\sum_q w(q)\, f(q)}{\sum_q w(q)}, \quad "
        r"w(q) = \exp\!\left(-\frac{\lVert q-p \rVert^2}{2\sigma^2}\right)",
    ),
    "median": (
        "The k × k values around each pixel are sorted, and the **middle** value is used. "
        "One very bright or very dark pixel ends up at the end of the sorted list and is "
        "simply dropped, not averaged in. The output only contains values that already "
        "existed in the window. But a line only one pixel wide is also a minority in its "
        "window, so it can disappear too.",
        r"g(p) = \operatorname{median}\{\, f(q) : q \in \text{window}(p) \,\}",
    ),
    "bilateral": (
        "Each neighbour's weight is the product of two bells. One is for **distance** "
        "(controlled by sigma space) and one is for **brightness difference** (controlled "
        "by sigma color). So a neighbour counts only if it is near **and** similar. Across "
        "an edge the brightness difference is large, so the other side is hardly mixed in "
        "and the edge stays sharp.\n\n"
        "* **Diameter:** size of the neighbourhood (window width in pixels).\n"
        "* **Sigma color:** how different two brightness values (0–255) can be while still "
        "influencing each other. Larger = more mixing, weaker edge protection.\n"
        "* **Sigma space:** how far away (in pixels) neighbours still influence the result.",
        r"w(q) = \exp\!\left(-\frac{\lVert q-p \rVert^2}{2\sigma_s^2}\right)"
        r"\exp\!\left(-\frac{(f(q)-f(p))^2}{2\sigma_c^2}\right), \quad "
        r"g(p) = \frac{\sum_q w(q)\, f(q)}{\sum_q w(q)}",
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
                "Noise standard deviation (σ)",
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
    return noise_type, strength, seed


def kernel_size_control(key, label="Kernel size (window)"):
    """An odd window-size selector (3 x 3 ... 15 x 15)."""
    return st.select_slider(
        label,
        options=KERNEL_SIZES,
        value=3,
        format_func=lambda k: f"{k} × {k}",
        key=key,
        persist_state="page",
        help="How many neighbouring pixels are used: 3 × 3 = 9 pixels. Larger = stronger smoothing, more blur.",
    )


def show_filter_controls():
    """Draw section 3 of the sidebar and return (filter_type, parameters).

    `parameters` uses exactly the argument names of the src/filters.py function.
    Only the controls of the selected filter are shown; each control has its own
    key and persist_state="page", so its value is remembered while another
    filter is selected.
    """
    with st.sidebar:
        st.divider()
        st.header("3. Remove Noise")
        filter_type = st.radio(
            "Filter",
            FILTER_TYPES,
            format_func=lambda key: FILTER_OPTIONS[key].label,
            key="filter_type",
        )
        option = FILTER_OPTIONS[filter_type]
        st.caption(option.explanation)
        defaults = option.defaults

        if filter_type == "mean":
            parameters = {"kernel_size": kernel_size_control("mean_kernel_size")}
        elif filter_type == "gaussian":
            low, high, step = GAUSSIAN_FILTER_SIGMA_RANGE
            parameters = {
                "kernel_size": kernel_size_control("gaussian_kernel_size"),
                "sigma": st.slider(
                    "Gaussian filter σ (blur width in pixels, 0 = auto)",
                    min_value=low,
                    max_value=high,
                    value=defaults["sigma"],
                    step=step,
                    format="%.1f",
                    key="gaussian_filter_sigma",
                    persist_state="page",
                    help=(
                        "Controls how strongly the filter smooths. 0 lets OpenCV choose a value "
                        "from the kernel size. This is NOT the σ of Gaussian noise."
                    ),
                ),
            }
        elif filter_type == "median":
            parameters = {"kernel_size": kernel_size_control("median_kernel_size")}
            st.caption("It can also remove thin lines and fine details.")
        else:
            low, high, step = BILATERAL_SIGMA_RANGE
            parameters = {
                "diameter": st.select_slider(
                    "Diameter (neighbourhood size)",
                    options=BILATERAL_DIAMETERS,
                    value=defaults["diameter"],
                    format_func=lambda d: f"{d} pixels",
                    key="bilateral_diameter",
                    persist_state="page",
                    help="Width of the square neighbourhood. Larger = more neighbours, slower.",
                ),
                "sigma_color": st.slider(
                    "Sigma color",
                    min_value=low,
                    max_value=high,
                    value=defaults["sigma_color"],
                    step=step,
                    key="bilateral_sigma_color",
                    persist_state="page",
                    help="How different two brightness values (0–255) can be while still influencing each other.",
                ),
                "sigma_space": st.slider(
                    "Sigma space",
                    min_value=low,
                    max_value=high,
                    value=defaults["sigma_space"],
                    step=step,
                    key="bilateral_sigma_space",
                    persist_state="page",
                    help="How far away (in pixels) neighbouring pixels can still influence the result.",
                ),
            }
        st.divider()
        st.caption("MSE/PSNR measurements will appear in the next stage.")
    return filter_type, parameters


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
        ("3. Remove noise", "Mean, Gaussian, median or bilateral filter.", "Available"),
        ("4. Compare", "MSE and PSNR against the clean grayscale reference.", "Next stage"),
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


def show_comparison(image, noisy, noise_label, seed, filtered, filter_labels):
    """Original grayscale, noisy and filtered image side by side, at the same compact size.

    `filtered` is None if the filter failed; then only the original and noisy
    images are shown (the error message is shown above them).
    """
    filter_short, filter_long = filter_labels
    st.subheader("Original grayscale → noisy → filtered")
    columns = st.columns(3)
    shown_original = fit_for_display(image.grayscale)
    # output_format="PNG" makes Streamlit send the exact pixels (no extra JPEG compression).
    columns[0].image(shown_original, caption="Original Grayscale", output_format="PNG")
    columns[1].image(fit_for_display(noisy), caption=noise_label, output_format="PNG")
    if filtered is not None:
        columns[2].image(fit_for_display(filtered), caption=filter_short, output_format="PNG")

    st.markdown(
        f"**Settings:** noise = {noise_label} · seed = {seed} · filter = {filter_long} · "
        f"{image.width} × {image.height} pixels"
    )
    st.caption(
        f"Pixel fingerprint of the noisy image: `{pixel_fingerprint(noisy)}`. "
        "It is calculated from every pixel value: the same image, settings and seed always "
        "give the same fingerprint."
    )
    if filtered is not None:
        st.caption(
            f"Pixel fingerprint of the filtered image: `{pixel_fingerprint(filtered)}`. "
            "Fingerprints only identify pixels; they say nothing about quality "
            "(MSE and PSNR come in the next stage)."
        )
        st.caption(
            "The filtered image is the noisy image after filtering. Filtering can reduce "
            "noise, but it does not recover the exact original."
        )
    if shown_original.shape != image.grayscale.shape:
        st.caption(
            f"The images are shown smaller than their real size ({image.width} × {image.height}). "
            "Shrinking averages neighbouring pixels and makes noise look weaker. "
            "Use \"Inspect details\" below to see the real pixels."
        )


def show_zoom(images_with_labels):
    """Show the same small square of every image, enlarged so single pixels are visible.

    images_with_labels: list of (image, label); all images have the same shape,
    so crop_square returns the same region for each of them.
    """
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

        crops = [crop_square(image, x_percent, y_percent, size) for image, _ in images_with_labels]
        top, left = crops[0][1]
        side = crops[0][0].shape[0]
        factor = max(1, ZOOM_DISPLAY_SIZE // side)
        where = f"rows {top}–{top + side - 1}, columns {left}–{left + side - 1}"
        st.caption(f"Region shown in every image: {where}.")
        for column, (crop, region), (_, label) in zip(st.columns(len(crops)), crops, images_with_labels):
            crop_top, crop_left = region
            column.image(
                enlarge_pixels(crop, factor),
                caption=f"{label} (rows {crop_top}–{crop_top + side - 1}, columns {crop_left}–{crop_left + side - 1})",
                output_format="PNG",
            )
        st.caption(f"Each image pixel is drawn as a {factor} × {factor} block. Nothing is smoothed or changed.")


def show_noise_explanation(noise_type):
    with st.expander("How does this noise work?"):
        text, formula = NOISE_DETAILS[noise_type]
        st.markdown(text)
        st.caption("Formula used by src/noise.py (f = clean pixel, g = noisy pixel, N = number of pixels):")
        st.latex(formula)


def show_filter_explanation(filter_type):
    option = FILTER_OPTIONS[filter_type]
    with st.expander("How does this filter work?"):
        text, formula = FILTER_DETAILS[filter_type]
        st.markdown(text)
        st.markdown(f"**Benefit:** {option.benefit}  \n**Limitation:** {option.limitation}")
        st.caption("Formula (f = noisy image, g = filtered image, p = pixel, q = neighbour in the window):")
        st.latex(formula)
        st.caption("No filter is best for every image and noise type. Stage 5D will measure them with MSE and PSNR.")


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

    filter_type, parameters = show_filter_controls()
    try:
        # The filter always gets the NOISY image (never the clean reference).
        filtered = apply_selected_filter(noisy, filter_type, parameters)
    except (TypeError, ValueError) as error:
        filtered = None
        st.error(f"**The filter could not be applied.** {error} The other images are still shown.", icon="🚫")

    noise_label = describe_noise(noise_type, strength)
    filter_labels = (describe_filter(filter_type, parameters, short=True), describe_filter(filter_type, parameters))
    show_comparison(image, noisy, noise_label, seed, filtered, filter_labels)

    zoom_images = [(image.grayscale, "Original Grayscale"), (noisy, noise_label)]
    if filtered is not None:
        zoom_images.append((filtered, filter_labels[0]))
    show_zoom(zoom_images)
    show_noise_explanation(noise_type)
    show_filter_explanation(filter_type)
    show_dimensions(image)
    show_details(image)


main()
