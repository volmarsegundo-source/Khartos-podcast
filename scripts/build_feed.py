#!/usr/bin/env python3
"""Monta o site do podcast (feed.xml + index.html) a partir dos episódios baixados.

Uso: python scripts/build_feed.py releases.json site/ https://podcast.khartos.com
releases.json: lista [{tagName, name, body, publishedAt}] (saída do gh release view --json).
Espera os áudios em site/audio/<tagName>.mp3.
"""
import html
import json
import re
import subprocess
import sys
import urllib.parse
from datetime import datetime
from email.utils import format_datetime
from pathlib import Path
from zoneinfo import ZoneInfo

SHOW_TITLE = "Rota da Semana — Khartos"
# Links em texto simples (descrição do feed e resumo dos episódios): mesma taxonomia do cartão, campanha "feed".
KHARTOS_FEED_URL = "https://khartos.com/?utm_source=podcast&utm_medium=rota-da-semana&utm_campaign=feed"
SHOW_DESC = ("Conversa semanal e descontraída sobre viagens com Marco Polo, o guia explorador do Khartos, e Nina, viajante digital: "
             "destinos em alta e o que fazer neles, dicas para economizar e, no meio do papo, as novidades que "
             "mudam a sua viagem (vistos, regras de entrada, saúde e direitos do passageiro). Apresentadores virtuais "
             "(vozes geradas por IA); fontes e links nas notas de cada episódio. "
             f"Planeje a sua próxima viagem como uma expedição no Khartos: {KHARTOS_FEED_URL}")
AUTHOR = "Khartos"
KHARTOS_URL = "https://khartos.com/?utm_source=podcast&utm_medium=rota-da-semana&utm_campaign=audio"
KHARTOS_PITCH = ("Planejar uma viagem não precisa ser planilha e dezenas de abas abertas. No Khartos você percorre a sua "
                 "viagem como uma expedição: conta o que sonha e como gosta de viajar, conhece o destino, monta o roteiro "
                 "dia a dia e se prepara com um checklist. O Marco Polo, o guia do Khartos, acompanha cada etapa, e a "
                 "viagem continua sendo sua: cada viagem é um mapa que você desenha.")
MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto",
         "setembro", "outubro", "novembro", "dezembro"]


def duration(path: Path) -> int:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True).stdout.strip()
    return int(float(out))


def inline(text: str) -> str:
    """Escapa HTML e converte [texto](url), **negrito** e *itálico* em tags."""
    text = html.escape(text, quote=False)
    text = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<a href="\2">\1</a>', text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*([^*\s][^*]*)\*(?!\*)", r"<i>\1</i>", text)
    return text


def md_to_html(text: str, web: bool = False) -> str:
    """Markdown simples → HTML. No feed (web=False) usa só p, b, i, a, ul, li, que o app Podcasts exibe;
    na página web (web=True) os títulos viram <h2>."""
    out, in_list = [], False
    for raw in text.splitlines():
        line = raw.strip()
        if re.match(r"^[-*]\s+", line):
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{inline(re.sub(r'^[-*]\s+', '', line))}</li>")
            continue
        if in_list:
            out.append("</ul>")
            in_list = False
        if not line:
            continue
        m = re.match(r"^#{1,6}\s*(.*)$", line)
        if m:
            out.append(f"<h2>{inline(m.group(1))}</h2>" if web else f"<p><b>{inline(m.group(1))}</b></p>")
        else:
            out.append(f"<p>{inline(line)}</p>")
    if in_list:
        out.append("</ul>")
    return "\n".join(out)


def plain(text: str) -> str:
    """Versão em texto simples (itunes:summary): sem marcação, links viram 'texto (url)'."""
    text = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r"\1 (\2)", text)
    text = re.sub(r"[*#]", "", text)
    return text.strip()


CSS = """
:root{--bg:#f6f7f9;--card:#fff;--ink:#14181f;--mut:#5b6573;--acc:#0b6bcb;--line:#e3e7ec}
@media(prefers-color-scheme:dark){:root{--bg:#0f1318;--card:#171c23;--ink:#eef1f5;--mut:#9aa5b3;--acc:#5aa9ff;--line:#262d37}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif}
main{max-width:760px;margin:0 auto;padding:20px 16px 56px}a{color:var(--acc)}
.hero{display:flex;gap:18px;align-items:center;margin:8px 0 22px}.hero img{width:112px;height:112px;border-radius:18px;flex:none}
h1{font-size:1.6rem;line-height:1.2;margin:0 0 6px}.sub{color:var(--mut);margin:0}
.card{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:18px;margin:16px 0}
.card h2{font-size:1.05rem;margin:0 0 10px}.card h3{margin:0 0 4px;font-size:1.2rem}.meta{color:var(--mut);font-size:.9rem;margin:0 0 12px}
audio{width:100%;margin:6px 0 10px}.row{display:flex;flex-wrap:wrap;gap:8px}
.btn{display:inline-block;border:1px solid var(--line);background:var(--card);color:var(--ink);border-radius:999px;padding:8px 14px;font:inherit;font-size:.92rem;cursor:pointer;text-decoration:none}
.btn.main{background:var(--acc);border-color:var(--acc);color:#fff}.btn:hover{filter:brightness(.96)}
.notes h2{font-size:1.1rem;margin:26px 0 6px;padding-top:14px;border-top:1px solid var(--line)}.notes ul{padding-left:20px}.notes li{margin:7px 0}
.eps a.ep{display:block;text-decoration:none;color:inherit;padding:12px 0;border-top:1px solid var(--line)}.eps a.ep:first-child{border-top:0}
.eps b{display:block}.eps span{color:var(--mut);font-size:.9rem}
footer{color:var(--mut);font-size:.85rem;margin-top:28px}
"""

PLAYER_JS = """
<script>
(function(){
  var a=document.getElementById('player'); if(!a) return;
  var key='pos:'+a.getAttribute('data-id');
  try{var p=parseFloat(localStorage.getItem(key)); if(p>5) a.currentTime=p;}catch(e){}
  a.addEventListener('timeupdate',function(){try{localStorage.setItem(key,a.currentTime)}catch(e){}});
  document.getElementById('back').onclick=function(){a.currentTime=Math.max(0,a.currentTime-15)};
  document.getElementById('fwd').onclick=function(){a.currentTime+=30};
  var sp=[1,1.25,1.5,1.75,2],i=0,b=document.getElementById('speed');
  b.onclick=function(){i=(i+1)%sp.length;a.playbackRate=sp[i];b.textContent=sp[i]+'x'};
})();
function copyText(t,btn){
  var done=function(){var o=btn.textContent;btn.textContent='Copiado!';setTimeout(function(){btn.textContent=o},1600)};
  if(navigator.clipboard){navigator.clipboard.writeText(t).then(done,function(){prompt('Copie:',t)})}else{prompt('Copie:',t)}
}
function nativeShare(t,u){if(navigator.share){navigator.share({title:t,url:u})}else{copyText(u,event.target)}}
</script>
"""


def pt_date(dt: datetime) -> str:
    d = dt.astimezone(ZoneInfo("America/Sao_Paulo"))
    return f"{d.day} de {MESES[d.month - 1]} de {d.year}"


def intro_of(body: str) -> str:
    for line in body.splitlines():
        line = line.strip()
        if line and not line.startswith(("#", "-", "*")):
            return re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", line).replace("**", "")
    return SHOW_DESC


def page(title: str, desc: str, url: str, base: str, inner: str) -> str:
    t, d = html.escape(title, quote=True), html.escape(desc, quote=True)
    return f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex">
<title>{t}</title><meta name="description" content="{d}">
<meta property="og:type" content="website"><meta property="og:title" content="{t}">
<meta property="og:description" content="{d}"><meta property="og:image" content="{base}/cover.png">
<meta property="og:url" content="{url}"><meta name="twitter:card" content="summary">
<link rel="alternate" type="application/rss+xml" title="Rota da Semana — Khartos" href="{base}/feed.xml">
<link rel="icon" href="{base}/cover.png"><style>{CSS}</style></head><body><main>{inner}{PLAYER_JS}
<footer>Um podcast do <a href="{KHARTOS_URL}">Khartos</a>. Apresentadores virtuais (vozes geradas por IA). Conteúdo baseado em notícias públicas, com fontes nas notas de cada episódio.</footer></main></body></html>"""


def khartos_card() -> str:
    return f"""<section class="card"><h2>Transforme essas ideias em viagem no Khartos</h2>
<p style="margin:0 0 12px">{KHARTOS_PITCH}</p>
<div class="row"><a class="btn main" href="{KHARTOS_URL}" target="_blank" rel="noopener">Planejar minha viagem no Khartos</a></div></section>"""


def khartos_notes_html() -> str:
    return (f'<hr><p><strong>Planeje a sua viagem no Khartos.</strong> {KHARTOS_PITCH} '
            f'<a href="{KHARTOS_URL}">Conheça o Khartos</a></p>')


def khartos_notes_plain() -> str:
    return f"\n\nPlaneje a sua viagem no Khartos. {KHARTOS_PITCH} Conheça: {KHARTOS_FEED_URL}"


def subscribe_card(base: str) -> str:
    feed = f"{base}/feed.xml"
    nohttp = feed.replace("https://", "")
    enc = urllib.parse.quote(feed, safe="")
    title = urllib.parse.quote(html.unescape(SHOW_TITLE))
    return f"""<section class="card"><h2>Ouvir no seu app de podcasts</h2>
<p class="meta" style="margin:0 0 8px">iPhone</p><div class="row">
<a class="btn main" href="podcast://{nohttp}">Apple Podcasts</a>
<a class="btn" href="overcast://x-callback-url/add?url={feed}">Overcast</a>
<a class="btn" href="pktc://subscribe/{nohttp}">Pocket Casts</a></div>
<p class="meta" style="margin:14px 0 8px">Android e Samsung</p><div class="row">
<a class="btn main" href="https://antennapod.org/deeplink/subscribe?url={enc}&amp;title={title}">AntennaPod</a>
<a class="btn" href="pktc://subscribe/{nohttp}">Pocket Casts</a>
<a class="btn" href="podcastaddict://{nohttp}">Podcast Addict</a>
<a class="btn" href="playerfm://{nohttp}">Player FM</a></div>
<div class="row" style="margin-top:14px"><button class="btn" onclick="copyText('{feed}',this)">Copiar endereço do feed</button></div>
<p class="meta" style="margin:10px 0 0">Cada botão abre o app no celular, se ele estiver instalado. No Spotify, YouTube Music, Castbox ou qualquer outro app, copie o endereço do feed e use “seguir por URL” / “adicionar por RSS”.</p></section>"""


def player_html(ep: dict) -> str:
    return f"""<audio id="player" data-id="{ep['tag']}" controls preload="none" src="{ep['audio']}"></audio>
<div class="row"><button class="btn" id="back">⏪ 15 s</button><button class="btn" id="fwd">30 s ⏩</button>
<button class="btn" id="speed">1x</button><a class="btn" href="{ep['audio']}" download>Baixar MP3</a></div>"""


def share_html(ep: dict) -> str:
    msg = f"{ep['title']} — {ep['url']}"
    wa = "https://wa.me/?text=" + urllib.parse.quote(msg)
    mail = "mailto:?subject=" + urllib.parse.quote(ep["title"]) + "&body=" + urllib.parse.quote(
        f"{ep['intro']}\n\nOuça e veja as fontes: {ep['url']}")
    return f"""<div class="row" style="margin-top:12px"><button class="btn main" onclick="nativeShare('{html.escape(ep['title'], quote=True)}','{ep['url']}')">Compartilhar</button>
<a class="btn" href="{wa}">WhatsApp</a><a class="btn" href="{mail}">E-mail</a>
<button class="btn" onclick="copyText('{ep['url']}',this)">Copiar link</button></div>"""


def build_site(site: Path, base: str, eps: list) -> None:
    """index.html (página do podcast) e ep/<tag>/index.html (uma página por episódio)."""
    for ep in eps:
        inner = f"""<p><a href="{base}/">← {SHOW_TITLE}</a></p>
<section class="card"><h3>{html.escape(ep['title'])}</h3><p class="meta">{ep['date']} · {ep['mins']} min</p>
{player_html(ep)}{share_html(ep)}</section>
{subscribe_card(base)}
{khartos_card()}
<section class="card notes">{ep['notes_web']}</section>"""
        d = site / "ep" / ep["tag"]
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(page(f"{ep['title']} — Rota da Semana", ep["intro"], ep["url"], base, inner), encoding="utf-8")

    latest = eps[0] if eps else None
    hero = f"""<div class="hero"><img src="{base}/cover.png" alt="Capa do podcast"><div>
<h1>{SHOW_TITLE}</h1><p class="sub">Toda quinta: uma conversa leve de cerca de 15 minutos sobre destinos, roteiros e o que há de novo no mundo das viagens.</p></div></div>"""
    feat = ""
    if latest:
        feat = f"""<section class="card"><p class="meta" style="margin-bottom:4px">Episódio mais recente</p>
<h3><a href="{latest['url']}" style="text-decoration:none;color:inherit">{html.escape(latest['title'])}</a></h3>
<p class="meta">{latest['date']} · {latest['mins']} min</p>{player_html(latest)}{share_html(latest)}
<p style="margin:12px 0 0"><a href="{latest['url']}">Ver notas, fontes e links →</a></p></section>"""
    rows = "".join(f"""<a class="ep" href="{e['url']}"><b>{html.escape(e['title'])}</b><span>{e['date']} · {e['mins']} min</span></a>"""
                   for e in eps)
    inner = f"{hero}{feat}{subscribe_card(base)}{khartos_card()}<section class=\"card eps\"><h2>Todos os episódios</h2>{rows}</section>"
    (site / "index.html").write_text(page(html.unescape(SHOW_TITLE), SHOW_DESC, base + "/", base, inner), encoding="utf-8")


def main() -> None:
    releases = json.loads(Path(sys.argv[1]).read_text())
    site = Path(sys.argv[2])
    base = sys.argv[3].rstrip("/")
    releases.sort(key=lambda r: r["publishedAt"], reverse=True)

    items, eps = [], []
    for r in releases:
        mp3 = site / "audio" / f"{r['tagName']}.mp3"
        if not mp3.exists():
            continue
        url = f"{base}/audio/{mp3.name}"
        pub = datetime.fromisoformat(r["publishedAt"].replace("Z", "+00:00"))
        secs = duration(mp3)
        body = r.get("body") or ""
        notes = md_to_html(body)
        items.append(f"""    <item>
      <title>{html.escape(r['name'])}</title>
      <link>{base}/ep/{r['tagName']}/</link>
      <guid isPermaLink="false">{r['tagName']}</guid>
      <pubDate>{format_datetime(pub)}</pubDate>
      <enclosure url="{url}" length="{mp3.stat().st_size}" type="audio/mpeg"/>
      <itunes:duration>{secs}</itunes:duration>
      <itunes:explicit>false</itunes:explicit>
      <itunes:summary><![CDATA[{plain(body) + khartos_notes_plain()}]]></itunes:summary>
      <description><![CDATA[{notes + khartos_notes_html()}]]></description>
    </item>""")
        eps.append({"tag": r["tagName"], "title": r["name"], "date": pt_date(pub), "mins": max(1, round(secs / 60)),
                    "audio": url, "url": f"{base}/ep/{r['tagName']}/", "intro": intro_of(body),
                    "notes_web": md_to_html(body, web=True)})

    now = format_datetime(datetime.now().astimezone())
    feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{SHOW_TITLE}</title>
    <link>{base}/</link>
    <atom:link href="{base}/feed.xml" rel="self" type="application/rss+xml"/>
    <language>pt-br</language>
    <description>{SHOW_DESC}</description>
    <lastBuildDate>{now}</lastBuildDate>
    <itunes:author>{AUTHOR}</itunes:author>
    <itunes:summary>{SHOW_DESC}</itunes:summary>
    <itunes:image href="{base}/cover.png"/>
    <itunes:category text="Society &amp; Culture"><itunes:category text="Places &amp; Travel"/></itunes:category>
    <itunes:owner><itunes:name>Khartos</itunes:name><itunes:email>hello@khartos.com</itunes:email></itunes:owner>
    <itunes:type>episodic</itunes:type>
    <itunes:explicit>false</itunes:explicit>
{chr(10).join(items)}
  </channel>
</rss>
"""
    (site / "feed.xml").write_text(feed, encoding="utf-8")
    build_site(site, base, eps)
    print(f"feed com {len(items)} episódios")


if __name__ == "__main__":
    main()
