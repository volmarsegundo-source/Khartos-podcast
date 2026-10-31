# Arquitetura

Mesmo pipeline do podcast `radar-ia`, adaptado ao Khartos (nomes, vozes, textos e capa).

## Componentes

1. **Tarefa agendada do Claude** (cron `47 7 * * 4`, America/Sao_Paulo): pesquisa a web, escreve `roteiro.txt` e `notas.md` e dá push na `main`. O prompt vive na tarefa; o formato e o tom estão em `CLAUDE.md`.
2. **GitHub Actions** (`.github/workflows/episodio.yml`): para cada pasta de episódio sem Release, roda `scripts/tts.py`, cria a Release `ep-AAAA-MM-DD` com o MP3, baixa os últimos 12 MP3 e roda `scripts/build_feed.py`.
3. **`scripts/tts.py`**: separa falas por locutor (`MARCO POLO`, `NINA`), sintetiza com Google Cloud TTS (Chirp 3 HD pt-BR, limite de 4.500 bytes por requisição, retry em 429/5xx), insere pausas, junta, normaliza (~-19 LUFS) e codifica MP3 mono 64 kbps.
4. **`scripts/build_feed.py`**: monta `feed.xml` (com `itunes:block`), a página do podcast (player, assinar, compartilhar) e uma página por episódio com as notas.
5. **GitHub Pages** publica o site; o app Podcasts segue o feed.

## Decisões

- Áudio fora do git: o MP3 vive nas Releases; o repositório guarda só texto.
- Repositório e site públicos (Pages gratuito); por isso nada confidencial e `noindex` nas páginas.
- Duas vozes distintas (Marco Polo: `Algenib`, voz grave e firme, Nina: `Aoede`) para o formato conversa.
- Um episódio já publicado é ignorado; refazer exige o marcador `refazer`.

## Limites

- Google TTS: nível gratuito de 1 milhão de caracteres por mês nas vozes Chirp 3 HD, compartilhado com outros podcasts que usem a mesma chave.
- A sessão do Claude não cria Releases, não ativa Pages nem cadastra secrets; só o push dispara o workflow.
