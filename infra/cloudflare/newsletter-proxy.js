// Cloudflare Worker: serve https://newsletter.khartos.com/<caminho> a partir de
// https://podcast.khartos.com/newsletter/<caminho> (GitHub Pages), sem mudar o endereço que o leitor vê.
// Passo a passo de instalação em docs/newsletter-dominio.md.

const UPSTREAM = "https://podcast.khartos.com";
const PREFIX = "/newsletter";

export function rewriteLocation(location, origin) {
  return location
    .replace(/^https?:\/\/podcast\.khartos\.com\/newsletter/i, origin)
    .replace(/^\/newsletter(?=\/|$)/, "");
}

export default {
  async fetch(request) {
    if (request.method !== "GET" && request.method !== "HEAD") {
      return new Response("Método não permitido", { status: 405, headers: { Allow: "GET, HEAD" } });
    }
    const url = new URL(request.url);
    const headers = { "User-Agent": "newsletter-khartos-proxy/1.0", Accept: request.headers.get("Accept") || "*/*" };
    const range = request.headers.get("Range");
    if (range) headers.Range = range;

    const upstream = await fetch(UPSTREAM + PREFIX + url.pathname + url.search, {
      method: request.method,
      headers,
      redirect: "manual",
      cf: { cacheEverything: true, cacheTtlByStatus: { "200-299": 300, "404": 30, "500-599": 0 } },
    });

    const out = new Headers(upstream.headers);
    out.delete("set-cookie");
    const location = out.get("location");
    if (location) out.set("location", rewriteLocation(location, url.origin));
    return new Response(request.method === "HEAD" ? null : upstream.body, { status: upstream.status, headers: out });
  },
};
