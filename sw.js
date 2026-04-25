/* ============================================================
   ROMANS ROAD — SERVICE WORKER
   Network-first when online (fresh HTML/CSS/JS), cache as fallback
   for offline. Bump CACHE_NAME after deploys when you want every
   client to drop old cached blobs immediately.
   ============================================================ */

const CACHE_NAME = 'romans-road-v3';

const CORE_ASSETS = [
  '/',
  '/index.html',
  '/Romans_Road.html',
  '/Romans_Road_2.html',
  '/Romans_Road_3.html',
  '/search.html',
  '/style.css',
  '/nav.js',
  '/manifest.json',
  'https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,600;1,400&family=Cinzel:wght@400;600&display=swap'
];

function isSameOrigin(url) {
  return url.origin === self.location.origin;
}

function isNavigationRequest(req) {
  return req.mode === 'navigate' || (req.headers.get('accept') || '').includes('text/html');
}

function stash(cache, req, response) {
  if (req.method !== 'GET' || !response || !response.ok) return;
  const clone = response.clone();
  return cache.put(req, clone);
}

// ── INSTALL: warm cache; take control quickly ──────────────
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache =>
        Promise.allSettled(
          CORE_ASSETS.map(u => cache.add(u).catch(() => {}))
        )
      )
      .then(() => self.skipWaiting())
  );
});

// ── ACTIVATE: delete every cache except current ────────────
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

// ── FETCH: network-first on same-origin; cache when offline ─
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);

  if (url.pathname.startsWith('/api/')) {
    event.respondWith(fetch(event.request));
    return;
  }

  if (event.request.method !== 'GET') {
    return;
  }

  // Cross-origin (fonts, etc.): try network, fall back to cache
  if (!isSameOrigin(url)) {
    event.respondWith(
      caches.open(CACHE_NAME).then(cache =>
        fetch(event.request)
          .then(response => {
            if (response.ok) stash(cache, event.request, response);
            return response;
          })
          .catch(() => cache.match(event.request))
      )
    );
    return;
  }

  event.respondWith(
    caches.open(CACHE_NAME).then(cache => {
      const tryNetwork = () =>
        fetch(event.request)
          .then(response => {
            if (response.ok) stash(cache, event.request, response);
            return response;
          })
          .catch(() => cache.match(event.request).then(cached => {
            if (cached) return cached;
            if (isNavigationRequest(event.request)) {
              return cache.match('/index.html');
            }
          }));

      // HTML navigations: always try network first (fresh pages)
      if (isNavigationRequest(event.request)) {
        return tryNetwork();
      }

      // CSS, JS, JSON, documents by URL: network first, cache fallback
      return tryNetwork();
    })
  );
});
