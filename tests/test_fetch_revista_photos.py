"""Testes do download de fotos do Commons (sem rede: a API é simulada)."""
import base64
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import fetch_revista_photos as fp  # noqa: E402

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    Image = None


def fake_api(license_name="CC BY-SA 4.0", artist='<a href="x">Ana <b>Souza</b></a>', mime="image/jpeg"):
    return json.dumps({"query": {"pages": {"1": {"imageinfo": [{
        "url": "https://upload.wikimedia.org/x.jpg", "thumburl": "https://upload.wikimedia.org/t.jpg",
        "descriptionurl": "https://commons.wikimedia.org/wiki/File:X.jpg", "mime": mime, "width": 4000, "height": 3000,
        "extmetadata": {"LicenseShortName": {"value": license_name}, "Artist": {"value": artist}}}]}}}}).encode()


class Lookup(unittest.TestCase):
    def setUp(self):
        self.orig = fp.http_get

    def tearDown(self):
        fp.http_get = self.orig

    def test_accepts_open_licenses_and_cleans_author(self):
        for lic in ("CC BY-SA 4.0", "CC BY 2.0", "CC0", "Public domain", "CC BY-SA 3.0"):
            with self.subTest(lic=lic):
                fp.http_get = lambda url, tries=5, lic=lic: fake_api(lic)
                info = fp.lookup("File:X.jpg")
                self.assertEqual(info["credito"], "Ana Souza")
                self.assertEqual(info["licenca"], lic)

    def test_rejects_non_open_licenses(self):
        for lic in ("CC BY-NC 4.0", "CC BY-ND 2.0", "CC BY-NC-SA 3.0", "All rights reserved", "", "GFDL only", "Fair use"):
            with self.subTest(lic=lic):
                fp.http_get = lambda url, tries=5, lic=lic: fake_api(lic)
                with self.assertRaises(fp.PhotoError):
                    fp.lookup("File:X.jpg")

    def test_missing_file_and_non_image_fail(self):
        fp.http_get = lambda url, tries=5: json.dumps({"query": {"pages": {"-1": {"missing": ""}}}}).encode()
        with self.assertRaises(fp.PhotoError):
            fp.lookup("File:Nao existe.jpg")
        fp.http_get = lambda url, tries=5: fake_api(mime="application/pdf")
        with self.assertRaises(fp.PhotoError):
            fp.lookup("File:X.pdf")


@unittest.skipIf(Image is None, "Pillow não instalado")
class Process(unittest.TestCase):
    def test_downloads_fills_metadata_and_is_idempotent(self):
        buf = io.BytesIO()
        Image.new("RGB", (2000, 1200), (10, 80, 120)).save(buf, "JPEG")
        orig, calls = fp.http_get, []

        def fake(url, tries=5):
            calls.append(url)
            return fake_api() if "api.php" in url else buf.getvalue()

        fp.http_get = fake
        fp.time.sleep = lambda s: None
        try:
            with tempfile.TemporaryDirectory() as tmp:
                ep = Path(tmp)
                (ep / "revista.json").write_text(json.dumps({"imagens": {"foto": {"commons": "File:X.jpg", "alt": "a", "legenda": "l"}}}), encoding="utf-8")
                self.assertEqual(fp.process(ep, log=lambda *_: None), 1)
                rev = json.loads((ep / "revista.json").read_text(encoding="utf-8"))["imagens"]["foto"]
                self.assertEqual((rev["file"], rev["credito"], rev["licenca"]), ("foto.jpg", "Ana Souza", "CC BY-SA 4.0"))
                self.assertTrue(rev["url"].startswith("https://commons.wikimedia.org/wiki/"))
                web = Image.open(ep / "revista" / "img" / "foto.jpg")
                mail = Image.open(ep / "revista" / "img" / "foto-e.jpg")
                self.assertEqual((web.width, mail.width), (1500, 900))
                n_calls = len(calls)
                self.assertEqual(fp.process(ep, log=lambda *_: None), 0)
                self.assertEqual(len(calls), n_calls, "segunda execução não baixa de novo")
        finally:
            fp.http_get = orig


if __name__ == "__main__":
    unittest.main()
