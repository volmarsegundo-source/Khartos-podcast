"""Taxonomia de UTM dos links para o Khartos gerados por scripts/build_feed.py.

utm_source=podcast; utm_medium=feed (descrição do programa e resumo/descrição dos episódios no
feed) ou site (cartão e rodapé da página); utm_campaign=rota-da-semana; utm_content=ep-AAAA-MM-DD
quando o link pertence a um episódio.

Rodar: python3 -m unittest discover -s tests -p "test_*.py"
"""
import importlib.util
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("build_feed", ROOT / "scripts" / "build_feed.py")
bf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bf)

TAG = "ep-2026-10-30"


def qs(url: str) -> dict:
    return {k: v[0] for k, v in parse_qs(urlparse(url.replace("&amp;", "&")).query).items()}


def khartos_links(text: str) -> list:
    return re.findall(r"https://khartos\.com[^\s\"'<>\]]*", text)


class KhartosUrl(unittest.TestCase):
    def test_feed_com_episodio(self):
        self.assertEqual(
            bf.khartos_url("feed", TAG),
            "https://khartos.com/?utm_source=podcast&utm_medium=feed&utm_campaign=rota-da-semana&utm_content=ep-2026-10-30",
        )

    def test_site_sem_episodio_nao_tem_content(self):
        self.assertEqual(
            bf.khartos_url("site"),
            "https://khartos.com/?utm_source=podcast&utm_medium=site&utm_campaign=rota-da-semana",
        )

    def test_descricao_do_programa_usa_feed_sem_content(self):
        links = khartos_links(bf.SHOW_DESC)
        self.assertEqual(links, [bf.khartos_url("feed")])

    def test_cartao_da_pagina_usa_site(self):
        self.assertIn(bf.khartos_url("site", TAG), bf.khartos_card(TAG))
        self.assertIn(bf.khartos_url("site"), bf.khartos_card())

    def test_resumo_do_episodio_usa_feed_com_content(self):
        self.assertIn(bf.khartos_url("feed", TAG), bf.khartos_notes_plain(TAG))
        self.assertIn(bf.khartos_url("feed", TAG), bf.khartos_notes_html(TAG))


class SiteGerado(unittest.TestCase):
    """Gera o site com um episódio de teste e confere TODOS os links para o Khartos."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        tmp = Path(cls.tmp.name)
        (tmp / "site" / "audio").mkdir(parents=True)
        (tmp / "site" / "audio" / f"{TAG}.mp3").write_bytes(b"mp3")
        (tmp / "releases.json").write_text(json.dumps([{
            "tagName": TAG, "name": "Rota da Semana — teste", "publishedAt": "2026-10-30T10:47:00Z",
            "body": "Intro.\n\n## Destinos da semana\n- **Gramado:** dica — [Fonte](https://example.com)\n",
        }]), encoding="utf-8")
        bf.duration = lambda mp3: 900  # sem ffprobe
        argv = sys.argv
        sys.argv = ["build_feed.py", str(tmp / "releases.json"), str(tmp / "site"), "https://podcast.khartos.com"]
        try:
            bf.main()
        finally:
            sys.argv = argv
        cls.site = tmp / "site"

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def arquivos(self):
        return [self.site / "feed.xml", self.site / "index.html", self.site / "ep" / TAG / "index.html"]

    def test_nenhum_link_para_o_khartos_sem_utm(self):
        for f in self.arquivos():
            for link in khartos_links(f.read_text(encoding="utf-8")):
                self.assertEqual(qs(link).get("utm_source"), "podcast", f"{f.name}: {link}")

    def test_taxonomia_em_todos_os_links(self):
        for f in self.arquivos():
            for link in khartos_links(f.read_text(encoding="utf-8")):
                q = qs(link)
                self.assertEqual(q.get("utm_campaign"), "rota-da-semana", f"{f.name}: {link}")
                self.assertIn(q.get("utm_medium"), ("feed", "site"), f"{f.name}: {link}")
                if "utm_content" in q:
                    self.assertEqual(q["utm_content"], TAG, f"{f.name}: {link}")

    def test_medium_por_superficie(self):
        feed = (self.site / "feed.xml").read_text(encoding="utf-8")
        self.assertTrue(all(qs(l)["utm_medium"] == "feed" for l in khartos_links(feed)))
        # Links clicáveis (href) das páginas: cartão e rodapé = site. A meta og:description da home
        # reaproveita a descrição do programa (SHOW_DESC), que é medium=feed, e não é um link clicável.
        for pagina in (self.site / "index.html", self.site / "ep" / TAG / "index.html"):
            hrefs = re.findall(r'href="(https://khartos\.com[^"]*)"', pagina.read_text(encoding="utf-8"))
            self.assertTrue(hrefs, pagina.name)
            self.assertTrue(all(qs(l)["utm_medium"] == "site" for l in hrefs), pagina.name)

    def test_links_de_episodio_tem_content(self):
        feed = (self.site / "feed.xml").read_text(encoding="utf-8")
        item = feed.split("<item>", 1)[1]
        self.assertTrue(khartos_links(item))
        self.assertTrue(all(qs(l).get("utm_content") == TAG for l in khartos_links(item)))
        pagina = (self.site / "ep" / TAG / "index.html").read_text(encoding="utf-8")
        self.assertTrue(all(qs(l).get("utm_content") == TAG for l in khartos_links(pagina)))

    def test_sem_taxonomia_antiga(self):
        for f in self.arquivos():
            t = f.read_text(encoding="utf-8")
            self.assertNotIn("utm_campaign=audio", t)
            self.assertNotIn("utm_campaign=feed", t)
            self.assertNotIn("utm_medium=rota-da-semana", t)


if __name__ == "__main__":
    unittest.main()
