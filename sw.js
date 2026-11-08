/* Splendid London Walks: keeps the app and the map tiles you've seen available offline. */
const APP = 'sw-app-v1';
const TILES = 'sw-tiles-v1';
const SHELL = [
  './', 'index.html', 'manifest.webmanifest',
  'icons/icon-32.png', 'icons/icon-180.png', 'icons/icon-192.png', 'icons/icon-512.png', 'icons/maskable-512.png',
  'fonts/playfair-display-latin-500-italic.woff2', 'fonts/playfair-display-latin-600-italic.woff2',
  'fonts/playfair-display-latin-700-italic.woff2', 'fonts/playfair-display-latin-700-normal.woff2',
  'fonts/lora-latin-400-normal.woff2', 'fonts/lora-latin-400-italic.woff2', 'fonts/lora-latin-600-normal.woff2'
];
self.addEventListener('install', e => {
  e.waitUntil(caches.open(APP).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== APP && k !== TILES).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
async function trimTiles(max) {
  const c = await caches.open(TILES); const keys = await c.keys();
  for (let i = 0; i < keys.length - max; i++) await c.delete(keys[i]);
}
self.addEventListener('fetch', e => {
  const req = e.request; if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.hostname.endsWith('basemaps.cartocdn.com')) {
    // Map tiles: from the phone's cache first, otherwise fetch and keep.
    e.respondWith(caches.open(TILES).then(async c => {
      const hit = await c.match(req.url); if (hit) return hit;
      try { const r = await fetch(req); if (r.ok || r.type === 'opaque') { c.put(req.url, r.clone()); if (Math.random() < 0.02) trimTiles(4000); } return r; }
      catch (err) { return new Response('', { status: 504 }); }
    }));
    return;
  }
  if (url.origin !== location.origin) return;
  if (req.mode === 'navigate' || url.pathname.endsWith('/') || url.pathname.endsWith('index.html')) {
    // The app page: newest version when online, saved copy when not.
    e.respondWith(fetch(req).then(r => { const copy = r.clone(); caches.open(APP).then(c => c.put('index.html', copy)); return r; })
      .catch(() => caches.match('index.html')));
    return;
  }
  e.respondWith(caches.match(req).then(hit => hit || fetch(req)));
});
