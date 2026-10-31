# Rota da Semana — Khartos — podcast semanal de viagens

Bate-papo leve de cerca de 15 minutos sobre viagens, com dois apresentadores virtuais (vozes geradas por IA): **Marco Polo**, o guia explorador do Khartos, e **Nina**, viajante digital. Primeiro vêm os destinos em alta e o que fazer neles, depois os bastidores da viagem (rotas, tarifas, tendências) e, em doses curtas, as novidades que mudam o planejamento: vistos, regras de entrada, saúde e direitos do passageiro, sempre com o "o que fazer". As fontes são citadas na conversa e os links ficam nas notas do episódio, no app Podcasts.

Toda quinta-feira às 7h47 (horário de São Paulo) uma tarefa agendada do Claude pesquisa as notícias da semana e envia o roteiro a este repositório; o resto é automático.

**Página do podcast (para compartilhar):** `https://volmarsegundo-source.github.io/khartos-podcast/`
**Feed (para colar no app Podcasts):** `https://volmarsegundo-source.github.io/khartos-podcast/feed.xml`

## Status

| Item | Situação |
|---|---|
| Tarefa agendada "Rota da Semana — pesquisa semanal de turismo" | Ativa, quintas 7h47 (America/Sao_Paulo) |
| Pipeline de áudio, Releases e feed (copiado do radar-ia) | Código pronto; depende da configuração inicial em `docs/operacao.md` (Pages e secret) |
| Primeira execução automática | Pendente: quinta, 05/11/2026 |

## Documentação

| Arquivo | Conteúdo |
|---|---|
| [`CLAUDE.md`](CLAUDE.md) | Guia para o Claude: tom, estrutura e formato do episódio, regras e limitações |
| [`docs/arquitetura.md`](docs/arquitetura.md) | Componentes, fluxo de dados e limites |
| [`docs/operacao.md`](docs/operacao.md) | Configuração inicial, verificação da automação, ajustes e solução de problemas |

## Visão geral

```
Tarefa agendada do Claude (quinta 7h47) ──push──▶ episodes/AAAA-MM-DD/{roteiro.txt, notas.md}
                                                        │
                                      GitHub Actions ◀──┘
                                      1. Google Cloud TTS: uma voz por locutor (MARCO POLO, NINA) → MP3
                                      2. Release "ep-AAAA-MM-DD" (arquivo permanente)
                                      3. GitHub Pages: feed.xml + página do podcast + uma página por episódio
                                                        │
                                      App Podcasts (iPhone / Apple Watch) ◀── segue o feed
```

## Estrutura

```
.github/workflows/episodio.yml   gera áudio, cria Release, publica o feed
scripts/tts.py                   roteiro (diálogo) → MP3 (Google TTS, duas vozes, pausas, ffmpeg)
scripts/build_feed.py            Releases → feed.xml + página do podcast e dos episódios
assets/cover.png                 capa (1400×1400)
episodes/AAAA-MM-DD/             roteiro.txt e notas.md de cada episódio
docs/                            arquitetura e operação
```
