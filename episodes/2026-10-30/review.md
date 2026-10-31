# Revisão editorial — episódio 2026-10-30
**Resultado:** LIBERADO
**Revisores:** brand-strategist, copy-chief, marketing-cmo
**Ciclos de correção:** 0
**Resumo:** A: 0 (0 pendentes) · B: 16 · C: 19

> **Natureza desta revisão: teste do mecanismo.** O episódio 1 já está publicado (Release `ep-2026-10-30`). Para não alterar texto publicado nem regerar áudio, **nenhum achado foi corrigido** (ciclo de correção = 0); os B ficam `pendente` como alerta e os C `registrado`. Os revisores só apontam; as classes abaixo são as atribuídas por eles, sem edição.
> Os três revisores foram executados como subagentes genéricos instruídos a ler `.claude/agents/<nome>.md` e `docs/editorial-guardrails.md`, porque este ambiente não registra os agentes do repositório como tipos de subagente. O `copy-chief` não conseguiu conferir links online (hosts fora da rede permitida).
> Pontos para o PO: (1) o texto "afirmação factual sem fonte e data" está na definição de A no `CLAUDE.md`, mas o copy-chief classificou como B os achados 18 e 19 (fonte sem data) e o 16 (ingresso sem fonte nem data); definir se A é "sem nenhuma fonte" ou "sem fonte e data". (2) Achados 9, 23, 32 e 33 (UTM): a regra do PO cobre o cartão, que já leva `utm_source=podcast`; a descrição do feed e o resumo em texto simples não levam.

## Achados

### brand-strategist
| ID | Classe | Revisor | Arquivo — trecho (máx. 15 palavras) | Motivo | Status |
|---|---|---|---|---|---|
| 1 | B | brand-strategist | roteiro.txt — "o orçamento do evento é de quarenta e um milhões de reais" | Bloco 1 (~1.270 palavras) acumula orçamento, visitas, LED, tarifas e ônibus: soa como noticiário, não "histórias e cenas". | pendente |
| 2 | B | brand-strategist | roteiro.txt — "A jangada até as piscinas custa de sessenta a sessenta e cinco reais por adulto" | Marco Polo lê a matéria e quase não conta cena; o guia perde a voz própria (vale também para os rankings do Bloco 2). | pendente |
| 3 | C | brand-strategist | roteiro.txt — "Bem-vindos à Rota da Semana, o podcast do Khartos que transforma a sua próxima viagem" | Promessa de produto na abertura, perto de falar como o Khartos; o viajante deixa de ser o sujeito. | registrado |
| 4 | C | brand-strategist | roteiro.txt — "já atravessei desertos, mares e uns bons aeroportos lotados para chegar até aqui" | Autorreferência no primeiro minuto; leve, mas no limite de "poucos eu". | registrado |
| 5 | C | brand-strategist | roteiro.txt — "Ou seja: se chover, o desfile continua, e você não precisa assistir" | "Ou seja:" duas vezes; "bússola" e "aventura" também repetem: começo de bordão. | registrado |
| 6 | C | brand-strategist | roteiro.txt — "O que fazer: guarde todos os comprovantes, tire foto das notas e dos recibos" | Imperativos em série no Bloco 3 e no Fechamento, contra "oferece, não impõe". | registrado |
| 7 | C | brand-strategist | roteiro.txt — "elas começaram a valer na segunda-feira, vinte e seis" | A sigla "Anac" não é explicada pela Nina (explica Etias e Braztoa). | registrado |
| 8 | C | brand-strategist | roteiro.txt — "Chegou a hora do nosso pit stop de avisos. Dois pontos, rápidos e sem drama." | Bloco 3 tem 479 palavras, ~19,8% das 2.422: colado no teto de 20%. | registrado |
| 9 | C | brand-strategist | scripts/build_feed.py — "Planeje a sua próxima viagem como uma expedição no Khartos: https://khartos.com" | Descrição do feed e `khartos_notes_plain()` sem UTM (ver nota 2). | registrado |
| 10 | C | brand-strategist | newsletter.md — "O Natal Luz de Gramado, sem cair nas armadilhas" | Assunto promete armadilhas que o corpo não trata; tom levemente alarmista. | registrado |
| 11 | C | brand-strategist | newsletter.md — "Novas regras da Anac para atrasos e cancelamentos: em vigor desde 26/10/2026." | "Datas e prazos" e parte do checklist repetem o Bloco 3 e as notas quase literalmente. | registrado |

### copy-chief
| ID | Classe | Revisor | Arquivo — trecho (máx. 15 palavras) | Motivo | Status |
|---|---|---|---|---|---|
| 12 | B | copy-chief | roteiro.txt — "um destino do Caribe que ganhou voo direto de São Paulo" | Voo dado como fato; as fontes (jan e jul) mostram só plano e anúncio. | pendente |
| 13 | B | copy-chief | notas.md / newsletter.md — "o novo voo direto para Punta Cana" | Mesmo problema: "novo voo direto" como fato; fontes dizem "planejou" e "listada". | pendente |
| 14 | B | copy-chief | roteiro.txt — "A jangada até as piscinas custa de sessenta a sessenta e cinco reais" | Preços de guia de junho sem ressalva de que podem mudar. | pendente |
| 15 | B | copy-chief | roteiro.txt — "O ônibus executivo da linha cento e noventa e cinco custa cerca de vinte e cinco reais" | Distância, tempo, ônibus e transfer sem atribuição clara ao guia e sem ressalva. | pendente |
| 16 | B | copy-chief | roteiro.txt — "Os espetáculos pagos têm ingresso à parte, vendido no site oficial do evento" | Afirmação factual sem fonte nem data; ausente das notas. | pendente |
| 17 | B | copy-chief | roteiro.txt — "O Natal Luz in Concert celebra quinze anos da Orquestra Sinfônica de Gramado" | Detalhes (músicos, solistas, horários) sem fonte dita no trecho e fora das notas. | pendente |
| 18 | B | copy-chief | roteiro.txt — "O escritório de imigração BAL informou que a União Europeia aponta o início" | Fonte BAL sem data no áudio e nas notas. | pendente |
| 19 | B | copy-chief | roteiro.txt — "O Jornal do Comércio, de Porto Alegre, informa que o orçamento" | Fonte sem data no áudio e nas notas. | pendente |
| 20 | B | copy-chief | roteiro.txt — "o mesmo site independente fala em vinte euros por autorização" | Valor só de site independente, sem conferência no portal oficial; o site nem é nomeado no áudio. | pendente |
| 21 | B | copy-chief | newsletter.md — "sites independentes estimam algo em torno de abril de 2027" | Estimativa ligada ao link do portal oficial; as notas a atribuem a um único site independente. | pendente |
| 22 | B | copy-chief | newsletter.md — "Dica de economia: misture espetáculos pagos com as atrações gratuitas do Natal Luz" | A newsletter repete o episódio (dica, horários, Anac, ETIAS, comprovantes), com pouca informação nova. | pendente |
| 23 | B | copy-chief | scripts/build_feed.py — "Conheça: https://khartos.com" | Descrição em texto puro do feed sem `utm_source=podcast` (ver nota 2). | pendente |
| 24 | C | copy-chief | roteiro.txt — "as regras novas da Anac exigem comprovação para pedir reembolso" | Generaliza: a comprovação vale para reembolso em situações excepcionais, não para toda assistência. | registrado |
| 25 | C | copy-chief | roteiro.txt — "Já fica a sugestão: dá para combinar as duas praias numa viagem só." | Sugestão nossa sem o rótulo "dica nossa". | registrado |
| 26 | C | copy-chief | roteiro.txt — "hoje, ainda não é preciso pedir o Etias" | Afirmação categórica no presente, sem data da checagem. | registrado |
| 27 | C | copy-chief | roteiro.txt / notas.md — Anac sem link primário | Só fonte secundária (Panrotas); link da Anac daria base à regra. | registrado |
| 28 | C | copy-chief | newsletter.md — "a cidade é conhecida pelo café colonial, pelo fondue e pelo chocolate" | Fato geral sem "dica nossa" ou fonte. | registrado |
| 29 | C | copy-chief | newsletter.md — "A Parada de Natal acontece sexta, sábado e domingo, às 15h." | Horários sem fonte junto ao trecho; só o aviso de confirmar no site oficial. | registrado |
| 30 | C | copy-chief | newsletter.md — "O Natal Luz de Gramado, sem cair nas armadilhas" | "Armadilhas" sugere risco que o texto não demonstra. | registrado |
| 31 | C | copy-chief | roteiro.txt / notas.md — fontes de jun/2026, jan/2026, jul/2026 e dez/2025 | Boa parte do material não é "notícia da semana": só Natal Luz, Anac e ETIAS são recentes. | registrado |

### marketing-cmo
| ID | Classe | Revisor | Arquivo — trecho (máx. 15 palavras) | Motivo | Status |
|---|---|---|---|---|---|
| 32 | B | marketing-cmo | scripts/build_feed.py — "Planeje a sua próxima viagem como uma expedição no Khartos: https://khartos.com" | Link da descrição do feed sem UTM (ver nota 2). | pendente |
| 33 | B | marketing-cmo | scripts/build_feed.py — "Conheça: https://khartos.com" | `khartos_notes_plain` (itunes:summary) sem UTM; atribuição inconsistente com `KHARTOS_URL`. | pendente |
| 34 | C | marketing-cmo | scripts/build_feed.py — "Apresentadores virtuais (vozes geradas por IA); fontes e links nas notas de cada episódio." | Aviso textual permitido, mas na mesma frase da chamada ao Khartos; PO confere se não parece ênfase em IA. | registrado |
| 35 | C | marketing-cmo | roteiro.txt — "as histórias, as fontes e as dicas são para valer" | Compromisso público de confiabilidade em áudio; ok se as fontes forem verificadas. | registrado |

## Itens para aprovação do PO (do marketing-cmo)
- Descrição do produto na newsletter ("No Khartos") e no cartão: confirmar que corresponde ao que o app faz hoje.
- Primeira publicação do feed e da página com a chamada ao Khartos (o episódio 1 fixa o texto-padrão).
- Newsletter: só rascunho; antes de qualquer envio, consentimento (LGPD), descadastro, plataforma e entregabilidade.
- Decisão sobre UTM na descrição do feed e no resumo em texto simples.
