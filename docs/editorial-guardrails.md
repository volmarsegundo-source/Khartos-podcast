# Guardrails editoriais (públicos)

Regras **operacionais** para quem escreve e revisa o episódio, as notas e o rascunho de newsletter do "Rota da Semana — Khartos". Este repositório é público: aqui entram só regras de voz, tom e segurança editorial. Estratégia, segmentação, plano comercial, métricas internas e a lista de afirmações não aprovadas do Khartos **não** vivem aqui e não devem ser reconstruídas neste repositório.

Quem usa: a tarefa agendada (ao escrever), os revisores em `.claude/agents/` (ao revisar) e o PO.

## Voz — MARCO POLO
- Explorador que conduz e conta histórias de viagem, com humor leve e específico.
- **Oferece, não impõe:** "se te interessa, vale…", nunca "você deve…".
- Poucos "eu". Sem autoglorificação ("eu, o grande Marco Polo") e sem caricatura medieval.
- Sem série de exclamações, sem épico forçado e sem bordões repetidos.
- Fatos pequenos e concretos a serviço da conversa; nada de despejo enciclopédico.
- Fala como personagem, não como o Khartos: "o Khartos pode ajudar a…", nunca "eu sou o Khartos".
- Não atribui ao guia capacidades que o episódio não consiga comprovar.

## Voz — NINA
- Viajante digital, curiosa e prática; pergunta o que o ouvinte perguntaria.
- Explica siglas e termos novos em linguagem simples, com uma analogia curta quando ajuda.
- É o contraponto prático: custo, tempo, burocracia e o que fazer, sem sermão.

## Tom
- **Viagem primeiro, burocracia depois:** cerca de dois terços leves (destinos, passeios, dicas); regras, vistos e saúde em dose curta (até ~20%), com bom humor e sempre terminando em "o que fazer".
- Sem tom de noticiário pesado, sem alarmismo, sem moralismo.
- Respeito cultural: nada de estereótipo sobre lugares ou pessoas.

## O que o áudio nunca faz
- **Nunca cita inteligência artificial, modelos, "vozes sintéticas" nem "apresentadores virtuais".** O aviso existe só em texto, na página do podcast e no rodapé do site.
- Não cita bônus, créditos ou recompensas do produto, nem números deles.
- Não promete prazo ou duração de resultado do produto ("em 5 minutos", "num instante").
- Não traz URL, símbolo ou markdown no roteiro (as vozes leem tudo).

## Fontes e claims
- **Nenhuma afirmação factual sem fonte e data** (preço, data, regra, número, ranking, promoção). Sem fonte, vira opinião ou sugestão, dita como tal ("dica nossa").
- Nunca inventar link, preço, citação, depoimento ou pesquisa. Se não achou a fonte, rebaixe a frase.
- Ressalvas explícitas: promoção que pode acabar, dado só da empresa, projeção, informação não confirmada. Fontes divergentes: mostre a divergência.
- Regras de entrada, vistos e saúde: sempre "confirme na fonte oficial". Sem aconselhamento jurídico ou médico; seguro-viagem sem valores e sem "obrigatório" ou "recomendado" categórico.
- Parafrasear sempre; no máximo uma citação curta (menos de 15 palavras) por fonte.

## Classes de achado (decisão do PO)
- **A (bloqueia):** afirmação sobre visto, saúde, regras de entrada ou legislação SEM fonte identificável OU SEM a data da regra.
- **B:** nos demais temas, ausência de fonte ou de data; também afirmações com fonte citada, mas fraca ou desatualizada.
- **C:** informativo.

## Chamada ao Khartos
- É gerada pelo `scripts/build_feed.py` (cartão na página, rodapé e fim das descrições do feed). **Não entra no roteiro.**
- Fala da **proposta de valor**: viajar como uma expedição, com perfil, guia do destino, roteiro e checklist, tendo o Marco Polo como guia. **Sem ênfase em IA/tecnologia**; sem preço, "grátis", "o melhor" ou número de usuários.
- O link do **cartão** leva `utm_source=podcast`. (O link do rascunho de newsletter segue o formato do `CLAUDE.md`, com `utm_source=newsletter`; links de texto simples na descrição do feed estão em decisão do PO.)

## Newsletter (rascunho)
- **Complementa** o episódio, nunca é cópia do roteiro nem das notas: aprofunda um destino, traz datas e prazos com fonte e um checklist prático.
- É só rascunho para o PO revisar. **Nada é enviado.** Antes de qualquer envio: consentimento (LGPD), descadastro, plataforma de envio e entregabilidade.

## Conteúdo que nunca entra neste repositório
Qualquer material interno de estratégia ou negócio do Khartos, dados de usuários, chaves ou segredos, e qualquer afirmação sobre o produto que não esteja aprovada e sustentada por fonte pública.
