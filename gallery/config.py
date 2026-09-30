"""Filesystem layout and shared build settings."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


PAGE_SIZE = 28
PREVIEW_WIDTH = 380
PREVIEW_ASPECT_RATIO = 16 / 10
MAX_IMAGE_DIMENSION = 1920
WATERMARK_HEIGHT = 17
BRAND_WATERMARK_WIDTH_RATIO = 0.28
BRAND_WATERMARK_OPACITY = 0.78
BRAND_WATERMARK_MARGIN_RATIO = 0.03


@dataclass(frozen=True)
class SitePaths:
    """The repository paths used by the gallery generator."""

    root: Path

    @classmethod
    def from_root(cls, root: Path | str = ".") -> "SitePaths":
        return cls(Path(root).resolve())

    @property
    def docs(self) -> Path:
        return self.root / "docs"

    @property
    def input_dir(self) -> Path:
        return self.docs / "input_material"

    @property
    def images_dir(self) -> Path:
        return self.docs / "images"

    @property
    def previews_dir(self) -> Path:
        return self.docs / "images_preview"

    @property
    def pages_dir(self) -> Path:
        return self.docs / "pages"

    @property
    def assets_dir(self) -> Path:
        return self.docs / "assets"

    @property
    def site_css(self) -> Path:
        return self.assets_dir / "site.css"

    @property
    def site_script(self) -> Path:
        return self.assets_dir / "site.js"

    @property
    def brand_watermark(self) -> Path:
        return self.assets_dir / "brand-watermark.png"

    @property
    def image_log(self) -> Path:
        return self.images_dir / "image_log.csv"

    @property
    def image_manifest(self) -> Path:
        return self.images_dir / "image_manifest.json"

    @property
    def date_data(self) -> Path:
        return self.docs / "datedata.csv"

    @property
    def airport_data(self) -> Path:
        return self.docs / "airportdata.csv"

    @property
    def gallery_data(self) -> Path:
        return self.docs / "gallery-data.json"

    @property
    def index_page(self) -> Path:
        return self.docs / "index.html"

    @property
    def filter_page(self) -> Path:
        return self.docs / "photos.html"

    def ensure_directories(self) -> None:
        for directory in (
            self.docs,
            self.input_dir,
            self.images_dir,
            self.previews_dir,
            self.pages_dir,
            self.assets_dir,
        ):
            directory.mkdir(parents=True, exist_ok=True)
