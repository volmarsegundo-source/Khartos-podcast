#!/usr/bin/env python3
"""Executa o trecho REAL de .github/workflows/episodio.yml ("Gerar áudio dos episódios novos")
com gh, git e TTS simulados e confere quando o portão da revisão roda.

Garantia testada: episódio que já tem Release (e não tem o marcador `refazer`) NÃO passa pelo
portão nem pelo review.md. Com `refazer` o áudio vai ser regerado, então o portão roda e, se
bloquear, a Release existente fica intacta.
"""
import os
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
STEP = "Gerar áudio dos episódios novos"

A_PENDENTE = """**Resultado:** BLOQUEADO (A pendente)

| ID | Classe | Revisor | Arquivo — trecho | Motivo | Status |
|---|---|---|---|---|---|
| 1 | A | copy-chief | notas.md — "x" | regra de entrada sem a data da regra | pendente |
"""
LIBERADO = "**Resultado:** LIBERADO\n"
A_NEWSLETTER = """**Resultado:** LIBERADO
**Newsletter:** COM A PENDENTE (não usar até corrigir)

| ID | Classe | Revisor | Arquivo — trecho | Motivo | Status |
|---|---|---|---|---|---|
| 1 | A | marketing-cmo | newsletter.md — "x" | regra de entrada sem fonte identificável | pendente |
"""
NAO_EXECUTADA = "**Resultado:** REVISÃO NÃO EXECUTADA\n**Motivo:** ambiente sem os agentes\n"

# nome -> (já tem Release?, refazer?, review.md ou None)
CASOS = {
    "A": (True, False, A_PENDENTE),   # publicado, A pendente, sem refazer  -> portão NÃO roda
    "B": (False, False, A_PENDENTE),  # novo, A pendente                     -> bloqueado
    "C": (False, False, LIBERADO),    # novo, liberado                       -> gera áudio
    "D": (True, True, A_PENDENTE),    # publicado + refazer, A pendente      -> bloqueado, Release intacta
    "E": (True, True, LIBERADO),      # publicado + refazer, liberado        -> apaga e regera
    "F": (True, False, None),         # publicado, sem review.md             -> portão NÃO roda
    "G": (False, False, A_NEWSLETTER),  # novo, A só na newsletter            -> áudio liberado com aviso
    "H": (False, False, A_PENDENTE + A_NEWSLETTER.split("---|\n", 1)[1]),  # novo, A no podcast e na newsletter -> bloqueado
    "I": (False, False, NAO_EXECUTADA),  # novo, revisão não executada         -> áudio liberado com aviso
}


def run_block() -> str:
    wf = yaml.safe_load((REPO / ".github/workflows/episodio.yml").read_text(encoding="utf-8"))
    for job in wf["jobs"].values():
        for step in job["steps"]:
            if step.get("name") == STEP:
                return step["run"]
    raise SystemExit(f"passo '{STEP}' não encontrado")


def exe(path: Path, body: str) -> None:
    path.write_text(body, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IEXEC)


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="gate-loop-"))
    try:
        (tmp / "scripts").mkdir()
        shutil.copy(REPO / "scripts/review_gate.py", tmp / "scripts/review_gate.py")
        (tmp / "scripts/tts.py").write_text(
            'import sys, pathlib\nd = pathlib.Path(sys.argv[1])\n'
            'open("tts.log", "a").write(d.name + "\\n")\n(d / "episodio.mp3").write_text("mp3")\n',
            encoding="utf-8",
        )
        bindir = tmp / "bin"
        bindir.mkdir()
        published = tmp / "published.txt"
        exe(bindir / "gh", f"""#!/bin/bash
P="{published}"
case "$1 $2" in
  "release view") grep -qx "$3" "$P" ;;
  "release delete") echo "delete $3" >> gh.log; grep -vx "$3" "$P" > "$P.n" || true; mv "$P.n" "$P" ;;
  "release create") echo "create $3" >> gh.log; echo "$3" >> "$P" ;;
  *) exit 0 ;;
esac
""")
        exe(bindir / "git", "#!/bin/bash\necho \"git $*\" >> git.log\nexit 0\n")
        published.write_text("", encoding="utf-8")
        for nome, (tem_release, refazer, review) in CASOS.items():
            d = tmp / "episodes" / nome
            d.mkdir(parents=True)
            (d / "roteiro.txt").write_text("MARCO POLO: oi\n", encoding="utf-8")
            (d / "notas.md").write_text(f"# Episódio {nome}\ncorpo\n", encoding="utf-8")
            if refazer:
                (d / "refazer").write_text("", encoding="utf-8")
            if review is not None:
                (d / "review.md").write_text(review, encoding="utf-8")
            if tem_release:
                with open(published, "a", encoding="utf-8") as f:
                    f.write(f"ep-{nome}\n")
        env = dict(os.environ, PATH=f"{bindir}:{os.environ['PATH']}", GITHUB_STEP_SUMMARY=str(tmp / "summary.md"))
        r = subprocess.run(["bash", "-c", run_block()], cwd=tmp, env=env, capture_output=True, text=True)
        if r.returncode != 0:
            print(r.stdout, r.stderr)
            print("FALHA: o passo terminou com erro")
            return 1

        def lines(name):
            p = tmp / name
            return sorted(p.read_text(encoding="utf-8").split()) if p.exists() else []

        tts = lines("tts.log")
        gh = (tmp / "gh.log").read_text(encoding="utf-8").splitlines() if (tmp / "gh.log").exists() else []
        blocked = lines("review-blocked.txt")
        summary = (tmp / "summary.md").read_text(encoding="utf-8") if (tmp / "summary.md").exists() else ""
        esperado = {
            "áudio gerado para": (tts, ["C", "E", "G", "I"]),
            "bloqueados pelo portão": (blocked, ["B", "D", "H"]),
            "Releases apagadas": (sorted(x.split()[1] for x in gh if x.startswith("delete")), ["ep-E"]),
            "Releases criadas": (sorted(x.split()[1] for x in gh if x.startswith("create")), ["ep-C", "ep-E", "ep-G", "ep-I"]),
        }
        ok = True
        for k, (obtido, esp) in esperado.items():
            bom = obtido == esp
            ok &= bom
            print(f"{'OK  ' if bom else 'FALHA'} {k}: {obtido} (esperado {esp})")
        # A e F já tinham Release e não tinham refazer: o portão não pode ter olhado o review.md deles
        for nome in ("A", "F"):
            tocou = f"{nome}:" in summary or f"{nome}: " in summary
            bom = not tocou
            ok &= bom
            print(f"{'OK  ' if bom else 'FALHA'} episódio {nome} (publicado, sem refazer): portão não avaliou ({'avaliou' if tocou else 'sem menção no resumo do job'})")
        for nome, texto in (("G", "**G: newsletter com A pendente**"), ("I", "**I: revisão não executada**")):
            bom = texto in summary
            ok &= bom
            print(f"{'OK  ' if bom else 'FALHA'} episódio {nome}: aviso visível no resumo do job ({'presente' if bom else 'ausente'})")
        bom = "ep-D" in (tmp / "published.txt").read_text(encoding="utf-8").split()
        ok &= bom
        print(f"{'OK  ' if bom else 'FALHA'} episódio D (refazer bloqueado): Release existente intacta")
        return 0 if ok else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
