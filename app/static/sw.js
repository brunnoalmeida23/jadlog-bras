const CACHE_NAME = "jadlog-bras-v2";

const ARQUIVOS_ESTATICOS = [
  "/",
  "/simulador/",
  "/consulta/",
  "/manifest.json",
  "/static/css/style.css",
  "/static/js/main.js",
  "/static/logo-jadlog.png",
  "/static/icons/launchericon-192x192.png",
  "/static/icons/launchericon-512x512.png"
];

self.addEventListener("install", (event) => {
  self.skipWaiting();

  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ARQUIVOS_ESTATICOS);
    })
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((nomes) => {
      return Promise.all(
        nomes
          .filter((nome) => nome !== CACHE_NAME)
          .map((nome) => caches.delete(nome))
      );
    })
  );

  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET") {
    return;
  }

  const requisicao = event.request;

  if (requisicao.mode === "navigate") {
    event.respondWith(
      fetch(requisicao).catch(() => caches.match("/"))
    );
    return;
  }

  event.respondWith(
    caches.match(requisicao).then((cache) => {
      return cache || fetch(requisicao);
    })
  );
});
