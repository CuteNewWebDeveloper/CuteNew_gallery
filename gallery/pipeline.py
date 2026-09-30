"""The explicit, side-effect-contained gallery build pipeline."""

from __future__ import annotations

import hashlib
import os
import tempfile
import uuid
from dataclasses import dataclass
from pathlib import Path

from PIL import Image

from .config import PAGE_SIZE, SitePaths
from .images import (
    FULL_IMAGE_QUALITY,
    add_watermark,
    build_gallery_assets,
    build_legacy_compatible_full_asset,
    crop_to_preview_ratio,
    encode_jpeg,
    open_normalized_image,
    remove_watermark,
)
from .metadata import (
    IMAGE_SUFFIXES,
    UploadValidationError,
    date_counts,
    load_manifest,
    load_records,
    next_image_id,
    parse_upload_filename,
    read_airport_descriptions,
    reconcile_manifest,
    save_manifest,
    save_records,
)
from .models import ImageRecord, UploadMetadata
from .render import (
    render_airport_csv,
    render_date_csv,
    render_detail_page,
    render_filter_page,
    render_gallery_data,
    render_gallery_page,
    render_site_css,
    render_site_script,
)


@dataclass(frozen=True)
class IngestResult:
    added: tuple[str, ...]
    duplicates: tuple[str, ...]


@dataclass(frozen=True)
class _StagedImage:
    source: Path
    record: ImageRecord
    full_image: bytes
    preview: bytes
    checksum: str


class GalleryPipeline:
    """Coordinates upload ingestion and deterministic static-site generation."""

    def __init__(self, paths: SitePaths) -> None:
        self.paths = paths

    def ingest(self) -> IngestResult:
        """Validate and ingest every top-level image in docs/input_material.

        Validation and image rendering complete before any submitted upload is deleted.
        This deliberately leaves malformed uploads in place for a human to correct.
        """

        self.paths.ensure_directories()
        candidates = self._validated_uploads()
        records = load_records(self.paths.image_log)
        if not candidates:
            self.rebuild_site(records=records)
            return IngestResult(added=(), duplicates=())
        manifest = self._reconciled_manifest(records)
        known_checksums = set(manifest.values())

        next_id = next_image_id(records)
        staged: list[_StagedImage] = []
        duplicates: list[Path] = []
        for source, metadata in candidates:
            full_image, preview = build_gallery_assets(source, metadata, self.paths.brand_watermark)
            checksum = hashlib.md5(full_image).hexdigest()
            legacy_checksum = checksum
            if checksum not in known_checksums:
                legacy_checksum = hashlib.md5(
                    build_legacy_compatible_full_asset(source, metadata)
                ).hexdigest()
            if checksum in known_checksums or legacy_checksum in known_checksums:
                duplicates.append(source)
                continue

            filename = f"{uuid.uuid4()}.jpg"
            record = ImageRecord(
                image_id=next_id,
                filename=filename,
                taken_at=metadata.taken_at,
                location=metadata.location,
                photographer=metadata.photographer,
            )
            next_id += 1
            staged.append(
                _StagedImage(
                    source=source,
                    record=record,
                    full_image=full_image,
                    preview=preview,
                    checksum=checksum,
                )
            )
            known_checksums.add(checksum)

        for item in staged:
            _write_bytes_atomically(self.paths.images_dir / item.record.filename, item.full_image)
            _write_bytes_atomically(self.paths.previews_dir / item.record.filename, item.preview)
            _write_text_atomically(
                self.paths.pages_dir / f"Page{item.record.stem}.html",
                render_detail_page(item.record),
            )
            manifest[item.record.filename] = item.checksum

        updated_records = [*records, *(item.record for item in staged)]
        save_records(self.paths.image_log, updated_records)
        save_manifest(self.paths.image_manifest, manifest)
        self.rebuild_site(records=updated_records)

        for source in [*(item.source for item in staged), *duplicates]:
            source.unlink()

        return IngestResult(
            added=tuple(item.record.filename for item in staged),
            duplicates=tuple(path.name for path in duplicates),
        )

    def rebuild_site(self, *, records: list[ImageRecord] | None = None, include_detail_pages: bool = False) -> None:
        """Rebuild gallery indexes and client-side data without touching original images."""

        self.paths.ensure_directories()
        records = load_records(self.paths.image_log) if records is None else records
        ordered_records = sorted(records, key=lambda record: record.image_id, reverse=True)

        pages = [
            ordered_records[index : index + PAGE_SIZE]
            for index in range(0, len(ordered_records), PAGE_SIZE)
        ] or [[]]
        total_pages = len(pages)
        for page_number, page_records in enumerate(pages, start=1):
            output = self.paths.index_page if page_number == 1 else self.paths.docs / f"page{page_number}.html"
            _write_text_atomically(output, render_gallery_page(page_records, page_number, total_pages))

        if include_detail_pages:
            for record in records:
                _write_text_atomically(
                    self.paths.pages_dir / f"Page{record.stem}.html", render_detail_page(record)
                )

        descriptions = read_airport_descriptions(self.paths.airport_data)
        _write_text_atomically(self.paths.site_css, render_site_css())
        _write_text_atomically(self.paths.site_script, render_site_script())
        _write_text_atomically(self.paths.gallery_data, render_gallery_data(records))
        _write_text_atomically(self.paths.date_data, render_date_csv(date_counts(records)))
        _write_text_atomically(self.paths.airport_data, render_airport_csv(descriptions, records))
        _write_text_atomically(self.paths.filter_page, render_filter_page())

    def build_manifest(self) -> int:
        """Scan checked-out gallery images and persist their checksums for future ingestion."""

        self.paths.ensure_directories()
        manifest = reconcile_manifest(self.paths.images_dir, load_manifest(self.paths.image_manifest))
        missing = sorted({record.filename for record in load_records(self.paths.image_log)} - set(manifest))
        if missing:
            preview = ", ".join(missing[:3])
            suffix = " …" if len(missing) > 3 else ""
            raise RuntimeError(
                "Cannot build a complete manifest because these gallery images are not checked out: "
                f"{preview}{suffix}"
            )
        save_manifest(self.paths.image_manifest, manifest)
        return len(manifest)

    def refresh_watermarks(self) -> int:
        """Rebuild legacy full-image watermark bars from image_log.csv metadata.

        This is intentionally a manual maintenance operation. It assumes every full-size
        image already has the historic 17px bottom bar and will fail loudly if an image
        is too small to satisfy that invariant. Existing brand overlays remain intact;
        this command does not apply a new overlay to historic images.
        """

        records = load_records(self.paths.image_log)
        manifest = self._reconciled_manifest(records)
        updated = 0
        for record in records:
            image_path = self.paths.images_dir / record.filename
            if not image_path.exists():
                raise FileNotFoundError(f"Missing full-size image referenced by image_log.csv: {record.filename}")
            source = open_normalized_image(image_path, cap_long_edge=False)
            base = remove_watermark(source)
            metadata = UploadMetadata(record.taken_at, record.location, record.photographer)
            payload = encode_jpeg(add_watermark(base, metadata), FULL_IMAGE_QUALITY)
            _write_bytes_atomically(image_path, payload)
            manifest[record.filename] = hashlib.md5(payload).hexdigest()
            updated += 1
        save_manifest(self.paths.image_manifest, manifest)
        return updated

    def crop_previews(self) -> int:
        """Center-crop existing previews in a deliberate bulk-maintenance operation."""

        updated = 0
        for image_path in sorted(self.paths.previews_dir.glob("*")):
            if not image_path.is_file() or image_path.suffix.lower() not in IMAGE_SUFFIXES:
                continue
            with Image.open(image_path) as source:
                if abs(source.width / source.height - (16 / 10)) < 0.01:
                    continue
                cropped = crop_to_preview_ratio(source.convert("RGB"))
            _write_bytes_atomically(image_path, encode_jpeg(cropped, quality=95))
            updated += 1
        return updated

    def _validated_uploads(self) -> list[tuple[Path, UploadMetadata]]:
        invalid: list[str] = []
        uploads: list[tuple[Path, UploadMetadata]] = []
        for path in sorted(self.paths.input_dir.iterdir()):
            if path.is_dir():
                continue
            try:
                metadata = parse_upload_filename(path)
                # Decode during validation, so a broken image cannot leave a half-built gallery.
                open_normalized_image(path)
            except (UploadValidationError, OSError, ValueError) as error:
                invalid.append(str(error))
            else:
                uploads.append((path, metadata))

        if invalid:
            details = "\n- ".join(invalid)
            raise UploadValidationError(f"Invalid uploads; nothing was changed:\n- {details}")
        return uploads

    def _reconciled_manifest(self, records: list[ImageRecord]) -> dict[str, str]:
        manifest = reconcile_manifest(self.paths.images_dir, load_manifest(self.paths.image_manifest))
        missing = sorted({record.filename for record in records} - set(manifest))
        if missing:
            preview = ", ".join(missing[:3])
            suffix = " …" if len(missing) > 3 else ""
            raise RuntimeError(
                "The image manifest is incomplete because referenced images are not checked out: "
                f"{preview}{suffix}. Run 'python -m gallery manifest' from a full checkout first."
            )
        return manifest


def _write_text_atomically(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8").replace("\r\n", "\n") == content:
        return
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as temporary:
        temporary.write(content)
        temporary_path = Path(temporary.name)
    os.replace(temporary_path, path)


def _write_bytes_atomically(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as temporary:
        temporary.write(content)
        temporary_path = Path(temporary.name)
    os.replace(temporary_path, path)
