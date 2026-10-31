# Rota da Semana — Khartos — guia para o Claude

Podcast semanal do Khartos (app brasileiro de planejamento de viagens com IA, do Volmar, São Paulo). Toda quinta às 7h47 (America/Sao_Paulo) uma tarefa agendada do Claude pesquisa as notícias de turismo e viagens da semana e envia a este repositório o roteiro do episódio: um bate-papo leve de ~15 minutos entre dois apresentadores virtuais, **MARCO POLO** (o guia explorador do Khartos, que conduz e conta as histórias) e **NINA** (viajante digital, contraponto prático e curiosa). O resto é automático.

Documentação: `README.md` (visão geral), `docs/arquitetura.md` (componentes e limites) e `docs/operacao.md` (configuração, verificação, problemas). Ao mudar o pipeline, atualize esses arquivos no mesmo commit.

## Fluxo

1. **Tarefa agendada "Rota da Semana — pesquisa semanal de turismo"** (cron `47 7 * * 4`, fuso America/Sao_Paulo). O prompt completo fica na própria tarefa. Para mudar escopo, tom, tamanho ou horário, altere a tarefa (update_trigger), não este repositório.
2. A tarefa cria `episodes/AAAA-MM-DD/roteiro.txt` e `episodes/AAAA-MM-DD/notas.md` e faz push na `main`.
3. O push em `episodes/**` dispara `.github/workflows/episodio.yml`: `scripts/tts.py` gera o áudio (Google Cloud Text-to-Speech, Chirp 3 HD pt-BR, uma voz por locutor), cria a Release `ep-AAAA-MM-DD` com o MP3 e `scripts/build_feed.py` monta `feed.xml`, a página do podcast e uma página por episódio (GitHub Pages).
4. O app Podcasts segue o feed e baixa os episódios novos.

Feed: `https://volmarsegundo-source.github.io/khartos-podcast/feed.xml` · Página: `https://volmarsegundo-source.github.io/khartos-podcast/`

## Tom e estrutura do episódio

**Regra de ouro: o podcast é viagem primeiro, burocracia depois.** Cerca de dois terços da conversa são leves e inspiradores (destinos, o que fazer, dicas); a parte de regras, vistos e saúde é curta, contada com bom humor e sempre termina em "o que fazer". Nada de tom de noticiário pesado.

- **Abertura (curta):** MARCO POLO e NINA se apresentam, avisam que são apresentadores virtuais com vozes geradas por IA, citam o período da semana e dão o gostinho do que vem.
- **Bloco 1 — Destinos da semana:** 3 a 4 destinos em alta ou muito procurados pelos brasileiros (por tendência de busca, promoções, temporada, eventos, voos novos), e **o que fazer em cada um**: passeios, comida, bairros, melhor época, quanto tempo ficar, uma dica de economia. Histórias e cenas, não lista.
- **Bloco 2 — Bastidores da viagem:** 2 a 3 notícias leves ou úteis (rotas novas, promoções e tarifas, aeroportos, hotéis, experiências, tendências, câmbio e custo de vida em destinos populares).
- **Bloco 3 — Antes de embarcar:** 2 a 3 itens de atenção da semana (mudança de regra de entrada ou visto, alerta de saúde, direitos do passageiro, golpes, legislação), no máximo ~20% do episódio, com o ponto de atenção e o que fazer. Marco Polo preserva o clima de aventura; Nina traduz o "burocratês".
- **Fechamento — O que levar na mala desta semana:** 3 recados práticos (um deles pode ser inspirador) e despedida calorosa.
- Tamanho: 1.900 a 2.600 palavras de roteiro (cerca de 13 a 17 minutos).
- Marco Polo é um personagem: conta o mundo como um explorador, com histórias e curiosidades de viagem, sem exagero de bordões. Nina pergunta o que o ouvinte perguntaria, explica siglas e termos novos em linguagem simples e traz a visão de quem viaja hoje.
- **Fontes:** citar oralmente a fonte e a data das notícias e das informações factuais (regras, preços, datas, números), com ressalvas (promoção que pode acabar, dado só da empresa, projeção, informação não confirmada). Recomendações de passeios e dicas gerais podem ser apresentadas como tal. Regras de entrada, vistos e saúde: sempre mandar confirmar na fonte oficial antes de viajar; não é aconselhamento jurídico nem médico. Nunca inventar links, preços ou fatos.
- Fecha o episódio uma linha "Os links estão nas notas do episódio, no aplicativo."

## Formatos de arquivo

- **`roteiro.txt` (o gerador de áudio depende disto):** cada fala numa linha que começa com `MARCO POLO: ` ou `NINA: ` (maiúsculas, dois pontos e espaço), linha em branco entre falas, falas de no máximo ~90 palavras. Linhas que começam com `# ` marcam a mudança de bloco (não são faladas; geram pausa longa), por exemplo `# Bloco 1 — Destinos da semana`, `# Bloco 2 — Bastidores da viagem`, `# Bloco 3 — Antes de embarcar`, `# Fechamento — O que levar na mala`. Linhas sem rótulo continuam a fala anterior. Não usar outro tipo de linha.
- **Pronúncia:** as vozes são sintéticas; escrever por extenso o que soaria mal (siglas como se lê, números e anos, valores em reais e dólares por extenso), sem URLs, símbolos nem markdown.
- **`notas.md`:** 1ª linha `# Rota da Semana — semana de DD a DD/MM/AAAA`; uma frase de apresentação; `## Destinos da semana` (item `- **Destino:** o que fazer, melhor época, dica — [Fonte](URL)` quando houver fonte); `## Bastidores da viagem` e `## Antes de embarcar` com itens `- **Título**, data: resumo — [Fonte](URL)`; `## O que levar na mala` com os recados; `## Conceitos explicados` com `- **Termo:** explicação`. Todo link deve ser real. O feed converte o markdown em HTML.

## Regras

- Episódio com Release existente é ignorado. Para refazer, crie o arquivo vazio `episodes/AAAA-MM-DD/refazer` junto com a correção e dê push: o workflow apaga a Release e a tag, regera o áudio e remove o marcador.
- Nunca commitar MP3 nem chaves. O secret `GOOGLE_TTS_API_KEY` fica em Settings › Secrets and variables › Actions.
- Vozes e velocidade: variáveis do repositório `TTS_VOICE_MARCO` (padrão `pt-BR-Chirp3-HD-Fenrir`), `TTS_VOICE_NINA` (padrão `pt-BR-Chirp3-HD-Aoede`), `TTS_VOICE` (modo narrador) e `TTS_RATE` (padrão `1.0`).
- O repositório e o site são públicos (Pages gratuito). O feed tem `itunes:block`. Não colocar conteúdo confidencial.
- Custo: ~14 mil caracteres por episódio; o nível gratuito do Google TTS (Chirp 3 HD) é 1 milhão de caracteres por mês, compartilhado com outros podcasts que usem a mesma chave.

## Limitações do ambiente do Claude

- A sessão só acessa o repositório depois de `add_repo` (owner `volmarsegundo-source`, repo `khartos-podcast`, access `push`). Não cria Releases nem apaga, não ativa Pages, não cadastra secrets e não dispara workflows pela API; só o push dispara o workflow.
- A sessão não alcança `github.io` nem `cloudfront.net`: para conferir o feed, abra no navegador.
