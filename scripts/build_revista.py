#!/usr/bin/env python3
"""Gera a revista da Rota da Semana (web, PDF A4 e e-mail de capa) a partir de episodes/AAAA-MM-DD/revista.json.

Fonte única por edição:
  episodes/AAAA-MM-DD/revista.json       conteúdo, páginas, fotos (com crédito e licença) e e-mail de capa
  episodes/AAAA-MM-DD/revista/img/*.jpg  fotos já tratadas (scripts/prep_revista_images.py)

Saídas em OUT/newsletter/AAAA-MM-DD/ (espelha a URL pública; o diretório pode ser publicado como está):
  index.html          a revista na web (páginas em rolagem; vira A4 na impressão)
  revista.pdf         a mesma revista em páginas A4 (precisa de Chrome; --pdf)
  email.html          e-mail de capa e destaques, com fotos, que leva à revista
  email.txt           versão em texto simples do e-mail
  email-assunto.txt   3 opções de assunto e a pré-visualização
  img/                as fotos usadas

Uso:
  python3 scripts/build_revista.py [episodes] [--episodio AAAA-MM-DD] --out DIR [--site DIR] [--pdf]
          [--base URL] [--assunto N]

--site publica a revista em DIR/newsletter/AAAA-MM-DD/ (index.html, revista.pdf, img/) para edições com o
arquivo vazio episodes/AAAA-MM-DD/newsletter.aprovada e, para rascunhos, em DIR/newsletter/preview/AAAA-MM-DD/
(com faixa de rascunho; a página é noindex e não é linkada em lugar nenhum). --base muda a raiz pública usada nos links do e-mail
(padrão https://podcast.khartos.com; use file:///... para conferir localmente).
Nada aqui envia e-mail.
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import parse_qsl, quote, urlencode, urlparse, urlunparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_newsletter as bn  # noqa: E402  (reaproveita o miolo de e-mail e UTM)

PUBLIC_BASE = "https://podcast.khartos.com"
APROVADA = bn.APROVADA
MARCO_NAVY = "https://khartos.com/characters/marco-polo/marco-polo-welcoming-navy.webp"
KHARTOS_FIXED = ("No Khartos, a viagem vira uma expedição: você conta como gosta de viajar, recebe o guia do destino, "
                 "monta o roteiro dia a dia e se prepara com um checklist. O Marco Polo acompanha; a rota é sua.")
KHARTOS_URL = "https://khartos.com/?utm_source=newsletter&utm_medium=email&utm_campaign=rota-da-semana"
BLOCKS = {"p", "lead", "h3", "lista", "foto", "cartoes", "tabela", "aviso", "dias", "timeline", "checklist",
          "citacao", "colunas", "cta", "dois_blocos"}
LAYOUTS = {"capa", "sumario", "hero", "texto", "faixa", "navy", "creditos"}


class RevistaError(ValueError):
    pass


def root_url(base: str, date: str) -> str:
    """Endereço público de uma edição. Com NEWSLETTER_ROOT (ex.: https://newsletter.khartos.com), a edição fica em
    NEWSLETTER_ROOT/AAAA-MM-DD; sem ela, em BASE/newsletter/AAAA-MM-DD (podcast.khartos.com)."""
    custom = os.environ.get("NEWSLETTER_ROOT", "").strip().rstrip("/")
    return f"{custom}/{date}" if custom else f"{base}/newsletter/{date}"


# ---------------------------------------------------------------- inline

LINK = bn.LINK


def inline_web(text: str) -> str:
    out, pos = [], 0

    def fmt(chunk):
        chunk = html.escape(chunk, quote=False)
        chunk = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", chunk)
        return re.sub(r"(?<!\*)\*([^*\s][^*]*?)\*(?!\*)", r"<i>\1</i>", chunk)

    for m in LINK.finditer(text):
        out.append(fmt(text[pos:m.start()]))
        out.append(f'<a href="{html.escape(m.group(2), quote=True)}" target="_blank" rel="noopener">'
                   f'{html.escape(m.group(1), quote=False)}</a>')
        pos = m.end()
    out.append(fmt(text[pos:]))
    return "".join(out)


def plain(text: str) -> str:
    return bn.inline_text(text)


def esc(s: str) -> str:
    return html.escape(s, quote=True)


# ---------------------------------------------------------------- validação

def _walk_text(obj):
    """Gera todo texto da revista (para coletar links e checar)."""
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for k, v in obj.items():
            if k in ("t", "layout", "id", "foto", "bg", "tam", "tom", "utm", "file", "ancora"):
                continue
            yield from _walk_text(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _walk_text(v)


def validate(rev: dict, img_dir: Path) -> None:
    for k in ("edicao", "email", "imagens", "paginas"):
        if k not in rev:
            raise RevistaError(f"chave obrigatória ausente: {k!r}")
    ed = rev["edicao"]
    for k in ("numero", "data", "periodo", "titulo", "subtitulo", "capa"):
        if k not in ed:
            raise RevistaError(f"edicao.{k} ausente")
    em = rev["email"]
    if len(em.get("assuntos", [])) != 3 or not em.get("preview"):
        raise RevistaError("email deve ter 3 assuntos e preview")
    imgs = rev["imagens"]
    for iid, im in imgs.items():
        for k in ("file", "alt", "credito", "licenca", "url"):
            if not im.get(k):
                dica = " (rode scripts/fetch_revista_photos.py)" if im.get("commons") else ""
                raise RevistaError(f"imagem {iid}: campo {k!r} ausente{dica}")
        if not (img_dir / im["file"]).exists():
            raise RevistaError(f"imagem {iid}: arquivo {im['file']} não existe em {img_dir}")
    seen = set()

    def check_blocks(blocks, where):
        for b in blocks:
            t = b.get("t")
            if t not in BLOCKS:
                raise RevistaError(f"{where}: bloco desconhecido {t!r}")
            if t == "foto" and b.get("id") not in imgs:
                raise RevistaError(f"{where}: foto {b.get('id')!r} sem cadastro em imagens")
            if t == "colunas":
                check_blocks(b.get("a", []), where)
                check_blocks(b.get("b", []), where)
            if t == "dias":
                for d in b["itens"]:
                    if d.get("foto") and d["foto"] not in imgs:
                        raise RevistaError(f"{where}: foto {d['foto']!r} sem cadastro")

    for p in rev["paginas"]:
        if p.get("layout") not in LAYOUTS:
            raise RevistaError(f"página {p.get('id')!r}: layout desconhecido {p.get('layout')!r}")
        if not p.get("id") or p["id"] in seen:
            raise RevistaError(f"id de página ausente ou repetido: {p.get('id')!r}")
        seen.add(p["id"])
        if p.get("foto") and p["foto"] not in imgs:
            raise RevistaError(f"página {p['id']}: foto {p['foto']!r} sem cadastro")
        check_blocks(p.get("blocos", []), f"página {p['id']}")
    if ed["capa"] not in imgs:
        raise RevistaError("edicao.capa não está em imagens")
    n_pages = len(rev["paginas"])
    if n_pages < 15:
        raise RevistaError(f"a revista tem {n_pages} páginas; mínimo 15")
    text = " ".join(_walk_text(rev))
    if re.search(r"(?i)\bgr[aá]tis\b|\bo melhor\b|\bimperd[ií]vel\b|dos sonhos|\btransforma\b", text):
        raise RevistaError("texto com expressão vetada (grátis, o melhor, imperdível, dos sonhos, transforma)")
    for u in re.findall(r"\((https?://[^)\s]+)\)", text):
        if not u.startswith("https://") and not u.startswith("http://"):
            raise RevistaError(f"link inválido: {u}")
    for iid in rev["email"].get("destaques", []):
        pass
    for d in rev["email"].get("destaques", []):
        if d.get("foto") not in imgs:
            raise RevistaError(f"email.destaques: foto {d.get('foto')!r} sem cadastro")
        if d.get("ancora") not in seen:
            raise RevistaError(f"email.destaques: âncora {d.get('ancora')!r} não é página")


def collect_links(rev: dict) -> list:
    """[(texto, url, [ids de página])] sem repetir URL."""
    found: dict = {}
    for p in rev["paginas"]:
        for t in _walk_text({k: v for k, v in p.items() if k != "blocos"} | {"blocos": p.get("blocos", [])}):
            for m in LINK.finditer(t):
                url = m.group(2)
                ent = found.setdefault(url, [m.group(1), []])
                if p["id"] not in ent[1]:
                    ent[1].append(p["id"])
    return [(v[0], u, v[1]) for u, v in found.items()]


# ---------------------------------------------------------------- web

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400&family=IBM+Plex+Mono:wght@400;500;600'
         '&family=Instrument+Serif:ital@0;1&family=Plus+Jakarta+Sans:wght@700&display=swap" rel="stylesheet">')

WEB_CSS = """
:root{--navy:#040d1b;--navy2:#1a2332;--on-navy:#dae3f7;--on-navy-dim:#9fb0cc;--orange:#fe932c;--orange-d:#904d00;--teal:#1c9a8e;--teal-d:#005049;--teal-l:#6bd8cb;
--bg:#f9f9f9;--card:#ffffff;--soft:#f3f3f3;--soft2:#eeeeee;--ink:#1a1c1c;--ink2:#45474c;--mute:#75777d;--line:#e2e2e2;--line2:#c5c6cc;
--serif:'Instrument Serif',Georgia,'Times New Roman',serif;--sans:'DM Sans','Segoe UI',Roboto,Helvetica,Arial,sans-serif;--mono:'IBM Plex Mono','Courier New',monospace;
--r8:8px;--r12:12px;--r16:16px;--r24:24px}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);font:400 17px/1.65 var(--sans);-webkit-font-smoothing:antialiased}
a{color:var(--teal-d);text-decoration:underline;text-underline-offset:2px}
img{max-width:100%;display:block}
h1,h2,h3,h4{font-family:var(--serif);font-weight:400;margin:0;letter-spacing:-.01em}
.pg{position:relative;width:100%;overflow:hidden}
.in{max-width:1120px;margin:0 auto;padding:84px 32px 96px}
.rh{position:absolute;top:0;left:0;right:0;z-index:5;display:flex;justify-content:space-between;gap:12px;padding:20px 32px;font:500 11px/1 var(--mono);letter-spacing:.14em;text-transform:uppercase;color:var(--mute)}
.pf{position:absolute;bottom:18px;right:32px;z-index:5;font:500 11px/1 var(--mono);letter-spacing:.14em;color:var(--mute)}
.bg-navy,.hero,.capa,.faixa{background:var(--navy);color:var(--on-navy)}
.bg-navy .rh,.bg-navy .pf,.hero .rh,.hero .pf,.capa .rh,.capa .pf,.faixa .rh,.faixa .pf{color:rgba(218,227,247,.72)}
.bg-soft{background:var(--soft)}
.kick{margin:0 0 18px;font:600 12px/1.2 var(--mono);letter-spacing:.18em;text-transform:uppercase;color:var(--teal)}
.bg-navy .kick,.hero .kick,.capa .kick,.faixa .kick{color:var(--teal-l)}
h2.t{font-size:clamp(38px,5.2vw,68px);line-height:1.04;margin:0 0 24px;max-width:18ch}
.lead{font:400 clamp(19px,2vw,23px)/1.5 var(--sans);color:var(--ink2);max-width:58ch;margin:0 0 32px}
.bg-navy .lead,.hero .lead,.capa .lead,.faixa .lead{color:var(--on-navy)}
.body p{max-width:64ch;margin:0 0 18px}.body p.dc::first-letter{font:400 4.6em/.8 var(--serif);float:left;padding:.06em .12em 0 0;color:var(--teal-d)}
h3{font-size:clamp(24px,2.4vw,30px);line-height:1.15;margin:34px 0 10px}
.body ul{margin:0 0 20px;padding-left:1.15em;max-width:64ch}.body li{margin:8px 0}
.body ul.ord{list-style:none;padding:0;counter-reset:n}.body ul.ord li{counter-increment:n;padding-left:44px;position:relative}.body ul.ord li:before{content:counter(n);position:absolute;left:0;top:-2px;font:400 28px/1 var(--serif);color:var(--teal)}
/* fotos */
.fig{margin:28px 0}.fig img{width:100%;height:auto;border-radius:var(--r16);object-fit:cover}
.fig figcaption{display:flex;flex-direction:column;gap:2px;margin-top:10px;font:400 12px/1.5 var(--mono);color:var(--mute)}
.fig figcaption span{color:var(--ink2);font:500 13px/1.45 var(--sans)}.fig figcaption a{color:inherit}
.fig.wide img{aspect-ratio:21/9}.fig.meia img{aspect-ratio:4/3}.fig.full{margin-left:calc(50% - 50vw);margin-right:calc(50% - 50vw);width:100vw;max-width:none}.fig.full img{border-radius:0;aspect-ratio:21/9}.fig.full figcaption{padding:0 32px;max-width:1120px;margin:10px auto 0}
.bg-navy .fig figcaption span,.hero .fig figcaption span{color:var(--on-navy)}
/* grid */
.cols{display:grid;grid-template-columns:1fr;gap:36px 56px;align-items:start}
@media(min-width:900px){.cols{grid-template-columns:1fr 1fr}.cols.c58{grid-template-columns:5fr 3fr}.cols.c85{grid-template-columns:3fr 5fr}}
/* cartões de dados */
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:16px;margin:28px 0}
.card{background:var(--card);border:1px solid var(--line);border-radius:var(--r16);padding:22px 22px 20px}
.bg-soft .card{border-color:transparent}
.card .v{font:400 clamp(36px,4vw,50px)/1 var(--serif);color:var(--navy);margin:0 0 8px}
.card .l{font:600 11px/1.4 var(--mono);letter-spacing:.12em;text-transform:uppercase;color:var(--teal-d);margin:0 0 8px}
.card .n{font-size:14.5px;line-height:1.55;color:var(--ink2);margin:0}
.bg-navy .card{background:var(--navy2);border-color:rgba(218,227,247,.12)}.bg-navy .card .v{color:var(--on-navy)}.bg-navy .card .l{color:var(--teal-l)}.bg-navy .card .n{color:var(--on-navy-dim)}
/* tabela */
table.tb{width:100%;border-collapse:collapse;margin:24px 0;font-size:15.5px}
table.tb th{font:600 11px/1.3 var(--mono);letter-spacing:.12em;text-transform:uppercase;text-align:left;color:var(--teal-d);padding:0 14px 10px 0;border-bottom:2px solid var(--teal)}
table.tb td{padding:13px 14px 13px 0;border-bottom:1px solid var(--line);vertical-align:top}
.tbn{font-size:13.5px;color:var(--mute);margin:-8px 0 24px}
/* aviso */
.aviso{border-radius:var(--r12);background:var(--card);border:1px solid var(--line);border-left:4px solid var(--teal);padding:18px 22px;margin:24px 0;max-width:64ch}
.bg-soft .aviso{border-color:transparent;border-left:4px solid var(--teal)}
.aviso.alerta{border-left-color:var(--orange)}.aviso.dica{border-left-color:var(--teal-d)}
.aviso .r{font:600 11px/1.2 var(--mono);letter-spacing:.14em;text-transform:uppercase;color:var(--teal-d);margin:0 0 8px}.aviso.alerta .r{color:var(--orange-d)}
.aviso p{margin:0}
.bg-navy .aviso{background:var(--navy2);border-color:rgba(218,227,247,.12)}.bg-navy .aviso .r{color:var(--teal-l)}
/* dias */
.dias{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:20px;margin:28px 0}
.dia{background:var(--card);border-radius:var(--r16);overflow:hidden;border:1px solid var(--line)}
.dia img{width:100%;aspect-ratio:3/2;object-fit:cover}
.dia .db{padding:20px 22px 22px}.dia .n{font:400 54px/1 var(--serif);color:var(--orange);margin:0 0 4px}
.dia .r{font:600 11px/1.2 var(--mono);letter-spacing:.14em;text-transform:uppercase;color:var(--teal-d);margin:0 0 6px}
.dia h4{font-size:26px;line-height:1.1;margin:0 0 10px}.dia p{margin:0 0 10px;font-size:15.5px;line-height:1.6}
/* timeline */
.tl{position:relative;margin:30px 0;padding-left:32px;max-width:760px}.tl:before{content:"";position:absolute;left:7px;top:6px;bottom:6px;width:2px;background:var(--teal)}
.tl .it{position:relative;margin:0 0 28px}.tl .it:before{content:"";position:absolute;left:-32px;top:6px;width:16px;height:16px;border-radius:50%;background:var(--bg);border:3px solid var(--orange)}
.bg-soft .tl .it:before{background:var(--soft)}.bg-navy .tl .it:before{background:var(--navy)}
.tl .d{font:600 12px/1.2 var(--mono);letter-spacing:.14em;text-transform:uppercase;color:var(--teal-d);margin:0 0 6px}.bg-navy .tl .d{color:var(--teal-l)}
.tl h4{font-size:27px;line-height:1.12;margin:0 0 6px}.tl p{margin:0;max-width:60ch;font-size:16px}
/* checklist */
.ck{list-style:none;margin:24px 0;padding:0;display:grid;gap:12px;max-width:760px}
.ck li{display:flex;gap:14px;align-items:flex-start;background:var(--card);border:1px solid var(--line);border-radius:var(--r12);padding:14px 18px}
.ck li:before{content:"";flex:none;width:20px;height:20px;margin-top:3px;border:2px solid var(--line2);border-radius:5px}
/* citação */
.cit{margin:34px 0;padding:0 0 0 26px;border-left:4px solid var(--orange);max-width:44ch}.cit p{font:400 clamp(28px,3.2vw,40px)/1.15 var(--serif);margin:0 0 12px;color:var(--navy)}
.cit small{font:400 12px/1.5 var(--mono);color:var(--mute)}.bg-navy .cit p,.faixa .cit p{color:var(--on-navy)}
/* cta */
.btn{display:inline-block;background:var(--orange);color:var(--navy);font:700 16px/1 var(--sans);padding:16px 30px;border-radius:var(--r8);text-decoration:none;margin:8px 0}
.btn.sec{background:transparent;color:var(--teal-l);border:1px solid rgba(218,227,247,.3)}
/* capa */
.capa{min-height:100vh;display:flex;align-items:flex-end}
.capa .bgimg,.hero .bgimg,.faixa .bgimg{position:absolute;inset:0;z-index:0}.capa .bgimg img,.hero .bgimg img,.faixa .bgimg img{width:100%;height:100%;object-fit:cover}
.capa .ov,.hero .ov,.faixa .ov{position:absolute;inset:0;z-index:1;background:linear-gradient(180deg,rgba(4,13,27,.55) 0%,rgba(4,13,27,.15) 38%,rgba(4,13,27,.88) 100%)}
.capa .in,.hero .hin,.faixa .fin{position:relative;z-index:2}
.capa h1{font-size:clamp(54px,9vw,128px);line-height:.96;margin:0 0 22px;max-width:13ch}
.capa .sub{font:400 clamp(19px,2vw,25px)/1.45 var(--sans);max-width:46ch;margin:0 0 34px;color:var(--on-navy)}
.chamadas{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:18px 28px;border-top:1px solid rgba(218,227,247,.28);padding-top:22px}
.chamadas b{display:block;font:600 11px/1.2 var(--mono);letter-spacing:.16em;text-transform:uppercase;color:var(--teal-l);margin:0 0 6px}.chamadas span{font-size:15.5px;line-height:1.5;color:var(--on-navy)}
.brand{font:500 12px/1 var(--mono);letter-spacing:.2em;text-transform:uppercase;color:var(--on-navy);margin:0 0 28px;display:flex;gap:14px;align-items:center}.brand i{display:block;width:34px;height:2px;background:var(--orange)}
.cred-img{position:absolute;right:32px;top:64px;z-index:3;font:400 11px/1.4 var(--mono);color:rgba(218,227,247,.78);max-width:40ch;text-align:right}.cred-img a{color:inherit}
/* hero (abertura de seção) */
.hero{position:relative;overflow:hidden;min-height:88vh;display:flex;flex-direction:column;justify-content:flex-end}
.hero-wrap{position:relative;background:var(--bg)}
.hero .hin{max-width:1120px;margin:0 auto;padding:120px 32px 56px;width:100%}
.hero h2.t{font-size:clamp(46px,7.6vw,104px);line-height:.98;max-width:14ch;color:#fff}
.hero .lead{max-width:50ch}
.hero-body{background:var(--bg);color:var(--ink)}
/* faixa */
.faixa{min-height:78vh;display:flex;align-items:center}.faixa .fin{max-width:1120px;margin:0 auto;padding:96px 32px;width:100%}
.faixa .big{font:400 clamp(70px,13vw,190px)/.9 var(--serif);color:#fff;margin:0 0 14px}.faixa .sm{font:400 clamp(22px,2.6vw,32px)/1.25 var(--serif);max-width:26ch;color:var(--on-navy);margin:0}
.faixa .ov{background:linear-gradient(90deg,rgba(4,13,27,.88) 0%,rgba(4,13,27,.62) 45%,rgba(4,13,27,.35) 100%)}
.draftbar{position:sticky;top:0;z-index:50;background:#fffbeb;color:#663500;text-align:center;font:500 12px/1 var(--mono);letter-spacing:.06em;padding:9px 12px}
/* marca, navegação e compartilhamento */
.lg{width:28px;height:28px;flex:none}
.brand-lg{display:inline-flex;align-items:center;gap:10px;color:var(--navy);text-decoration:none;font:700 22px/1 'Plus Jakarta Sans',var(--sans);letter-spacing:-.02em}
.brand-lg.sm{font-size:15px;gap:8px}.brand-lg.sm .lg{width:20px;height:20px}.brand-lg.big{font-size:30px;gap:12px}.brand-lg.big .lg{width:40px;height:40px}
.capa .brand-lg,.faixa .brand-lg,.bg-navy .brand-lg,.hero .brand-lg{color:#f9f9ff}
.cover-logo{position:absolute;top:30px;left:32px;z-index:6}.pb{position:absolute;bottom:14px;left:32px;z-index:5}
.topbar{position:sticky;top:0;z-index:60;display:flex;justify-content:space-between;align-items:center;gap:12px;padding:10px 24px;background:rgba(249,249,249,.94);-webkit-backdrop-filter:blur(8px);backdrop-filter:blur(8px);border-bottom:1px solid var(--line)}
.tb-nav{display:flex;align-items:center;gap:6px;flex-wrap:wrap}
.tb-nav a,.tb-nav button{font:600 14px/1 var(--sans);color:var(--ink);text-decoration:none;padding:10px 13px;border-radius:999px;border:1px solid transparent;background:none;cursor:pointer}
.tb-nav a:hover,.tb-nav button:hover{background:var(--soft2)}.tb-nav .tb-pri{background:var(--navy);color:#fff}.tb-nav .tb-pri:hover{background:var(--navy2)}
.sharepanel{position:absolute;right:24px;top:100%;margin-top:6px;background:var(--card);border:1px solid var(--line);border-radius:var(--r16);padding:14px;box-shadow:0 12px 32px rgba(4,13,27,.18);max-width:min(92vw,430px)}
.share{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.sb{font:600 14px/1 var(--sans);color:var(--ink);background:var(--card);border:1px solid var(--line2);border-radius:999px;padding:11px 15px;text-decoration:none;cursor:pointer}
.sb:hover{background:var(--soft2)}.sb-main{background:var(--navy);color:#fff;border-color:var(--navy)}.sb-main:hover{background:var(--navy2)}.sb-ok{font:500 12px/1 var(--mono);color:var(--teal-d)}
.sb:focus-visible,.tb-nav a:focus-visible,.tb-nav button:focus-visible,.brand-lg:focus-visible{outline:3px solid var(--orange);outline-offset:2px}
.share-end{background:var(--soft);padding:72px 24px}.share-end .box{max-width:860px;margin:0 auto}.share-end h2{font-size:clamp(30px,4vw,48px);margin:0 0 20px}
.share-end .nav2{margin-top:24px}.share-end .nav2 a{margin-right:20px;font-weight:600}
/* sumário */
.toc{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:18px;margin-top:10px}
.toc a{display:flex;gap:18px;align-items:flex-start;text-decoration:none;color:inherit;background:var(--card);border:1px solid var(--line);border-radius:var(--r16);padding:14px;transition:transform .15s}
.toc a:hover{transform:translateY(-2px)}.toc img{width:96px;height:96px;border-radius:var(--r12);object-fit:cover;flex:none}
.toc .nn{font:400 38px/1 var(--serif);color:var(--orange)}.toc .s{font:600 10.5px/1.2 var(--mono);letter-spacing:.14em;text-transform:uppercase;color:var(--teal-d);margin:6px 0 4px}
.toc h4{font-size:24px;line-height:1.1;margin:0 0 4px}.toc p{margin:0;font-size:14px;line-height:1.5;color:var(--ink2)}
/* créditos */
.cr{columns:2 340px;column-gap:48px;font-size:14px;line-height:1.55}.cr li{break-inside:avoid;margin:0 0 12px}.cr .m{font:400 12px/1.5 var(--mono);color:var(--mute)}
.fontes{columns:2 340px;column-gap:48px;font-size:13.5px;line-height:1.5;padding-left:1.4em}.fontes li{break-inside:avoid;margin:0 0 8px;word-break:break-word}.fontes .m{display:block;font:400 10.5px/1.35 var(--mono);color:var(--mute)}
/* rodapé */
.legal{max-width:70ch;font-size:13.5px;line-height:1.6;color:var(--mute);margin-top:34px}.bg-navy .legal{color:var(--on-navy-dim)}
.marco{display:flex;gap:22px;align-items:center;margin:26px 0}.marco img{width:96px;height:96px;border-radius:50%;border:2px solid var(--navy2);flex:none}
@media(max-width:700px){.cover-logo{left:20px;top:22px}.pb{left:20px}.topbar{padding:8px 14px}.tb-nav a,.tb-nav button{padding:9px 10px;font-size:13px}.sharepanel{right:10px}.share-end{padding:56px 20px}.cred-img{right:20px;top:58px;max-width:26ch}.rh span:nth-child(2){display:none}.rh{white-space:nowrap}.body p.dc::first-letter{font-size:3.6em}.in{padding:76px 20px 84px}.rh{padding:16px 20px}.pf{right:20px}.hero .hin{padding:110px 20px 48px}.faixa .fin{padding:84px 20px}.cred-img{right:20px;max-width:30ch}.fig.full figcaption{padding:0 20px}}
/* impressão: cada .pg vira uma página A4 */
@page{size:210mm 297mm;margin:0}
@media print{
 html{scroll-behavior:auto}body{font-size:10.4pt;line-height:1.5;-webkit-print-color-adjust:exact;print-color-adjust:exact}
 .pg{width:210mm;min-height:297mm;height:auto;overflow:visible;break-after:page;page-break-after:always}
 .in{padding:20mm 15mm 18mm;max-width:none}.rh{padding:9mm 15mm 0}.pf{right:15mm;bottom:8mm}
 h2.t{font-size:34pt;max-width:none;margin-bottom:12pt}.lead{font-size:12.5pt;margin-bottom:14pt}h3{font-size:16pt;margin:14pt 0 5pt}
 .cols{grid-template-columns:1fr 1fr;gap:10mm}.cols.c58{grid-template-columns:5fr 3fr}.cols.c85{grid-template-columns:3fr 5fr}
 .cards{grid-template-columns:repeat(3,1fr);gap:8pt;margin:12pt 0}.card{padding:11pt}.card .v{font-size:26pt}.card .n{font-size:8.6pt}
 .dias{grid-template-columns:repeat(3,1fr);gap:9pt}.dia .n{font-size:30pt}.dia h4{font-size:15pt}.dia p{font-size:8.8pt}
 .fig{margin:10pt 0}.fig.wide img{aspect-ratio:2/1}.fig.meia img{aspect-ratio:3/2}.fig.full{margin:10pt -15mm;width:210mm}.fig.full img{aspect-ratio:2.4/1}.fig figcaption{font-size:7.4pt}.fig figcaption span{font-size:8.4pt}
 .capa,.faixa{min-height:0;height:297mm}.capa h1{font-size:64pt}.capa .sub{font-size:13pt}
 .hero-wrap{width:210mm;min-height:297mm;height:auto;overflow:visible;break-after:page;page-break-after:always}
 .hero{min-height:0;height:138mm}.hero h2.t{font-size:40pt}.hero .hin{padding:30mm 15mm 9mm}.hero .lead{font-size:12pt;margin-bottom:0}
 .hero-body{height:auto;min-height:159mm}.hero-body .in{padding:9mm 15mm 14mm}
 .faixa .big{font-size:110pt}
 .toc{grid-template-columns:1fr 1fr 1fr;gap:7pt}.toc img{display:none}.toc a{padding:8pt}.toc h4{font-size:12pt}.toc p{display:none}.toc .nn{font-size:20pt}.toc .s{font-size:7pt}
 .tl h4{font-size:16pt}.tl p{font-size:9.4pt}.cr{font-size:7.4pt;columns:3;column-gap:8mm}.fontes{font-size:7pt;columns:3;column-gap:8mm;line-height:1.35}.fontes li{margin:0 0 3pt}.fontes .m{font-size:5.6pt}.cit p{font-size:19pt}
 .legal{font-size:8.4pt}.draftbar,.topbar,.share-end{display:none}.pb{left:15mm;bottom:6mm}.brand-lg.sm{font-size:11pt}.cover-logo{top:9mm;left:15mm}
}
"""


def _sim_css(print_body: str) -> str:
    """Mesmas regras de impressão, prefixadas por html.sim, para medir a altura de cada página na tela."""
    out = []
    for sel, decl in re.findall(r"([^{}]+)\{([^{}]*)\}", print_body):
        sels = []
        for s in sel.split(","):
            s = s.strip()
            if not s:
                continue
            sels.append("html.sim" if s == "html" else "html.sim " + s)
        out.append(",".join(sels) + "{" + decl + "}")
    return "".join(out)


_HEAD, _PRINT = WEB_CSS.split("@page{size:210mm 297mm;margin:0}\n@media print{", 1)
_PRINT_BODY = _PRINT.rsplit("}", 1)[0]
WEB_CSS = _HEAD + "@page{size:210mm 297mm;margin:0}\n@media print{" + _PRINT_BODY + "}\n" + _sim_css(_PRINT_BODY)

FIT_JS = """<script>
(function(){
 if(location.search.indexOf('pdf')<0) return;
 var H=1122;
 function fit(){
  document.documentElement.classList.add('sim');
  document.querySelectorAll('.pg,.hero-wrap').forEach(function(p){
   if(p.classList.contains('capa')||p.classList.contains('faixa')) return;
   var inner=p.querySelector('.hero-body .in')||p.querySelector('.in'); if(!inner) return;
   var z=1,tries=0;
   inner.style.zoom=1;
   while(tries++<6){
    var over=p.scrollHeight-H;
    if(over<=1) break;
    var body=inner.getBoundingClientRect().height;
    z=Math.max(0.55,z*Math.max(0.5,(body-over-2)/body));
    inner.style.zoom=z;
    if(z<=0.55) break;
   }
   p.setAttribute('data-zoom',z.toFixed(2));
  });
  document.documentElement.setAttribute('data-fit','done');
 }
 (document.fonts&&document.fonts.ready?document.fonts.ready:Promise.resolve()).then(function(){setTimeout(fit,300)});
})();
</script>"""


LOGO_SVG = ('<svg class="lg" viewBox="0 0 64 64" aria-hidden="true" focusable="false">'
            '<circle cx="32" cy="32" r="28" fill="none" stroke="currentColor" stroke-width="3"/>'
            '<circle cx="32" cy="32" r="22" fill="none" stroke="currentColor" stroke-width="1.5"/>'
            '<polygon points="32,8 27,32 32,28 37,32" fill="#fe932c"/>'
            '<polygon points="32,56 27,32 32,36 37,32" fill="currentColor"/>'
            '<line x1="6" y1="32" x2="14" y2="32" stroke="currentColor" stroke-width="2"/>'
            '<line x1="50" y1="32" x2="58" y2="32" stroke="currentColor" stroke-width="2"/>'
            '<circle cx="32" cy="32" r="2.5" fill="currentColor"/></svg>')
KHARTOS_SITE = "https://khartos.com/?utm_source=newsletter&utm_medium=web&utm_campaign=rota-da-semana&utm_content=logo"


def home_url() -> str:
    """Home da newsletter: NEWSLETTER_ROOT (ex.: https://newsletter.khartos.com) ou podcast.khartos.com/newsletter."""
    custom = os.environ.get("NEWSLETTER_ROOT", "").strip().rstrip("/")
    return (custom or f"{PUBLIC_BASE}/newsletter") + "/"


def logo_html(href: str, cls: str = "", label: str = "Khartos: ir para o início") -> str:
    return f'<a class="brand-lg {cls}" href="{esc(href)}" aria-label="{esc(label)}">{LOGO_SVG}<span>Khartos</span></a>'


def share_url(url: str, canal: str) -> str:
    return f"{url}{'&' if '?' in url else '?'}utm_source=compartilhar&utm_medium={canal}&utm_campaign=rota-da-semana"


def share_row(url: str, title: str, text: str) -> str:
    """Botões de compartilhamento: nativo (quando o navegador tem), WhatsApp, Facebook, LinkedIn, X, Telegram, e-mail e copiar link."""
    q = lambda s: quote(s, safe="")
    chans = [
        ("WhatsApp", f"https://wa.me/?text={q(text + ' ' + share_url(url, 'whatsapp'))}", True),
        ("Facebook", f"https://www.facebook.com/sharer/sharer.php?u={q(share_url(url, 'facebook'))}", True),
        ("LinkedIn", f"https://www.linkedin.com/sharing/share-offsite/?url={q(share_url(url, 'linkedin'))}", True),
        ("X", f"https://twitter.com/intent/tweet?text={q(text)}&url={q(share_url(url, 'x'))}", True),
        ("Telegram", f"https://t.me/share/url?url={q(share_url(url, 'telegram'))}&text={q(text)}", True),
        ("E-mail", f"mailto:?subject={q(title)}&body={q(text + chr(10) + chr(10) + share_url(url, 'email'))}", False),
    ]
    links = "".join(
        f'<a class="sb" href="{esc(h)}"' + (' target="_blank" rel="noopener noreferrer"' if blank else "") + f">{n}</a>"
        for n, h, blank in chans)
    native = (f'<button type="button" class="sb sb-main" data-native-share hidden data-url="{esc(share_url(url, "nativo"))}" '
              f'data-title="{esc(title)}" data-text="{esc(text)}">Compartilhar</button>')
    copy = f'<button type="button" class="sb" data-copy="{esc(share_url(url, "link"))}">Copiar link</button>'
    return f'<div class="share" role="group" aria-label="Compartilhar">{native}{links}{copy}<span class="sb-ok" role="status" aria-live="polite"></span></div>'


PAGE_JS = """<script>
(function(){
 var d=document;
 d.querySelectorAll('[data-native-share]').forEach(function(b){
  if(!navigator.share) return; b.hidden=false;
  b.addEventListener('click',function(){navigator.share({title:b.dataset.title,text:b.dataset.text,url:b.dataset.url}).catch(function(){})});
 });
 d.querySelectorAll('[data-copy]').forEach(function(b){
  b.addEventListener('click',function(){
   var u=b.dataset.copy, ok=b.parentNode.querySelector('.sb-ok');
   function done(){ if(ok){ok.textContent='Link copiado'; setTimeout(function(){ok.textContent=''},2200)} }
   if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(u).then(done,function(){window.prompt('Copie o link:',u)})}else{window.prompt('Copie o link:',u)}
  });
 });
 var t=d.querySelector('[data-share-toggle]'), p=d.getElementById('sharepanel');
 if(t&&p){
  var set=function(o){p.hidden=!o;t.setAttribute('aria-expanded',o?'true':'false')};
  t.addEventListener('click',function(e){e.stopPropagation();set(p.hidden)});
  d.addEventListener('click',function(e){if(!p.hidden&&!p.contains(e.target))set(false)});
  d.addEventListener('keydown',function(e){if(e.key==='Escape'&&!p.hidden){set(false);t.focus()}});
 }
})();
</script>"""


def img_tag(rev, iid, img_rel, cls="", alt=None, pos=None):
    im = rev["imagens"][iid]
    style = f' style="object-position:{esc(im["foco"])}"' if im.get("foco") else ""
    return f'<img src="{img_rel}/{esc(im["file"])}" alt="{esc(alt if alt is not None else im["alt"])}" loading="lazy"{style}>'


def credit_html(im, light=False) -> str:
    return (f'Foto: {esc(im["credito"])} · {esc(im["licenca"])} · <a href="{esc(im["url"])}" target="_blank" rel="noopener">'
            f'Wikimedia Commons</a>')


def render_block(rev, b, img_rel) -> str:
    t = b["t"]
    if t == "p":
        cls = ' class="dc"' if b.get("capitular") else ""
        return f"<p{cls}>{inline_web(b['x'])}</p>"
    if t == "lead":
        return f'<p class="lead">{inline_web(b["x"])}</p>'
    if t == "h3":
        return f"<h3>{inline_web(b['x'])}</h3>"
    if t == "lista":
        cls = ' class="ord"' if b.get("ordenada") else ""
        return f"<ul{cls}>" + "".join(f"<li>{inline_web(i)}</li>" for i in b["itens"]) + "</ul>"
    if t == "foto":
        im = rev["imagens"][b["id"]]
        cap = im.get("legenda", "")
        return (f'<figure class="fig {b.get("tam", "wide")}">{img_tag(rev, b["id"], img_rel)}<figcaption>'
                + (f"<span>{inline_web(cap)}</span>" if cap else "") + f"<small>{credit_html(im)}</small></figcaption></figure>")
    if t == "cartoes":
        return '<div class="cards">' + "".join(
            f'<div class="card"><p class="v">{inline_web(c["valor"])}</p><p class="l">{inline_web(c["rotulo"])}</p>'
            + (f'<p class="n">{inline_web(c["nota"])}</p>' if c.get("nota") else "") + "</div>" for c in b["itens"]) + "</div>"
    if t == "tabela":
        head = "".join(f"<th>{inline_web(h)}</th>" for h in b["cab"])
        rows = "".join("<tr>" + "".join(f"<td>{inline_web(c)}</td>" for c in r) + "</tr>" for r in b["linhas"])
        note = f'<p class="tbn">{inline_web(b["nota"])}</p>' if b.get("nota") else ""
        return f'<table class="tb"><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table>{note}'
    if t == "aviso":
        return (f'<div class="aviso {esc(b.get("tom", ""))}"><p class="r">{inline_web(b["rotulo"])}</p>'
                f'<p>{inline_web(b["x"])}</p></div>')
    if t == "dias":
        out = []
        for d in b["itens"]:
            foto = ""
            if d.get("foto"):
                foto = img_tag(rev, d["foto"], img_rel)
            out.append(f'<div class="dia">{foto}<div class="db"><p class="n">{esc(d.get("n", ""))}</p>'
                       f'<p class="r">{inline_web(d["rotulo"])}</p><h4>{inline_web(d["titulo"])}</h4>'
                       f'<p>{inline_web(d["x"])}</p></div></div>')
        return '<div class="dias">' + "".join(out) + "</div>"
    if t == "timeline":
        return '<div class="tl">' + "".join(
            f'<div class="it"><p class="d">{inline_web(i["data"])}</p><h4>{inline_web(i["titulo"])}</h4>'
            + (f'<p>{inline_web(i["x"])}</p>' if i.get("x") else "") + "</div>" for i in b["itens"]) + "</div>"
    if t == "checklist":
        return '<ul class="ck">' + "".join(f"<li><span>{inline_web(i)}</span></li>" for i in b["itens"]) + "</ul>"
    if t == "citacao":
        return (f'<blockquote class="cit"><p>{inline_web(b["x"])}</p>'
                + (f'<small>{inline_web(b["fonte"])}</small>' if b.get("fonte") else "") + "</blockquote>")
    if t == "colunas":
        cls = esc(b.get("prop", ""))
        a = "".join(render_block(rev, x, img_rel) for x in b["a"])
        c = "".join(render_block(rev, x, img_rel) for x in b["b"])
        return f'<div class="cols {cls}"><div>{a}</div><div>{c}</div></div>'
    if t == "cta":
        url = bn.with_utm(b["url"], "web", b.get("utm", "cta"), "revista")
        sec = " sec" if b.get("secundario") else ""
        return f'<p><a class="btn{sec}" href="{esc(url)}">{esc(b["rotulo"])}</a></p>'
    raise RevistaError(f"bloco sem renderer: {t}")


def page_title_html(p, light=True) -> str:
    out = ""
    if p.get("secao"):
        out += f'<p class="kick">{inline_web(p["secao"])}</p>'
    if p.get("titulo"):
        out += f'<h2 class="t">{inline_web(p["titulo"])}</h2>'
    if p.get("lead"):
        out += f'<p class="lead">{inline_web(p["lead"])}</p>'
    return out


def render_page(rev, p, n, total, img_rel, links) -> str:
    ed = rev["edicao"]
    pid, lay = p["id"], p["layout"]
    num = f"{n:02d} / {total:02d}"
    rh = (f'<div class="rh"><span>Rota da Semana · Khartos</span><span>{esc(p.get("rodape", p.get("secao", "")) or "")}'
          f'</span><span>Edição {ed["numero"]}</span></div>')
    home = home_url()
    pf = f'<div class="pb">{logo_html(home, "sm")}</div><div class="pf">{num}</div>'
    blocks = "".join(render_block(rev, b, img_rel) for b in p.get("blocos", []))
    if lay == "capa":
        im = rev["imagens"][ed["capa"]]
        chamadas = "".join(f'<div><b>{esc(c["rotulo"])}</b><span>{inline_web(c["x"])}</span></div>' for c in p.get("chamadas", []))
        return (f'<section class="pg capa" id="{pid}"><div class="bgimg">{img_tag(rev, ed["capa"], img_rel)}</div><div class="ov"></div>'
                f'<div class="cover-logo">{logo_html(home, "big")}</div><div class="cred-img">{credit_html(im)}</div>'
                f'<div class="in"><p class="brand">Rota da Semana · Khartos <i></i> Edição {ed["numero"]}</p>'
                f'<p class="kick">{esc(ed["periodo"])}</p><h1>{inline_web(ed["titulo"])}</h1>'
                f'<p class="sub">{inline_web(ed["subtitulo"])}</p><div class="chamadas">{chamadas}</div></div><div class="pf">{num}</div></section>')
    if lay == "sumario":
        items = []
        for i, q in enumerate(rev["paginas"], 1):
            if not q.get("sumario"):
                continue
            ph = q.get("foto") or next((b["id"] for b in q.get("blocos", []) if b["t"] == "foto"), None)
            th = (f'<img src="{img_rel}/{esc(rev["imagens"][ph]["file"])}" alt="" loading="lazy">' if ph else "")
            items.append(f'<a href="#{q["id"]}">{th}<div><div class="nn">{i:02d}</div><div class="s">{inline_web(q.get("secao", ""))}</div>'
                         f'<h4>{inline_web(q["sumario"] if isinstance(q["sumario"], str) else q["titulo"])}</h4>'
                         f'<p>{inline_web(q.get("resumo", ""))}</p></div></a>')
        return (f'<section class="pg bg-soft" id="{pid}">{rh}<div class="in">{page_title_html(p)}'
                f'<div class="toc">{"".join(items)}</div>{blocks}</div>{pf}</section>')
    if lay == "hero":
        im = rev["imagens"][p["foto"]]
        return (f'<section class="hero-wrap" id="{pid}"><div class="hero"><div class="bgimg">{img_tag(rev, p["foto"], img_rel)}</div>'
                f'<div class="ov"></div>{rh}<div class="cred-img">{credit_html(im)}</div><div class="hin">{page_title_html(p)}</div></div>'
                f'<div class="hero-body"><div class="in body">{blocks}</div></div>{pf}</section>')
    if lay == "faixa":
        im = rev["imagens"][p["foto"]]
        return (f'<section class="pg faixa" id="{pid}"><div class="bgimg">{img_tag(rev, p["foto"], img_rel)}</div><div class="ov"></div>{rh}'
                f'<div class="cred-img">{credit_html(im)}</div><div class="fin"><p class="kick">{inline_web(p.get("secao", ""))}</p>'
                f'<p class="big">{inline_web(p["destaque"])}</p><p class="sm">{inline_web(p["legenda_destaque"])}</p>'
                f'{blocks}</div>{pf}</section>')
    if lay == "creditos":
        itens = [im for iid, im in rev["imagens"].items() if iid in rev.get("_usadas", set())]
        if p.get("metade"):
            meio = (len(itens) + 1) // 2
            itens = itens[:meio] if p["metade"] == 1 else itens[meio:]
        cred = "".join(
            f'<li><b>{inline_web(im.get("legenda") or im["alt"])}</b><br><span class="m">{credit_html(im)}</span></li>'
            for im in itens)
        def _host(u):
            pu = urlparse(u)
            s = (pu.netloc + pu.path).rstrip("/")
            return s if len(s) <= 58 else s[:57] + "…"
        fontes = "".join(f'<li><a href="{esc(u)}" target="_blank" rel="noopener">{esc(t)}</a><span class="m">{esc(_host(u))}</span></li>' for t, u, _ in links)
        parte = p.get("parte")
        corpo = ""
        if parte in (None, "fotos"):
            corpo += f'<h3>Fotos</h3><ul class="cr" style="list-style:none;padding:0">{cred}</ul>'
        if parte in (None, "fontes"):
            corpo += f'<h3>Fontes citadas</h3><ol class="fontes">{fontes}</ol>'
        return (f'<section class="pg bg-soft" id="{pid}">{rh}<div class="in body">{page_title_html(p)}'
                f'{corpo}{blocks}</div>{pf}</section>')
    bg = {"navy": "bg-navy", "soft": "bg-soft"}.get(p.get("bg", ""), "")
    if lay == "navy":
        bg = "bg-navy"
    body_cls = "in body"
    extra = ""
    if lay == "navy" and p.get("marco"):
        extra = (f'<div class="marco"><img src="{MARCO_NAVY}" alt="" width="96" height="96">'
                 f'<p style="margin:0;max-width:46ch">{inline_web(KHARTOS_FIXED)}</p></div>')
    return (f'<section class="pg {bg}" id="{pid}">{rh}<div class="{body_cls}">{page_title_html(p)}{blocks}{extra}</div>{pf}</section>')


def render_web(rev: dict, subject_idx: int, draft: bool = False) -> str:
    ed = rev["edicao"]
    pages = rev["paginas"]
    used = set()
    for p in pages:
        if p.get("foto"):
            used.add(p["foto"])
        stack = list(p.get("blocos", []))
        while stack:
            b = stack.pop()
            if b["t"] == "foto":
                used.add(b["id"])
            if b["t"] == "dias":
                used.update(d["foto"] for d in b["itens"] if d.get("foto"))
            stack.extend(b.get("a", []) + b.get("b", []))
    used.add(ed["capa"])
    rev["_usadas"] = used
    links = collect_links(rev)
    body = "".join(render_page(rev, p, i, len(pages), "img", links) for i, p in enumerate(pages, 1))
    home = home_url()
    edition_url = root_url(PUBLIC_BASE, ed["data"]) + "/"
    title_txt = plain(ed["titulo"])
    stext = f"{title_txt}: edição {ed['numero']} da Rota da Semana, a newsletter do Khartos"
    topbar = (f'<header class="topbar">{logo_html(home)}<nav class="tb-nav" aria-label="Navegação da edição">'
              f'<a href="{esc(home)}">&larr; Todas as edições</a><a href="revista.pdf" target="_blank" rel="noopener">Baixar PDF</a>'
              f'<button type="button" class="tb-pri" data-share-toggle aria-expanded="false" aria-controls="sharepanel">Compartilhar</button></nav>'
              f'<div class="sharepanel" id="sharepanel" hidden>{share_row(edition_url, title_txt, stext)}</div></header>')
    end = (f'<section class="share-end" id="compartilhar"><div class="box"><p class="kick">Gostou desta edição?</p>'
           f'<h2>Compartilhe com quem viaja com você</h2>{share_row(edition_url, title_txt, stext)}'
           f'<p class="nav2"><a href="{esc(home)}">&larr; Ver todas as edições</a><a href="#top">Voltar ao topo</a>'
           f'<a href="revista.pdf" target="_blank" rel="noopener">Baixar o PDF</a></p></div></section>')
    bar = '<div class="draftbar">Rascunho · aguardando aprovação · nada foi enviado</div>' if draft else ""
    title = f'{ed["titulo"]} — Rota da Semana, edição {ed["numero"]}'
    return f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex">
<title>{esc(plain(title))}</title><meta name="description" content="{esc(plain(ed["subtitulo"]))}">
<meta property="og:title" content="{esc(plain(title))}"><meta property="og:description" content="{esc(plain(ed["subtitulo"]))}">
<meta property="og:image" content="{root_url(PUBLIC_BASE, ed["data"])}/img/{esc(rev["imagens"][ed["capa"]]["file"])}">
<meta property="og:url" content="{root_url(PUBLIC_BASE, ed["data"])}/"><link rel="canonical" href="{root_url(PUBLIC_BASE, ed["data"])}/">
{FONTS}<style>{WEB_CSS}</style></head><body id="top">{bar}{topbar}{body}{end}{PAGE_JS}{FIT_JS}</body></html>"""


# ---------------------------------------------------------------- e-mail

def render_email(rev: dict, base: str, subject_idx: int, number: int) -> str:
    ed, em = rev["edicao"], rev["email"]
    date = ed["data"]
    root = root_url(base, date)
    imgs = rev["imagens"]

    def eimg(iid):
        f = imgs[iid]["file"]
        return f"{root}/img/{f.rsplit('.', 1)[0]}-e.jpg"

    def link(anchor=None, content="cta-revista"):
        u = root + "/" + (f"#{anchor}" if anchor else "")
        return bn.with_utm(u, "email", content, f"edicao-{number}")

    def ph(iid, h=None):
        im = imgs[iid]
        return (f'<img src="{eimg(iid)}" alt="{esc(im["alt"])}" width="600" style="display:block;width:100%;max-width:600px;'
                f'height:auto;border:0;"{"" if not h else ""}>')

    P, ROW = bn._p, bn._row
    rows = []
    # destaques
    for i, d in enumerate(em["destaques"]):
        im = imgs[d["foto"]]
        card = (f'<tr><td style="padding:0;">{ph(d["foto"])}</td></tr>'
                f'<tr><td style="padding:22px 40px 32px 40px;" class="mobile-padding">'
                f'<p style="margin:0 0 8px 0;font-family:{bn.FONT_BODY};font-size:12px;line-height:16px;letter-spacing:1.2px;'
                f'text-transform:uppercase;font-weight:700;color:#005049;" class="dark-link">{esc(d["secao"])}</p>'
                f'<h2 style="margin:0 0 10px 0;font-family:{bn.FONT_SERIF};font-size:30px;line-height:34px;font-weight:400;color:#1a1c1c;" '
                f'class="mobile-font-h2 dark-text">{bn.inline_html(d["titulo"])}</h2>'
                f'{P(bn.inline_html(d["x"]), mb=12, cls="mobile-font-base dark-text")}'
                f'<a href="{esc(link(d["ancora"], "destaque-" + str(i + 1)))}" class="dark-link" style="font-family:{bn.FONT_BODY};'
                f'font-size:15px;font-weight:700;color:#005049;text-decoration:underline;">Ler na revista &rarr;</a>'
                f'<p style="margin:10px 0 0 0;font-family:\'IBM Plex Mono\',\'Courier New\',monospace;font-size:11px;line-height:16px;'
                f'color:#75777d;" class="dark-text-muted">Foto: {esc(im["credito"])} · {esc(im["licenca"])} · Wikimedia Commons</p>'
                f'</td></tr>')
        rows.append(card)
    body_rows = "".join(rows)

    # datas e checklist reaproveitados das páginas
    def find_block(page_id, kind):
        for p in rev["paginas"]:
            if p["id"] == page_id:
                for b in p.get("blocos", []):
                    if b["t"] == kind:
                        return b
        return None

    tl = find_block(em.get("datas_de", ""), "timeline")
    ck = find_block(em.get("checklist_de", ""), "checklist")
    extra = []
    if tl:
        items = "".join(
            f'<tr><td style="border-left:3px solid #1c9a8e;padding:0 0 0 16px;">'
            f'{P(esc(bn.inline_text(i["data"])), size=12, lh=16, color="#005049", mb=2, cls="dark-link", weight="700")}'
            f'{P(esc(bn.inline_text(i["titulo"])), size=17, lh=24, mb=2, weight="700")}'
            f'{P(bn.inline_html(i.get("x", "")), size=15, lh=23, color="#45474c", mb=0, cls="dark-text-secondary")}</td></tr>'
            f'<tr><td style="height:16px;font-size:1px;line-height:1px;">&nbsp;</td></tr>' for i in tl["itens"])
        extra.append(bn._section_title("Datas e prazos", mb=20) +
                     ROW('<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">' + items + "</table>"))
    if ck:
        box = ('<table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr><td style="width:18px;height:18px;'
               'border:2px solid #c5c6cc;border-radius:3px;" class="dark-border">&nbsp;</td></tr></table>')
        trs = "".join(f'<tr><td width="28" valign="top" style="padding:3px 0 12px 0;">{box}</td>'
                      f'<td valign="top" style="padding:0 0 12px 8px;font-family:{bn.FONT_BODY};font-size:16px;line-height:26px;'
                      f'color:#1a1c1c;" class="mobile-font-base dark-text">{bn.inline_html(i)}</td></tr>' for i in ck["itens"])
        extra.append(bn._section_title("Checklist da semana", mb=16) +
                     ROW('<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">' + trs + "</table>", bottom=24))
    ep_url = bn.with_utm(f"{base}/ep/ep-{date}/", "email", "cta-episodio", f"edicao-{number}")
    podcast = (bn._section_title("No podcast", mb=12) +
               ROW(P(bn.inline_html(em["podcast"]), mb=20) + bn._button(ep_url, "Ouvir o episódio"), bottom=32))
    kh_url = bn.with_utm(KHARTOS_URL, "email", "cta-khartos", f"edicao-{number}")
    khartos = (
        '<table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0" style="max-width:600px;width:100%;'
        'background-color:#040d1b;" class="mobile-full dark-bg-khartos"><tr><td style="padding:32px 40px;" class="mobile-padding">'
        '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>'
        f'<td width="88" valign="top" style="padding-right:16px;" class="mobile-hide"><img src="{MARCO_NAVY}" alt="" width="72" height="72" '
        'style="display:block;width:72px;height:72px;border-radius:50%;border:2px solid #1a2332;"></td><td valign="top">'
        f'<p style="margin:0 0 10px 0;font-family:{bn.FONT_BODY};font-size:13px;line-height:18px;letter-spacing:0.5px;text-transform:uppercase;'
        f'color:#6bd8cb;">No Khartos</p><p style="margin:0 0 20px 0;font-family:{bn.FONT_BODY};font-size:15px;line-height:24px;color:#dae3f7;">'
        f'{esc(KHARTOS_FIXED)}</p><a href="{esc(kh_url)}" style="display:inline-block;font-family:{bn.FONT_BODY};font-size:15px;'
        'line-height:20px;font-weight:700;color:#fe932c;text-decoration:underline;">Planejar minha viagem &rarr;</a></td></tr></table></td></tr></table>')
    foot_lines = rev.get("rodape", [])
    foot = "".join(P(bn.inline_html(l), size=13, lh=20, color="#75777d", mb=12, cls="dark-text-muted") for l in foot_lines)
    foot += P('Você recebe este e-mail porque se inscreveu na newsletter Rota da Semana. '
              f'<a href="{bn.UNSUB}" class="dark-link" style="color:#005049;text-decoration:underline;">Descadastrar em um clique</a>',
              size=13, lh=20, color="#75777d", mb=12, cls="dark-text-muted")
    foot += P(bn.SENDER, size=13, lh=20, color="#75777d", mb=0, cls="dark-text-muted")
    footer = ('<table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0" style="max-width:600px;width:100%;'
              f'background-color:#eeeeee;" class="mobile-full dark-bg-card"><tr><td style="padding:28px 40px;" class="mobile-padding">{foot}</td></tr></table>')

    subject = em["assuntos"][subject_idx]
    pre = ('<span style="display:none !important;font-size:1px;line-height:1px;max-height:0px;max-width:0px;opacity:0;overflow:hidden;'
           f'mso-hide:all;">{esc(em["preview"])}</span><span style="display:none !important;font-size:1px;line-height:1px;max-height:0px;'
           'max-width:0px;opacity:0;overflow:hidden;mso-hide:all;">' + "&zwnj;&nbsp;" * 40 + "</span>")
    capa_im = imgs[ed["capa"]]
    css = bn.CSS
    head = (f'<table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0" style="max-width:600px;width:100%;'
            f'background-color:#040d1b;" class="mobile-full dark-bg-navy"><tr><td style="padding:26px 40px 22px 40px;" class="mobile-padding">'
            f'<p style="margin:0;font-family:{bn.FONT_BODY};font-size:12px;line-height:16px;letter-spacing:1.4px;text-transform:uppercase;'
            f'color:#6bd8cb;">Rota da Semana &middot; Khartos &middot; Edição {number}</p></td></tr>'
            f'<tr><td style="padding:0;">{ph(ed["capa"])}</td></tr>'
            f'<tr><td style="padding:28px 40px 12px 40px;" class="mobile-padding">'
            f'<p style="margin:0 0 12px 0;font-family:{bn.FONT_BODY};font-size:13px;line-height:18px;color:#818a9d;">Semana de {esc(ed["periodo"])}</p>'
            f'<h1 style="margin:0 0 14px 0;font-family:{bn.FONT_SERIF};font-size:38px;line-height:42px;font-weight:400;color:#dae3f7;" '
            f'class="mobile-font-h1">{bn.inline_html(ed["titulo"])}</h1>'
            f'<p style="margin:0 0 24px 0;font-family:{bn.FONT_BODY};font-size:17px;line-height:26px;color:#dae3f7;">'
            f'{bn.inline_html(em["abertura"])}</p>{bn._button(link(None, "cta-revista"), "Ler a revista completa")}'
            f'<p style="margin:14px 0 0 0;text-align:center;font-family:{bn.FONT_BODY};font-size:13px;line-height:20px;color:#9fb0cc;">'
            f'<a href="{esc(link(None, "pdf").replace(root + "/", root + "/revista.pdf"))}" style="color:#6bd8cb;text-decoration:underline;">'
            f'Baixar em PDF</a></p></td></tr>'
            f'<tr><td style="padding:0 40px 22px 40px;" class="mobile-padding"><p style="margin:0;font-family:\'IBM Plex Mono\',\'Courier New\',monospace;'
            f'font-size:10px;line-height:14px;color:#818a9d;">Capa: {esc(capa_im["credito"])} · {esc(capa_im["licenca"])} · Wikimedia Commons</p></td></tr></table>')
    return f"""<!DOCTYPE html>
<html lang="pt-BR" xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><meta http-equiv="X-UA-Compatible" content="IE=edge">
<meta name="color-scheme" content="light dark"><meta name="supported-color-schemes" content="light dark"><title>{esc(subject)}</title>
<!--[if mso]><noscript><xml><o:OfficeDocumentSettings><o:PixelsPerInch>96</o:PixelsPerInch></o:OfficeDocumentSettings></xml></noscript><![endif]-->
<!--[if !mso]><!--><link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Instrument+Serif&display=swap" rel="stylesheet"><!--<![endif]-->
<style>{css}</style></head>
<body style="margin:0;padding:0;background-color:#f9f9f9;-webkit-font-smoothing:antialiased;" class="dark-bg-body">{pre}
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:#f9f9f9;" class="dark-bg-body"><tr><td align="center" style="padding:0;">
{head}
<table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0" style="max-width:600px;width:100%;background-color:#ffffff;" class="mobile-full dark-bg-surface">
{bn._section_title("Nesta edição", top=36, mb=20)}{body_rows}{"".join(extra)}{podcast}
</table>
{khartos}{footer}
</td></tr></table></body></html>
"""


def render_text(rev: dict, base: str, subject_idx: int, number: int) -> str:
    ed, em = rev["edicao"], rev["email"]
    date = ed["data"]
    root = root_url(base, date)
    out = ["ROTA DA SEMANA · KHARTOS", em["assuntos"][subject_idx], f"Edição {number} · Semana de {ed['periodo']}", "",
           plain(ed["subtitulo"]), "", plain(em["abertura"]), "", "Ler a revista completa: " + bn.with_utm(root + "/", "email", "cta-revista", f"edicao-{number}"),
           "Baixar em PDF: " + bn.with_utm(root + "/revista.pdf", "email", "pdf", f"edicao-{number}"), "", "NESTA EDIÇÃO", ""]
    for i, d in enumerate(em["destaques"], 1):
        out += [f"{d['secao']}: {plain(d['titulo'])}", plain(d["x"]),
                "Ler: " + bn.with_utm(f"{root}/#{d['ancora']}", "email", f"destaque-{i}", f"edicao-{number}"), ""]
    for key, kind, title in (("datas_de", "timeline", "DATAS E PRAZOS"), ("checklist_de", "checklist", "CHECKLIST DA SEMANA")):
        for p in rev["paginas"]:
            if p["id"] == em.get(key):
                for b in p.get("blocos", []):
                    if b["t"] == kind:
                        out += [title, ""]
                        if kind == "timeline":
                            for i in b["itens"]:
                                out += [f"- {plain(i['data'])}: {plain(i['titulo'])}. {plain(i.get('x', ''))}".strip(), ""]
                        else:
                            out += ["[ ] " + plain(i) for i in b["itens"]] + [""]
    out += ["NO PODCAST", "", plain(em["podcast"]), "Ouvir: " + bn.with_utm(f"{base}/ep/ep-{date}/", "email", "cta-episodio", f"edicao-{number}"),
            "", "NO KHARTOS", "", KHARTOS_FIXED, bn.with_utm(KHARTOS_URL, "email", "cta-khartos", f"edicao-{number}"), "", "--"]
    out += [plain(l) for l in rev.get("rodape", [])]
    out += ["Você recebe este e-mail porque se inscreveu na newsletter Rota da Semana.", f"Descadastrar: {bn.UNSUB}", bn.SENDER, ""]
    return "\n".join(out)


def render_subjects(rev: dict) -> str:
    em = rev["email"]
    lines = ["Assuntos (até 60 caracteres; a promessa nos primeiros 40):"]
    lines += [f"{i}. {s}  [{len(s)} caracteres]" for i, s in enumerate(em["assuntos"], 1)]
    lines += ["", f"Pré-visualização [{len(em['preview'])} caracteres, máximo 90]:", em["preview"], ""]
    return "\n".join(lines)


CARTO = re.compile(r"\b(mapa|rotas?|expedi[cç][aã]o|expedi[cç][oõ]es|b[uú]ssola|cartograf\w*|atlas)\b", re.I)


def carto_por_pagina(rev: dict) -> list:
    """Páginas com mais de 2 termos cartográficos (o nome do programa não conta; o bloco do Khartos conta 2)."""
    bad = []
    for p in rev["paginas"]:
        txt = " ".join(_walk_text(p))
        txt = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", txt).replace("Rota da Semana", "")
        n = len(CARTO.findall(txt)) + (2 if p.get("marco") else 0)
        if n > 2:
            bad.append((p["id"], n))
    return bad


def lint(rev: dict, email_html: str) -> list:
    w = [f"página {i} tem {n} termos cartográficos (máximo 2 por página)" for i, n in carto_por_pagina(rev)]
    em = rev["email"]
    for i, s in enumerate(em["assuntos"], 1):
        if len(s) > 60:
            w.append(f"assunto {i} tem {len(s)} caracteres (máximo 60)")
    if len(em["preview"]) > 90:
        w.append(f"pré-visualização tem {len(em['preview'])} caracteres (máximo 90)")
    kb = len(email_html.encode("utf-8")) / 1024
    if kb > 80:
        w.append(f"HTML de e-mail com {kb:.0f} KB (Gmail recorta acima de 102 KB; meta: até 80 KB)")
    return w


# ---------------------------------------------------------------- PDF e saída

def find_chrome() -> str | None:
    for c in ("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "google-chrome", "google-chrome-stable",
              "chromium", "chromium-browser"):
        p = c if c.startswith("/") else shutil.which(c)
        if p and Path(p).exists():
            return p
    return None


def make_pdf(index_html: Path, pdf: Path) -> bool:
    chrome = find_chrome()
    if not chrome:
        print("  aviso: Chrome não encontrado; PDF não gerado", file=sys.stderr)
        return False
    cmd = [chrome, "--headless=new", "--disable-gpu", "--no-sandbox", "--no-pdf-header-footer", "--window-size=794,1123",
           "--virtual-time-budget=20000", f"--print-to-pdf={pdf}", index_html.resolve().as_uri() + "?pdf=1"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    return pdf.exists() and pdf.stat().st_size > 10_000


def build(ep_dir: Path, out: Path | None, site: Path | None, base: str, subject_idx: int, want_pdf: bool) -> list:
    rev = json.loads((ep_dir / "revista.json").read_text(encoding="utf-8"))
    img_dir = ep_dir / "revista" / "img"
    validate(rev, img_dir)
    number = rev["edicao"]["numero"]
    date = ep_dir.name
    if rev["edicao"]["data"] != date:
        raise RevistaError(f"edicao.data ({rev['edicao']['data']}) difere da pasta ({date})")
    approved = (ep_dir / APROVADA).exists()
    web = render_web(rev, subject_idx, draft=not approved)
    email = render_email(rev, base, subject_idx, number)
    text = render_text(rev, base, subject_idx, number)

    def emit(d: Path, with_email: bool):
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(web, encoding="utf-8")
        used = rev["_usadas"] | {a["foto"] for a in rev["email"]["destaques"]}
        (d / "img").mkdir(exist_ok=True)
        for iid in used:
            f = rev["imagens"][iid]["file"]
            shutil.copy2(img_dir / f, d / "img" / f)
            e = f.rsplit(".", 1)[0] + "-e.jpg"
            if (img_dir / e).exists():
                shutil.copy2(img_dir / e, d / "img" / e)
        if with_email:
            (d / "email.html").write_text(email, encoding="utf-8")
            (d / "email.txt").write_text(text, encoding="utf-8")
            (d / "email-assunto.txt").write_text(render_subjects(rev), encoding="utf-8")

    pdf_ok = None
    if out:
        emit(out / "newsletter" / date, True)
        if want_pdf:
            pdf_ok = make_pdf(out / "newsletter" / date / "index.html", out / "newsletter" / date / "revista.pdf")
    if site:
        # aprovada: /newsletter/AAAA-MM-DD/ ; rascunho: /newsletter/preview/AAAA-MM-DD/ (com faixa de rascunho, noindex)
        d = site / "newsletter" / date if approved else site / "newsletter" / "preview" / date
        emit(d, False)
        src = (out / "newsletter" / date / "revista.pdf") if out else None
        if src and src.exists():
            shutil.copy2(src, d / "revista.pdf")
        elif want_pdf:
            make_pdf(d / "index.html", d / "revista.pdf")
    warns = lint(rev, email)
    if want_pdf and pdf_ok is False:
        warns.append("PDF não gerado")
    return warns


def write_index(site: Path, dirs: list) -> int:
    """site/newsletter/index.html: lista das edições aprovadas (a raiz de newsletter.khartos.com)."""
    items = []
    for d in sorted(dirs, reverse=True):
        if not (d / APROVADA).exists():
            continue
        try:
            ed = json.loads((d / "revista.json").read_text(encoding="utf-8"))["edicao"]
            capa = json.loads((d / "revista.json").read_text(encoding="utf-8"))["imagens"][ed["capa"]]["file"]
        except (KeyError, ValueError, OSError):
            continue
        base = f"{d.name}/"
        items.append(
            f'<div class="ed"><img src="{base}img/{esc(capa)}" alt="" loading="lazy"><div>'
            f'<p class="kick">Edição {ed["numero"]} · {esc(ed["periodo"])}</p><h2><a href="{base}">{inline_web(ed["titulo"])}</a></h2>'
            f'<p>{inline_web(ed["subtitulo"])}</p><p class="m"><a href="{base}">Ler na web</a> · '
            f'<a href="{base}revista.pdf" target="_blank" rel="noopener">Baixar o PDF</a></p></div></div>')
    if not items:
        return 0
    css = WEB_CSS + (".ixh{display:flex;justify-content:space-between;align-items:center;gap:12px;max-width:960px;margin:0 auto;padding:22px 24px 0}"
                     ".ix{max-width:960px;margin:0 auto;padding:36px 24px 72px}.ix h1{font-size:clamp(40px,6vw,72px);line-height:1.02;margin:0 0 14px}"
                     ".ix h1 .h1sub{display:block;font-size:.5em;color:var(--teal-d);margin-top:8px}.ix .sub{color:var(--ink2);max-width:56ch;margin:0 0 22px}"
                     ".ix .share{margin:0 0 36px}.ed{display:flex;gap:22px;align-items:center;color:inherit;"
                     "background:var(--card);border:1px solid var(--line);border-radius:var(--r16);padding:14px;margin:0 0 16px}.ed img{width:200px;height:130px;"
                     "object-fit:cover;border-radius:var(--r12);flex:none}.ed h2{font-size:28px;margin:0 0 6px}.ed h2 a{color:inherit;text-decoration:none}.ed p{margin:0 0 6px}.ed .m{color:var(--teal-d);font-weight:600}"
                     ".ixf{max-width:960px;margin:0 auto;padding:0 24px 56px;color:var(--mute);font-size:14px}"
                     "@media(max-width:640px){.ed{flex-direction:column;align-items:flex-start}.ed img{width:100%;height:auto;aspect-ratio:16/9}}")
    home = home_url()
    name = "Rota da Semana, a newsletter do Khartos"
    page = (f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<meta name="robots" content="noindex"><title>Rota da Semana · a newsletter do Khartos</title>'
            f'<link rel="canonical" href="{esc(home)}">{FONTS}<style>{css}</style></head><body>'
            f'<header class="ixh">{logo_html(KHARTOS_SITE, "", "Khartos: abrir o site")}</header>'
            f'<main class="ix"><p class="kick">Rota da Semana · Khartos</p>'
            f'<h1>Rota da Semana<span class="h1sub">a newsletter do Khartos</span></h1>'
            f'<p class="sub">Uma edição por semana, com fotos, fontes e o que conferir antes de embarcar.</p>'
            f'{share_row(home, name, name)}{"".join(items)}</main>'
            f'<footer class="ixf">Rota da Semana é o podcast e a newsletter do Khartos.</footer>{PAGE_JS}</body></html>')
    out = site / "newsletter"
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(page, encoding="utf-8")
    return len(items)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("episodes", nargs="?", default="episodes")
    ap.add_argument("--episodio")
    ap.add_argument("--out")
    ap.add_argument("--site", help="publica a revista: aprovada em /newsletter/DATA/, rascunho em /newsletter/preview/DATA/")
    ap.add_argument("--pdf", action="store_true")
    ap.add_argument("--base", default=PUBLIC_BASE)
    ap.add_argument("--assunto", type=int, default=1, choices=[1, 2, 3])
    a = ap.parse_args()
    if not a.out and not a.site:
        ap.error("informe --out e/ou --site")
    root = Path(a.episodes)
    dirs = sorted(d for d in root.iterdir() if d.is_dir() and (d / "revista.json").exists())
    if a.episodio:
        dirs = [d for d in dirs if d.name == a.episodio]
        if not dirs:
            print(f"erro: sem revista.json para {a.episodio}", file=sys.stderr)
            return 1
    rc = 0
    for d in dirs:
        try:
            warns = build(d, Path(a.out) if a.out else None, Path(a.site) if a.site else None, a.base.rstrip("/"), a.assunto - 1, a.pdf)
            print(f"{d.name}: ok ({'aprovada' if (d / APROVADA).exists() else 'rascunho'})")
            for w in warns:
                print(f"  aviso: {w}", file=sys.stderr)
        except (RevistaError, KeyError) as e:
            print(f"{d.name}: ERRO: {e!r}", file=sys.stderr)
            rc = 1
    if a.site:
        n = write_index(Path(a.site), dirs)
        if n:
            print(f"índice: {n} edição(ões) aprovada(s)")
    return rc


if __name__ == "__main__":
    sys.exit(main())
