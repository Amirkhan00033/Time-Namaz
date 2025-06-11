const cacheName = 'namaz-app-v1';
const staticAssets = [
  '/',
  '/static/icons/mosque-192.png',
  '/static/icons/mosque-512.png'
];

self.addEventListener('install', async event => {
  const cache = await caches.open(cacheName);
  await cache.addAll(staticAssets);
  return self.skipWaiting();
});

self.addEventListener('activate', event => {
  self.clients.claim();
});

self.addEventListener('fetch', async event => {
  const req = event.request;
  const cache = await caches.open(cacheName);
  const cachedResponse = await cache.match(req);
  return cachedResponse || fetch(req);
});
