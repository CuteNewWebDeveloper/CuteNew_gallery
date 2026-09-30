"""Backward-compatible entry point for manually refreshing watermark bars."""

from gallery.cli import main


if __name__ == "__main__":
    raise SystemExit(main(["watermark"]))
