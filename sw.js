/* ============================================================
   ROMANS ROAD — SERVICE WORKER
   Caches all volumes for offline reading.
   ============================================================ */

const CACHE_NAME = 'romans-road-v2';

const CORE_ASSETS = [
  '/',
  '/index.html',
  '/Romans_Road.html',
  '/Romans_Road_2.html',
  '/style.css',
  '/nav.js',
  '/manifest.json',
  'https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,600;1,400&family=Cinzel:wght@400;600&display=swap'
];

// ── INSTALL: cache all core assets ─────────────────────────
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(CORE_ASSETS))
      .then(() => self.skipWaiting())
  );
});

// ── ACTIVATE: clear old caches ─────────────────────────────
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys
          .filter(key => key !== CACHE_NAME)
          .map(key => caches.delete(key))
      )
    ).then(() => self.clients.claim())
  );
});

// ── FETCH: cache-first for local, network-first for API ────
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);

  // EXPANSION SLOT: API calls bypass cache
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(fetch(event.request));
    return;
  }

  // Cache-first strategy for everything else
  event.respondWith(
    caches.match(event.request).then(cached => {
      if (cached) return cached;
      return fetch(event.request).then(response => {
        // Cache successful GET responses
        if (event.request.method === 'GET' && response.status === 200) {
          const clone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
        }
        return response;
      }).catch(() => {
        // Offline fallback
        if (event.request.destination === 'document') {
          return caches.match('/index.html');
        }
      });
    })
  );
});
