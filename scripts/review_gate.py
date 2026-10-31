#!/usr/bin/env python3
"""Portão da revisão editorial: lê episodes/AAAA-MM-DD/review.md.

Uso: python scripts/review_gate.py episodes/AAAA-MM-DD

Códigos de saída:
  0   LIBERADO (sem achado A pendente)
  10  BLOQUEADO (achado A pendente no PODCAST: roteiro, notas ou chamada ao Khartos):
      o workflow não gera áudio nem Release
  11  NEWSLETTER COM A PENDENTE (nenhum A no podcast): o áudio é liberado, mas o
      aviso fica visível (anotação e resumo do job) e a newsletter não deve ser
      usada até ser corrigida
  20  REVISÃO NÃO EXECUTADA (sem review.md, ou review.md sem resultado legível):
      NÃO bloqueia, mas emite aviso visível (anotação e resumo do job)

Escopo de cada achado: vem do arquivo da coluna "Arquivo — trecho". `newsletter.md` =
newsletter; qualquer outro arquivo (roteiro.txt, notas.md, scripts/build_feed.py...) =
podcast. Achado que cita arquivos dos dois tipos conta como podcast.

Formato do review.md: ver CLAUDE.md, seção "Revisão editorial".

Classes de achado (decisão do PO, texto literal):
  A (bloqueia): afirmação sobre visto, saúde, regras de entrada ou legislação SEM fonte identificável OU SEM a data da regra.
  B: nos demais temas, ausência de fonte ou de data; também afirmações com fonte citada, mas fraca ou desatualizada.
  C: informativo.
Também são A (decisão do PO), emitidos só pelo núcleo fixo: (a) áudio que cita IA ou
apresentadores virtuais; (b) número de bônus; (c) promessa de tempo; (d) conteúdo
interno do Khartos em texto público. Tom, URL no roteiro e estilo permanecem B.
O portão só conta achados A pendentes do núcleo fixo.
"""
import os
import re
import sys
from pathlib import Path

A_DEF = (
    "A = afirmação sobre visto, saúde, regras de entrada ou legislação SEM fonte identificável "
    "OU SEM a data da regra; ou áudio que cita IA/apresentadores virtuais, número de bônus, "
    "promessa de tempo, conteúdo interno do Khartos em texto público"
)

# Só o núcleo fixo pode bloquear (CLAUDE.md, "Roteamento dos revisores").
CORE = {"brand-strategist", "copy-chief", "marketing-cmo"}


def annotate(level: str, msg: str) -> None:
    print(f"::{level}::{msg}")


def summary(line: str) -> None:
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if path:
        with open(path, "a", encoding="utf-8") as f:
            f.write(line + "\n")


def scope(arquivo_trecho: str) -> str:
    """'newsletter' se todos os arquivos citados são newsletter.md; senão 'podcast'."""
    arquivos = re.split(r"\s+—\s+", arquivo_trecho, maxsplit=1)[0]
    nomes = [n.strip() for n in re.split(r"\s*[,/]\s*", arquivos) if n.strip()]
    return "newsletter" if nomes and all(n == "newsletter.md" for n in nomes) else "podcast"


def pending_a(text: str) -> tuple[int, int, list[str]]:
    """Conta achados A pendentes do núcleo fixo (Classe = A, Status = pendente).

    Retorna (a_no_podcast, a_na_newsletter, revisores_sob_demanda_com_A).
    Um A pendente vindo de agente sob demanda não bloqueia: é tratado como B.
    """
    pod, news, ignorados = 0, 0, []
    for line in text.splitlines():
        cells = [c.strip().lower() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 6 and cells[1] == "a" and cells[-1] == "pendente":
            if cells[2] not in CORE:
                ignorados.append(cells[2])
            elif scope(cells[3]) == "newsletter":
                news += 1
            else:
                pod += 1
    return pod, news, ignorados


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
    pod, news, ignorados = pending_a(text)
    if ignorados:
        annotate("warning", f"{name}: achado A de agente sob demanda ({', '.join(sorted(set(ignorados)))}) tratado como B; só o núcleo fixo bloqueia.")
    if news > 0:
        annotate("warning", f"{name}: newsletter com A pendente ({news}). Não use esta newsletter até corrigir.")
        summary(f"- ⚠️ **{name}: newsletter com A pendente** ({news}); não use esta newsletter até corrigir.")
    if pod > 0 or result.startswith("BLOQUEADO"):
        annotate("error", f"{name}: {pod} achado(s) A pendente(s) no podcast em review.md ({A_DEF}). Áudio e Release NÃO gerados. Corrija o texto, atualize review.md e faça push.")
        summary(f"- ⛔ **{name}: bloqueado pela revisão** ({pod} achado(s) A pendente(s) no podcast); sem áudio e sem Release.")
        return 10
    if news > 0:
        return 11
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
