#!/usr/bin/env python3
"""Portão da revisão editorial: lê episodes/AAAA-MM-DD/review.md.

Uso: python scripts/review_gate.py episodes/AAAA-MM-DD

Códigos de saída:
  0   LIBERADO (sem achado A pendente)
  10  BLOQUEADO (achado A pendente): o workflow não gera áudio nem Release
  20  REVISÃO NÃO EXECUTADA (sem review.md, ou review.md sem resultado legível):
      NÃO bloqueia, mas emite aviso visível (anotação e resumo do job)

Formato do review.md: ver CLAUDE.md, seção "Revisão editorial".
"""
import os
import re
import sys
from pathlib import Path


def annotate(level: str, msg: str) -> None:
    print(f"::{level}::{msg}")


def summary(line: str) -> None:
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if path:
        with open(path, "a", encoding="utf-8") as f:
            f.write(line + "\n")


# Só o núcleo fixo pode bloquear (CLAUDE.md, "Roteamento dos revisores").
CORE = {"brand-strategist", "copy-chief", "marketing-cmo"}


def pending_a(text: str) -> tuple[int, list[str]]:
    """Conta achados A pendentes do núcleo fixo (Classe = A, Status = pendente).

    Um A pendente vindo de agente sob demanda não bloqueia: é tratado como B.
    Retorna (bloqueantes, revisores_sob_demanda_com_A).
    """
    n, ignorados = 0, []
    for line in text.splitlines():
        cells = [c.strip().lower() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 6 and cells[1] == "a" and cells[-1] == "pendente":
            if cells[2] in CORE:
                n += 1
            else:
                ignorados.append(cells[2])
    return n, ignorados


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    ep = Path(sys.argv[1])
    name = ep.name
    review = ep / "review.md"
    if not review.is_file():
        annotate("warning", f"{name}: revisão editorial NÃO EXECUTADA (sem review.md). O episódio segue sem bloqueio.")
        summary(f"- ⚠️ **{name}: revisão não executada** (sem `review.md`); episódio liberado sem revisão.")
        return 20
    text = review.read_text(encoding="utf-8")
    m = re.search(r"\*\*Resultado:\*\*\s*(.+)", text)
    result = (m.group(1).strip().upper() if m else "")
    n, ignorados = pending_a(text)
    if ignorados:
        annotate("warning", f"{name}: achado A de agente sob demanda ({', '.join(sorted(set(ignorados)))}) tratado como B; só o núcleo fixo bloqueia.")
    if n > 0 or result.startswith("BLOQUEADO"):
        annotate("error", f"{name}: {n} achado(s) A pendente(s) em review.md. Áudio e Release NÃO gerados. Corrija o texto, atualize review.md e faça push.")
        summary(f"- ⛔ **{name}: bloqueado pela revisão** ({n} achado(s) A pendente(s)); sem áudio e sem Release.")
        return 10
    if result.startswith("REVISÃO NÃO EXECUTADA") or result.startswith("REVISAO NAO EXECUTADA"):
        annotate("warning", f"{name}: revisão editorial NÃO EXECUTADA (registrado em review.md). O episódio segue sem bloqueio.")
        summary(f"- ⚠️ **{name}: revisão não executada** (registrado em `review.md`); episódio liberado sem revisão.")
        return 20
    if result.startswith("LIBERADO"):
        summary(f"- ✅ {name}: revisão editorial liberada (sem achado A pendente).")
        return 0
    annotate("warning", f"{name}: review.md sem 'Resultado' legível; tratado como revisão NÃO EXECUTADA. O episódio segue sem bloqueio.")
    summary(f"- ⚠️ **{name}: `review.md` ilegível**; tratado como revisão não executada.")
    return 20


if __name__ == "__main__":
    sys.exit(main())
