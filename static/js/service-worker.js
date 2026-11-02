const CACHE_NAME = 'leonardrao-v2';
const PRECACHE_URLS = [
    '/',
    '/game/',
    '/tools/',
    '/guestbook/',
    '/game/2048/',
    '/game/maze3d/',
    '/game/sudoku/',
    '/game/minesweeper/',
    '/tools/timer/',
    '/tools/stopwatch/',
    '/tools/base-converter/',
    '/static/css/output.css?v=14',
    '/static/favicon.svg',
    '/static/icons/icon-192.png',
    '/static/icons/icon-512.png',
    '/static/manifest.json',
    '/static/games/2048.js',
    '/static/games/maze3d.js',
    '/static/games/sudoku.js',
    '/static/games/minesweeper.js',
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

    const isAsset = url.pathname.startsWith('/static/') ||
        /\.(js|css|png|svg|json|ico|woff|woff2)$/.test(url.pathname);

    if (isAsset) {
        // Stale-while-revalidate: serve cache instantly, refresh in background
        event.respondWith(
            caches.match(request).then(cached => {
                const fetchPromise = fetch(request).then(response => {
                    if (response.ok) {
                        const clone = response.clone();
                        caches.open(CACHE_NAME).then(cache => cache.put(request, clone));
                    }
                    return response;
                }).catch(() => cached);
                return cached || fetchPromise;
            })
        );
    } else {
        // Network-first for pages, fall back to cache when offline
        event.respondWith(
            fetch(request)
                .then(response => {
                    if (response.ok) {
                        const clone = response.clone();
                        caches.open(CACHE_NAME).then(cache => cache.put(request, clone));
                    }
                    return response;
                })
                .catch(() =>
                    caches.match(request).then(cached => cached || caches.match('/'))
                )
        );
    }
});
