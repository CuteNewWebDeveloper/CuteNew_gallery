"""Build and maintain the CuteNew static gallery."""

from .config import SitePaths
from .pipeline import GalleryPipeline

__all__ = ["GalleryPipeline", "SitePaths"]
