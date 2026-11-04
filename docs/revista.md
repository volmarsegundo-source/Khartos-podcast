# Formato da revista (`revista.json`)

A revista Rota da Semana é gerada por `scripts/build_revista.py` a partir de `episodes/AAAA-MM-DD/revista.json` e das fotos em `episodes/AAAA-MM-DD/revista/img/`. Este documento descreve o formato para quem escreve uma edição nova. A operação (comandos, publicação, aprovação) está em `docs/operacao.md`.

## Passo a passo de uma edição

1. **Pesquisar.** Cada fato precisa de fonte e data. Prefira fonte primária (órgão, empresa, legislação); fonte secundária (imprensa, guia, enciclopédia) entra identificada como tal. Quando duas fontes divergem, mostre a divergência. Não invente número, preço, data nem link.
2. **Escolher as fotos** no Wikimedia Commons (busca em `commons.wikimedia.org`, ou pela API com `generator=search&gsrnamespace=6`), só com licença CC0, domínio público, CC BY ou CC BY-SA. Olhe cada foto antes de usar: a legenda tem de dizer só o que a imagem mostra, e imagem ilustrativa de outro lugar ou ano deve ser legendada assim.
3. **Declarar as fotos só pelo título do arquivo:** em `imagens`, use `{"commons": "File:Nome do arquivo.jpg", "alt": "…", "legenda": "…"}`. Depois rode `python3 scripts/fetch_revista_photos.py episodes --episodio AAAA-MM-DD` (precisa de Pillow): ele confere a licença, preenche `credito`, `licenca`, `url` e `file` no `revista.json` e baixa `revista/img/<id>.jpg` e `<id>-e.jpg`. O CI roda esse mesmo passo, então as fotos não precisam ir para o git. Se tiver as fotos em disco, `scripts/prep_revista_images.py` as trata sem rede.
4. **Escrever o `revista.json`** (abaixo).
5. **Gerar e conferir:** `python3 scripts/build_revista.py episodes --episodio AAAA-MM-DD --out /tmp/revista --pdf --base file:///tmp/revista`. Abra `index.html`, `revista.pdf` e `email.html`. Confira também os avisos do gerador.
6. **Validar visualmente:** o CI publica o rascunho em `https://podcast.khartos.com/newsletter/preview/AAAA-MM-DD/` (faixa de rascunho, sem indexação, sem link em lugar nenhum), com o PDF em `…/revista.pdf`.
7. **Aprovar:** o PO cria o arquivo vazio `episodes/AAAA-MM-DD/newsletter.aprovada` e dá push; a revista passa para `https://podcast.khartos.com/newsletter/AAAA-MM-DD/`.

## Estrutura

```json
{
  "edicao": {"numero": 2, "data": "2026-11-04", "periodo": "28/10 a 04/11/2026",
             "titulo": "…", "subtitulo": "…", "capa": "id-da-foto"},
  "email": {"assuntos": ["…", "…", "…"], "preview": "…", "abertura": "…", "podcast": "…",
            "datas_de": "id-da-pagina-com-timeline", "checklist_de": "id-da-pagina-com-checklist",
            "destaques": [{"foto": "id", "secao": "…", "titulo": "…", "x": "…", "ancora": "id-da-pagina"}]},
  "imagens": {"id": {"commons": "File:Nome do arquivo.jpg", "alt": "…", "legenda": "…"}},
  "paginas": [{"id": "…", "layout": "…", "secao": "…", "titulo": "…", "lead": "…", "blocos": [ … ]}],
  "rodape": ["linha 1", "linha 2"]
}
```

Depois do `fetch_revista_photos.py`, cada imagem ganha `file`, `credito`, `licenca` e `url` no próprio `revista.json`. Texto aceita `**negrito**`, `*itálico*` e links `[texto](https://…)`. As fontes citadas na página de fontes são coletadas dos links do texto.

## Layouts de página

| `layout` | Uso |
|---|---|
| `capa` | Capa em tela cheia, com `chamadas` (`rotulo`, `x`). A foto vem de `edicao.capa`. |
| `sumario` | Sumário automático das páginas com `sumario` (texto do item ou `true`) e `resumo`. |
| `hero` | Abertura de seção: foto em tela cheia (`foto`), título, lead e `blocos` abaixo. |
| `texto` | Página de leitura. `bg: "soft"` dá fundo cinza claro. |
| `faixa` | Número em destaque sobre foto: `destaque`, `legenda_destaque`, `foto`. |
| `navy` | Página escura. Com `marco: true`, traz o bloco fixo do Khartos, em terceira pessoa. |
| `creditos` | Fotos e fontes, geradas sozinhas. `parte: "fotos"` ou `"fontes"` divide em duas páginas; `metade: 1` ou `2` reparte a lista de fotos entre duas páginas. |

## Blocos (`t`)

`p` (com `capitular: true` para letra capitular), `lead`, `h3`, `lista` (`itens`, `ordenada`), `foto` (`id`, `tam`: `wide`, `meia` ou `full`), `cartoes` (`valor`, `rotulo`, `nota`), `tabela` (`cab`, `linhas`, `nota`), `aviso` (`rotulo`, `x`, `tom`: `alerta` ou `dica`), `dias` (`n`, `rotulo`, `titulo`, `x`, `foto`), `timeline` (`data`, `titulo`, `x`), `checklist` (`itens`), `citacao` (`x`, `fonte`), `colunas` (`a`, `b`, `prop`: `c58` ou `c85`) e `cta` (`rotulo`, `url`, `utm`, `secundario`).

## Regras que o gerador cobra

- Mínimo de 15 páginas; layouts e blocos conhecidos; toda foto citada tem cadastro, arquivo, autor, licença e URL.
- O destaque do e-mail aponta para uma página existente, e `edicao.data` é igual à pasta do episódio.
- Expressões vetadas no texto: "grátis", "o melhor", "imperdível", "dos sonhos", "transforma".
- Aviso (não erro) para: assunto com mais de 60 caracteres, pré-visualização com mais de 90, HTML de e-mail acima de 80 KB e página com mais de 2 termos cartográficos ("mapa", "rota", "expedição", "bússola", "cartografar", "atlas"). O nome do programa não conta; o bloco do Khartos conta 2.

## Regras editoriais da revista

- Viagem primeiro, burocracia depois. O Marco Polo acompanha: não apresenta nem recomenda o Khartos, que aparece só no bloco final, em terceira pessoa.
- Regras de entrada, vistos e saúde: sempre "confirme na fonte oficial", sem aconselhamento jurídico ou médico.
- Black Friday só com ângulo processual, sem curadoria de ofertas. Sem preço do produto, sem "grátis" como promessa e sem número de usuários.
- Opinião e dica sem fonte levam o rótulo **(opinião editorial)**. Conta feita pela redação com valores oficiais vem identificada como tal.

## Identidade, navegação e compartilhamento (automáticos)

Nada disto entra no `revista.json`: o gerador cuida, e toda edição nova já sai assim.

- **Logo do Khartos:** o mesmo ícone de bússola (`Compass`, do Lucide) e o nome "Khartos" em Plus Jakarta Sans negrito que a navegação e a landing do app usam (navy no fundo claro, `#fdfbf6` no escuro). Fica grande no canto superior esquerdo da capa e pequena no rodapé esquerdo de todas as outras páginas, com o número da página à direita. É um link para a home da newsletter, inclusive no PDF. Os arquivos de `public/logos/khartos/` do app não são a logo em uso.
- **Página web da edição:** barra fixa no topo com a logo (volta à home), "Todas as edições", "Baixar PDF" (abre em nova aba) e "Compartilhar". No fim da revista há uma seção "Gostou desta edição?" com os mesmos botões, "Ver todas as edições", "Voltar ao topo" e "Baixar o PDF". A barra e a seção não entram no PDF.
- **Botões de compartilhamento:** compartilhamento nativo (em celulares e navegadores que oferecem), WhatsApp, Facebook, LinkedIn, X, Telegram, e-mail e copiar link, com aviso de "Link copiado". Cada link leva `utm_source=compartilhar` e o canal em `utm_medium`.
- **Home da newsletter** (`/newsletter/`, ou a raiz de `newsletter.khartos.com`): logo, o título "Rota da Semana" com a frase "A newsletter do Khartos: uma edição por semana…" e a lista das edições aprovadas. **Cada card de edição traz os botões de compartilhamento dessa edição**, além de "Ler na web" e "Baixar o PDF" (nova aba, para fechar e voltar à home).

## PDF

O PDF sai em A4, uma folha por página. O gerador mede cada página e reduz o texto o necessário para caber numa folha, até 55% do tamanho; abaixo de 75% a página fica pequena demais, e a solução é dividi-la em duas.
