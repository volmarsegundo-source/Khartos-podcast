# Rota da Semana — Khartos — guia para o Claude

Podcast semanal do Khartos (app brasileiro de planejamento de viagens, do Volmar, São Paulo), que também serve de porta de entrada para o app: a chamada ao Khartos (página, rodapé e descrições do feed) é gerada automaticamente pelo `build_feed.py`, não precisa constar no roteiro. Toda quinta às 7h47 (America/Sao_Paulo) uma tarefa agendada do Claude pesquisa as notícias de turismo e viagens da semana e envia a este repositório o roteiro do episódio: um bate-papo leve de ~15 minutos entre dois apresentadores virtuais, **MARCO POLO** (o guia explorador do Khartos, que conduz e conta as histórias) e **NINA** (viajante digital, contraponto prático e curiosa). O resto é automático.

Documentação: `README.md` (visão geral), `docs/arquitetura.md` (componentes e limites) e `docs/operacao.md` (configuração, verificação, problemas). Ao mudar o pipeline, atualize esses arquivos no mesmo commit.

## Fluxo

1. **Tarefa agendada "Rota da Semana — pesquisa semanal de turismo"** (cron `47 7 * * 4`, fuso America/Sao_Paulo). O prompt completo fica na própria tarefa. Para mudar escopo, tom, tamanho ou horário, altere a tarefa (update_trigger), não este repositório.
2. A tarefa cria `episodes/AAAA-MM-DD/roteiro.txt`, `episodes/AAAA-MM-DD/notas.md` e `episodes/AAAA-MM-DD/newsletter.md` (rascunho, nunca enviado) e faz push na `main`.
3. O push em `episodes/**` dispara `.github/workflows/episodio.yml`: `scripts/tts.py` gera o áudio (Google Cloud Text-to-Speech, Chirp 3 HD pt-BR, uma voz por locutor), cria a Release `ep-AAAA-MM-DD` com o MP3 e `scripts/build_feed.py` monta `feed.xml`, a página do podcast e uma página por episódio (GitHub Pages).
4. O app Podcasts segue o feed e baixa os episódios novos.

Feed: `https://podcast.khartos.com/feed.xml` · Página: `https://podcast.khartos.com/`

## Tom e estrutura do episódio

**Regra de ouro: o podcast é viagem primeiro, burocracia depois.** Cerca de dois terços da conversa são leves e inspiradores (destinos, o que fazer, dicas); a parte de regras, vistos e saúde é curta, contada com bom humor e sempre termina em "o que fazer". Nada de tom de noticiário pesado.

- **Abertura (curta):** MARCO POLO e NINA se apresentam, citam o período da semana e dão o gostinho do que vem. **Não mencionar no áudio que são apresentadores virtuais nem que as vozes são geradas por IA**: esse aviso já é feito por texto na página do podcast e no rodapé do site.
- **Bloco 1 — Destinos da semana:** 3 a 4 destinos em alta ou muito procurados pelos brasileiros (por tendência de busca, promoções, temporada, eventos, voos novos), e **o que fazer em cada um**: passeios, comida, bairros, melhor época, quanto tempo ficar, uma dica de economia. Histórias e cenas, não lista.
- **Bloco 2 — Bastidores da viagem:** 2 a 3 notícias leves ou úteis (rotas novas, promoções e tarifas, aeroportos, hotéis, experiências, tendências, câmbio e custo de vida em destinos populares).
- **Bloco 3 — Antes de embarcar:** 2 a 3 itens de atenção da semana (mudança de regra de entrada ou visto, alerta de saúde, direitos do passageiro, golpes, legislação), no máximo ~20% do episódio, com o ponto de atenção e o que fazer. Marco Polo preserva o clima de aventura; Nina traduz o "burocratês".
- **Fechamento — O que levar na mala desta semana:** 3 recados práticos (um deles pode ser inspirador) e despedida calorosa.
- Tamanho: 1.900 a 2.600 palavras de roteiro (cerca de 13 a 17 minutos).
- **Marco Polo é host editorial, não porta-voz do Khartos:** fala do mundo, de destinos, prazos e boas práticas de viagem; não apresenta, recomenda, promete nem descreve funcionalidades do Khartos e não convida a usar o app (o CTA fica nos textos de descrição, em voz da marca). Na abertura, no máximo o nome do programa: "Bem-vindos à Rota da Semana, o podcast do Khartos." Sem promessas de marca ("transforma a sua viagem") na fala dele. Ao falar do papel dele fora do app, preferir "acompanha"/"companheiro".
- Marco Polo é um personagem: conta o mundo como um explorador, com histórias e curiosidades de viagem, sem exagero de bordões. Nina pergunta o que o ouvinte perguntaria, explica siglas e termos novos em linguagem simples e traz a visão de quem viaja hoje.
- **Fontes:** citar oralmente a fonte e a data das notícias e das informações factuais (regras, preços, datas, números), com ressalvas (promoção que pode acabar, dado só da empresa, projeção, informação não confirmada). Recomendações de passeios e dicas gerais podem ser apresentadas como tal. Regras de entrada, vistos e saúde: sempre mandar confirmar na fonte oficial antes de viajar; não é aconselhamento jurídico nem médico. Nunca inventar links, preços ou fatos.
- Fecha o episódio uma linha "Os links estão nas notas do episódio, no aplicativo."

## Formatos de arquivo

- **`roteiro.txt` (o gerador de áudio depende disto):** cada fala numa linha que começa com `MARCO POLO: ` ou `NINA: ` (maiúsculas, dois pontos e espaço), linha em branco entre falas, falas de no máximo ~90 palavras. Linhas que começam com `# ` marcam a mudança de bloco (não são faladas; geram pausa longa), por exemplo `# Bloco 1 — Destinos da semana`, `# Bloco 2 — Bastidores da viagem`, `# Bloco 3 — Antes de embarcar`, `# Fechamento — O que levar na mala`. Linhas sem rótulo continuam a fala anterior. Não usar outro tipo de linha.
- **Pronúncia:** as vozes são sintéticas; escrever por extenso o que soaria mal (siglas como se lê, números e anos, valores em reais e dólares por extenso), sem URLs, símbolos nem markdown.
- **`notas.md`:** 1ª linha `# Rota da Semana — semana de DD a DD/MM/AAAA`; uma frase de apresentação; `## Destinos da semana` (item `- **Destino:** o que fazer, melhor época, dica — [Fonte](URL)` quando houver fonte); `## Bastidores da viagem` e `## Antes de embarcar` com itens `- **Título**, data: resumo — [Fonte](URL)`; `## O que levar na mala` com os recados; `## Conceitos explicados` com `- **Termo:** explicação`. Todo link deve ser real. O feed converte o markdown em HTML.

## Rascunho de newsletter (`newsletter.md`)

Aproveita a pesquisa da semana, mas **complementa** o episódio: não copia o roteiro nem as notas. É só um rascunho para o PO revisar; **nada é enviado** (não há lista nem envio automático, e o repositório é público: só conteúdo baseado em fontes públicas). Português do Brasil, **400 a 550 palavras** (leitura de 2 a 3 minutos no celular), tom leve de viagem, sem destaque para tecnologia. A voz é a da **Rota da Semana** (editoria do podcast; "nós" com parcimônia); **o Khartos nunca fala em primeira pessoa** e aparece só no bloco final, em terceira pessoa. Estrutura:
- `# Rascunho — newsletter da semana de DD a DD/MM/AAAA`
- `## Assunto` — 3 opções de assunto (até 60 caracteres; a promessa cabe nos primeiros 40, porque o celular corta; sem clickbait, sem "grátis" como isca) e 1 frase de pré-cabeçalho (até 90 caracteres) que **complementa** o assunto, sem repeti-lo.
- `## Abertura` — 2 a 3 linhas, começando pela situação do leitor (quem vai, quando, o que precisa decidir), sem repetir a abertura do áudio.
- `## Um destino, mais fundo` — um destino do episódio com mais profundidade do que o áudio comporta. Obrigatório: **Dia 1, Dia 2, Dia 3** (sugestão da Rota da Semana, não programa oficial; "confirme com a organização"), **Erro comum** e **Dica de economia**. Opcional, **só com fonte e data**: Onde comer, Melhor época. Sem fonte, o subitem não entra (nada de "dica geral nossa"). Horários, datas e nomes de atrações sempre com fonte e data no texto.
- `## No podcast` — 2 frases (sem repetir a abertura do áudio, sem duração em minutos) e o link do episódio (`https://podcast.khartos.com/ep/ep-AAAA-MM-DD/`). É o **CTA principal** da edição.
- `## Datas e prazos` — até 3 itens (viagem e regras), cada um com fato, [Fonte](URL) e data, ressalva (promoção pode acabar, dado só da empresa, projeção, estimativa) e **uma frase "o que fazer"**. A fonte citada é a que afirma o fato; não colar link "oficial" genérico numa afirmação de terceiro.
- `## Checklist da semana` — 3 a 5 itens, cada um derivado de um bloco desta edição (no máximo 1 item evergreen).
- `## No Khartos` — bloco fixo (até 40 palavras), em terceira pessoa: "No Khartos, a viagem vira uma expedição: você conta como gosta de viajar, recebe o guia do destino, monta o roteiro dia a dia e se prepara com um checklist. O Marco Polo acompanha; a rota é sua." + link `https://khartos.com/?utm_source=newsletter&utm_medium=email&utm_campaign=rota-da-semana`. Sem promessas não comprovadas (preço, "grátis", números de usuários, "o melhor", "não esquecer nada", velocidade, nomes de modelos de IA).
- `## Rodapé` — linhas fixas: "Regras de entrada, vistos e saúde mudam. Confirme sempre na fonte oficial antes de viajar. Este conteúdo não é aconselhamento jurídico nem médico." · "Rota da Semana é o podcast do Khartos. Apresentadores virtuais, com vozes geradas por IA. Fontes e links nas notas do episódio." · `[Fase 2: descadastro em um clique e identificação do remetente]`.
Regras: todo link real; seguro-viagem sem valores em dinheiro e sem afirmar categoricamente "obrigatório" ou "recomendado"; regras de entrada, vistos e saúde sempre com "confirme na fonte oficial"; sem aconselhamento jurídico ou médico; nunca inventar links, preços ou fatos; Marco Polo é companheiro, não porta-voz: não apresenta nem recomenda o Khartos em primeira pessoa (ver C6); no máximo 2 termos cartográficos no e-mail inteiro ("expedição" e "rota" contam).

## Regras

- Episódio com Release existente é ignorado. Para refazer, crie o arquivo vazio `episodes/AAAA-MM-DD/refazer` junto com a correção e dê push: o workflow apaga a Release e a tag, regera o áudio e remove o marcador.
- Nunca commitar MP3 nem chaves. O secret `GOOGLE_TTS_API_KEY` fica em Settings › Secrets and variables › Actions.
- Vozes e velocidade: variáveis do repositório `TTS_VOICE_MARCO` (padrão `pt-BR-Chirp3-HD-Sadaltager`), `TTS_VOICE_NINA` (padrão `pt-BR-Chirp3-HD-Aoede`), `TTS_VOICE` (modo narrador) e `TTS_RATE` (padrão `1.0`).
- O repositório e o site são públicos (Pages gratuito). O feed é listável em diretórios (sem `itunes:block`; dono `hello@khartos.com`, categoria Society & Culture › Places & Travel). Não colocar conteúdo confidencial.
- Custo: ~14 mil caracteres por episódio; o nível gratuito do Google TTS (Chirp 3 HD) é 1 milhão de caracteres por mês, compartilhado com outros podcasts que usem a mesma chave.

## Limitações do ambiente do Claude

- A sessão só acessa o repositório depois de `add_repo` (owner `volmarsegundo-source`, repo `khartos-podcast`, access `push`). Não cria Releases nem apaga, não ativa Pages, não cadastra secrets e não dispara workflows pela API; só o push dispara o workflow.
- A sessão não alcança `github.io` nem `cloudfront.net`: para conferir o feed, abra no navegador.
