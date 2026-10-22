// Sheen service worker: serves the app offline. Generated into app/sw.js by src/build.py.
const CACHE = "sheen-1.0.0-eec1a40dc7";
const ASSETS = ["./", "fonts/fira-code-400.woff2", "fonts/fira-code-500.woff2", "fonts/fira-code-700.woff2", "fonts/fonts.css", "fonts/geist-mono-400.woff2", "fonts/geist-mono-500.woff2", "fonts/geist-mono-700.woff2", "fonts/ibm-plex-mono-400.woff2", "fonts/ibm-plex-mono-500.woff2", "fonts/ibm-plex-mono-700.woff2", "fonts/jetbrains-mono-400.woff2", "fonts/jetbrains-mono-500.woff2", "fonts/jetbrains-mono-700.woff2", "icon-180.png", "icon-192.png", "icon-512.png", "icon.svg", "index.html", "manifest.webmanifest", "vendor/highlight.min.js"];

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE).then((cache) => cache.addAll(ASSETS)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k.startsWith("sheen-") && k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

// Cache first, refreshed in the background, so a new build is picked up on the next visit.
self.addEventListener("fetch", (event) => {
  const { request } = event;
  if (request.method !== "GET" || new URL(request.url).origin !== self.location.origin) return;
  event.respondWith(
    caches.open(CACHE).then(async (cache) => {
      const cached = await cache.match(request, { ignoreSearch: true });
      const network = fetch(request)
        .then((response) => {
          if (response.ok) cache.put(request, response.clone());
          return response;
        })
        .catch(() => cached);
      return cached || network;
    })
  );
});
