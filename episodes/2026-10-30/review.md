# Revisão editorial — episódio 2026-10-30
**Resultado:** BLOQUEADO (A pendente)
**Ciclos de correção:** 0
**Resumo:** A: 2 (2 pendentes) · B: 32 · C: 22 · Tokens da revisão: ~460 mil (estimado; 5 revisores)

> **Natureza desta revisão: teste do roteamento.** O episódio 1 já está publicado (Release `ep-2026-10-30`), então o resultado "BLOQUEADO" **não afeta nada**: o portão só roda para episódio sem Release ou com `refazer`. Para não alterar texto publicado nem regerar áudio, **nenhum achado foi corrigido** (ciclo = 0). Se o episódio fosse novo, os 2 achados A (copy-chief) impediriam o áudio até serem corrigidos.
> Classes pela **nova definição de A** (A = afirmação factual sem nenhuma fonte; fonte sem data, só secundária ou sem ressalva é B). Os revisores só apontam; as classes são as atribuídas por eles, sem edição. O `brand-strategist` foi reaproveitado da primeira rodada; os demais rodaram nesta.
> Nenhum revisor conseguiu conferir links online (hosts fora da rede permitida). Vários achados se repetem entre revisores (ETIAS, UTM, voo direto, assunto "armadilhas"); foram mantidos por revisor.
> UTM: os achados de links sem UTM na descrição e no resumo do feed são tratados no PR #3; a taxonomia (medium/campaign, `utm_content`, identificador de episódio) é decisão do PO.

## Agentes acionados
| Agente | Papel | Status | Razão (uma linha) |
|---|---|---|---|
| brand-strategist | núcleo fixo | rodou | sempre roda (podcast). Resultado da primeira rodada reaproveitado: mesmos arquivos e mesma definição. |
| copy-chief | núcleo fixo | rodou | sempre roda (podcast). Reclassificou os achados pela nova definição de A. |
| marketing-cmo | núcleo fixo | rodou | sempre roda (newsletter), com escopo só na `newsletter.md`. |
| competitive-intelligence | sob demanda | rodou | rankings, tarifas e rotas de terceiros (Braztoa, Kayak, Booking, Latam, Gol) são fato central. |
| marketing-analytics | sob demanda | rodou | primeiro episódio define links com UTM (cartão, feed, newsletter). |
| content-seo-strategist | sob demanda | limite | critério atendido (destino novo; assunto promete "armadilhas"), mas o teto de 5 revisores foi atingido; prioridade menor. |
| growth-performance | sob demanda | dispensado | cartão e CTA seguem o padrão gerado por `build_feed.py`; sem mudança de oferta. |
| social-media-strategist | sob demanda | dispensado | sem material para redes sociais no episódio. |

## Achados A e B
| ID | Classe | Revisor | Arquivo — trecho (máx. 15 palavras) | Motivo | Status |
|---|---|---|---|---|---|
| 1 | A | copy-chief | roteiro.txt — "Os espetáculos pagos têm ingresso à parte, vendido no site oficial" | Sem nenhuma fonte: não atribuído no áudio, ausente das notas (reclassificado B→A). | pendente |
| 2 | A | copy-chief | roteiro.txt — "quinze anos da Orquestra Sinfônica de Gramado, com cerca de quarenta músicos e oito solistas" | Números sem nenhuma fonte: não atribuídos no áudio, ausentes das notas (reclassificado B→A). | pendente |
| 3 | B | brand-strategist | roteiro.txt — "o orçamento do evento é de quarenta e um milhões de reais" | Bloco 1 (~1.270 palavras) acumula orçamento, visitas, LED, tarifas e ônibus: soa como noticiário, não "histórias e cenas". | pendente |
| 4 | B | brand-strategist | roteiro.txt — "A jangada até as piscinas custa de sessenta a sessenta e cinco reais por adulto" | Marco Polo lê a matéria e quase não conta cena; o guia perde a voz própria (vale também para os rankings do Bloco 2). | pendente |
| 5 | B | copy-chief | roteiro.txt — "um destino do Caribe que ganhou voo direto de São Paulo" | Fontes dizem "planejava" e "listou"; o texto afirma como realidade (fato mais firme que a fonte). | pendente |
| 6 | B | copy-chief | notas.md / newsletter.md — "o novo voo direto para Punta Cana" | Notas hedgeiam, newsletter não; fato mais firme que a fonte. | pendente |
| 7 | B | copy-chief | roteiro.txt — "A jangada até as piscinas custa de sessenta a sessenta e cinco reais" | Fonte citada (Jovem Pan, 11/06/2026), sem ressalva de que o preço pode ter mudado. | pendente |
| 8 | B | copy-chief | roteiro.txt — "O ônibus executivo da linha cento e noventa e cinco custa cerca de vinte e cinco reais" | Mesma fonte; sem ressalva de variação. | pendente |
| 9 | B | copy-chief | roteiro.txt — "O escritório de imigração BAL informou que a União Europeia aponta o início" | Fonte nomeada, sem data do artigo no áudio e nas notas (fonte sem data). | pendente |
| 10 | B | copy-chief | roteiro.txt — "O Jornal do Comércio, de Porto Alegre, informa que o orçamento" | Fonte nomeada, sem data da publicação (fonte sem data). | pendente |
| 11 | B | copy-chief | roteiro.txt — "o mesmo site independente fala em vinte euros por autorização" | Valor só de site independente (ETIAS Answers), não nomeado no áudio; o portal oficial seria a fonte primária. | pendente |
| 12 | B | copy-chief | newsletter.md — "sites independentes estimam algo em torno de abril de 2027" | Fonte é um único site; plural incorreto e link do portal oficial não traz a estimativa. | pendente |
| 13 | B | copy-chief | newsletter.md — "Dica de economia: misture espetáculos pagos com as atrações gratuitas do Natal Luz" | Newsletter repete dicas, horários, Anac e ETIAS do episódio, com pouca informação nova. | pendente |
| 14 | B | copy-chief | scripts/build_feed.py — "Conheça: https://khartos.com" | Resumo em texto simples sem UTM, inconsistente com o cartão (tratado no PR #3). | pendente |
| 15 | B | copy-chief | roteiro.txt — "as regras novas da Anac exigem comprovação para pedir reembolso" | Fechamento generaliza; a fonte limita a comprovação a situações excepcionais (reclassificado C→B). | pendente |
| 16 | B | copy-chief | roteiro.txt / notas.md — Anac sem link primário | Só fonte secundária (Panrotas) para regra da própria Anac (reclassificado C→B). | pendente |
| 17 | B | copy-chief | newsletter.md — "O Natal Luz de Gramado, sem cair nas armadilhas" | Assunto promete mais do que o corpo demonstra: hype não sustentado (reclassificado C→B). | pendente |
| 18 | B | marketing-cmo | newsletter.md — "sites independentes estimam algo em torno de abril de 2027" | Fonte sem nome e sem data; o link do portal da UE não cobre a estimativa (as notas nomeiam as fontes). | pendente |
| 19 | B | marketing-cmo | newsletter.md — "Novas regras da Anac… em vigor desde 26/10/2026." | Fonte só secundária (Panrotas) para regra regulatória; a ressalva "confirme na fonte oficial" atenua. | pendente |
| 20 | B | marketing-cmo | newsletter.md — "O Natal Luz de Gramado, sem cair nas armadilhas" | Assunto mais forte do que o conteúdo sustenta (só um "erro comum"). | pendente |
| 21 | B | competitive-intelligence | roteiro.txt — "Latam planejava um voo direto de Guarulhos ... operação esperada a partir de julho" | Plano de jan/2026 dito como "ganhou voo direto"; sem checagem de que opera (INFERENCE dito como FACT). | pendente |
| 22 | B | competitive-intelligence | roteiro.txt — "Latam falou em voos de São Paulo para a Cidade do Cabo" | Anúncio da empresa sem data de início ou status; "falou em" mistura plano e rota ativa (vale para Ushuaia e Gol Rio–Lisboa). | pendente |
| 23 | B | competitive-intelligence | roteiro.txt — "Segundo a CNN Brasil, que citou a plataforma Kayak ... Orlando, Miami, Lisboa, Madrid e Paris" | Ranking de terceiro só por fonte secundária, sem base ou período; sem a ressalva "busca, não compra". | pendente |
| 24 | B | competitive-intelligence | roteiro.txt — "Segundo a CNN Brasil, que reuniu levantamentos da associação de operadoras Braztoa" | Mistura "mais citados", "mais procurados" e "buscas"; sem data do levantamento ("fim do ano passado"). | pendente |
| 25 | B | competitive-intelligence | roteiro.txt — "Maceió ... ficou em primeiro lugar nas férias de verão" | Ranking de operadoras lido como lista fechada, sem base ou período; firmeza demais para fonte única. | pendente |
| 26 | B | competitive-intelligence | newsletter.md — "sites independentes estimam algo em torno de abril de 2027" | Plural sem base (um site, ETIAS Answers); o link é do portal oficial, que não traz a estimativa. | pendente |
| 27 | B | competitive-intelligence | roteiro.txt — "O mesmo site independente fala em vinte euros por autorização" | Taxa de terceiro a confrontar com a fonte oficial; valor de julho/2025 pode ter mudado. | pendente |
| 28 | B | marketing-analytics | scripts/build_feed.py — "utm_source=podcast&utm_medium=rota-da-semana&utm_campaign=audio" | Taxonomia invertida vs. newsletter: medium traz a série e campaign o formato ("audio"). | pendente |
| 29 | B | marketing-analytics | scripts/build_feed.py — "<footer>Um podcast do <a href=\"{KHARTOS_URL}\">Khartos</a>" | Rodapé, cartão e link HTML usam a mesma URL, sem `utm_content`: não se distingue o clique. | pendente |
| 30 | B | marketing-analytics | scripts/build_feed.py — "Planeje a sua próxima viagem como uma expedição no Khartos: https://khartos.com" | Descrição do feed sem UTM: o tráfego do feed cai em direto (tratado no PR #3). | pendente |
| 31 | B | marketing-analytics | scripts/build_feed.py — "Planeje a sua viagem no Khartos. {KHARTOS_PITCH} Conheça: https://khartos.com" | Resumo do episódio sem UTM e diferente da descrição em HTML (tratado no PR #3). | pendente |
| 32 | B | marketing-analytics | newsletter.md — "Ouça em https://podcast.khartos.com/ep/ep-2026-10-30/" | Link da newsletter para o episódio sem UTM; não se mede newsletter→escuta. | pendente |
| 33 | B | marketing-analytics | scripts/build_feed.py — "utm_campaign=audio" | Campaign e medium constantes entre episódios, sem identificador de episódio. | pendente |
| 34 | B | marketing-analytics | scripts/build_feed.py — "utm_source=podcast&utm_medium=rota-da-semana&utm_campaign=audio" | Limitação não explícita: sem analytics próprio; só há numerador (sessões com UTM), sem denominador (ouvintes). | pendente |

<details><summary>C — informativos (22)</summary>

| ID | Classe | Revisor | Arquivo — trecho (máx. 15 palavras) | Motivo | Status |
|---|---|---|---|---|---|
| 35 | C | brand-strategist | roteiro.txt — "Bem-vindos à Rota da Semana, o podcast do Khartos que transforma a sua próxima viagem" | Promessa de produto na abertura, perto de falar como o Khartos; o viajante deixa de ser o sujeito. | registrado |
| 36 | C | brand-strategist | roteiro.txt — "já atravessei desertos, mares e uns bons aeroportos lotados para chegar até aqui" | Autorreferência no primeiro minuto; leve, mas no limite de "poucos eu". | registrado |
| 37 | C | brand-strategist | roteiro.txt — "Ou seja: se chover, o desfile continua, e você não precisa assistir" | "Ou seja:" duas vezes; "bússola" e "aventura" também repetem: começo de bordão. | registrado |
| 38 | C | brand-strategist | roteiro.txt — "O que fazer: guarde todos os comprovantes, tire foto das notas e dos recibos" | Imperativos em série no Bloco 3 e no Fechamento, contra "oferece, não impõe". | registrado |
| 39 | C | brand-strategist | roteiro.txt — "elas começaram a valer na segunda-feira, vinte e seis" | A sigla "Anac" não é explicada pela Nina (explica Etias e Braztoa). | registrado |
| 40 | C | brand-strategist | roteiro.txt — "Chegou a hora do nosso pit stop de avisos. Dois pontos, rápidos e sem drama." | Bloco 3 tem 479 palavras, ~19,8% das 2.422: colado no teto de 20%. | registrado |
| 41 | C | brand-strategist | scripts/build_feed.py — "Planeje a sua próxima viagem como uma expedição no Khartos: https://khartos.com" | Descrição do feed e resumo sem UTM (tratado no PR #3). | registrado |
| 42 | C | brand-strategist | newsletter.md — "O Natal Luz de Gramado, sem cair nas armadilhas" | Assunto promete armadilhas que o corpo não trata; tom levemente alarmista. | registrado |
| 43 | C | brand-strategist | newsletter.md — "Novas regras da Anac para atrasos e cancelamentos: em vigor desde 26/10/2026." | "Datas e prazos" e parte do checklist repetem o Bloco 3 e as notas quase literalmente. | registrado |
| 44 | C | copy-chief | roteiro.txt — "Já fica a sugestão: dá para combinar as duas praias numa viagem só." | Rotulado como sugestão; não é afirmação factual. | registrado |
| 45 | C | copy-chief | roteiro.txt — "hoje, ainda não é preciso pedir o Etias" | Fontes existem; só estilo: presente categórico sem data da checagem. | registrado |
| 46 | C | copy-chief | newsletter.md — "a cidade é conhecida pelo café colonial, pelo fondue e pelo chocolate" | Conhecimento geral de destino; não requer fonte. | registrado |
| 47 | C | copy-chief | newsletter.md — "A Parada de Natal acontece sexta, sábado e domingo, às 15h." | Horário com fonte nas notas; newsletter orienta confirmar no site oficial. | registrado |
| 48 | C | copy-chief | roteiro.txt / notas.md — fontes de jun/2026, jan/2026, jul/2026 e dez/2025 | Datas declaradas; informativo: boa parte do material não é "notícia da semana". | registrado |
| 49 | C | marketing-cmo | newsletter.md — "No primeiro episódio da Rota da Semana" | Dado de série vai desatualizar; considerar formulação neutra. | registrado |
| 50 | C | competitive-intelligence | roteiro.txt — "A jangada ... custa de sessenta a sessenta e cinco reais por adulto em dois mil e vinte e seis" | Fonte única (Jovem Pan, junho/2026); dizer "em junho" e que os valores variam por temporada. | registrado |
| 51 | C | competitive-intelligence | roteiro.txt — "Foi um dos mais citados, junto de Orlando, Paris, Buenos Aires e Santiago" | Lista da Braztoa sem ordem nem números; vale deixar explícito que não é ordenada. | registrado |
| 52 | C | competitive-intelligence | notas.md — "Maceió liderou as férias de verão e Porto de Galinhas ficou entre os destinos nacionais mais citados" | Boa atribuição; indicar o recorte (operadoras, não busca) e que é levantamento de 2025. | registrado |
| 53 | C | competitive-intelligence | newsletter.md — "Datas próximas ao Natal e ao Ano-Novo costumam ser as mais procuradas" | Corretamente marcada como dica geral nossa (HYPOTHESIS); só registro. | registrado |
| 54 | C | marketing-analytics | docs/editorial-guardrails.md — "O link do **cartão** leva `utm_source=podcast`." | Falta um quadro de taxonomia (source, medium, campaign, content) e a regra de quais links levam UTM. | registrado |
| 55 | C | marketing-analytics | newsletter.md — "utm_source=newsletter&utm_medium=email&utm_campaign=rota-da-semana" | Convenção mais próxima do padrão; usar de referência para o cartão. Sem lista nem envio, não há métrica. | registrado |
| 56 | C | marketing-analytics | docs/operacao.md — "Seguir Programa por URL" | Audiência hoje = downloads dos assets das Releases (inclui bots); documentar como proxy. | registrado |

</details>

## Itens para aprovação do PO
- Descrição do produto na newsletter ("No Khartos") e no cartão: confirmar que corresponde ao que o app faz hoje.
- Primeira publicação do feed e da página com a chamada ao Khartos (o episódio 1 fixa o texto-padrão).
- Newsletter: só rascunho; antes de qualquer envio, consentimento (LGPD), descadastro, plataforma e entregabilidade; resolver os B antes de enviar.
- Assunto "sem cair nas armadilhas" (mais forte do que o conteúdo): manter ou trocar pelas opções 1 ou 3.
- Taxonomia de UTM (medium/campaign, `utm_content`, episódio).
