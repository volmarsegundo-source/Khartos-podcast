# Operação

## Configuração inicial (a fazer uma vez)

1. **Chave do Google Cloud TTS:** pode reutilizar a chave do `radar-ia` (a cota gratuita é compartilhada). Para uma chave nova: console.cloud.google.com › projeto com a **Cloud Text-to-Speech API** ativa › APIs e serviços › Credenciais › Chave de API (restrição de API: somente Text-to-Speech).
2. **Secret:** neste repositório, Settings › Secrets and variables › Actions › New repository secret, nome `GOOGLE_TTS_API_KEY`.
3. **GitHub Pages:** Settings › Pages › Build and deployment › Source: **GitHub Actions**.
4. **Primeiro build:** aba Actions › "Gerar episódio e publicar feed" › Run workflow (ou qualquer push em `episodes/**`). Se ficar em "Waiting", aprove o ambiente `github-pages`.
5. **iPhone:** Podcasts › Biblioteca › ⋯ › Seguir Programa por URL › `https://volmarsegundo-source.github.io/khartos-podcast/feed.xml`.
6. **Apple Watch:** app Watch no iPhone › Podcasts › Personalizado › ativar o programa.

## Rotina semanal

Nada a fazer. Na quinta, às 7h47, a tarefa roda; poucos minutos depois o episódio aparece no app Podcasts e na página do podcast.

## Verificar a automação (primeira execução: 05/11/2026)

1. Notificação da tarefa chegou.
2. Existe `episodes/AAAA-MM-DD` com `roteiro.txt` e `notas.md` e o commit `Episódio AAAA-MM-DD` na `main`.
3. Actions: "Gerar episódio e publicar feed" terminou com ✓ (3 a 5 minutos).
4. Releases: existe `ep-AAAA-MM-DD` com o MP3.
5. A página e o `feed.xml` mostram o episódio; no app Podcasts, puxe a tela para atualizar.

## Ajustes

- Escopo, tom, tamanho, fontes e horário: altere a tarefa agendada (update_trigger).
- Vozes: variáveis do repositório `TTS_VOICE_MARCO` (padrão `pt-BR-Chirp3-HD-Sadaltager`, voz de sábio; alternativas: `Algenib`, rouca e firme, e `Alnilam`, mais firme), `TTS_VOICE_NINA`, `TTS_RATE` (Settings › Secrets and variables › Actions › Variables).
- Visual da página: `scripts/build_feed.py` (CSS e templates no próprio arquivo).
- Refazer um episódio: crie `episodes/AAAA-MM-DD/refazer` (arquivo vazio) com a correção e dê push.

## Solução de problemas

- **Workflow falha em "Gerar áudio":** confira o secret `GOOGLE_TTS_API_KEY` e se a Text-to-Speech API está ativa e dentro da cota.
- **Fala com a voz errada ou lida em modo narrador:** confira se as linhas começam com `MARCO POLO: ` ou `NINA: `.
- **Episódio não aparece no app:** o Apple Podcasts atualiza por consulta periódica; deixe de seguir e siga de novo por URL.
- **XML do feed quebrado:** `&` no título deve ser `&amp;`.
