// Ziyaret sayacı — Cloudflare Worker + KV
// Tekil ziyaretçi: IP + tarayıcı imzası hash'i, 24 saat boyunca tekrar sayılmaz.
// Tekillik kaydı Cache API'de tutulur; KV'ye yalnız toplam yazılır (ücretsiz
// plandaki 1.000 yazma/gün limiti dolmasın diye biriktirilerek).

const ANAHTAR = "toplam";
const YAZMA_ESIGI = 20;        // bu kadar yeni ziyarette bir KV'ye yaz
const YAZMA_ARALIGI = 300000;  // ya da 5 dakikada bir
const ZIYARET_TTL = 86400;     // aynı ziyaretçi 24 saat içinde tekrar sayılmaz

let bellekToplam = null;   // KV'den okunan son değer
let bekleyen = 0;          // henüz yazılmamış artış
let sonYazma = 0;

async function hash(metin) {
  const veri = new TextEncoder().encode(metin);
  const ozet = await crypto.subtle.digest("SHA-256", veri);
  return [...new Uint8Array(ozet)].slice(0, 12).map((b) => b.toString(16).padStart(2, "0")).join("");
}

async function toplamiOku(env) {
  if (bellekToplam === null) {
    const ham = await env.SAYAC.get(ANAHTAR);
    bellekToplam = ham ? parseInt(ham, 10) || 0 : 0;
  }
  return bellekToplam + bekleyen;
}

async function belkiYaz(env) {
  const simdi = Date.now();
  if (bekleyen === 0) return;
  if (bekleyen < YAZMA_ESIGI && simdi - sonYazma < YAZMA_ARALIGI) return;
  const yeni = bellekToplam + bekleyen;
  bekleyen = 0;
  bellekToplam = yeni;
  sonYazma = simdi;
  await env.SAYAC.put(ANAHTAR, String(yeni));
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const basliklar = {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
      "access-control-allow-origin": "https://ozamaninparasiyla.com",
    };

    if (url.pathname !== "/api/sayac") {
      return new Response(JSON.stringify({ hata: "yok" }), { status: 404, headers: basliklar });
    }
    if (request.method !== "GET") {
      return new Response(JSON.stringify({ hata: "yalnız GET" }), { status: 405, headers: basliklar });
    }

    // Sayaç yalnız kendi sayfamızdan çağrılabilsin (curl ile şişirmeyi zorlaştırır)
    const kaynak = request.headers.get("origin") || request.headers.get("referer") || "";
    if (kaynak && !kaynak.startsWith("https://ozamaninparasiyla.com")) {
      return new Response(JSON.stringify({ hata: "yetkisiz kaynak" }), { status: 403, headers: basliklar });
    }

    const ip = request.headers.get("cf-connecting-ip") || "";
    const ua = request.headers.get("user-agent") || "";
    const parmak = await hash(ip + "|" + ua);

    const cache = caches.default;
    const izAnahtari = new Request("https://sayac.internal/z/" + parmak);
    let yeniZiyaret = false;
    if (!(await cache.match(izAnahtari))) {
      yeniZiyaret = true;
      bekleyen += 1;
      ctx.waitUntil(cache.put(izAnahtari, new Response("1", {
        headers: { "cache-control": "max-age=" + ZIYARET_TTL },
      })));
    }

    const toplam = await toplamiOku(env);
    ctx.waitUntil(belkiYaz(env));

    return new Response(JSON.stringify({ toplam: toplam, yeni: yeniZiyaret }), { headers: basliklar });
  },
};
