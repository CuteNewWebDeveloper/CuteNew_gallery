"""Small, explicit data models used by the build pipeline."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class UploadMetadata:
    taken_at: str
    location: str
    photographer: str


@dataclass(frozen=True)
class ImageRecord:
    image_id: int
    filename: str
    taken_at: str
    location: str
    photographer: str
    note: str = ""

    @property
    def stem(self) -> str:
        return self.filename.rsplit(".", 1)[0]

    @classmethod
    def from_csv_row(cls, row: dict[str, str], line_number: int) -> "ImageRecord":
        try:
            image_id = int(row["image_id"])
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError(f"image_log.csv line {line_number} has an invalid image_id") from error

        filename = (row.get("image_name") or "").strip()
        if not filename:
            raise ValueError(f"image_log.csv line {line_number} has no image_name")

        return cls(
            image_id=image_id,
            filename=filename,
            taken_at=(row.get("time") or "").strip(),
            location=(row.get("location") or "").strip(),
            photographer=(row.get("photographer_name") or "").strip(),
            note=(row.get("note") or "").strip(),
        )
