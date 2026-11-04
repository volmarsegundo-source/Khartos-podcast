"""Testes do gerador da revista. Rodar na raiz do repositório: python3 -m unittest discover -s tests -v"""
import base64
import copy
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import build_revista as br  # noqa: E402

TINY_JPG = base64.b64decode("/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAA0JCgsKCA0LCgsODg0PEyAVExISEyccHhcgLikxMC4pLSwzOko+MzZGNywtQFdBRkxOUlNSMj5aYVpQYEpRUk//2wBDAQ4ODhMREyYVFSZPNS01T09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT0//wAARCAAKABADASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwDnqKKK7jzT/9k=")


def make_rev(n_pages=16):
    img = {"file": "a.jpg", "alt": "Descrição", "legenda": "Legenda", "credito": "Autora Teste", "licenca": "CC BY 4.0",
           "url": "https://commons.wikimedia.org/wiki/File:A.jpg"}
    pages = [{"id": "capa", "layout": "capa", "chamadas": [{"rotulo": "Destino", "x": "Chamada"}]},
             {"id": "sumario", "layout": "sumario", "secao": "Nesta edição", "titulo": "Sumário"}]
    for i in range(n_pages - 4):
        pages.append({"id": f"p{i}", "layout": "texto", "secao": "Seção", "titulo": f"Título {i}", "sumario": True, "resumo": "Resumo.",
                      "blocos": [{"t": "p", "x": "Texto com [fonte](https://example.com/%d)." % i}, {"t": "foto", "id": "a"}]})
    pages.append({"id": "podcast", "layout": "navy", "secao": "No podcast", "titulo": "Episódio", "marco": True,
                  "blocos": [{"t": "cta", "rotulo": "Ouvir", "url": "https://podcast.khartos.com/ep/ep-2027-01-08/"}]})
    pages.append({"id": "creditos", "layout": "creditos", "secao": "Créditos", "titulo": "Fotos e fontes"})
    return {"edicao": {"numero": 3, "data": "2027-01-08", "periodo": "01 a 08/01/2027", "titulo": "Título da capa",
                       "subtitulo": "Subtítulo.", "capa": "a"},
            "email": {"assuntos": ["Assunto um", "Assunto dois", "Assunto três"], "preview": "Prévia curta.", "abertura": "Abertura.",
                      "podcast": "Frase do podcast.", "datas_de": "p0", "checklist_de": "p1",
                      "destaques": [{"foto": "a", "secao": "Destino", "titulo": "Título", "x": "Resumo.", "ancora": "p0"}]},
            "imagens": {"a": img}, "paginas": pages, "rodape": ["Aviso de rodapé."]}


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.ep = self.root / "episodes" / "2027-01-08"
        (self.ep / "revista" / "img").mkdir(parents=True)
        (self.ep / "revista" / "img" / "a.jpg").write_bytes(TINY_JPG)
        (self.ep / "revista" / "img" / "a-e.jpg").write_bytes(TINY_JPG)
        (self.ep / "roteiro.txt").write_text("MARCO POLO: oi\n", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, rev):
        (self.ep / "revista.json").write_text(json.dumps(rev, ensure_ascii=False), encoding="utf-8")

    def build(self, rev=None, site=False):
        self.write(rev or make_rev())
        out = self.root / "out"
        return br.build(self.ep, out, (self.root / "site") if site else None, "https://podcast.khartos.com", 0, False)


class Outputs(Base):
    def test_builds_all_outputs_in_public_layout(self):
        self.build()
        d = self.root / "out" / "newsletter" / "2027-01-08"
        for f in ("index.html", "email.html", "email.txt", "email-assunto.txt", "img/a.jpg", "img/a-e.jpg"):
            self.assertTrue((d / f).exists(), f)

    def test_email_has_platform_placeholders_and_absolute_image_urls(self):
        self.build()
        email = (self.root / "out" / "newsletter" / "2027-01-08" / "email.html").read_text(encoding="utf-8")
        self.assertIn(br.bn.UNSUB, email)
        self.assertIn(br.bn.SENDER, email)
        self.assertIn("https://podcast.khartos.com/newsletter/2027-01-08/img/a-e.jpg", email)
        self.assertIn("utm_term=edicao-3", email)

    def test_web_has_no_placeholders_and_internal_anchors_resolve(self):
        self.build()
        web = (self.root / "out" / "newsletter" / "2027-01-08" / "index.html").read_text(encoding="utf-8")
        self.assertNotIn("{{", web)
        ids = set(re.findall(r'id="([^"]+)"', web))
        for a in re.findall(r'href="#([^"]+)"', web):
            self.assertIn(a, ids)

    def test_credits_page_lists_photo_credit_and_sources(self):
        self.build()
        web = (self.root / "out" / "newsletter" / "2027-01-08" / "index.html").read_text(encoding="utf-8")
        self.assertIn("Autora Teste", web)
        self.assertIn("https://example.com/0", web)
        self.assertIn("Wikimedia Commons", web)

    def test_print_css_makes_each_page_an_a4_sheet(self):
        self.build()
        web = (self.root / "out" / "newsletter" / "2027-01-08" / "index.html").read_text(encoding="utf-8")
        self.assertIn("@page{size:210mm 297mm", web)


class Validation(Base):
    def test_fewer_than_15_pages_fails(self):
        with self.assertRaises(br.RevistaError):
            self.build(make_rev(14))

    def test_unknown_block_fails(self):
        rev = make_rev()
        rev["paginas"][3]["blocos"].append({"t": "inventado"})
        with self.assertRaises(br.RevistaError):
            self.build(rev)

    def test_unregistered_image_fails(self):
        rev = make_rev()
        rev["paginas"][3]["blocos"].append({"t": "foto", "id": "zzz"})
        with self.assertRaises(br.RevistaError):
            self.build(rev)

    def test_missing_image_file_fails(self):
        (self.ep / "revista" / "img" / "a.jpg").unlink()
        with self.assertRaises(br.RevistaError):
            self.build()

    def test_image_without_license_fails(self):
        rev = make_rev()
        rev["imagens"]["a"]["licenca"] = ""
        with self.assertRaises(br.RevistaError):
            self.build(rev)

    def test_vetoed_expression_fails(self):
        for word in ("grátis", "o melhor destino", "aventura imperdível", "roteiro dos sonhos", "transforma"):
            with self.subTest(word=word):
                rev = copy.deepcopy(make_rev())
                rev["paginas"][3]["blocos"].append({"t": "p", "x": f"Algo {word} aqui."})
                with self.assertRaises(br.RevistaError):
                    self.build(rev)

    def test_email_anchor_must_be_a_page(self):
        rev = make_rev()
        rev["email"]["destaques"][0]["ancora"] = "nao-existe"
        with self.assertRaises(br.RevistaError):
            self.build(rev)

    def test_date_must_match_folder(self):
        rev = make_rev()
        rev["edicao"]["data"] = "2027-02-02"
        with self.assertRaises(br.RevistaError):
            self.build(rev)


class Publishing(Base):
    def test_draft_goes_to_preview_and_approved_goes_to_the_public_path(self):
        self.build(site=True)
        pub = self.root / "site" / "newsletter" / "2027-01-08"
        prev = self.root / "site" / "newsletter" / "preview" / "2027-01-08"
        self.assertFalse(pub.exists(), "rascunho não vai ao caminho público")
        html = (prev / "index.html").read_text(encoding="utf-8")
        self.assertIn("aguardando aprovação", html)
        self.assertIn('name="robots" content="noindex"', html)
        self.assertTrue((prev / "img" / "a.jpg").exists())
        (self.ep / br.APROVADA).write_text("", encoding="utf-8")
        self.build(site=True)
        self.assertTrue((pub / "index.html").exists())
        self.assertNotIn("aguardando aprovação", (pub / "index.html").read_text(encoding="utf-8"))
        self.assertFalse((pub / "email.html").exists(), "o e-mail não vai para o site")


class Extras(Base):
    def test_credits_can_be_split_into_photos_and_sources_pages(self):
        rev = make_rev()
        rev["paginas"][-1] = {"id": "creditos", "layout": "creditos", "parte": "fotos", "secao": "Créditos", "titulo": "Fotos"}
        rev["paginas"].append({"id": "fontes", "layout": "creditos", "parte": "fontes", "secao": "Fontes", "titulo": "Fontes"})
        self.build(rev)
        web = (self.root / "out" / "newsletter" / "2027-01-08" / "index.html").read_text(encoding="utf-8")
        photos = re.search(r'id="creditos".*?</section>', web, re.S).group(0)
        sources = re.search(r'id="fontes".*?</section>', web, re.S).group(0)
        self.assertIn("Autora Teste", photos)
        self.assertNotIn("example.com", photos)
        self.assertIn("example.com/0", sources)
        self.assertNotIn("Autora Teste", sources)

    def test_pdf_fit_script_only_runs_with_pdf_flag_and_sources_show_host(self):
        self.build()
        web = (self.root / "out" / "newsletter" / "2027-01-08" / "index.html").read_text(encoding="utf-8")
        self.assertIn("location.search.indexOf('pdf')", web)
        self.assertIn("html.sim", web)
        self.assertIn("example.com/0", web)

    def test_cartographic_terms_per_page_are_linted(self):
        rev = make_rev()
        rev["paginas"][3]["blocos"].append({"t": "p", "x": "O mapa, a rota e a bússola da expedição."})
        warns = br.lint(rev, "")
        self.assertTrue(any("termos cartográficos" in w for w in warns))
        ok = make_rev()
        self.assertFalse(any("termos cartográficos" in w for w in br.lint(ok, "")))
        ok["paginas"][3]["blocos"].append({"t": "p", "x": "Assista à Rota da Semana."})
        self.assertFalse(any("termos cartográficos" in w for w in br.lint(ok, "")), "o nome do programa não conta")


class Domain(Base):
    def test_default_root_is_podcast_domain_and_env_overrides_it(self):
        import os
        os.environ.pop("NEWSLETTER_ROOT", None)
        self.assertEqual(br.root_url("https://podcast.khartos.com", "2027-01-08"), "https://podcast.khartos.com/newsletter/2027-01-08")
        os.environ["NEWSLETTER_ROOT"] = "https://newsletter.khartos.com/"
        try:
            self.assertEqual(br.root_url("https://podcast.khartos.com", "2027-01-08"), "https://newsletter.khartos.com/2027-01-08")
            self.build()
            d = self.root / "out" / "newsletter" / "2027-01-08"
            email = (d / "email.html").read_text(encoding="utf-8")
            web = (d / "index.html").read_text(encoding="utf-8")
            self.assertIn("https://newsletter.khartos.com/2027-01-08/img/a-e.jpg", email)
            self.assertIn("https://newsletter.khartos.com/2027-01-08/revista.pdf", email)
            self.assertIn('rel="canonical" href="https://newsletter.khartos.com/2027-01-08/"', web)
            self.assertIn("https://podcast.khartos.com/ep/ep-2027-01-08/", email, "o episódio continua no domínio do podcast")
        finally:
            os.environ.pop("NEWSLETTER_ROOT", None)

    def test_index_lists_only_approved_editions_newest_first(self):
        for name, ok in (("2027-01-01", True), ("2027-01-08", True), ("2027-01-15", False)):
            d = self.root / "episodes" / name
            (d / "revista" / "img").mkdir(parents=True, exist_ok=True)
            (d / "revista.json").write_text(json.dumps(make_rev()), encoding="utf-8")
            if ok:
                (d / br.APROVADA).write_text("", encoding="utf-8")
        site = self.root / "site"
        n = br.write_index(site, sorted((self.root / "episodes").iterdir()))
        self.assertEqual(n, 2)
        html = (site / "newsletter" / "index.html").read_text(encoding="utf-8")
        self.assertIn('href="2027-01-08/"', html)
        self.assertIn('href="2027-01-01/revista.pdf"', html)
        self.assertNotIn("2027-01-15", html)
        self.assertLess(html.index("2027-01-08/"), html.index("2027-01-01/"))
        self.assertEqual(br.write_index(self.root / "vazio", [self.root / "episodes" / "2027-01-15"]), 0)


if __name__ == "__main__":
    unittest.main()
