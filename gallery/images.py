"""Image normalization, watermarking, thumbnailing, and checksum-ready encoding."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

from .config import (
    BRAND_WATERMARK_MARGIN_RATIO,
    BRAND_WATERMARK_OPACITY,
    BRAND_WATERMARK_WIDTH_RATIO,
    MAX_IMAGE_DIMENSION,
    PREVIEW_ASPECT_RATIO,
    PREVIEW_WIDTH,
    WATERMARK_HEIGHT,
)
from .models import UploadMetadata


FULL_IMAGE_QUALITY = 100
PREVIEW_IMAGE_QUALITY = 55


def open_normalized_image(path: Path, *, cap_long_edge: bool = True) -> Image.Image:
    """Open an image safely, normalize its orientation, and optionally cap its long edge."""

    with Image.open(path) as source:
        image = ImageOps.exif_transpose(source)
        if image.mode != "RGB":
            image = image.convert("RGB")
        else:
            image = image.copy()
        image.load()

    width, height = image.size
    long_edge = max(width, height)
    if not cap_long_edge or long_edge <= MAX_IMAGE_DIMENSION:
        return image

    scale = MAX_IMAGE_DIMENSION / long_edge
    target_size = (round(width * scale), round(height * scale))
    return image.resize(target_size, Image.Resampling.LANCZOS)


def load_font(size: int = 12) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Use a CJK-capable font when it is available on the current runner."""

    candidates = (
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/arphic/ukai.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "C:/Windows/Fonts/simhei.ttf",
    )
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


def add_watermark(image: Image.Image, metadata: UploadMetadata) -> Image.Image:
    """Return a full-size gallery image with the traditional bottom information bar."""

    if image.mode != "RGB":
        image = image.convert("RGB")
    width, height = image.size
    result = Image.new("RGB", (width, height + WATERMARK_HEIGHT), "black")
    result.paste(image, (0, 0))

    draw = ImageDraw.Draw(result)
    font = load_font(12)
    year = metadata.taken_at.split(".", 1)[0]
    left_text = f" © {year} {metadata.photographer}, All Rights Reserved."
    right_text = f"[{metadata.taken_at}, {metadata.location.upper()}] CuteNew Gallery Images"
    left_box = draw.textbbox((0, 0), left_text, font=font)
    right_box = draw.textbbox((0, 0), right_text, font=font)
    left_width = left_box[2] - left_box[0]
    right_width = right_box[2] - right_box[0]
    text_height = left_box[3] - left_box[1]

    margin = 20
    central_width = width // 2
    start_x = max((width - central_width) // 2, left_width + margin + 10)
    end_x = min(width - (right_width + margin + 10), start_x + central_width)
    y_top = height + 3
    if end_x > start_x:
        for x in range(start_x, end_x, 30):
            draw.polygon(
                ((x, y_top), (x + 20, y_top), (x + 25, y_top + 10), (x + 5, y_top + 10)),
                fill="white",
            )

    text_y = height + (WATERMARK_HEIGHT - text_height) // 2
    draw.text((10, text_y), left_text, fill="white", font=font)
    draw.text((max(10, width - right_width - 10), text_y), right_text, fill="white", font=font)
    return result


def add_brand_watermark(image: Image.Image, watermark_path: Path) -> Image.Image:
    """Overlay the tracked transparent brand watermark in the image's lower-right corner."""

    if not watermark_path.is_file():
        raise FileNotFoundError(
            f"Missing brand watermark asset: {watermark_path}. Restore docs/assets/brand-watermark.png."
        )

    with Image.open(watermark_path) as source:
        watermark = source.convert("RGBA")
    if watermark.getchannel("A").getbbox() is None:
        raise ValueError(f"Brand watermark asset is fully transparent: {watermark_path}")

    width, height = image.size
    margin = max(2, round(min(width, height) * BRAND_WATERMARK_MARGIN_RATIO))
    margin = min(margin, max(0, (width - 1) // 2), max(0, (height - 1) // 2))
    available_width = max(1, width - 2 * margin)
    available_height = max(1, height - 2 * margin)
    target_width = min(available_width, max(1, round(width * BRAND_WATERMARK_WIDTH_RATIO)))
    target_height = max(1, round(target_width * watermark.height / watermark.width))
    if target_height > available_height:
        target_height = available_height
        target_width = max(1, round(target_height * watermark.width / watermark.height))

    watermark = watermark.resize((target_width, target_height), Image.Resampling.LANCZOS)
    alpha = watermark.getchannel("A").point(lambda value: round(value * BRAND_WATERMARK_OPACITY))
    watermark.putalpha(alpha)

    result = image.convert("RGBA")
    result.alpha_composite(watermark, (width - margin - target_width, height - margin - target_height))
    return result.convert("RGB")


def remove_watermark(image: Image.Image) -> Image.Image:
    """Remove the legacy 17px bar before a deliberate bulk watermark refresh."""

    width, height = image.size
    if height <= WATERMARK_HEIGHT:
        raise ValueError("image is too short to contain a watermark bar")
    return image.crop((0, 0, width, height - WATERMARK_HEIGHT))


def crop_to_preview_ratio(image: Image.Image) -> Image.Image:
    """Center-crop an image to the gallery's 16:10 thumbnail ratio."""

    width, height = image.size
    current_ratio = width / height
    if abs(current_ratio - PREVIEW_ASPECT_RATIO) < 0.01:
        return image.copy()

    if current_ratio > PREVIEW_ASPECT_RATIO:
        target_width = int(height * PREVIEW_ASPECT_RATIO)
        left = (width - target_width) // 2
        return image.crop((left, 0, left + target_width, height))

    target_height = int(width / PREVIEW_ASPECT_RATIO)
    top = (height - target_height) // 2
    return image.crop((0, top, width, top + target_height))


def build_preview(image: Image.Image) -> Image.Image:
    """Create the legacy 380px-wide, centered-crop preview without a watermark."""

    width, height = image.size
    target_height = max(1, round(PREVIEW_WIDTH * height / width))
    resized = image.resize((PREVIEW_WIDTH, target_height), Image.Resampling.LANCZOS)
    return crop_to_preview_ratio(resized)


def encode_jpeg(image: Image.Image, quality: int) -> bytes:
    buffer = BytesIO()
    image.convert("RGB").save(buffer, format="JPEG", quality=quality)
    return buffer.getvalue()


def build_gallery_assets(
    source_path: Path, metadata: UploadMetadata, brand_watermark_path: Path
) -> tuple[bytes, bytes]:
    """Build a brand-watermarked full image and clean preview bytes without mutating the upload."""

    normalized = open_normalized_image(source_path)
    full_image = add_watermark(add_brand_watermark(normalized, brand_watermark_path), metadata)
    preview = build_preview(normalized)
    return (
        encode_jpeg(full_image, FULL_IMAGE_QUALITY),
        encode_jpeg(preview, PREVIEW_IMAGE_QUALITY),
    )


def build_legacy_compatible_full_asset(source_path: Path, metadata: UploadMetadata) -> bytes:
    """Reproduce the previous full-image encoding for duplicate checks.

    Older long-edge images were JPEG-encoded once after resizing and once again after
    their information bar was added. New images use the cleaner one-pass pipeline,
    but checking this historical representation avoids accepting a duplicate merely
    because the legacy encoder made different bytes.
    """

    with Image.open(source_path) as source:
        image = source.copy()

    width, height = image.size
    if max(width, height) > MAX_IMAGE_DIMENSION:
        scale = MAX_IMAGE_DIMENSION / max(width, height)
        image = image.resize((int(width * scale), int(height * scale)), Image.Resampling.LANCZOS)
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
        resized_payload = encode_jpeg(image, quality=95)
        with Image.open(BytesIO(resized_payload)) as resized:
            image = resized.copy()

    return encode_jpeg(add_watermark(image, metadata), FULL_IMAGE_QUALITY)
