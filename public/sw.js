const CACHE_NAME = 'sf-tennis-v9';
const STATIC_ASSETS = [
  '/',
  '/login',
  '/dashboard',
  '/timetable',
  '/admin/groups',
  '/coach/my-groups',
  '/static/css/main.css',
  '/static/icons/icon-192.png?v=8',
  '/static/icons/icon-192-maskable.png?v=8',
  '/static/icons/icon-512.png?v=8',
  '/static/icons/icon-512-maskable.png?v=8',
  '/manifest.json?v=8'
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(STATIC_ASSETS);
    })
  );
  self.skipWaiting();
});

// Activate event - clean old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME)
          .map((name) => caches.delete(name))
      );
    })
  );
  self.clients.claim();
});

// Fetch event - network first, fallback to cache
self.addEventListener('fetch', (event) => {
  // Skip non-GET requests
  if (event.request.method !== 'GET') return;

  // Skip external requests
  const url = new URL(event.request.url);
  if (url.origin !== location.origin) {
    return;
  }

  event.respondWith(
    // Bypass browser HTTP cache so SW always gets fresh data
    fetch(event.request, { cache: 'no-cache' })
      .then((response) => {
        // Clone and cache successful responses
        if (response.ok) {
          const cloned = response.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, cloned);
          });
        }
        return response;
      })
      .catch(() => {
        // Network failed, try cache
        return caches.match(event.request).then((cached) => {
          return cached || caches.match('/');
        });
      })
  );
});
