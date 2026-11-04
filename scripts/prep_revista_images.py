#!/usr/bin/env python3
"""Trata as fotos de uma edição da revista: remove EXIF, corrige orientação e gera duas versões.

Uso: python3 scripts/prep_revista_images.py ORIGINAIS/ episodes/AAAA-MM-DD/revista/img/

Para cada JPG/PNG de entrada grava:
  <nome>.jpg     até 1500 px de largura, qualidade 72, progressivo (web e PDF)
  <nome>-e.jpg   até 900 px de largura, qualidade 70 (e-mail, que mostra 600 px)
Requer Pillow (pip install pillow). Não amplia imagens menores que o limite.
"""
import sys
from pathlib import Path

from PIL import Image, ImageOps


def save(img: Image.Image, path: Path, width: int, quality: int) -> None:
    im = img.copy()
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    im.save(path, "JPEG", quality=quality, optimize=True, progressive=True)


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    dst.mkdir(parents=True, exist_ok=True)
    n = 0
    for f in sorted(src.iterdir()):
        if f.suffix.lower() not in (".jpg", ".jpeg", ".png"):
            continue
        img = ImageOps.exif_transpose(Image.open(f)).convert("RGB")
        stem = f.stem
        save(img, dst / f"{stem}.jpg", 1500, 72)
        save(img, dst / f"{stem}-e.jpg", 900, 70)
        n += 1
        print(f"{stem}: {(dst / (stem + '.jpg')).stat().st_size // 1024} KB web, {(dst / (stem + '-e.jpg')).stat().st_size // 1024} KB e-mail")
    print(f"{n} fotos tratadas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
