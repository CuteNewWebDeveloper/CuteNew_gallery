"""Backward-compatible entry point for the gallery ingestion workflow."""

from gallery.cli import main


if __name__ == "__main__":
    raise SystemExit(main(["ingest"]))
