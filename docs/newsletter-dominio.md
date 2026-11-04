# Domínio `newsletter.khartos.com` (proxy no Cloudflare)

**Decisão (04/11/2026):** `newsletter.khartos.com` é um proxy no Cloudflare para a newsletter que já está no GitHub Pages do podcast. O leitor vê `https://newsletter.khartos.com/2026-11-04/`, e o Cloudflare busca `https://podcast.khartos.com/newsletter/2026-11-04/`. Não há repositório novo nem mudança de hospedagem.

```
leitor ──▶ newsletter.khartos.com (Cloudflare Worker) ──▶ podcast.khartos.com/newsletter/… (GitHub Pages)
```

| Endereço novo | Vem de |
|---|---|
| `newsletter.khartos.com/` | `podcast.khartos.com/newsletter/` (índice das edições aprovadas, gerado pelo CI) |
| `newsletter.khartos.com/AAAA-MM-DD/` | `podcast.khartos.com/newsletter/AAAA-MM-DD/` (revista web) |
| `newsletter.khartos.com/AAAA-MM-DD/revista.pdf` | o PDF da edição |

O código do Worker está em `infra/cloudflare/newsletter-proxy.js`, com testes em `infra/cloudflare/newsletter-proxy.test.mjs` (`node infra/cloudflare/newsletter-proxy.test.mjs`).

## Passo a passo (quem tem acesso ao Cloudflare da zona `khartos.com`)

1. **Criar o Worker.** No painel do Cloudflare: *Workers & Pages* → *Create* → *Create Worker*. Dê o nome `newsletter-proxy` e clique em *Deploy*. Depois clique em *Edit code*, apague o código de exemplo, cole o conteúdo de `infra/cloudflare/newsletter-proxy.js` e clique em *Deploy*.
2. **Ligar o domínio ao Worker.** Há dois caminhos. Em algumas contas, a janela de *Custom Domain* responde "No zones match" mesmo com a zona ativa; nesse caso use a alternativa (registro A mais rota), que foi a usada em 04/11/2026. Caminho direto: no Worker, abra a aba *Domains* (ou *Settings* → *Domains & Routes*) → *Add* → *Custom Domain* → `newsletter.khartos.com`. O Cloudflare cria o registro DNS e o certificado sozinho. Hoje `newsletter.khartos.com` não tem nenhum registro, então não há conflito. Se aparecer erro de registro existente, apague o registro antigo do subdomínio e repita.
   - *Alternativa, se preferir rota em vez de domínio personalizado:* em *DNS* → *Records*, crie um registro **A** com nome `newsletter`, valor `192.0.2.1` e *Proxy status* ligado (nuvem laranja); depois, no Worker, *Add* → *Route* → `newsletter.khartos.com/*` na zona `khartos.com`. O IP `192.0.2.1` é reservado para documentação e nunca recebe tráfego: o Worker responde antes.
3. **Esperar o certificado** (de alguns minutos até cerca de uma hora no primeiro uso).
4. **Verificar** (os três primeiros devem dar 200, e o quarto deve mostrar o redirecionamento para o próprio `newsletter.khartos.com`):
   ```bash
   curl -sI https://newsletter.khartos.com/ | head -1
   curl -sI https://newsletter.khartos.com/2026-11-04/ | head -1
   curl -sI https://newsletter.khartos.com/2026-11-04/revista.pdf | head -3
   curl -sI https://newsletter.khartos.com/2026-11-04 | grep -i -E "^HTTP|^location"
   ```
5. **Mudar o gerador para o novo endereço** (só depois de o passo 4 funcionar). No GitHub: *Settings* → *Secrets and variables* → *Actions* → *Variables* → *New repository variable*, com nome `NEWSLETTER_ROOT` e valor `https://newsletter.khartos.com`; ou, no terminal, `gh variable set NEWSLETTER_ROOT --body https://newsletter.khartos.com -R volmarsegundo-source/Khartos-podcast`. Na próxima execução do workflow (um push em `episodes/`, `scripts/` ou `.github/workflows/`, ou *Run workflow*), o e-mail de capa, as metatags `og:` e o `canonical` passam a usar o novo endereço. Para voltar atrás, apague a variável. O episódio continua no domínio do podcast.
6. **Recomendado:** em *Settings* → *Pages* do repositório, ligue *Enforce HTTPS* para `podcast.khartos.com` (hoje desligado).

## Cuidados

- **`noindex`:** as páginas da revista têm `noindex`. Remova-o (em `build_revista.py`) só quando quiser que o Google as indexe.
- **Links antigos:** `podcast.khartos.com/newsletter/…` continua funcionando. O `canonical` aponta para o endereço novo quando `NEWSLETTER_ROOT` está definida.
- **Dependência:** se o GitHub Pages cair, a newsletter cai junto. O plano gratuito de Workers tem limite diário de requisições (confira o valor atual na página de preços do Cloudflare); o cache de 5 minutos do Worker reduz a carga.
- **Rollback:** apague o *Custom Domain* (ou a rota e o registro A) do Worker. Nada mais muda.
- **Envio de e-mail (fase 2) é outra coisa.** Este domínio serve só a web. Não configure SPF, DKIM nem DMARC aqui: o envio deve usar um subdomínio dedicado (por exemplo `news.khartos.com`), como recomenda a pesquisa de mercado de 31/10/2026. Veja `docs/roadmap.md`.
