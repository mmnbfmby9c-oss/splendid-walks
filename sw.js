/* Splendid London Walks: keeps the app, and map tiles you've already looked at, available offline. */
const APP = 'sw-app-v2';
const TILES = 'sw-osm-v1';      // OpenStreetMap tiles you've viewed
const TILEMETA = 'sw-osm-meta-v1';
const WEEK = 7 * 24 * 3600 * 1000;
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
  const keep = [APP, TILES, TILEMETA];
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => !keep.includes(k)).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
async function trimTiles(max) {
  const c = await caches.open(TILES), m = await caches.open(TILEMETA); const keys = await c.keys();
  for (let i = 0; i < keys.length - max; i++) { await c.delete(keys[i]); await m.delete(keys[i].url); }
}
async function tile(req) {
  const c = await caches.open(TILES), m = await caches.open(TILEMETA);
  const hit = await c.match(req.url);
  if (hit) {
    const t = await m.match(req.url); const age = t ? Date.now() - Number(await t.text()) : Infinity;
    if (age < WEEK) return hit;                       // fresh enough: no network needed
  }
  try {
    const r = await fetch(req);
    if (r.ok || r.type === 'opaque') {
      c.put(req.url, r.clone()); m.put(req.url, new Response(String(Date.now())));
      if (Math.random() < 0.02) trimTiles(3000);
    }
    return r;
  } catch (err) {
    return hit || new Response('', { status: 504 });  // offline: an older tile is better than none
  }
}
self.addEventListener('fetch', e => {
  const req = e.request; if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.hostname === 'tile.openstreetmap.org') { e.respondWith(tile(req)); return; }
  if (url.origin !== location.origin) return;
  if (req.mode === 'navigate' || url.pathname.endsWith('/') || url.pathname.endsWith('index.html')) {
    e.respondWith(fetch(req).then(r => { const copy = r.clone(); caches.open(APP).then(c => c.put('index.html', copy)); return r; })
      .catch(() => caches.match('index.html')));
    return;
  }
  e.respondWith(caches.match(req).then(hit => hit || fetch(req)));
});
