/* ═══════════ 梦华经纬 · Service Worker ═══════════
   两级缓存（承姊妹站，无外部瓦片故无 TILES 层）：
   SHELL 外壳预存 · TEXTS 全文/阅读块懒载（首查后整本离线）
   VERSION 与 index.html 的 ?v 同步递升（教训：勿加 ignoreSearch 把页面钉死旧版；
   SW 预存键必须与页面请求键（含 ?v=）逐字对齐——差一个 query 即严格键不中） */

const VERSION = "v1";
const SHELL = `mhj-${VERSION}-shell`;
const TEXTS = `mhj-${VERSION}-texts`;

const SHELL_FILES = [
  "./", "./index.html", "./manifest.json",
  "./css/main.css?v=1",
  "./vendor/leaflet.js", "./vendor/leaflet.css?v=1",
  "./data/site_data.js?v=1", "./data/stats.js?v=1",
  "./icons/icon-192.png", "./icons/icon-512.png", "./icons/apple-touch-icon.png",
  "./js/config.js?v=1", "./js/map.js?v=1", "./js/rail.js?v=1",
  "./js/reader.js?v=1", "./js/search.js?v=1", "./js/suishi.js?v=1",
  "./js/stats.js?v=1", "./js/bookmarks.js?v=1", "./js/export.js?v=1", "./js/app.js?v=1",
];

self.addEventListener("install", e => {
  e.waitUntil(
    caches.open(SHELL).then(c => c.addAll(SHELL_FILES)).then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", e => {
  e.waitUntil(
    caches.keys().then(keys =>
      /* 精确保留本版两仓（勿用 endsWith(VERSION) 激活清理——会误删/漏删，四站翻车实录） */
      Promise.all(keys.filter(k => ![SHELL, TEXTS].includes(k)).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", e => {
  const url = new URL(e.request.url);
  if (e.request.method !== "GET") return;
  if (url.origin !== location.origin) return;

  /* 网络优先（防 SW 钉死旧版），失败回缓存，再失败回外壳 */
  e.respondWith(
    fetch(e.request).then(r => {
      if (/\/data\/(text|sections|xref_)/.test(url.pathname)) {
        const cp = r.clone();
        caches.open(TEXTS).then(c => c.put(e.request, cp));
      }
      return r;
    }).catch(() =>
      caches.match(e.request).then(hit => hit || caches.match("./index.html"))
    )
  );
});
