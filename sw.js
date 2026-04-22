/* ============================================================
   ROMANS ROAD — SERVICE WORKER
   Cache disabled. Always serve fresh content from network.
   ============================================================ */

// Clear all existing caches on activate
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.map(key => caches.delete(key))))
      .then(() => self.clients.claim())
      .then(() => {
        self.clients.matchAll({ type: 'window' }).then(clients => {
          clients.forEach(client => client.navigate(client.url));
        });
      })
  );
});
