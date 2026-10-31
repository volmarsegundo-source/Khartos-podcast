# Operação

## Configuração inicial (a fazer uma vez)

1. **Chave do Google Cloud TTS:** pode reutilizar a chave do `radar-ia` (a cota gratuita é compartilhada). Para uma chave nova: console.cloud.google.com › projeto com a **Cloud Text-to-Speech API** ativa › APIs e serviços › Credenciais › Chave de API (restrição de API: somente Text-to-Speech).
2. **Secret:** neste repositório, Settings › Secrets and variables › Actions › New repository secret, nome `GOOGLE_TTS_API_KEY`.
3. **GitHub Pages:** Settings › Pages › Build and deployment › Source: **GitHub Actions**.
   Domínio próprio: Settings › Pages › Custom domain = `podcast.khartos.com` (DNS: `CNAME podcast` → `<conta>.github.io`, sem proxy). A base de todas as URLs do site e do feed é `https://podcast.khartos.com` (definida em `.github/workflows/episodio.yml`).
4. **Primeiro build:** aba Actions › "Gerar episódio e publicar feed" › Run workflow (ou qualquer push em `episodes/**`). Se ficar em "Waiting", aprove o ambiente `github-pages`.
5. **iPhone:** Podcasts › Biblioteca › ⋯ › Seguir Programa por URL › `https://podcast.khartos.com/feed.xml`.
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

## Botões de assinar (página do podcast)
- iPhone: Apple Podcasts, Overcast e Pocket Casts. Android/Samsung: AntennaPod (link https, funciona no navegador), Pocket Casts, Podcast Addict e Player FM (esquemas `podcastaddict://` e `playerfm://` seguidos do feed sem `https://`; conferidos em lista da comunidade, teste num Android antes de divulgar).
- Spotify, YouTube Music e Castbox não têm link por URL de feed: exigem cadastro do programa no diretório deles, e o feed já está liberado (sem `itunes:block`, dono `hello@khartos.com`, categoria Society & Culture › Places & Travel). Depois do cadastro manual, o botão de cada app entra na página. Quem usa esses apps antes disso copia o endereço do feed.

## Chamada para o Khartos (automática)
O `build_feed.py` acrescenta, sem depender do roteiro: o cartão "Transforme essas ideias em viagem no Khartos" (logo depois do bloco "Ouvir no seu app de podcasts") na página inicial e em cada episódio, o link no rodapé, a frase final na descrição do programa e o parágrafo com link no fim das notas de cada episódio no feed (`description` e `itunes:summary`). O texto e o link (com `utm_source=podcast`) ficam nas constantes `KHARTOS_PITCH` e `KHARTOS_URL` do script. Para mudar a mensagem ou a URL, edite essas constantes.
Diretriz de texto: falar da proposta de valor (viajar como expedição, conduzida e com mapa próprio) e não da tecnologia. Evitar afirmações sem comprovação (preço, promoção, "melhor", números de usuários) e manter o nome do guia como Marco Polo.

## Revisão editorial
Cada episódio traz `episodes/AAAA-MM-DD/review.md` (formato em `CLAUDE.md`): achados A (bloqueia), B (alerta) e C (informativo, recolhido) e a seção "Agentes acionados" (quais dos 8 agentes rodaram, foram dispensados ou ficaram de fora por limite). Núcleo fixo: `brand-strategist` e `copy-chief` (podcast) e `marketing-cmo` (newsletter); os demais rodam sob demanda, no máximo 5 revisores por episódio. Só o núcleo fixo pode emitir A. O texto é corrigido em até um ciclo; a revisão só aponta, não reescreve. Regras do roteamento: `CLAUDE.md`.
- **Achado A pendente:** o workflow não gera áudio nem Release (anotação de erro, resumo do job e a execução termina vermelha). Para liberar: corrija o texto, mude o `Status` do achado para `corrigido` e o `Resultado` para `LIBERADO`, e faça push.
- **Revisão não executada** (sem `review.md`, ou `Resultado: REVISÃO NÃO EXECUTADA`): o episódio segue, com aviso na anotação e no resumo do job.
- Episódios já publicados não são reavaliados (exceto com `refazer`).
- Regras de voz, tom e claims: `docs/editorial-guardrails.md`.

## Rascunho de newsletter
Cada episódio traz `episodes/AAAA-MM-DD/newsletter.md`: rascunho complementar (mini-guia, datas e prazos, checklist, chamada para o Khartos) para o PO revisar. Não há lista de assinantes nem envio; o arquivo não vai para o site nem para o feed. Antes de qualquer envio real: consentimento explícito (LGPD), descadastro, plataforma de envio e revisão de entregabilidade do domínio (SPF/DKIM/DMARC).
