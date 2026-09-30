"""Command-line interface for local use and GitHub Actions."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from .config import SitePaths
from .pipeline import GalleryPipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build and maintain the CuteNew Gallery static site.")
    parser.add_argument("--root", type=Path, default=Path("."), help="repository root (default: current directory)")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("ingest", help="validate uploads, create assets, and rebuild indexes")

    rebuild = commands.add_parser("rebuild", help="rebuild indexes and data from image_log.csv")
    rebuild.add_argument(
        "--details",
        action="store_true",
        help="also regenerate every individual image detail page",
    )
    commands.add_parser("manifest", help="scan checked-out full images and save their checksums")
    commands.add_parser("watermark", help="refresh all legacy image watermark bars")
    commands.add_parser("crop-previews", help="center-crop existing preview images to 16:10")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    pipeline = GalleryPipeline(SitePaths.from_root(args.root))

    if args.command == "ingest":
        result = pipeline.ingest()
        print(f"Added {len(result.added)} image(s); skipped {len(result.duplicates)} duplicate(s).")
    elif args.command == "rebuild":
        pipeline.rebuild_site(include_detail_pages=args.details)
        print("Gallery indexes and data rebuilt.")
    elif args.command == "manifest":
        count = pipeline.build_manifest()
        print(f"Image manifest contains {count} file(s).")
    elif args.command == "watermark":
        count = pipeline.refresh_watermarks()
        print(f"Refreshed {count} watermark bar(s).")
    elif args.command == "crop-previews":
        count = pipeline.crop_previews()
        print(f"Cropped {count} preview image(s).")
    return 0
