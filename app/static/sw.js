const CACHE_VERSION = "jadlog-bras-v3";

self.addEventListener("install", () => {
    self.skipWaiting();
});

self.addEventListener("activate", (event) => {
    event.waitUntil(
        (async () => {
            const cachesExistentes = await caches.keys();

            await Promise.all(
                cachesExistentes.map((cache) => caches.delete(cache))
            );

            await self.clients.claim();
        })()
    );
});

self.addEventListener("fetch", (event) => {
    const requisicao = event.request;

    if (requisicao.method !== "GET") {
        return;
    }

    const url = new URL(requisicao.url);

    const nuncaUsarCache =
        requisicao.mode === "navigate" ||
        url.pathname === "/" ||
        url.pathname === "/login" ||
        url.pathname === "/logout" ||
        url.pathname.startsWith("/simulador") ||
        url.pathname.startsWith("/consulta") ||
        url.pathname.startsWith("/api/") ||
        url.pathname.startsWith("/pdf/");

    if (nuncaUsarCache) {
        event.respondWith(
            fetch(requisicao, {
                cache: "no-store"
            })
        );

        return;
    }

    event.respondWith(
        fetch(requisicao).catch(() => caches.match(requisicao))
    );
});
