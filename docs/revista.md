# Formato da revista (`revista.json`)

A revista Rota da Semana é gerada por `scripts/build_revista.py` a partir de `episodes/AAAA-MM-DD/revista.json` e das fotos em `episodes/AAAA-MM-DD/revista/img/`. Este documento descreve o formato para quem escreve uma edição nova. A operação (comandos, publicação, aprovação) está em `docs/operacao.md`.

## Passo a passo de uma edição

1. **Pesquisar.** Cada fato precisa de fonte e data. Prefira fonte primária (órgão, empresa, legislação); fonte secundária (imprensa, guia, enciclopédia) entra identificada como tal. Quando duas fontes divergem, mostre a divergência. Não invente número, preço, data nem link.
2. **Escolher as fotos** no Wikimedia Commons, só com licença CC0, domínio público, CC BY ou CC BY-SA. Registre autor, licença e a página do Commons. Olhe cada foto antes de usar: a legenda tem de dizer só o que a imagem mostra, e imagem ilustrativa de outro lugar ou ano deve ser legendada assim.
3. **Tratar as fotos:** `python3 scripts/prep_revista_images.py ORIGINAIS/ episodes/AAAA-MM-DD/revista/img/` (precisa de Pillow). O nome do arquivo é o `id` da foto mais `.jpg`.
4. **Escrever o `revista.json`** (abaixo).
5. **Gerar e conferir:** `python3 scripts/build_revista.py episodes --episodio AAAA-MM-DD --out /tmp/revista --pdf --base file:///tmp/revista`. Abra `index.html`, `revista.pdf` e `email.html`. Confira também os avisos do gerador.
6. **Aprovar:** o PO cria o arquivo vazio `episodes/AAAA-MM-DD/newsletter.aprovada` e dá push. Sem ele, nada vai ao site.

## Estrutura

```json
{
  "edicao": {"numero": 2, "data": "2026-11-04", "periodo": "28/10 a 04/11/2026",
             "titulo": "…", "subtitulo": "…", "capa": "id-da-foto"},
  "email": {"assuntos": ["…", "…", "…"], "preview": "…", "abertura": "…", "podcast": "…",
            "datas_de": "id-da-pagina-com-timeline", "checklist_de": "id-da-pagina-com-checklist",
            "destaques": [{"foto": "id", "secao": "…", "titulo": "…", "x": "…", "ancora": "id-da-pagina"}]},
  "imagens": {"id": {"file": "id.jpg", "alt": "…", "legenda": "…", "credito": "Autor",
                     "licenca": "CC BY-SA 4.0", "url": "https://commons.wikimedia.org/wiki/File:…"}},
  "paginas": [{"id": "…", "layout": "…", "secao": "…", "titulo": "…", "lead": "…", "blocos": [ … ]}],
  "rodape": ["linha 1", "linha 2"]
}
```

Texto aceita `**negrito**`, `*itálico*` e links `[texto](https://…)`. As fontes citadas na página de fontes são coletadas dos links do texto.

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

## PDF

O PDF sai em A4, uma folha por página. O gerador mede cada página e reduz o texto o necessário para caber numa folha, até 55% do tamanho; abaixo de 75% a página fica pequena demais, e a solução é dividi-la em duas.
