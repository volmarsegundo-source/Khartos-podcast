# Roadmap e pendências

Registro vivo do que está planejado e do que está pendente. Ao concluir um item, mova-o para "Concluído" com a data.

## Pendência para a próxima execução da tarefa agendada

Nenhuma pendência de correção. A correção do episódio de 04/11/2026 (valor do ingresso de Noronha e Baía do Sueste) foi publicada em 18/11/2026: áudio regerado com o marcador `refazer`, notas e newsletter ajustadas, e links de fonte acrescentados (página de dúvidas e atrativos do parque).

### Observações da checagem de 04/11 (informativas)

Não são erros do episódio de 04/11:
- A Resolução ANAC 813/2026 vale desde 26/10/2026, mas o artigo 20 (dever de informar o passageiro) só vale a partir de 25/11/2026. A newsletter e as notas do episódio de 30/10 dizem apenas "em vigor desde 26/10".
- A exigência de passagem de volta para a África do Sul consta no site da South African Tourism, mas não na página da Embaixada da África do Sul no Brasil. O episódio de 04/11 atribui a informação à South African Tourism, o que está certo; vale manter "confirme na fonte oficial".

## Roadmap

### Domínio próprio da newsletter: `newsletter.khartos.com`

**Status: no ar desde 04/11/2026.** O proxy no Cloudflare serve o índice, as edições, os PDFs e as fotos (verificado de fora: 200 em todos, redirecionamento reescrito, POST bloqueado, certificado válido até 31/01/2027). A variável de repositório `NEWSLETTER_ROOT=https://newsletter.khartos.com` foi definida; o e-mail de capa, o `og:` e o `canonical` passam a usar o novo endereço no próximo deploy. Detalhes e rollback em `docs/newsletter-dominio.md`.

**Pendente:**
1. **PO:** ligar *Enforce HTTPS* no Pages do `podcast.khartos.com` (hoje desligado).
2. **Quando quiser indexar no Google:** remover o `noindex` das páginas (em `build_revista.py`).

**Fica para a fase 2 (antes do primeiro envio real):** identidade de envio em subdomínio dedicado (por exemplo `news.khartos.com`), plataforma de envio (a pesquisa recomenda Brevo), opt-in duplo com registro do consentimento, SPF, DKIM e DMARC do subdomínio (corrigindo o `rua` do DMARC, hoje em um Gmail pessoal), descadastro em um clique, política de privacidade com seção sobre a newsletter, formulário de inscrição real e aquecimento do domínio. O formulário "Novidades" da landing em produção é simulado e deve ser removido ou ligado antes de qualquer captação.

### Outros itens

- **Revista semanal pela tarefa agendada:** a próxima execução (quarta, 11/11/2026) é a primeira que já gera `revista.json`. Revisar o resultado e ajustar o `CLAUDE.md` e o prompt da rotina conforme o que faltar.
- **Prompt da rotina:** o texto novo foi entregue ao PO para colar na tela de edição da rotina; enquanto isso, o `CLAUDE.md` prevalece em caso de divergência.
- **Texto público do feed:** `scripts/build_feed.py` ainda diz "Toda quinta"; a tarefa roda às quartas e a publicação é manual. Decidir o texto.
- **Peso das fotos no git:** a edição de 04/11 tem cerca de 11,5 MB de fotos versionadas. As próximas podem ser baixadas só no CI (`commons` no `revista.json`).
- **Fotos mais consistentes:** avaliar a API do Unsplash (exige chave criada pelo PO) como segunda fonte, além do Wikimedia Commons.

## Concluído

- 18/11/2026: episódio de 04/11 corrigido e republicado (`refazer`); episódio de 18/11 publicado; newsletter curta de 18/11 aprovada e publicada em `newsletter.khartos.com/2026-11-18/` (revisada pelo time de marketing: fontes de Santiago trocadas, voz e assunto ajustados). Observação de infraestrutura: o passo "Instalar ffmpeg" estourou 8 minutos duas vezes seguidas; a terceira tentativa passou. Sem o ffmpeg o passo "Montar site" falha por falta do `ffprobe`.
- 18/11/2026: newsletter renomeada para **Guias de Destinos** (era "Rota da Semana" na capa, no cabeçalho, no e-mail e no texto de compartilhamento, e "Guia de Destinos" no singular na home). O podcast continua Rota da Semana. Renomeadas também as edições já publicadas (04/11, 11/11 e 12/11) e as regras do `CLAUDE.md`; `utm_campaign=rota-da-semana` mantido. O rótulo do rodapé do app Khartos (Explorar) passou a "Guias de Destinos" (o link para `newsletter.khartos.com` já existia desde 11/11). **Falta o PO** colar o prompt atualizado na rotina (ver "Prompt da rotina").
- 04/11/2026: gerador da revista, PDF A4, e-mail de capa, prévia pública dos rascunhos e busca de fotos pelo título do Commons (PR 4).
- 04/11/2026: logo corrigida para o ícone Compass do app, botões de compartilhamento no card de cada edição e título da home sem redundância.
- 04/11/2026: domínio `newsletter.khartos.com` no ar (proxy no Cloudflare); logo do Khartos, barra de navegação e botões de compartilhamento na revista.
- 04/11/2026: revista de 04/11 aprovada e publicada; índice das edições aprovadas; suporte a `NEWSLETTER_ROOT`; Worker e runbook do domínio `newsletter.khartos.com` (execução no Cloudflare concluída no mesmo dia).
