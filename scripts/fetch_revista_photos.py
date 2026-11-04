#!/usr/bin/env python3
"""Baixa e confere as fotos da revista a partir do nome do arquivo no Wikimedia Commons.

No revista.json, uma foto pode ser declarada só com o título do arquivo:

  "imagens": {"nor-pico": {"commons": "File:Morro do pico em Fernando de Noronha.jpg",
                           "alt": "…", "legenda": "…"}}

Este script, para cada foto com "commons" cujo arquivo ainda não existe em revista/img/:
  1. consulta a API do Commons e confere a licença (só CC0, domínio público, CC BY e CC BY-SA);
  2. preenche no revista.json o autor ("credito"), a licença ("licenca"), a página de origem ("url") e o "file";
  3. baixa a imagem (1500 px), remove EXIF e grava <id>.jpg (web) e <id>-e.jpg (e-mail) em revista/img/.
Uma foto fora das licenças aceitas ou inexistente derruba o script com mensagem clara. Requer Pillow.

Uso: python3 scripts/fetch_revista_photos.py [episodes] [--episodio AAAA-MM-DD]
No GitHub Actions ele roda antes do gerador; as fotos baixadas ali não precisam ir para o git.
Para achar candidatas: https://commons.wikimedia.org/w/index.php?search=...&ns6=1 (veja cada foto antes de usar).
"""
from __future__ import annotations

import argparse
import html
import io
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://commons.wikimedia.org/w/api.php"
UA = "KhartosPodcastBot/1.0 (https://podcast.khartos.com; hello@khartos.com)"
ALLOWED = re.compile(r"^(CC0|CC[ -]?BY(?:[ -]?SA)?\b|Public domain|PD\b|Domínio público)", re.I)
BLOCKED = re.compile(r"\b(NC|ND)\b|GFDL only|fair use", re.I)
WEB_W, MAIL_W = 1500, 900


class PhotoError(RuntimeError):
    pass


def http_get(url: str, tries: int = 5) -> bytes:
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and i < tries - 1:
                time.sleep(2 * (i + 1))
                continue
            raise PhotoError(f"HTTP {e.code} em {url[:90]}") from e
        except urllib.error.URLError as e:
            if i < tries - 1:
                time.sleep(2)
                continue
            raise PhotoError(f"falha de rede em {url[:90]}: {e.reason}") from e
    raise PhotoError(f"sem resposta de {url[:90]}")


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", text or ""))).strip()


def lookup(title: str) -> dict:
    """Metadados do arquivo no Commons, já com a licença conferida."""
    if not title.startswith("File:"):
        title = "File:" + title
    q = urllib.parse.urlencode({"action": "query", "titles": title, "prop": "imageinfo", "format": "json",
                                "iiprop": "url|size|mime|extmetadata", "iiurlwidth": WEB_W})
    data = json.loads(http_get(f"{API}?{q}"))
    page = next(iter(data["query"]["pages"].values()))
    if "imageinfo" not in page:
        raise PhotoError(f"arquivo não encontrado no Commons: {title}")
    info = page["imageinfo"][0]
    meta = info.get("extmetadata", {})
    lic = clean(meta.get("LicenseShortName", {}).get("value", ""))
    if not lic or BLOCKED.search(lic) or not ALLOWED.search(lic):
        raise PhotoError(f"licença não aceita para {title}: {lic or 'não informada'} (aceitas: CC0, domínio público, CC BY, CC BY-SA)")
    if not info.get("mime", "").startswith("image/"):
        raise PhotoError(f"{title} não é imagem ({info.get('mime')})")
    artist = clean(meta.get("Artist", {}).get("value", "")) or "autor não informado"
    return {"credito": artist, "licenca": lic, "url": info["descriptionurl"],
            "download": info.get("thumburl") or info["url"], "width": info.get("width", 0), "height": info.get("height", 0)}


def write_variants(raw: bytes, dst: Path, stem: str) -> None:
    try:
        from PIL import Image, ImageOps
    except ImportError as e:  # pragma: no cover
        raise PhotoError("Pillow não instalado (pip install pillow)") from e
    img = ImageOps.exif_transpose(Image.open(io.BytesIO(raw))).convert("RGB")
    for name, width, quality in ((f"{stem}.jpg", WEB_W, 72), (f"{stem}-e.jpg", MAIL_W, 70)):
        im = img.copy()
        if im.width > width:
            im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
        im.save(dst / name, "JPEG", quality=quality, optimize=True, progressive=True)


def process(ep_dir: Path, log=print) -> int:
    path = ep_dir / "revista.json"
    rev = json.loads(path.read_text(encoding="utf-8"))
    img_dir = ep_dir / "revista" / "img"
    img_dir.mkdir(parents=True, exist_ok=True)
    changed, n = False, 0
    for iid, im in rev.get("imagens", {}).items():
        title = im.get("commons")
        if not title:
            continue
        file = im.get("file") or f"{iid}.jpg"
        have_meta = all(im.get(k) for k in ("credito", "licenca", "url"))
        if (img_dir / file).exists() and (img_dir / (Path(file).stem + "-e.jpg")).exists() and have_meta:
            continue
        info = lookup(title)
        log(f"  {iid}: {info['licenca']} · {info['credito'][:40]} · {info['width']}x{info['height']}")
        write_variants(http_get(info["download"]), img_dir, Path(file).stem)
        im.update({"file": file, "credito": info["credito"], "licenca": info["licenca"], "url": info["url"]})
        changed, n = True, n + 1
        time.sleep(0.6)  # gentileza com a API do Commons
    if changed:
        path.write_text(json.dumps(rev, ensure_ascii=False, indent=1), encoding="utf-8")
    return n


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("episodes", nargs="?", default="episodes")
    ap.add_argument("--episodio")
    a = ap.parse_args()
    root = Path(a.episodes)
    dirs = sorted(d for d in root.iterdir() if d.is_dir() and (d / "revista.json").exists())
    if a.episodio:
        dirs = [d for d in dirs if d.name == a.episodio]
    rc = 0
    for d in dirs:
        try:
            n = process(d)
            print(f"{d.name}: {n} foto(s) baixada(s)")
        except PhotoError as e:
            print(f"{d.name}: ERRO: {e}", file=sys.stderr)
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
