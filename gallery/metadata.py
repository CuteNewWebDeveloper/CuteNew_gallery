"""Metadata parsing, persistence, hashing, and derived-data helpers."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import tempfile
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Iterable

from .models import ImageRecord, UploadMetadata


CSV_FIELDS = ("image_id", "image_name", "time", "location", "photographer_name", "note")
IMAGE_SUFFIXES = {".jpg", ".jpeg"}
_FULL_DATE = re.compile(r"^(?P<year>\d{4})[.-](?P<month>\d{1,2})[.-](?P<day>\d{1,2})$")


class UploadValidationError(ValueError):
    """Raised before mutation when an item in input_material is malformed."""


def parse_upload_filename(path: Path) -> UploadMetadata:
    """Parse the documented '<date> <location> <photographer>.jpg' naming convention."""

    if path.suffix.lower() not in IMAGE_SUFFIXES:
        raise UploadValidationError(f"{path.name}: only .jpg or .jpeg uploads are supported")

    parts = path.stem.split(maxsplit=2)
    if len(parts) != 3 or not all(parts):
        raise UploadValidationError(
            f"{path.name}: expected '<date> <location> <photographer>.jpg'"
        )

    photographer = parts[2].lstrip("-").strip()
    if not photographer:
        raise UploadValidationError(f"{path.name}: photographer cannot be empty")

    return UploadMetadata(taken_at=parts[0], location=parts[1], photographer=photographer)


def parse_full_date(value: str) -> date | None:
    """Parse the full dates supported by the calendar; partial dates remain display-only."""

    match = _FULL_DATE.fullmatch(value.strip())
    if not match:
        return None
    try:
        return date(
            int(match.group("year")),
            int(match.group("month")),
            int(match.group("day")),
        )
    except ValueError:
        return None


def load_records(path: Path) -> list[ImageRecord]:
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            return []
        missing = set(CSV_FIELDS) - set(reader.fieldnames)
        if missing:
            fields = ", ".join(sorted(missing))
            raise ValueError(f"{path} is missing required columns: {fields}")
        return [
            ImageRecord.from_csv_row(row, line_number)
            for line_number, row in enumerate(reader, start=2)
            if any((value or "").strip() for value in row.values())
        ]


def save_records(path: Path, records: Iterable[ImageRecord]) -> None:
    rows = list(records)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False
    ) as temporary:
        writer = csv.DictWriter(temporary, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for record in rows:
            writer.writerow(
                {
                    "image_id": record.image_id,
                    "image_name": record.filename,
                    "time": record.taken_at,
                    "location": record.location,
                    "photographer_name": record.photographer,
                    "note": record.note,
                }
            )
        temporary_path = Path(temporary.name)
    os.replace(temporary_path, path)


def next_image_id(records: Iterable[ImageRecord]) -> int:
    return max((record.image_id for record in records), default=0) + 1


def hash_file(path: Path, algorithm: str = "md5") -> str:
    hasher = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def load_manifest(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    files = payload.get("files", {}) if isinstance(payload, dict) else {}
    if not isinstance(files, dict):
        raise ValueError(f"{path} has an invalid manifest format")
    return {str(filename): str(checksum) for filename, checksum in files.items()}


def save_manifest(path: Path, checksums: dict[str, str]) -> None:
    payload = {"version": 1, "algorithm": "md5", "files": dict(sorted(checksums.items()))}
    _write_text_atomically(path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def reconcile_manifest(images_dir: Path, current: dict[str, str]) -> dict[str, str]:
    """Add hashes for gallery images whose checksum has not been recorded yet."""

    checksums = dict(current)
    existing_files = {
        path.name
        for path in images_dir.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
    }
    for filename in existing_files:
        if filename not in checksums:
            checksums[filename] = hash_file(images_dir / filename)
    return {filename: checksum for filename, checksum in checksums.items() if filename in existing_files}


def date_counts(records: Iterable[ImageRecord]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for record in records:
        parsed = parse_full_date(record.taken_at)
        if parsed is not None:
            counts[parsed.isoformat()] += 1
    return counts


def read_airport_descriptions(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or "code" not in reader.fieldnames:
            return {}
        return {
            (row.get("code") or "").strip().upper(): (row.get("description") or "").strip()
            for row in reader
            if (row.get("code") or "").strip()
        }


def _write_text_atomically(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as temporary:
        temporary.write(content)
        temporary_path = Path(temporary.name)
    os.replace(temporary_path, path)
