"""Backward-compatible entry point for manually cropping existing previews."""

from gallery.cli import main


if __name__ == "__main__":
    raise SystemExit(main(["crop-previews"]))
