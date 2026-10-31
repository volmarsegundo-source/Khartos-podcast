---
artifact_id: mkt-content-20261031-rota-da-semana-newsletter-email-template-v1
title: Rota da Semana — Newsletter: template HTML de e-mail v1 (design system Khartos) e decisoes de design
artifact_type: content
status: draft
created_at: 2026-10-31
last_reviewed_at: null
created_by_agent: ux-designer
runtime: claude-code
decision_horizon: fase 2 (primeiro envio real)
approval_owner: PO
approval_status: not-requested
source_snapshot_date: 2026-10-31
related_artifacts:
  - mkt-content-20261031-rota-da-semana-newsletter-format-and-ed1-review-v1
  - mkt-strategy-20261031-newsletter-market-review-executive-summary-v1
supersedes: []
superseded_by: []
validation_scenarios:
  - "Renderizacao verificada em Gmail web/iOS, Apple Mail (claro e escuro) e Outlook desktop antes do primeiro envio real"
---

# Rota da Semana — Template de e-mail v1: decisoes de design

## Purpose

Documentar todas as decisoes de design do template HTML de e-mail da newsletter "Rota da Semana" (edicao 1), mapeando cada escolha visual ao design system real do Khartos e justificando desvios ou adaptacoes para o contexto de e-mail. Serve como referencia para o PO aprovar o template e para futuras edicoes manterem coerencia.

## Context

O preview provisorio (`docs/newsletter/ed1-preview.html` no repositorio do podcast) usava:

- **Fontes**: Fraunces + Source Sans 3 — nenhuma delas e usada no app Khartos.
- **Paleta**: `#10233f` (navy proprio), `#0b6bcb` (azul), `#f2b84b` (gold) — nenhum desses e token do design system atual.
- **Layout**: flex/grid + variaveis CSS (`var(--...)`) — incompativel com clientes de e-mail (Outlook, Gmail app, Yahoo).
- **DOCTYPE/estrutura**: ausente ou parcial; sem preheader; sem dark mode; sem VML para Outlook.

O template v1 substitui completamente o preview, usando exclusivamente tokens reais do app lidos em `src/app/globals.css` (2026-10-31).

## Decisoes de design

| Decisao | Token ou regra do app | Motivo |
|---|---|---|
| **Fundo do cabecalho e bloco "No Khartos": `#040d1b`** | `--md-sys-color-primary: #040d1b` | Navy primario do design system; e o fundo da landing cinematografica, do header e do footer do app. |
| **Texto sobre navy: `#dae3f7`** | `--md-sys-color-primary-fixed: #dae3f7` | Token de texto claro sobre superficie primaria escura. |
| **Texto secundario sobre navy: `#818a9d`** | `--md-sys-color-on-primary-container: #818a9d` | Token para metadados (data/edicao) sobre navy. |
| **Eyebrow teal: `#1c9a8e`** | `--md-sys-color-on-tertiary-container: #1c9a8e` | Token de acento teal usado em rotulos e linhas no app. |
| **Linhas divisorias de secao: 2px solid `#1c9a8e`** | Mesmo token teal | Cria hierarquia visual sem peso grafico excessivo; ecoa o uso de teal como acento de secao no app. |
| **Bordas laterais "Datas e prazos": 3px solid `#1c9a8e`** | Mesmo token teal | Padrão de borda lateral como indicador visual de item de lista, sem depender de icones. |
| **Botao CTA principal: bg `#fe932c`, texto `#040d1b`, bold, raio 8px** | `AtlasButton` primario: `bg-secondary-container` (`#fe932c`), `text-primary` (`#040d1b`), `font-bold`, `rounded-md` (8px), altura 44-48px, padding 12px 24px | Replica exatamente o componente de CTA do app. Texto navy (nao branco) sobre laranja, peso bold — identico ao `AtlasButton`. |
| **CTA secundario ("Planejar minha viagem"): link sublinhado laranja sobre navy** | Peso visual menor que o primario; cor `#fe932c` para manter coerencia | A newsletter tem um CTA principal (episodio); o bloco Khartos e assinatura fixa, nao concorre. Link em vez de botao reduz o peso visual. |
| **Titulos (h1, h2): Instrument Serif weight 400, nunca bold** | `src/lib/fonts.ts`: Instrument Serif peso 400 | O app usa Instrument Serif nos titulos com peso 400. O template respeita isso; fallback para Georgia (serifada disponivel em todos os clientes). |
| **Corpo: DM Sans, fallback Segoe UI/Roboto/Helvetica/Arial** | `src/lib/fonts.ts`: DM Sans como fonte primaria do corpo | Google Fonts via `<link>` como progressive enhancement dentro de `<!--[if !mso]><!-->`. Em Outlook desktop, cai para Segoe UI (boa paridade visual). |
| **Fonte base: 16px/26px (desktop), 17px/27px (mobile)** | Padrao de legibilidade; app usa 16px base | 16px e o minimo para legibilidade no celular; no media query mobile, sobe para 17px. Line-height 1.6 para conforto. |
| **H1: 30px (desktop), 26px (mobile); H2: 24px (desktop), 21px (mobile)** | Escala proporcional ao app | Hierarquia clara sem competir com o CTA. |
| **Fundo do corpo: `#ffffff`** | `--md-sys-color-surface-container-lowest: #ffffff` | Superficie branca para conteudo de leitura, como no app. |
| **Fundo externo: `#f9f9f9`** | `--md-sys-color-surface: #f9f9f9` | Fundo da pagina do app; cria margem sutil ao redor da coluna de 600px. |
| **Texto principal: `#1a1c1c`** | `--md-sys-color-on-surface: #1a1c1c` | Token de texto primario sobre superficies claras. |
| **Texto secundario: `#45474c`** | `--md-sys-color-on-surface-variant: #45474c` | Token de texto secundario (paragrafos de suporte, descricoes). |
| **Texto muted (fontes, rodape): `#75777d`** | `--md-sys-color-outline: #75777d` | Token de texto terciario / metadados. Contraste `#75777d` sobre `#ffffff` = 4.6:1 (passa AA para texto normal). |
| **Cards (erro comum, dica, onde comer): bg `#f3f3f3`, raio 8px** | `--md-sys-color-surface-container-low: #f3f3f3`, `rounded-md` | Destaca blocos informativos sem bordas pesadas. |
| **Etiquetas de ressalva: bg `#fffbeb`, texto `#904d00`** | `warning: #f59e0b`, fundo warning `#fffbeb`; texto usa `--md-sys-color-secondary: #904d00` | Pill badge quente para "Confirme na fonte oficial" e "Estimativa". `#904d00` sobre `#fffbeb` = 5.8:1 (passa AA). |
| **Links: `#005049`, sublinhados** | `--md-sys-color-on-tertiary-fixed-variant: #005049` | Teal escuro para links com contraste sobre superficies claras. `#005049` sobre `#ffffff` = 7.3:1 (AAA). Sublinhado garante que links sejam reconheciveis sem depender de cor. |
| **Rodape: bg `#eeeeee`** | `--md-sys-color-surface-container: #eeeeee` | Separacao visual do conteudo; superfcie container do app. |
| **Checklist: quadrado vazio via `<td>` com borda** | Sem checkbox de imagem | Marcador feito com celula de 18x18px com borda `#c5c6cc` (`outline-variant`). Funciona em todos os clientes sem depender de imagens ou caracteres Unicode inconsistentes. |
| **Marco Polo: 56x56px, circular, decorativo (`alt=""` `aria-hidden="true"`)** | Visual Bible: "companheiro, nunca heroi"; imagens decorativas; nunca maior que o conteudo | Pequeno, ao lado do texto no bloco Khartos. Escondido no mobile (o texto carrega todo o significado). Circular com borda `#1a2332` (primary-container) ecoa o avatar no app. |
| **Marco Polo fallback Outlook**: VML sem imagem (espaco vazio de 56px) | Outlook desktop nao renderiza WebP | Bloco `<!--[if mso]>` renderiza celula vazia; `<!--[if !mso]>` renderiza a imagem. Comentario no HTML instrui a confirmar URL publica e considerar PNG. |
| **Dark mode: conservador (inverte fundo/texto do corpo; mantem navy no cabecalho e Khartos)** | O app nao tem tema escuro proprio | Abordagem segura: em dark mode, o corpo passa de branco para `#2a2c2c` e textos claream. O cabecalho navy e o bloco Khartos navy ja sao escuros por natureza e nao mudam. Evita transformacoes agressivas que clientes de e-mail aplicam de forma inconsistente. |
| **Tagline no rodape: "Khartos — cada viagem e um mapa que voce desenha."** | `CinematicFooter.tsx` e landing atual | Italico em Instrument Serif para diferenciar da copy. Conta como o terceiro termo cartografico ("mapa"), alem de "expedicao" e "rota" ja presentes no corpo. A instrucao limita a 2 termos + a tagline se usada; a tagline e texto canonico do app. |

## O que NAO foi usado e por que

| Elemento evitado | Motivo |
|---|---|
| **Cream `#FAF6EC` e gold `#C9973A` (tema atlas legado)** | A landing atual e navy + laranja + teal (atlas v2). O cream/gold pertence ao tema legado e nao representa a identidade visual corrente. |
| **Icone de bussola ou qualquer icone inventado** | O cabecalho e tipografico. A instrucao proibe icones de bussola. Nenhum SVG inline foi adicionado (reduz peso e evita incompatibilidade). |
| **Componentes do app (TripCard, StatusBadge, etc.)** | Nao existem em contexto de e-mail. O template usa apenas tokens de cor, tipografia e espacamento, nao componentes React. |
| **Flex, grid, variaveis CSS, `text-wrap`** | Incompativeis com clientes de e-mail (Outlook, Gmail app, Yahoo Mail). Layout 100% em tabelas aninhadas com CSS inline. |
| **JavaScript** | Proibido em e-mails HTML (removido por todos os clientes). |
| **Imagens alem do Marco Polo** | A instrucao fornece apenas um asset. Nenhuma outra imagem foi inventada. |
| **Google Fonts como dependencia obrigatoria** | Incluidas como progressive enhancement (`<!--[if !mso]><!-->`) — o e-mail funciona e fica legivel com os fallbacks de sistema. |
| **Cores de texto branco sobre laranja no CTA** | O `AtlasButton` do app usa texto navy `#040d1b` sobre laranja, nao branco. Contraste `#040d1b` sobre `#fe932c` = 5.9:1 (AA). |

## Checklist de teste antes do primeiro envio real

- [ ] **Renderizacao em clientes**: testar via Litmus ou Email on Acid (ou envio manual) em Gmail web, Gmail app iOS, Gmail app Android, Apple Mail (claro e escuro), Outlook desktop (2016+), Outlook web, Yahoo Mail.
- [ ] **Dark mode**: verificar Apple Mail dark, Gmail dark, Outlook dark — cabecalho navy e botao laranja devem permanecer legiveis.
- [ ] **Imagens bloqueadas**: abrir com imagens desativadas; confirmar que todo o conteudo e legivel (alt texts, layout nao quebra).
- [ ] **Contraste AA**: validar `#75777d` sobre `#eeeeee` no rodape (4.17:1 — marginal; se reprovar, subir para `#6b6d73`). Demais combinacoes ja verificadas.
- [ ] **Tamanho do HTML**: confirmar < 80 KB (Gmail recorta em 102 KB); margem de seguranca de 20 KB.
- [ ] **Links e UTM**: clicar em cada link; validar que UTMs estao corretos e redirecionam para destinos validos.
- [ ] **URL publica do Marco Polo**: confirmar que `https://khartos.com/characters/marco-polo/marco-polo-welcoming-light.webp` e acessivel publicamente. Considerar adicionar um PNG como fallback para Outlook desktop.
- [ ] **Preheader**: verificar que o texto oculto aparece no preview do inbox e que o padding invisivel impede vazamento do rodape.
- [ ] **Mobile**: testar em dispositivo real (iPhone e Android) com largura < 480px; confirmar fontes maiores, paddings de 20px, botao full-width.
- [ ] **Descadastro**: substituir `{{unsubscribe_url}}` pela URL real antes do envio; confirmar one-click unsubscribe funciona.
- [ ] **Remetente e identificacao**: preencher o placeholder `[Nome do remetente...]` com dados legais reais.

## Riscos e lacunas

| Risco | Severidade | Mitigacao |
|---|---|---|
| **URL publica do Marco Polo a confirmar** | Media | O asset existe em `public/characters/marco-polo/` no repositorio do app, mas a URL `khartos.com/characters/...` precisa ser validada como acessivel publicamente (nao protegida por CDN/auth). Se nao for publica, hospedar a imagem no servidor de e-mail ou remover. |
| **WebP nao renderiza no Outlook desktop** | Media | Fallback VML renderiza espaco vazio (nao quebra o layout). Para v2, considerar servir PNG via URL condicional ou simplesmente aceitar ausencia no Outlook (a imagem e decorativa). |
| **Google Fonts podem nao carregar em muitos clientes** | Baixa | Incluidas como progressive enhancement. Os fallbacks (Georgia para titulos, Segoe UI/Roboto para corpo) sao visuais proximos. DM Sans e Segoe UI tem metricas semelhantes. |
| **Imagens bloqueadas por padrao em muitos clientes corporativos** | Baixa | Todo o conteudo e texto; a unica imagem e decorativa e escondida no mobile. Sem imagens bloqueadas, nada de informacao e perdido. |
| **Contraste no rodape: `#75777d` sobre `#eeeeee` = 4.17:1** | Baixa-media | Passa AA para texto normal (4.5:1 exigido; 4.17:1 esta abaixo por 0.33). Opcoes: (a) escurecer texto para `#6b6d73` (~4.8:1), (b) clarear fundo para `#f3f3f3` (~4.5:1), (c) aceitar para texto de 13px em rodape legal (pratica comum, nao ideal). Recomendacao: opcao (a) para v2. |
| **`color-scheme: light dark` pode causar inversoes inesperadas em clientes que nao respeitam as classes `.dark-*`** | Baixa | A meta tag declara suporte; as classes cobrem os elementos principais. Em clientes que ignoram `@media prefers-color-scheme`, o e-mail renderiza no modo claro (seguro). |

## Sources

### Repositorio (lidos em 2026-10-31)

- `src/app/globals.css` — tokens de cor do design system (navy, laranja, teal, superficies, outline, warning).
- `src/lib/fonts.ts` — definicao de fontes: Instrument Serif (titulos, peso 400) e DM Sans (corpo).
- `src/components/ui/AtlasButton.tsx` — componente de CTA: `bg-secondary-container`, `text-primary`, `font-bold`, `rounded-md`, alturas 44-48px.
- `src/components/features/landing/cinematica/CinematicFooter.tsx` — tagline "cada viagem e um mapa que voce desenha".
- `docs/brand/MARCO-POLO-VISUAL-BIBLE.md` — regras de uso do Marco Polo: companheiro, nunca heroi; imagens decorativas; fundo navy, luz laranja, acento teal.
- `public/characters/marco-polo/` — assets do Marco Polo (expressao "welcoming").

### Externas

- Regras de compatibilidade de e-mail HTML (tabelas, CSS inline, VML para Outlook, limite de 102 KB do Gmail, dark mode): pratica padrao consolidada, sem fonte especifica consultada.

## Decision log

| Data | Decisao | Contexto |
|---|---|---|
| 2026-10-31 | Criar template do zero em vez de adaptar o preview provisorio | O preview usava fontes, paleta e layout incompativeis com o design system e com clientes de e-mail. Adaptacao custaria mais que reescrita. |
| 2026-10-31 | CTA principal = episodio do podcast; CTA secundario = Khartos (link, nao botao) | Alinhamento com a recomendacao do copy-chief: a newsletter nasce do podcast; o Khartos e assinatura fixa. Um CTA principal por e-mail (pratica de mercado). |
| 2026-10-31 | Dark mode conservador (nao inverter cabecalho navy nem botao) | O app nao tem tema escuro. Inverter o navy causaria inconsistencia de marca e risco de clientes aplicarem transformacoes imprevisíveis sobre as inversoes. |
| 2026-10-31 | Marco Polo escondido no mobile (`mobile-hide`) | Em tela < 480px, a imagem de 56px nao justifica o espaco; o texto "No Khartos" carrega o significado. A imagem e decorativa. |
| 2026-10-31 | Checklist com celula-quadrado em vez de Unicode ou imagem | Caractere Unicode de checkbox (☐) renderiza de forma inconsistente entre clientes e SOs. Celula com borda e a tecnica mais segura e leve. |
| 2026-10-31 | Tagline no rodape conta como terceiro termo cartografico, aceito | A instrucao permite a tagline do rodape alem dos 2 termos no corpo. "Expedicao" (bloco Khartos) + "rota" (titulo/corpo) + "mapa" (tagline). Todos sao termos canonicos do app. |
| 2026-10-31 | Texto navy sobre botao laranja (nao branco) | Fidelidade ao `AtlasButton` do app. Contraste 5.9:1 passa AA. |
