"""Testes do gerador de newsletter. Rodar na raiz do repositório: python3 -m unittest discover -s tests -v"""
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import build_newsletter as bn  # noqa: E402

EPISODES = ROOT / "episodes"
MINIMAL = """# Rascunho — newsletter da semana de 01 a 08/01/2027

## Assunto

- Um assunto de teste
- Outro assunto de teste
- Mais um assunto de teste

**Pré-visualização:** Uma prévia curta.

## Abertura

Abertura de teste.

## No podcast

Frase do episódio. Ouça em https://podcast.khartos.com/ep/ep-2027-01-08/

## Datas e prazos

- **Item:** fato com [Fonte, 01/01/2027](https://example.com/a). O que fazer: conferir.

## Checklist da semana

- Primeiro item.

## No Khartos

No Khartos, a viagem vira uma expedição. Comece em https://khartos.com/?utm_source=newsletter&utm_medium=email&utm_campaign=rota-da-semana

## Rodapé

Aviso de rodapé.
[Fase 2: descadastro em um clique e identificação do remetente]
"""


def episode_dirs():
    return sorted(d for d in EPISODES.iterdir() if d.is_dir() and (d / "newsletter.md").exists())


class RealEditions(unittest.TestCase):
    def test_every_edition_parses_and_renders(self):
        dirs = episode_dirs()
        self.assertTrue(dirs, "nenhuma edição com newsletter.md")
        for d in dirs:
            with self.subTest(episode=d.name):
                ed = bn.parse((d / "newsletter.md").read_text(encoding="utf-8"))
                n = bn.edition_number(d)
                email = bn.render_html(ed, mode="email", number=n, ep_date=d.name, subject_idx=0, draft=True)
                web = bn.render_html(ed, mode="web", number=n, ep_date=d.name, subject_idx=0, draft=True)
                text = bn.render_text(ed, number=n, ep_date=d.name, subject_idx=0)
                self.assertIn(bn.UNSUB, email)
                self.assertIn(bn.SENDER, email)
                self.assertNotIn("{{", web)
                self.assertNotIn("Fase 2", email + web + text)
                self.assertNotIn("**", text)
                self.assertNotIn("](", text)
                self.assertLess(len(email.encode("utf-8")), 80 * 1024)


class Rendering(unittest.TestCase):
    def setUp(self):
        self.ed = bn.parse(MINIMAL)

    def test_draft_banner_only_on_unapproved_web(self):
        kw = dict(number=1, ep_date="2027-01-08", subject_idx=0)
        self.assertIn("aguardando aprovação", bn.render_html(self.ed, mode="web", draft=True, **kw))
        self.assertNotIn("aguardando aprovação", bn.render_html(self.ed, mode="web", draft=False, **kw))
        self.assertNotIn("aguardando aprovação", bn.render_html(self.ed, mode="email", draft=True, **kw))

    def test_utm_follows_mode_and_edition(self):
        kw = dict(number=3, ep_date="2027-01-08", subject_idx=0, draft=False)
        email = bn.render_html(self.ed, mode="email", **kw)
        web = bn.render_html(self.ed, mode="web", **kw)
        for needle in ("utm_medium=email", "utm_content=cta-episodio", "utm_content=cta-khartos", "utm_term=edicao-3"):
            self.assertIn(needle.replace("&", "&amp;"), email)
        self.assertIn("utm_medium=web", web)
        self.assertNotIn("utm_medium=email", web)

    def test_text_after_label_is_capitalized_in_html_only(self):
        self.assertEqual(bn.cap("vendas até dezembro"), "Vendas até dezembro")
        ls = bn.label_split("**Decisão** (opinião editorial): com as datas firmes")
        self.assertEqual(ls, ("Decisão (opinião editorial)", "com as datas firmes"))
        self.assertEqual(bn.label_split("**Erro comum:** deixar para depois"), ("Erro comum", "deixar para depois"))

    def test_template_makes_no_free_promise(self):
        html = bn.render_html(self.ed, mode="email", number=1, ep_date="2027-01-08", subject_idx=0, draft=False)
        self.assertNotIn("grátis", html.lower())


class Validation(unittest.TestCase):
    def test_unknown_section_fails(self):
        with self.assertRaises(bn.NewsletterError):
            bn.parse(MINIMAL + "\n## Seção inventada\n\ntexto\n")

    def test_unrecognized_draft_marker_fails(self):
        with self.assertRaises(bn.NewsletterError):
            bn.parse(MINIMAL.replace("Abertura de teste.", "[A preencher depois]"))

    def test_missing_required_section_fails(self):
        with self.assertRaises(bn.NewsletterError):
            bn.parse(MINIMAL.replace("## Checklist da semana\n\n- Primeiro item.\n\n", ""))

    def test_omitted_destination_marker_is_accepted(self):
        ed = bn.parse(MINIMAL.replace("## No podcast", "[Bloco de destino omitido: pesquisa insuficiente]\n\n## No podcast"))
        self.assertTrue(ed["dest_omitted"])
        self.assertIsNone(ed["dest_kind"])

    def test_wrong_number_of_subjects_fails(self):
        with self.assertRaises(bn.NewsletterError):
            bn.parse(MINIMAL.replace("- Mais um assunto de teste\n", ""))


class Publishing(unittest.TestCase):
    def test_site_gets_only_approved_editions(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            for name in ("2027-01-01", "2027-01-08"):
                d = tmp / "episodes" / name
                d.mkdir(parents=True)
                (d / "roteiro.txt").write_text("MARCO POLO: oi\n", encoding="utf-8")
                (d / "newsletter.md").write_text(MINIMAL, encoding="utf-8")
            (tmp / "episodes" / "2027-01-08" / bn.APROVADA).write_text("", encoding="utf-8")
            site, out = tmp / "site", tmp / "out"
            for d in sorted((tmp / "episodes").iterdir()):
                bn.build(d, out, site, 0)
            self.assertFalse((site / "newsletter" / "2027-01-01").exists())
            self.assertTrue((site / "newsletter" / "2027-01-08" / "index.html").exists())
            for name in ("2027-01-01", "2027-01-08"):
                for f in ("email.html", "email.txt", "email-assunto.txt", "web.html"):
                    self.assertTrue((out / name / f).exists(), f"{name}/{f}")
            self.assertIn("Edição 2", (out / "2027-01-08" / "web.html").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
