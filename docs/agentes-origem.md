# Origem dos agentes portados

Os 8 agentes de `.claude/agents/` são **portes higienizados de agentes que já existem no Khartos**. Nenhum agente foi criado e nenhum original foi alterado. Este arquivo registra a origem para rastreabilidade; ele não contém conteúdo estratégico.

## Origem
- Repositório: o repositório privado do Khartos (`volmarsegundo-source/khartos`).
- Branch e commit: `marketing-ai-consolidation-v1` @ `a6bdd0c5` (`a6bdd0c594cc20015d735208fc5d0b9579a8c4c4`).
- As 8 definições são idênticas (mesmo hash) nas branches `marketing-ai-team-v1` @ `5f58675e` e `marketing-ai-context-pack-v1` @ `cad6afac`. Nenhuma está na `master` do Khartos.
- Verificação (no repositório privado): `git show origin/marketing-ai-consolidation-v1:.claude/agents/<nome>.md | sha256sum`.

## Tabela (sha256, 12 primeiros caracteres)
| Agente | Original (adaptador) | Original (canônico) | Porte (este repositório) | Papel neste fluxo | Pode emitir |
|---|---|---|---|---|---|
| `brand-strategist` | `9c99675c4887` | `fa19e28b3925` | `a769109793b3` | núcleo fixo (podcast) | A/B/C |
| `copy-chief` | `8a12e9d0e3a7` | `b9014cd93ad7` | `c83bde0f5276` | núcleo fixo (podcast) | A/B/C |
| `marketing-cmo` | `246cfd3dedbf` | `4c812c6e7111` | `6e85d1a3f14a` | núcleo fixo (newsletter) | A/B/C |
| `content-seo-strategist` | `70035ecce4a5` | `3c42cfbe3149` | `b08cd3faabc3` | sob demanda | B/C |
| `growth-performance` | `c30b5ca4f74b` | `0c7b22d6b571` | `d69ccd22f2a5` | sob demanda | B/C |
| `marketing-analytics` | `c244ad014c3a` | `7f5c0c064552` | `473bd99c48a5` | sob demanda | B/C |
| `social-media-strategist` | `cdb6acda021d` | `fd83ae1f00fe` | `a73d932fd052` | sob demanda | B/C |
| `competitive-intelligence` | `26a72b6a35b7` | `4eeab2961723` | `ca0207dcca75` | sob demanda | B/C |

## O que a higienização fez
- Manteve nome, descrição (com palavras proibidas reformuladas), ferramentas, modelo e papel; acrescentou o parágrafo "Neste repositório" com o papel no fluxo editorial.
- Removeu as referências a arquivos internos de governança, skills e artefatos, e a lista "Required skills". As regras de evidência e de claims que valem aqui estão em `docs/editorial-guardrails.md`.
- Reformulou termos que remetem a estratégia interna, sem mudar o papel do agente.
- Acrescentou a regra de revisão: **só aponta, não reescreve**.
- Não portou: qualquer material estratégico, de público ou de negócio, nem o conteúdo dos arquivos internos referenciados. Os 8 agentes são genéricos; nenhum dependia de conteúdo privado para a sua definição.
