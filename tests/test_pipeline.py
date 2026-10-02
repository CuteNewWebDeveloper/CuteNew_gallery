from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from gallery.config import SitePaths
from gallery.metadata import UploadValidationError, load_records
from gallery.models import ImageRecord
from gallery.pipeline import GalleryPipeline
from gallery.render import render_airport_csv


class GalleryPipelineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.paths = SitePaths.from_root(self.root)
        self.paths.ensure_directories()
        Image.new("RGBA", (100, 20), color=(0, 0, 0, 255)).save(self.paths.brand_watermark)
        self.pipeline = GalleryPipeline(self.paths)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def write_upload(self, filename: str) -> Path:
        path = self.paths.input_dir / filename
        Image.new("RGB", (800, 600), color=(20, 90, 160)).save(path, quality=100)
        return path

    def test_ingest_creates_assets_metadata_and_browsable_data(self) -> None:
        sentinel = self.paths.input_dir / "DonotDeleteME"
        sentinel.mkdir()
        (sentinel / "DONT.txt").write_text("keep this directory", encoding="utf-8")
        upload = self.write_upload("2025.1.2 PEK Alice Example.jpg")

        result = self.pipeline.ingest()

        self.assertEqual(len(result.added), 1)
        self.assertFalse(upload.exists())
        self.assertTrue((sentinel / "DONT.txt").exists())
        records = load_records(self.paths.image_log)
        self.assertEqual(len(records), 1)
        record = records[0]
        self.assertEqual((record.taken_at, record.location, record.photographer), ("2025.1.2", "PEK", "Alice Example"))
        self.assertTrue((self.paths.images_dir / record.filename).exists())
        self.assertTrue((self.paths.previews_dir / record.filename).exists())
        self.assertTrue((self.paths.pages_dir / f"Page{record.stem}.html").exists())
        self.assertTrue(self.paths.filter_page.exists())
        self.assertTrue(self.paths.site_css.exists())
        self.assertTrue(self.paths.site_script.exists())
        index_html = self.paths.index_page.read_text(encoding="utf-8")
        self.assertIn("assets/site.css", index_html)
        self.assertIn('class="gallery-hero"', index_html)
        self.assertIn('class="gallery-item gallery-item--wide"', index_html)
        self.assertIn('href="#main-content"', index_html)
        detail_html = (self.paths.pages_dir / f"Page{record.stem}.html").read_text(encoding="utf-8")
        self.assertIn('class="detail-stage"', detail_html)
        self.assertIn('class="detail-meta"', detail_html)
        self.assertIn("#122445", self.paths.site_css.read_text(encoding="utf-8"))
        self.assertIn("brand-action", self.paths.site_script.read_text(encoding="utf-8"))
        self.assertIn("2025-01-02,1", self.paths.date_data.read_text(encoding="utf-8"))
        self.assertIn("PEK", self.paths.airport_data.read_text(encoding="utf-8"))

        data = json.loads(self.paths.gallery_data.read_text(encoding="utf-8"))
        self.assertEqual(data[0]["date"], "2025-01-02")
        with Image.open(self.paths.previews_dir / record.filename) as preview:
            self.assertAlmostEqual(preview.width / preview.height, 16 / 10, delta=0.01)

    def test_ingest_adds_brand_watermark_to_full_image_but_not_preview(self) -> None:
        self.write_upload("2025.1.2 PEK Alice.jpg")

        self.pipeline.ingest()

        record = load_records(self.paths.image_log)[0]
        with Image.open(self.paths.images_dir / record.filename) as full_image:
            self.assertEqual(full_image.size, (800, 617))
            self.assertLess(sum(full_image.convert("RGB").getpixel((780, 580))), 80)
        with Image.open(self.paths.previews_dir / record.filename) as preview:
            self.assertGreater(sum(preview.convert("RGB").getpixel((370, 220))), 100)

    def test_reupload_of_identical_image_is_skipped_as_a_duplicate(self) -> None:
        upload = self.write_upload("2025.1.2 PEK Alice.jpg")
        original_payload = upload.read_bytes()
        self.pipeline.ingest()

        upload.write_bytes(original_payload)
        result = self.pipeline.ingest()

        self.assertEqual(result.added, ())
        self.assertEqual(result.duplicates, (upload.name,))
        self.assertFalse(upload.exists())
        self.assertEqual(len(load_records(self.paths.image_log)), 1)

    def test_invalid_upload_is_not_deleted(self) -> None:
        upload = self.write_upload("missing-required-parts.jpg")

        with self.assertRaises(UploadValidationError):
            self.pipeline.ingest()

        self.assertTrue(upload.exists())
        self.assertFalse(self.paths.image_log.exists())

    def test_rebuild_handles_an_empty_gallery(self) -> None:
        self.pipeline.rebuild_site()

        self.assertTrue(self.paths.index_page.exists())
        self.assertIn("暂无图片", self.paths.index_page.read_text(encoding="utf-8"))
        self.assertTrue(self.paths.filter_page.exists())
        self.assertTrue(self.paths.site_css.exists())
        self.assertTrue(self.paths.site_script.exists())

    def test_airport_catalog_excludes_non_airport_freeform_locations(self) -> None:
        records = [
            ImageRecord(1, "one.jpg", "2025.1.2", "PEK", "Alice"),
            ImageRecord(2, "two.jpg", "2025.1.2", "inflight", "Alice"),
            ImageRecord(3, "three.jpg", "2025.1.2", "北京朝阳", "Alice"),
        ]

        catalog = render_airport_csv({}, records)

        self.assertIn("PEK,", catalog)
        self.assertNotIn("INFLIGHT", catalog)
        self.assertNotIn("北京朝阳", catalog)


if __name__ == "__main__":
    unittest.main()
