# Revisão editorial — episódio 2026-10-30
**Resultado:** BLOQUEADO (A pendente) · **Ciclos de correção:** 0
**Resumo:** A 1 · B 21 · C 14 · ~400 mil tokens (5 revisores)

> Teste do roteamento: o episódio já está publicado, então nada é bloqueado de fato (o portão só roda sem Release ou com `refazer`); nenhum achado foi corrigido. Com episódio novo, o A impediria o áudio, mesmo vindo só da newsletter.
> Classes pela definição do PO (`CLAUDE.md`). Um achado por trecho; "Revisor" decidiu a classe. Links não conferidos online.

## Agentes acionados
| Agente | Papel | Status | Razão |
|---|---|---|---|
| brand-strategist | núcleo | rodou | podcast (resultado da 1ª rodada) |
| copy-chief | núcleo | rodou | podcast (reclassificou) |
| marketing-cmo | núcleo | rodou | newsletter |
| competitive-intelligence | sob demanda | rodou | vaga do podcast: rankings e tarifas de terceiros |
| content-seo-strategist | sob demanda | rodou | vaga da newsletter: assunto promete "armadilhas" |
| marketing-analytics | sob demanda | limite | UTM; vagas ocupadas (achados no commit 8e56f49) |
| growth-performance | sob demanda | limite | CTA da newsletter; vaga ficou com o content-seo |
| social-media-strategist | sob demanda | dispensado | sem material de redes sociais |

## Achados A e B
| ID | Classe | Revisor | Arquivo — trecho | Motivo | Status |
|---|---|---|---|---|---|
| 1 | A | marketing-cmo | newsletter.md — "sites independentes estimam ... abril de 2027" | ETIAS: site não nomeado; o link da UE não traz a estimativa. Também: copy-chief (B), competitive-intelligence (B). | pendente |
| 2 | B | copy-chief | roteiro.txt — "espetáculos pagos têm ingresso à parte" | Sem fonte (evento). Antes A. | pendente |
| 3 | B | copy-chief | roteiro.txt — "quinze anos da Orquestra Sinfônica de Gramado" | Números sem fonte. Antes A. | pendente |
| 4 | B | copy-chief | roteiro.txt, notas.md, newsletter.md — "o novo voo direto para Punta Cana" | A fonte diz plano; o texto afirma fato. Também: competitive-intelligence. | pendente |
| 5 | B | copy-chief | roteiro.txt — "A jangada ... sessenta a sessenta e cinco reais" | Fonte única, sem ressalva de variação. Também: competitive-intelligence, brand-strategist. | pendente |
| 6 | B | copy-chief | roteiro.txt — "ônibus executivo da linha cento e noventa e cinco" | Sem ressalva de variação de preço. | pendente |
| 7 | B | copy-chief | roteiro.txt — "O escritório de imigração BAL informou" | ETIAS: fonte secundária e sem data do artigo. | pendente |
| 8 | B | copy-chief | roteiro.txt — "O Jornal do Comércio ... informa que o orçamento" | Fonte sem data. | pendente |
| 9 | B | copy-chief | roteiro.txt — "o mesmo site independente fala em vinte euros" | Site não nomeado no áudio; confrontar com o portal da UE. Também: competitive-intelligence. | pendente |
| 10 | B | copy-chief | roteiro.txt — "quem não precisa de visto, como os brasileiros" | Regra de entrada sem data nem fonte; no limite com A. Achado novo. | pendente |
| 11 | B | copy-chief | roteiro.txt — "regras novas da Anac exigem comprovação" | Generaliza; a fonte limita a casos excepcionais. | pendente |
| 12 | B | copy-chief | roteiro.txt, notas.md, newsletter.md — Anac só por Panrotas | Fonte secundária (data presente), sem link da Anac. Também: marketing-cmo. | pendente |
| 13 | B | marketing-cmo | newsletter.md — "[Portal oficial da UE]" | Link sem data; o prazo citado já passou. | pendente |
| 14 | B | marketing-cmo | newsletter.md — "sem cair nas armadilhas" | O assunto promete mais que o corpo. Também: copy-chief, content-seo-strategist, brand-strategist. | pendente |
| 15 | B | content-seo-strategist | newsletter.md — "o seu roteiro de Natal" | Ambíguo: Gramado ou a cidade de Natal. Também: marketing-cmo. | pendente |
| 16 | B | copy-chief | newsletter.md — "Dica de economia: misture espetáculos pagos" | A newsletter repete o episódio. Também: content-seo-strategist, brand-strategist. | pendente |
| 17 | B | copy-chief | scripts/build_feed.py — "Conheça: https://khartos.com" | Feed sem UTM (PR #3). Também: brand-strategist. | pendente |
| 18 | B | brand-strategist | roteiro.txt — "orçamento do evento é de quarenta e um milhões" | Bloco 1 soa como noticiário; o guia perde a voz. | pendente |
| 19 | B | competitive-intelligence | roteiro.txt — "Latam falou em voos ... Cidade do Cabo" | Anúncio sem data nem status (vale para Ushuaia e Gol). | pendente |
| 20 | B | competitive-intelligence | roteiro.txt — "CNN Brasil, que citou a plataforma Kayak" | Fonte secundária; falta "busca, não compra". | pendente |
| 21 | B | competitive-intelligence | roteiro.txt — "levantamentos da associação Braztoa" | Mistura "citados", "procurados" e "buscas"; sem data. | pendente |
| 22 | B | competitive-intelligence | roteiro.txt — "Maceió ... primeiro lugar nas férias de verão" | Ranking de operadoras lido como lista fechada. | pendente |

<details><summary>C — informativos (14)</summary>

| ID | Classe | Revisor | Arquivo — trecho | Motivo | Status |
|---|---|---|---|---|---|
| 23 | C | brand-strategist | roteiro.txt — "podcast do Khartos que transforma a sua próxima viagem" | Promessa de produto na abertura. | registrado |
| 24 | C | brand-strategist | roteiro.txt — "já atravessei desertos, mares" | Autorreferência no primeiro minuto. | registrado |
| 25 | C | brand-strategist | roteiro.txt — "Ou seja: se chover, o desfile continua" | "Ou seja:" repetido; começo de bordão. | registrado |
| 26 | C | brand-strategist | roteiro.txt — "guarde todos os comprovantes" | Imperativos em série. | registrado |
| 27 | C | brand-strategist | roteiro.txt — "começaram a valer na segunda-feira, vinte e seis" | "Anac" não é explicada pela Nina. | registrado |
| 28 | C | brand-strategist | roteiro.txt — "pit stop de avisos" | Bloco 3 com ~19,8%, colado no teto de 20%. | registrado |
| 29 | C | copy-chief | roteiro.txt — "Já fica a sugestão" | Rotulado como sugestão; não é fato. | registrado |
| 30 | C | copy-chief | roteiro.txt — "hoje, ainda não é preciso pedir o Etias" | Presente categórico sem a data da checagem. | registrado |
| 31 | C | copy-chief | newsletter.md — "conhecida pelo café colonial, pelo fondue" | Conhecimento geral; marcar como dica. Também: content-seo-strategist. | registrado |
| 32 | C | copy-chief | newsletter.md — "A Parada de Natal ... às 15h." | Horário com fonte nas notas. | registrado |
| 33 | C | copy-chief | roteiro.txt, notas.md — fontes de jun/2026 a dez/2025 | Pouco material é "notícia da semana". | registrado |
| 34 | C | marketing-cmo | newsletter.md — "No primeiro episódio ... Ouça em" | "No podcast" tem 1 frase; o CLAUDE.md pede 2. | registrado |
| 35 | C | competitive-intelligence | roteiro.txt — "um dos mais citados, junto de Orlando" | Lista da Braztoa sem ordem; dizer que não é ordenada. | registrado |
| 36 | C | competitive-intelligence | notas.md — "Maceió liderou as férias de verão" | Indicar o recorte (operadoras) e que é de 2025. | registrado |

</details>

## Decisões do PO
- ETIAS na newsletter: nomear a fonte ou remover a estimativa de abril de 2027.
- Assunto "sem cair nas armadilhas": manter ou trocar.
- Taxonomia de UTM (medium, campaign, `utm_content`, episódio): achados do `marketing-analytics` no commit 8e56f49; o PR #3 cobre só os links sem UTM.
- Newsletter: só rascunho; antes de enviar, LGPD, descadastro, plataforma e os B.
