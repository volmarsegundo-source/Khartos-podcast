#!/usr/bin/env python3
"""Gera a newsletter da Rota da Semana a partir de episodes/AAAA-MM-DD/newsletter.md.

Saídas por edição (fonte única: o markdown):
  email.html           HTML de e-mail (tabelas, CSS inline, modo escuro) para colar na plataforma de envio
  email.txt            versão em texto simples do mesmo e-mail
  email-assunto.txt    as 3 opções de assunto e a pré-visualização
  web.html             a mesma newsletter como página web (com faixa de rascunho se não aprovada)

Uso:
  python3 scripts/build_newsletter.py [episodes] [--episodio AAAA-MM-DD] [--out DIR] [--site DIR] [--assunto N]

  --out DIR   grava as quatro saídas de cada edição em DIR/AAAA-MM-DD/ (rascunhos incluídos)
  --site DIR  publica DIR/newsletter/AAAA-MM-DD/index.html SÓ para edições aprovadas, isto é, com o
              arquivo vazio episodes/AAAA-MM-DD/newsletter.aprovada

Nada aqui envia e-mail. O e-mail sai com marcadores a trocar na plataforma de envio:
{{unsubscribe_url}} e {{identificacao_remetente}}.
"""
from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

FONT_BODY = "'DM Sans', 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
FONT_SERIF = "'Instrument Serif', Georgia, 'Times New Roman', serif"
MARCO_POLO_IMG = "https://khartos.com/characters/marco-polo/marco-polo-welcoming-light.webp"
UNSUB = "{{unsubscribe_url}}"
SENDER = "{{identificacao_remetente}}"
APROVADA = "newsletter.aprovada"

DEST_NAMES = ["Um destino, mais fundo", "O destino em 3 fatos", "Dois destinos, um ângulo"]
KNOWN = ["Assunto", "Abertura", *DEST_NAMES, "No podcast", "Datas e prazos",
         "Checklist da semana", "No Khartos", "Rodapé"]
REQUIRED = ["Assunto", "Abertura", "No podcast", "Datas e prazos", "Checklist da semana", "No Khartos", "Rodapé"]
MARKER_OMITTED = "[Bloco de destino omitido"
MARKER_PHASE2 = "[Fase 2"


class NewsletterError(ValueError):
    pass


# ---------------------------------------------------------------- leitura do markdown

def parse(md: str) -> dict:
    """Valida a estrutura do newsletter.md e devolve as partes. Falha alto em qualquer desvio."""
    lines = md.splitlines()
    first = lines[0].strip() if lines else ""
    m = re.match(r"^#\s+Rascunho\s+[—-]\s+newsletter da semana de (.+)$", first)
    if not m:
        raise NewsletterError("1ª linha deve ser '# Rascunho — newsletter da semana de DD a DD/MM/AAAA'")
    ed = {"period": m.group(1).strip(), "dest_omitted": False, "sections": {}, "dest_title": None, "dest_kind": None}
    current = None
    for raw in lines[1:]:
        s = raw.strip()
        if s.startswith(MARKER_OMITTED):
            ed["dest_omitted"] = True
            continue
        if s.startswith(MARKER_PHASE2):
            continue
        if re.fullmatch(r"\[[^\]]*\]", s):
            raise NewsletterError(f"marcador de rascunho não reconhecido: {s!r}")
        if s.startswith("## "):
            heading = s[3:].strip()
            name = next((k for k in KNOWN if heading.startswith(k)), None)
            if name is None:
                raise NewsletterError(f"seção desconhecida: {heading!r}")
            if name in ed["sections"]:
                raise NewsletterError(f"seção repetida: {name!r}")
            ed["sections"][name] = []
            current = name
            if name in DEST_NAMES:
                ed["dest_kind"] = name
                suffix = heading[len(name):].lstrip(" —-").strip()
                ed["dest_title"] = suffix or name
            continue
        if not s:
            continue
        if current is None:
            raise NewsletterError(f"texto fora de seção: {s[:50]!r}")
        ed["sections"][current].append(s)
    for name in REQUIRED:
        if name not in ed["sections"]:
            raise NewsletterError(f"seção obrigatória ausente: {name!r}")
    if len([n for n in ed["sections"] if n in DEST_NAMES]) > 1:
        raise NewsletterError("mais de um bloco de destino")
    sec = ed["sections"]
    subjects = [re.sub(r"^[-*]\s+", "", l) for l in sec["Assunto"] if re.match(r"^[-*]\s+", l)]
    pv = next((re.sub(r"^\*\*Pré-visualização:\*\*\s*", "", l) for l in sec["Assunto"]
               if l.startswith("**Pré-visualização:**")), "")
    if len(subjects) != 3 or not pv:
        raise NewsletterError("Assunto deve ter 3 opções e uma linha '**Pré-visualização:**'")
    ed["subjects"], ed["preview"] = subjects, pv
    return ed


def find_url(lines: list, what: str) -> tuple:
    """Separa a URL solta (episódio ou Khartos) do texto da seção."""
    text = " ".join(lines)
    m = re.search(r"https?://\S+", text)
    if not m:
        raise NewsletterError(f"seção '{what}' sem URL")
    url = m.group(0).rstrip(".,;")
    rest = (text[:m.start()] + text[m.end():]).strip()
    rest = re.sub(r"\s*(Ouça em|Comece em|Ouça:|Ouça)\s*$", "", rest).strip()
    return rest, url


def with_utm(url: str, medium: str, content: str, term: str) -> str:
    u = urlparse(url)
    q = dict(parse_qsl(u.query))
    q.setdefault("utm_source", "newsletter")
    q["utm_medium"] = medium
    q.setdefault("utm_campaign", "rota-da-semana")
    q["utm_content"] = content
    q["utm_term"] = term
    return urlunparse(u._replace(query=urlencode(q)))


def label_split(line: str):
    """'**Rótulo:** texto' → (rótulo, texto); 'Decisão (opinião editorial): …' mantém o parêntese no rótulo."""
    m = re.match(r"^\*\*(.+?)\*\*\s*(\([^)]*\))?\s*[:.]?\s*(.*)$", line)
    if not m:
        return None
    label = m.group(1).strip().rstrip(":.").strip()
    if m.group(2):
        label += " " + m.group(2)
    return label, m.group(3).strip()


def cap(text: str) -> str:
    return text[:1].upper() + text[1:] if text else text


def edition_number(ep_dir: Path) -> int:
    root = ep_dir.parent
    eps = sorted(d.name for d in root.iterdir() if d.is_dir() and (d / "roteiro.txt").exists())
    return eps.index(ep_dir.name) + 1 if ep_dir.name in eps else 1


# ---------------------------------------------------------------- inline

LINK = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")


def inline_html(text: str) -> str:
    out, pos = [], 0
    def fmt(chunk):
        chunk = html.escape(chunk, quote=False)
        chunk = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", chunk)
        chunk = re.sub(r"(?<!\*)\*([^*\s][^*]*?)\*(?!\*)", r"<i>\1</i>", chunk)
        return re.sub(r"(?<![\"'>=])(https?://[^\s<)]+[^\s<).,;])",
                      r'<a href="\1" class="dark-link" style="color:#005049;text-decoration:underline;">\1</a>', chunk)
    for m in LINK.finditer(text):
        out.append(fmt(text[pos:m.start()]))
        out.append(f'<a href="{html.escape(m.group(2), quote=True)}" class="dark-link" style="color:#005049;text-decoration:underline;">'
                   f'{html.escape(m.group(1), quote=False)}</a>')
        pos = m.end()
    out.append(fmt(text[pos:]))
    return "".join(out)


def inline_text(text: str) -> str:
    text = LINK.sub(r"\1 <\2>", text)
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    return re.sub(r"(?<!\*)\*([^*\s][^*]*?)\*(?!\*)", r"\1", text)


# ---------------------------------------------------------------- HTML

CSS = """
    body, table, td, p, a, li { -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; }
    table, td { mso-table-lspace: 0pt; mso-table-rspace: 0pt; }
    img { -ms-interpolation-mode: bicubic; border: 0; outline: none; text-decoration: none; }
    body { margin: 0; padding: 0; width: 100% !important; height: 100% !important; }
    :root { color-scheme: light dark; supported-color-schemes: light dark; }
    @media (prefers-color-scheme: dark) {
      .dark-bg-body { background-color: #1a1c1c !important; }
      .dark-bg-surface { background-color: #2a2c2c !important; }
      .dark-bg-card { background-color: #333636 !important; }
      .dark-text { color: #e8e8e8 !important; }
      .dark-text-secondary { color: #b0b0b0 !important; }
      .dark-text-muted { color: #9a9a9a !important; }
      .dark-border { border-color: #4a4c4c !important; }
      .dark-bg-navy { background-color: #040d1b !important; }
      .dark-bg-warning { background-color: #3d2e00 !important; }
      .dark-text-warning { color: #fbbf24 !important; }
      .dark-bg-khartos { background-color: #040d1b !important; }
      .dark-link { color: #6fd3c8 !important; }
    }
    @media only screen and (max-width: 480px) {
      .mobile-full { width: 100% !important; max-width: 100% !important; }
      .mobile-padding { padding-left: 20px !important; padding-right: 20px !important; }
      .mobile-font-base { font-size: 17px !important; line-height: 27px !important; }
      .mobile-font-h1 { font-size: 26px !important; line-height: 32px !important; }
      .mobile-font-h2 { font-size: 21px !important; line-height: 28px !important; }
      .mobile-font-h3 { font-size: 18px !important; line-height: 24px !important; }
      .mobile-hide { display: none !important; }
      .mobile-btn-full { display: block !important; width: 100% !important; text-align: center !important; }
    }
"""


def _p(text, size=16, lh=26, color="#1a1c1c", mb=0, cls="mobile-font-base dark-text", weight=""):
    w = f"font-weight:{weight};" if weight else ""
    return (f'<p style="margin:0 0 {mb}px 0;font-family:{FONT_BODY};font-size:{size}px;line-height:{lh}px;{w}'
            f'color:{color};" class="{cls}">{text}</p>')


def _row(inner, top=0, bottom=0):
    return (f'<tr><td style="padding:{top}px 40px {bottom}px 40px;" class="mobile-padding">{inner}</td></tr>')


def _section_title(text, top=32, mb=16):
    return _row(
        '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>'
        '<td style="border-top:2px solid #1c9a8e;padding-top:24px;">'
        f'<h2 style="margin:0 0 {mb}px 0;font-family:{FONT_SERIF};font-size:24px;line-height:30px;font-weight:400;'
        f'color:#1a1c1c;" class="mobile-font-h2 dark-text">{html.escape(text)}</h2></td></tr></table>', top=top)


def _card(label, text, top=16):
    lab = _p(html.escape(label), size=13, lh=18, color="#75777d", mb=4, cls="dark-text-muted", weight="700")
    lab = lab.replace("margin:0 0 4px 0;", "margin:0 0 4px 0;text-transform:uppercase;letter-spacing:0.3px;")
    return _row(
        '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>'
        f'<td style="background-color:#f3f3f3;border-radius:8px;padding:16px 20px;" class="dark-bg-card">{lab}'
        f'{_p(inline_html(cap(text)))}</td></tr></table>', top=top)


def _tags(body):
    tags = []
    if re.search(r"fonte oficial", body, re.I):
        tags.append("Confirme na fonte oficial")
    if re.search(r"estimativa", body, re.I):
        tags.append("Estimativa")
    return "".join(
        '<table role="presentation" cellpadding="0" cellspacing="0" border="0" style="margin:0 8px 8px 0;display:inline-block;">'
        '<tr><td style="background-color:#fffbeb;border-radius:4px;padding:4px 10px;" class="dark-bg-warning">'
        f'{_p(html.escape(t), size=12, lh=16, color="#904d00", cls="dark-text-warning", weight="700")}</td></tr></table>'
        for t in tags)


def _button(url, label):
    u = html.escape(url, quote=True)
    return (
        '<table role="presentation" cellpadding="0" cellspacing="0" border="0" style="margin:0 auto;" align="center" '
        'class="mobile-btn-full"><tr><td align="center" bgcolor="#fe932c" style="background-color:#fe932c;border-radius:8px;">'
        f'<!--[if mso]><v:roundrect xmlns:v="urn:schemas-microsoft-com:vml" xmlns:w="urn:schemas-microsoft-com:office:word" '
        f'href="{u}" style="height:48px;v-text-anchor:middle;width:240px;" arcsize="17%" stroke="f" fillcolor="#fe932c">'
        f'<w:anchorlock/><center style="color:#040d1b;font-family:\'Segoe UI\',Helvetica,Arial,sans-serif;font-size:16px;'
        f'font-weight:bold;">{html.escape(label)}</center></v:roundrect><![endif]-->'
        f'<!--[if !mso]><!--><a href="{u}" style="display:inline-block;padding:12px 32px;font-family:{FONT_BODY};'
        f'font-size:16px;line-height:24px;font-weight:700;color:#040d1b;text-decoration:none;border-radius:8px;">'
        f'{html.escape(label)}</a><!--<![endif]--></td></tr></table>')


def render_html(ed: dict, *, mode: str, number: int, ep_date: str, subject_idx: int, draft: bool) -> str:
    """mode='email' (marcadores da plataforma) ou 'web' (página pública)."""
    sec = ed["sections"]
    medium = "email" if mode == "email" else "web"
    term = f"edicao-{number}"
    subject = ed["subjects"][subject_idx]
    rows = []

    rows.append(_row(_p(inline_html(" ".join(sec["Abertura"]))), top=32))

    if ed["dest_kind"]:
        kind = ed["dest_kind"]
        rows.append(_section_title(ed["dest_title"]))
        first_card = True
        for line in sec[kind]:
            is_li = bool(re.match(r"^[-*]\s+", line))
            text = re.sub(r"^[-*]\s+", "", line)
            ls = label_split(text)
            if is_li and ls and re.match(r"^Dia \d", ls[0]):
                h3 = (f'<h3 style="margin:0 0 6px 0;font-family:{FONT_BODY};font-size:16px;line-height:22px;'
                      f'font-weight:700;color:#1a1c1c;" class="mobile-font-h3 dark-text">{html.escape(ls[0])}</h3>')
                rows.append(_row(h3 + _p(inline_html(cap(ls[1])), color="#45474c", mb=20, cls="mobile-font-base dark-text-secondary")))
            elif is_li:
                rows.append(_row(_p("&bull;&nbsp;" + inline_html(text), mb=12)))
            elif ls:
                rows.append(_card(ls[0], ls[1], top=0 if first_card else 16))
                first_card = False
            else:
                rows.append(_row(_p(inline_html(text), mb=20)))

    # No podcast (CTA principal)
    pod_text, pod_url = find_url(sec["No podcast"], "No podcast")
    pod_url = with_utm(pod_url, medium, "cta-episodio", term)
    rows.append(_section_title("No podcast", mb=12))
    rows.append(_row(_p(inline_html(pod_text), mb=24) + _button(pod_url, "Ouvir o episódio")))

    # Datas e prazos
    rows.append(_section_title("Datas e prazos", mb=20))
    items = [l for l in sec["Datas e prazos"] if re.match(r"^[-*]\s+", l)]
    for i, line in enumerate(items):
        text = re.sub(r"^[-*]\s+", "", line)
        ls = label_split(text)
        title, body = ls if ls else ("", text)
        inner = ('<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>'
                 '<td style="border-left:3px solid #1c9a8e;padding-left:16px;">'
                 + (_p(html.escape(title), lh=22, mb=4, weight="700") if title else "")
                 + _p(inline_html(cap(body)), size=15, lh=24, color="#45474c", mb=8, cls="dark-text-secondary")
                 + _tags(body) + '</td></tr></table>')
        rows.append(_row(inner, bottom=20 if i < len(items) - 1 else 0))

    # Checklist
    rows.append(_section_title("Checklist da semana", mb=16))
    box = ('<table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr><td style="width:18px;height:18px;'
           'border:2px solid #c5c6cc;border-radius:3px;" class="dark-border">&nbsp;</td></tr></table>')
    cl = [re.sub(r"^[-*]\s+", "", l) for l in sec["Checklist da semana"] if re.match(r"^[-*]\s+", l)]
    trs = "".join(
        f'<tr><td width="28" valign="top" style="padding:3px 0 12px 0;">{box}</td>'
        f'<td valign="top" style="padding:0 0 12px 8px;font-family:{FONT_BODY};font-size:16px;line-height:26px;'
        f'color:#1a1c1c;" class="mobile-font-base dark-text">{inline_html(t)}</td></tr>' for t in cl)
    rows.append(_row('<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">' + trs + '</table>',
                     bottom=24))

    # No Khartos (bloco fixo)
    kh_text, kh_url = find_url(sec["No Khartos"], "No Khartos")
    kh_url = with_utm(kh_url, medium, "cta-khartos", term)
    img = ('<td width="72" valign="top" style="padding-right:16px;" class="mobile-hide">'
           '<!--[if mso]><table role="presentation" cellpadding="0" cellspacing="0" border="0" width="56"><tr>'
           '<td style="width:56px;height:56px;">&nbsp;</td></tr></table><![endif]-->'
           f'<!--[if !mso]><!--><img src="{MARCO_POLO_IMG}" alt="" aria-hidden="true" width="56" height="56" '
           'style="display:block;width:56px;height:56px;border-radius:50%;border:2px solid #1a2332;object-fit:cover;">'
           '<!--<![endif]--></td>')
    khartos = (
        '<table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0" '
        'style="max-width:600px;width:100%;background-color:#040d1b;" class="mobile-full dark-bg-khartos"><tr>'
        '<td style="padding:32px 40px;" class="mobile-padding"><table role="presentation" width="100%" cellpadding="0" '
        f'cellspacing="0" border="0"><tr>{img}<td valign="top">'
        f'<p style="margin:0 0 10px 0;font-family:{FONT_BODY};font-size:13px;line-height:18px;letter-spacing:0.5px;'
        'text-transform:uppercase;color:#1c9a8e;">No Khartos</p>'
        f'<p style="margin:0 0 20px 0;font-family:{FONT_BODY};font-size:15px;line-height:24px;color:#dae3f7;">'
        f'{html.escape(kh_text)}</p>'
        f'<a href="{html.escape(kh_url, quote=True)}" style="display:inline-block;font-family:{FONT_BODY};font-size:15px;'
        'line-height:20px;font-weight:700;color:#fe932c;text-decoration:underline;">Planejar minha viagem &rarr;</a>'
        '</td></tr></table></td></tr></table>')

    # Rodapé
    foot = [_p(inline_html(l), size=13, lh=20, color="#75777d", mb=12, cls="dark-text-muted") for l in sec["Rodapé"]]
    if mode == "email":
        foot.append(_p("Você recebe este e-mail porque se inscreveu na newsletter Rota da Semana. "
                       f'<a href="{UNSUB}" class="dark-link" style="color:#005049;text-decoration:underline;">Descadastrar em um clique</a>',
                       size=13, lh=20, color="#75777d", mb=12, cls="dark-text-muted"))
        foot.append(_p(SENDER, size=13, lh=20, color="#75777d", mb=0, cls="dark-text-muted"))
    else:
        foot.append(_p("Você está lendo a versão web da newsletter Rota da Semana, do podcast do Khartos.",
                       size=13, lh=20, color="#75777d", mb=0, cls="dark-text-muted"))
    footer = ('<table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0" '
              'style="max-width:600px;width:100%;background-color:#eeeeee;" class="mobile-full dark-bg-card"><tr>'
              f'<td style="padding:28px 40px;" class="mobile-padding">{"".join(foot)}</td></tr></table>')

    banner = ""
    if mode == "web" and draft:
        banner = (f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" '
                  f'style="background-color:#fffbeb;"><tr><td align="center" style="padding:6px 16px;font-family:{FONT_BODY};'
                  'font-size:12px;line-height:16px;color:#663500;">Rascunho &middot; aguardando aprovação &middot; '
                  'nada foi enviado</td></tr></table>')
    pre = ""
    if mode == "email":
        pre = ('<span style="display:none !important;font-size:1px;line-height:1px;max-height:0px;max-width:0px;opacity:0;'
               f'overflow:hidden;mso-hide:all;">{html.escape(ed["preview"])}</span>'
               '<span style="display:none !important;font-size:1px;line-height:1px;max-height:0px;max-width:0px;opacity:0;'
               'overflow:hidden;mso-hide:all;">' + "&zwnj;&nbsp;" * 40 + "</span>")
    robots = '<meta name="robots" content="noindex">' if mode == "web" else ""

    return f"""<!DOCTYPE html>
<html lang="pt-BR" xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<meta name="color-scheme" content="light dark">
<meta name="supported-color-schemes" content="light dark">
{robots}
<title>{html.escape(subject)}</title>
<!--[if mso]><noscript><xml><o:OfficeDocumentSettings><o:PixelsPerInch>96</o:PixelsPerInch></o:OfficeDocumentSettings></xml></noscript><![endif]-->
<!--[if !mso]><!--><link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Instrument+Serif&display=swap" rel="stylesheet"><!--<![endif]-->
<style>{CSS}</style>
</head>
<body style="margin:0;padding:0;background-color:#f9f9f9;-webkit-font-smoothing:antialiased;" class="dark-bg-body">
{banner}{pre}
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:#f9f9f9;" class="dark-bg-body"><tr><td align="center" style="padding:0;">
<table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0" style="max-width:600px;width:100%;background-color:#040d1b;" class="mobile-full dark-bg-navy"><tr>
<td style="padding:32px 40px 28px 40px;" class="mobile-padding">
<p style="margin:0 0 16px 0;font-family:{FONT_BODY};font-size:13px;line-height:18px;letter-spacing:0.5px;text-transform:uppercase;color:#1c9a8e;">Rota da Semana &middot; Khartos</p>
<h1 style="margin:0 0 16px 0;font-family:{FONT_SERIF};font-size:30px;line-height:38px;font-weight:400;color:#dae3f7;" class="mobile-font-h1">{html.escape(subject)}</h1>
<p style="margin:0;font-family:{FONT_BODY};font-size:14px;line-height:20px;color:#818a9d;">Semana de {html.escape(ed["period"])} &middot; Edição {number}</p>
</td></tr></table>
<table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0" style="max-width:600px;width:100%;background-color:#ffffff;" class="mobile-full dark-bg-surface">
{chr(10).join(r for r in rows if r)}
</table>
{khartos}
{footer}
</td></tr></table>
</body>
</html>
"""


# ---------------------------------------------------------------- texto simples

def render_text(ed: dict, *, number: int, ep_date: str, subject_idx: int) -> str:
    sec = ed["sections"]
    term = f"edicao-{number}"
    out = ["ROTA DA SEMANA · KHARTOS", ed["subjects"][subject_idx], f"Semana de {ed['period']} · Edição {number}", "",
           inline_text(" ".join(sec["Abertura"])), ""]
    if ed["dest_kind"]:
        out += [ed["dest_title"].upper(), ""]
        for line in sec[ed["dest_kind"]]:
            text = re.sub(r"^[-*]\s+", "", line)
            ls = label_split(text)
            if ls:
                out.append(f"{ls[0]}: {inline_text(ls[1])}")
            else:
                out.append(inline_text(text))
            out.append("")
    pod_text, pod_url = find_url(sec["No podcast"], "No podcast")
    out += ["NO PODCAST", "", inline_text(pod_text), "Ouvir: " + with_utm(pod_url, "email", "cta-episodio", term), "",
            "DATAS E PRAZOS", ""]
    for line in sec["Datas e prazos"]:
        if re.match(r"^[-*]\s+", line):
            ls = label_split(re.sub(r"^[-*]\s+", "", line))
            out += [f"- {ls[0]}: {inline_text(ls[1])}" if ls else "- " + inline_text(re.sub(r"^[-*]\s+", "", line)), ""]
    out += ["CHECKLIST DA SEMANA", ""]
    out += ["[ ] " + inline_text(re.sub(r"^[-*]\s+", "", l)) for l in sec["Checklist da semana"] if re.match(r"^[-*]\s+", l)]
    kh_text, kh_url = find_url(sec["No Khartos"], "No Khartos")
    out += ["", "NO KHARTOS", "", kh_text, with_utm(kh_url, "email", "cta-khartos", term), "", "--"]
    out += [inline_text(l) for l in sec["Rodapé"]]
    out += ["Você recebe este e-mail porque se inscreveu na newsletter Rota da Semana.", f"Descadastrar: {UNSUB}", SENDER, ""]
    return "\n".join(out)


def render_subjects(ed: dict) -> str:
    lines = ["Assuntos (até 60 caracteres; a promessa nos primeiros 40):"]
    lines += [f"{i}. {s}  [{len(s)} caracteres]" for i, s in enumerate(ed["subjects"], 1)]
    lines += ["", f"Pré-visualização [{len(ed['preview'])} caracteres, máximo 90]:", ed["preview"], ""]
    return "\n".join(lines)


def lint(ed: dict, email_html: str) -> list:
    warns = []
    for i, s in enumerate(ed["subjects"], 1):
        if len(s) > 60:
            warns.append(f"assunto {i} tem {len(s)} caracteres (máximo 60)")
    if len(ed["preview"]) > 90:
        warns.append(f"pré-visualização tem {len(ed['preview'])} caracteres (máximo 90)")
    kb = len(email_html.encode("utf-8")) / 1024
    if kb > 80:
        warns.append(f"HTML de e-mail com {kb:.0f} KB (Gmail recorta acima de 102 KB; meta: até 80 KB)")
    return warns


# ---------------------------------------------------------------- principal

def build(ep_dir: Path, out: Path | None, site: Path | None, subject_idx: int) -> list:
    ed = parse((ep_dir / "newsletter.md").read_text(encoding="utf-8"))
    number, ep_date = edition_number(ep_dir), ep_dir.name
    approved = (ep_dir / APROVADA).exists()
    email_html = render_html(ed, mode="email", number=number, ep_date=ep_date, subject_idx=subject_idx, draft=not approved)
    web_html = render_html(ed, mode="web", number=number, ep_date=ep_date, subject_idx=subject_idx, draft=not approved)
    if out:
        d = out / ep_date
        d.mkdir(parents=True, exist_ok=True)
        (d / "email.html").write_text(email_html, encoding="utf-8")
        (d / "email.txt").write_text(render_text(ed, number=number, ep_date=ep_date, subject_idx=subject_idx), encoding="utf-8")
        (d / "email-assunto.txt").write_text(render_subjects(ed), encoding="utf-8")
        (d / "web.html").write_text(web_html, encoding="utf-8")
    if site and approved:
        d = site / "newsletter" / ep_date
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(web_html, encoding="utf-8")
    return lint(ed, email_html)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("episodes", nargs="?", default="episodes")
    ap.add_argument("--episodio", help="só esta edição (AAAA-MM-DD)")
    ap.add_argument("--out")
    ap.add_argument("--site")
    ap.add_argument("--assunto", type=int, default=1, choices=[1, 2, 3], help="opção de assunto usada no título (padrão 1)")
    a = ap.parse_args()
    if not a.out and not a.site:
        ap.error("informe --out e/ou --site")
    root = Path(a.episodes)
    dirs = sorted(d for d in root.iterdir() if d.is_dir() and (d / "newsletter.md").exists())
    # Edições com revista.json são geradas por scripts/build_revista.py (a revista substitui o formato curto)
    skipped = [d.name for d in dirs if (d / "revista.json").exists() and not a.episodio]
    dirs = [d for d in dirs if d.name not in skipped]
    for name in skipped:
        print(f"{name}: pulada (a edição tem revista.json; use scripts/build_revista.py)")
    if a.episodio:
        dirs = [d for d in dirs if d.name == a.episodio]
        if not dirs:
            print(f"erro: sem newsletter.md para {a.episodio}", file=sys.stderr)
            return 1
    rc = 0
    for d in dirs:
        try:
            warns = build(d, Path(a.out) if a.out else None, Path(a.site) if a.site else None, a.assunto - 1)
            status = "aprovada" if (d / APROVADA).exists() else "rascunho"
            print(f"{d.name}: ok ({status})")
            for w in warns:
                print(f"  aviso: {w}", file=sys.stderr)
        except NewsletterError as e:
            print(f"{d.name}: ERRO: {e}", file=sys.stderr)
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
