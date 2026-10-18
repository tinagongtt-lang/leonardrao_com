const CACHE_NAME = 'leonardrao-v1';
const PRECACHE_URLS = [
    '/',
    '/game/',
    '/tools/',
    '/guestbook/',
    '/game/2048/',
    '/game/maze3d/',
    '/tools/timer/',
    '/tools/stopwatch/',
    '/tools/base-converter/',
    '/static/css/output.css?v=3',
    '/static/favicon.svg',
    '/static/icons/icon-192.png',
    '/static/icons/icon-512.png',
    '/static/manifest.json',
    '/static/games/2048.js',
    '/static/games/maze3d.js',
    '/static/tools/timer.js',
    '/static/tools/stopwatch.js',
    '/static/tools/base_converter.js',
];

self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => cache.addAll(PRECACHE_URLS))
    );
    self.skipWaiting();
});

self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(keys =>
            Promise.all(
                keys.filter(key => key !== CACHE_NAME).map(key => caches.delete(key))
            )
        )
    );
    self.clients.claim();
});

self.addEventListener('fetch', event => {
    const { request } = event;
    if (request.method !== 'GET') return;

    const url = new URL(request.url);
    if (url.origin !== self.location.origin) return;

    const isStatic = url.pathname.startsWith('/static/') || url.pathname.startsWith('/captcha/');
    const isAsset = /\.(js|css|png|svg|json|ico|woff|woff2)$/.test(url.pathname);

    if (isStatic || isAsset) {
        event.respondWith(
            caches.match(request).then(cached => {
                if (cached) return cached;
                return fetch(request).then(response => {
                    const clone = response.clone();
                    caches.open(CACHE_NAME).then(cache => cache.put(request, clone));
                    return response;
                });
            })
        );
    } else {
        event.respondWith(
            fetch(request)
                .then(response => {
                    const clone = response.clone();
                    caches.open(CACHE_NAME).then(cache => cache.put(request, clone));
                    return response;
                })
                .catch(() =>
                    caches.match(request).then(cached => cached || caches.match('/'))
                )
        );
    }
});
