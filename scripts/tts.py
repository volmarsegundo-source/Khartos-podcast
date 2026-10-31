#!/usr/bin/env python3
"""Gera o MP3 de um episódio a partir do roteiro, usando Google Cloud Text-to-Speech.

Uso: python scripts/tts.py episodes/2026-11-02
Lê  <pasta>/roteiro.txt e grava <pasta>/episodio.mp3 (não versionado).

Formato do roteiro (diálogo entre dois apresentadores):
    # Bloco 1 — Visão geral          <- marcador de seção (não é falado; gera pausa longa)
    MARCO POLO: texto da fala...
    NINA: texto da fala...
Linhas sem rótulo continuam a fala anterior. Um roteiro sem nenhum rótulo é lido
inteiro por uma única voz (modo narrador, compatível com os episódios antigos).

Variáveis de ambiente:
  GOOGLE_TTS_API_KEY  chave de API do Google Cloud com a Text-to-Speech API habilitada
  TTS_VOICE_MARCO     voz do MARCO POLO (padrão: pt-BR-Chirp3-HD-Algenib)
  TTS_VOICE_NINA      voz da NINA       (padrão: pt-BR-Chirp3-HD-Aoede)
  TTS_VOICE           voz do modo narrador (padrão: igual à do MARCO POLO)
  TTS_RATE            velocidade (padrão: 1.0)
"""
import base64
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

MAX_BYTES = 4500  # limite da API é 5000 bytes por requisição
API = "https://texttospeech.googleapis.com/v1/text:synthesize?key={key}"
SAMPLE_RATE = 24000  # taxa de amostragem do PCM intermediário
PAUSE_TURN = 0.35    # segundos de pausa entre falas
PAUSE_SECTION = 1.4  # segundos de pausa em mudança de bloco

DEFAULT_VOICES = {
    "MARCO POLO": "pt-BR-Chirp3-HD-Algenib",
    "NINA": "pt-BR-Chirp3-HD-Aoede",
}
LABEL = re.compile(r"^\s*(MARCO POLO|NINA)\s*:\s*(.*)$", re.IGNORECASE)


def split_text(text: str, max_bytes: int = MAX_BYTES) -> list[str]:
    """Quebra por parágrafo; se um parágrafo for grande demais, quebra por frase."""
    chunks, cur = [], ""
    pieces = []
    for para in [p.strip() for p in text.split("\n\n") if p.strip()]:
        if len(para.encode()) <= max_bytes:
            pieces.append(para)
            continue
        sent = ""
        for s in para.replace(". ", ".\u0000").split("\u0000"):
            if len((sent + " " + s).encode()) > max_bytes and sent:
                pieces.append(sent.strip())
                sent = s
            else:
                sent = f"{sent} {s}" if sent else s
        if sent:
            pieces.append(sent.strip())
    for p in pieces:
        cand = f"{cur}\n\n{p}" if cur else p
        if len(cand.encode()) > max_bytes and cur:
            chunks.append(cur)
            cur = p
        else:
            cur = cand
    if cur:
        chunks.append(cur)
    return chunks


def parse_script(text: str) -> list[tuple]:
    """Devolve uma lista de ("section", título) e ("turn", locutor, texto)."""
    items: list[tuple] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#"):
            items.append(("section", line.lstrip("#").strip()))
            continue
        m = LABEL.match(line)
        if m:
            items.append(("turn", m.group(1).upper(), m.group(2).strip()))
        elif items and items[-1][0] == "turn":
            items[-1] = ("turn", items[-1][1], f"{items[-1][2]} {line}")
        else:
            items.append(("turn", "", line))  # texto solto, sem rótulo
    return items


def is_dialogue(items: list[tuple]) -> bool:
    return any(i[0] == "turn" and i[1] for i in items)


def synthesize(text: str, key: str, voice: str, rate: float) -> bytes:
    lang = "-".join(voice.split("-")[:2])
    body = {
        "input": {"text": text},
        "voice": {"languageCode": lang, "name": voice},
        "audioConfig": {"audioEncoding": "MP3", "speakingRate": rate},
    }
    data = json.dumps(body).encode()
    for attempt in range(6):
        req = urllib.request.Request(
            API.format(key=key), data=data, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return base64.b64decode(json.load(r)["audioContent"])
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors="replace")[:400]
            if e.code in (429, 500, 502, 503, 504) and attempt < 5:
                wait = 2 ** attempt
                print(f"  HTTP {e.code}, nova tentativa em {wait}s", flush=True)
                time.sleep(wait)
                continue
            raise RuntimeError(f"Google TTS HTTP {e.code} (voz {voice}): {detail}") from None
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt < 5:
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError(f"Google TTS inacessível: {e}") from None
    raise RuntimeError("Google TTS: tentativas esgotadas")


def mp3_to_pcm(mp3: bytes) -> bytes:
    """Decodifica MP3 para PCM s16le mono na taxa padrão."""
    return subprocess.run(
        ["ffmpeg", "-loglevel", "error", "-i", "pipe:0", "-ac", "1", "-ar", str(SAMPLE_RATE),
         "-f", "s16le", "pipe:1"],
        input=mp3, capture_output=True, check=True).stdout


def silence(seconds: float) -> bytes:
    return b"\x00\x00" * int(SAMPLE_RATE * seconds)


def encode(pcm: bytes, out: Path) -> None:
    """Normaliza o volume (padrão de podcast, mono) e grava o MP3 final."""
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "s16le", "-ar", str(SAMPLE_RATE), "-ac", "1",
         "-i", "pipe:0", "-af", "loudnorm=I=-19:TP=-1.5:LRA=11", "-ar", "44100", "-ac", "1",
         "-b:a", "64k", str(out)],
        input=pcm, check=True)


def voices_from_env() -> dict[str, str]:
    narrator = os.environ.get("TTS_VOICE") or os.environ.get("TTS_VOICE_MARCO") or DEFAULT_VOICES["MARCO POLO"]
    return {
        "MARCO POLO": os.environ.get("TTS_VOICE_MARCO") or DEFAULT_VOICES["MARCO POLO"],
        "NINA": os.environ.get("TTS_VOICE_NINA") or DEFAULT_VOICES["NINA"],
        "": narrator,
    }


def main() -> None:
    folder = Path(sys.argv[1])
    text = (folder / "roteiro.txt").read_text(encoding="utf-8").strip()
    key = os.environ["GOOGLE_TTS_API_KEY"]
    rate = float(os.environ.get("TTS_RATE") or "1.0")
    voices = voices_from_env()

    items = parse_script(text)
    dialogue = is_dialogue(items)
    if not dialogue:  # modo narrador: texto corrido, uma voz
        items = [("turn", "", c) for c in split_text(text)]

    turns = [i for i in items if i[0] == "turn"]
    spoken = sum(len(i[2]) for i in turns)
    print(f"{spoken} caracteres, {len(turns)} falas, "
          f"{'diálogo' if dialogue else 'narrador'}", flush=True)

    pcm = bytearray()
    prev = None
    for n, item in enumerate(items):
        if item[0] == "section":
            if prev is not None:
                pcm += silence(PAUSE_SECTION)
            prev = "section"
            continue
        _, speaker, content = item
        if prev == "turn":
            pcm += silence(PAUSE_TURN)
        for chunk in split_text(content):
            pcm += mp3_to_pcm(synthesize(chunk, key, voices.get(speaker, voices[""]), rate))
        prev = "turn"
        if n % 20 == 0:
            print(f"  {n}/{len(items)}", flush=True)

    out = (folder / "episodio.mp3").resolve()
    encode(bytes(pcm), out)
    print(f"OK: {out}")


if __name__ == "__main__":
    main()
