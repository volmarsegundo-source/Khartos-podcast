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

Nada a fazer. Na quarta, às 7h47, a tarefa roda e entrega os arquivos para revisão. Depois que o PO sobe os arquivos para `episodes/AAAA-MM-DD/` e dá push na `main`, o episódio aparece em poucos minutos no app Podcasts e na página do podcast.

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

## Revista e rascunho de newsletter
Cada episódio traz `episodes/AAAA-MM-DD/newsletter.md`: rascunho curto (mini-guia, datas e prazos, checklist, chamada para o Khartos) para o PO revisar. Edições mais ricas trazem também `revista.json` e fotos em `revista/img/`: a **revista Rota da Semana**, com mais de 15 páginas, fotos com crédito e licença, versão web, PDF A4 e um e-mail de capa que leva a ela. Quando existe `revista.json`, a revista substitui o formato curto daquela edição. **Não há lista de assinantes nem envio.** Antes de qualquer envio real: consentimento explícito (LGPD), descadastro, plataforma de envio e revisão de entregabilidade do domínio (SPF/DKIM/DMARC).

### A revista (`scripts/build_revista.py`)
Fonte única: `episodes/AAAA-MM-DD/revista.json` (edição, e-mail de capa, cadastro das fotos e lista de páginas) e `revista/img/*.jpg`. O formato e o passo a passo de uma edição estão em `docs/revista.md`. O gerador valida a estrutura e falha com mensagem clara em: menos de 15 páginas, bloco ou layout desconhecido, foto sem cadastro, arquivo ausente, foto sem autor, licença ou URL, destaque do e-mail apontando para página inexistente e expressões vetadas ("grátis", "o melhor", "imperdível", "dos sonhos", "transforma").

| Saída (`OUT/newsletter/AAAA-MM-DD/`) | Uso |
|---|---|
| `index.html` | a revista na web: páginas em rolagem, responsivo, modo claro; vira uma folha A4 por página na impressão |
| `revista.pdf` | a mesma revista em A4 (precisa de Chrome; opção `--pdf`) |
| `email.html` | e-mail de capa e destaques com fotos, que leva à revista; sai com `{{unsubscribe_url}}` e `{{identificacao_remetente}}` para trocar na plataforma de envio |
| `email.txt` | versão em texto simples |
| `email-assunto.txt` | 3 opções de assunto e a pré-visualização, com contagem de caracteres |
| `img/` | as fotos usadas (`nome.jpg` para web e PDF, `nome-e.jpg` para o e-mail) |

```bash
python3 scripts/build_revista.py episodes --episodio 2026-11-04 --out /tmp/revista --pdf --base file:///tmp/revista
python3 -m unittest discover -s tests -v
```
`--base` troca a raiz pública dos links e das imagens do e-mail; sem ele, vale `https://podcast.khartos.com`. A pasta de saída espelha a URL pública, então pode ser publicada como está.

### Fotos
Só entram fotos com licença CC0, domínio público, CC BY ou CC BY-SA, do Wikimedia Commons, com autor, licença e página de origem no `revista.json`; o crédito aparece sob cada foto e na página de créditos. `scripts/prep_revista_images.py ORIGINAIS/ episodes/AAAA-MM-DD/revista/img/` remove EXIF e gera as duas versões (precisa de Pillow).

### Publicação
O workflow instala Pillow, baixa as fotos declaradas só por `commons` (`scripts/fetch_revista_photos.py`) e roda os dois geradores em todo push; os rascunhos ficam também no artefato `newsletter` da execução (30 dias). A revista em rascunho vai para uma **prévia** em `https://podcast.khartos.com/newsletter/preview/AAAA-MM-DD/` (faixa de rascunho, `noindex`, sem link em lugar nenhum) para validação visual. Quando a pasta do episódio tem o arquivo vazio **`newsletter.aprovada`**, criado pelo PO após a revisão, ela passa para `https://podcast.khartos.com/newsletter/AAAA-MM-DD/` (com `revista.pdf` e `img/`). O e-mail nunca vai para o site. Uma falha nos geradores não impede a publicação do episódio.

### Domínio e índice
Com a variável de repositório `NEWSLETTER_ROOT` definida (por exemplo `https://newsletter.khartos.com`), os links e as imagens do e-mail de capa, as metatags `og:` e o `canonical` usam esse endereço; sem ela, usam `podcast.khartos.com/newsletter/`. O CI também gera `/newsletter/index.html`, com a lista das edições aprovadas. Passo a passo do domínio: `docs/newsletter-dominio.md`.

### Formato curto (`scripts/build_newsletter.py`)
Para edições sem `revista.json`, o `newsletter.md` gera `email.html`, `email.txt`, `email-assunto.txt` e `web.html`, com as mesmas regras de aprovação. Ele falha com mensagem clara em seção desconhecida ou ausente, marcador de rascunho não reconhecido e assuntos diferentes de 3. `--assunto N` escolhe qual das 3 opções vira o título.
