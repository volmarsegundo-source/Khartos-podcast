"""Testes da ordem do site do podcast. Rodar na raiz do repositório: python3 -m unittest discover -s tests -v"""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import build_feed as bf  # noqa: E402


class Order(unittest.TestCase):
    def test_newest_first_and_first_edition_marker_last(self):
        with tempfile.TemporaryDirectory() as t:
            eps = Path(t)
            (eps / "2027-01-20").mkdir()
            (eps / "2027-01-20" / bf.PRIMEIRA).write_text("", encoding="utf-8")
            rels = [{"tagName": "ep-2027-01-01", "publishedAt": "2027-01-01T12:00:00Z"},
                    {"tagName": "ep-2027-01-20", "publishedAt": "2027-01-20T12:00:00Z"},
                    {"tagName": "ep-2027-01-08", "publishedAt": "2027-01-08T12:00:00Z"}]
            rels.sort(key=lambda r: bf.chrono_key(r, eps), reverse=True)
            self.assertEqual([r["tagName"] for r in rels], ["ep-2027-01-08", "ep-2027-01-01", "ep-2027-01-20"])

    def test_without_marker_orders_by_published_at(self):
        with tempfile.TemporaryDirectory() as t:
            rels = [{"tagName": "ep-2027-01-01", "publishedAt": "2027-01-01T12:00:00Z"},
                    {"tagName": "ep-2027-01-08", "publishedAt": "2027-01-08T12:00:00Z"}]
            rels.sort(key=lambda r: bf.chrono_key(r, Path(t)), reverse=True)
            self.assertEqual(rels[0]["tagName"], "ep-2027-01-08")


if __name__ == "__main__":
    unittest.main()
