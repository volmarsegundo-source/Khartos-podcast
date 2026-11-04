# Roadmap e pendências

Registro vivo do que está planejado e do que está pendente. Ao concluir um item, mova-o para "Concluído" com a data.

## Pendência para a próxima execução da tarefa agendada (quarta, 11/11/2026)

### Corrigir o episódio de 04/11/2026 (já publicado)

A checagem feita em 04/11/2026 achou dois erros no episódio publicado. A revista da mesma edição já está correta.

**Erro 1: valor do ingresso do parque de Noronha.** O áudio, as notas e a newsletter dizem que o site mostra R$ 165 (ou R$ 330) "em outra página". Esse valor veio do briefing e não existe no site. A página de visitação do parque (https://www.parnanoronha.com.br/visitante) mostra R$ 393 e R$ 196,50, citando a Portaria ICMBio nº 4.932, de 15/10/2026. A página de dúvidas (https://www.parnanoronha.com.br/duvidas) ainda mostra R$ 373 e R$ 186,50. A imprensa de turismo relata reajuste de 2,34% em 1º/11/2026 (Brasilturis, 27/10/2026), o que sugere página de dúvidas desatualizada, sem confirmação oficial.

**Erro 2: mergulho na Baía do Sueste.** A matéria do O Tempo (03/11/2026) cita mergulho no Sueste, mas o aviso do parque (https://www.parnanoronha.com.br/atrativos, sem data) diz que o banho e as atividades no mar estão suspensos; só dá para caminhar na areia e observar o mar e o mangue.

**Trocas exatas** (em `episodes/2026-11-04/`):

| Arquivo | Trocar | Por |
|---|---|---|
| `roteiro.txt` | "cento e noventa e seis reais e cinquenta centavos numa página e cento e sessenta e cinco reais em outra" | "cento e noventa e seis reais e cinquenta centavos numa página e cento e oitenta e seis reais e cinquenta centavos em outra" |
| `roteiro.txt` | "No Sueste, o mergulho." | "No Sueste, a matéria cita mergulho, mas o aviso do parque diz que o banho e as atividades no mar estão suspensos, então confira antes de ir." |
| `notas.md` | "R$ 330 e R$ 165 em outra página" | "R$ 373 e R$ 186,50 na página de dúvidas" |
| `notas.md` | "Baía do Sueste, Praia do Cachorro" (em "Atrações citadas") | "Baía do Sueste (o aviso do parque diz que o banho está suspenso), Praia do Cachorro" |
| `newsletter.md` | "R$ 165 em outra" | "R$ 186,50 em outra" |
| `newsletter.md` | "**Dia 3:** mergulho na Baía do Sueste" | "**Dia 3:** Baía do Sueste, onde o aviso do parque diz que o banho está suspenso e só dá para caminhar e observar" |

Depois das trocas, confira que o roteiro continua com 1.900 a 2.600 palavras e sem linhas fora do formato (`python3 -m unittest discover -s tests`).

**Como a tarefa agendada entrega:** a tarefa não faz push. Na próxima execução, além da edição nova, ela deve entregar os três arquivos corrigidos de 04/11 (`roteiro.txt`, `notas.md` e `newsletter.md`) separados dos da edição nova, com o prefixo `2026-11-04-` no nome, e lembrar o PO do passo abaixo.

**Como publicar a correção (PO):** suba os arquivos corrigidos para `episodes/2026-11-04/`, crie o arquivo vazio `episodes/2026-11-04/refazer` e dê push na `main`. O workflow apaga a Release `ep-2026-11-04` e a tag, regera o áudio e remove o marcador. Os ouvintes que já baixaram o episódio ficam com o áudio antigo.

**Outras observações da checagem (não são erros do episódio de 04/11):**
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

- 04/11/2026: gerador da revista, PDF A4, e-mail de capa, prévia pública dos rascunhos e busca de fotos pelo título do Commons (PR 4).
- 04/11/2026: logo corrigida para o ícone Compass do app, botões de compartilhamento no card de cada edição e título da home sem redundância.
- 04/11/2026: domínio `newsletter.khartos.com` no ar (proxy no Cloudflare); logo do Khartos, barra de navegação e botões de compartilhamento na revista.
- 04/11/2026: revista de 04/11 aprovada e publicada; índice das edições aprovadas; suporte a `NEWSLETTER_ROOT`; Worker e runbook do domínio `newsletter.khartos.com` (execução no Cloudflare concluída no mesmo dia).
