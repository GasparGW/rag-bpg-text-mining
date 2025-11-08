/**
 * BPG Consultas - Service Worker
 * Handles offline caching and background sync
 */

const CACHE_NAME = 'bpg-consultas-v2.1';
const API_CACHE_NAME = 'bpg-api-cache-v2.1';

// Recursos estáticos para cachear
const STATIC_ASSETS = [
    '/pwa/',
    '/pwa/index.html',
    '/pwa/manifest.json',
    '/pwa/css/styles.css',
    '/pwa/js/app.js',
    '/pwa/js/db.js',
    '/pwa/icons/icon-192.png',
    '/pwa/icons/icon-512.png'
];

// ============================================
// INSTALL - Cachear recursos estáticos
// ============================================

self.addEventListener('install', (event) => {
    console.log('🔧 Service Worker: Instalando...');
    
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('📦 Cacheando recursos estáticos');
                return cache.addAll(STATIC_ASSETS);
            })
            .then(() => {
                console.log('✅ Service Worker: Instalado');
                return self.skipWaiting();
            })
            .catch((error) => {
                console.error('❌ Error en install:', error);
            })
    );
});

// ============================================
// ACTIVATE - Limpiar cachés viejos
// ============================================

self.addEventListener('activate', (event) => {
    console.log('🚀 Service Worker: Activando...');
    
    event.waitUntil(
        caches.keys()
            .then((cacheNames) => {
                return Promise.all(
                    cacheNames.map((cacheName) => {
                        if (cacheName !== CACHE_NAME && cacheName !== API_CACHE_NAME) {
                            console.log('🗑️ Eliminando caché viejo:', cacheName);
                            return caches.delete(cacheName);
                        }
                    })
                );
            })
            .then(() => {
                console.log('✅ Service Worker: Activado');
                return self.clients.claim();
            })
    );
});

// ============================================
// FETCH - Estrategia de caché
// ============================================

self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);
    
    // Solo interceptar requests de mismo origen o API
    if (url.origin !== location.origin && !url.href.includes('localhost:8000')) {
        return;
    }
    
    // Estrategia según tipo de request
    if (isAPIRequest(request)) {
        // API: Network First, fallback to Cache
        event.respondWith(networkFirstStrategy(request));
    } else {
        // Estáticos: Cache First, fallback to Network
        event.respondWith(cacheFirstStrategy(request));
    }
});

// ============================================
// ESTRATEGIAS DE CACHÉ
// ============================================

/**
 * Cache First Strategy
 * Intenta servir desde caché, si falla va a red
 * Ideal para: Assets estáticos (CSS, JS, imágenes)
 */
async function cacheFirstStrategy(request) {
    try {
        // Buscar en caché
        const cachedResponse = await caches.match(request);
        
        if (cachedResponse) {
            console.log('📦 Desde caché:', request.url);
            return cachedResponse;
        }
        
        // Si no está en caché, ir a red
        console.log('🌐 Desde red:', request.url);
        const networkResponse = await fetch(request);
        
        // Cachear la respuesta para futuro
        if (networkResponse.ok) {
            const cache = await caches.open(CACHE_NAME);
            cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
        
    } catch (error) {
        console.error('❌ Error en cacheFirstStrategy:', error);
        
        // Fallback: página offline
        if (request.mode === 'navigate') {
            return caches.match('/pwa/index.html');
        }
        
        throw error;
    }
}

/**
 * Network First Strategy
 * Intenta red primero, si falla usa caché
 * Ideal para: Llamadas a API (datos dinámicos)
 */
async function networkFirstStrategy(request) {
    try {
        // Intentar red primero
        console.log('🌐 API desde red:', request.url);
        const networkResponse = await fetch(request);
        
        if (networkResponse.ok) {
            // Cachear respuesta exitosa
            const cache = await caches.open(API_CACHE_NAME);
            cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
        
    } catch (error) {
        console.log('❌ Red falló, buscando en caché:', request.url);
        
        // Si red falla, intentar caché
        const cachedResponse = await caches.match(request);
        
        if (cachedResponse) {
            console.log('📦 Usando respuesta cacheada');
            return cachedResponse;
        }
        
        // Si no hay caché, retornar error offline
        return new Response(
            JSON.stringify({
                success: false,
                error: 'Sin conexión y sin datos en caché',
                offline: true
            }),
            {
                status: 503,
                headers: { 'Content-Type': 'application/json' }
            }
        );
    }
}

// ============================================
// UTILIDADES
// ============================================

function isAPIRequest(request) {
    const url = new URL(request.url);
    return url.pathname.startsWith('/api/') || url.port === '8000';
}

// ============================================
// MENSAJES (desde app.js)
// ============================================

self.addEventListener('message', (event) => {
    console.log('📨 Mensaje recibido:', event.data);
    
    if (event.data.type === 'CHECK_UPDATE') {
        // Verificar si hay actualización disponible
        self.registration.update();
    }
    
    if (event.data.type === 'SKIP_WAITING') {
        // Activar nueva versión inmediatamente
        self.skipWaiting();
    }
    
    if (event.data.type === 'CLEAR_CACHE') {
        // Limpiar caché manualmente
        event.waitUntil(
            caches.keys().then((names) => {
                return Promise.all(names.map(name => caches.delete(name)));
            })
        );
    }
});

// ============================================
// BACKGROUND SYNC (Opcional - para futuro)
// ============================================

self.addEventListener('sync', (event) => {
    console.log('🔄 Background sync:', event.tag);
    
    if (event.tag === 'sync-queries') {
        event.waitUntil(syncPendingQueries());
    }
});

async function syncPendingQueries() {
    // Implementar sincronización de queries pendientes
    // cuando se recupere la conexión
    console.log('🔄 Sincronizando queries pendientes...');
    // TODO: Implementar lógica de sincronización
}

// ============================================
// PUSH NOTIFICATIONS (Opcional - para futuro)
// ============================================

self.addEventListener('push', (event) => {
    console.log('📬 Push notification recibida');
    
    const data = event.data ? event.data.json() : {};
    const title = data.title || 'BPG Consultas';
    const options = {
        body: data.body || 'Nueva actualización disponible',
        icon: '/pwa/icons/icon-192.png',
        badge: '/pwa/icons/icon-192.png',
        vibrate: [200, 100, 200],
        data: data
    };
    
    event.waitUntil(
        self.registration.showNotification(title, options)
    );
});

self.addEventListener('notificationclick', (event) => {
    console.log('🔔 Notificación clickeada');
    
    event.notification.close();
    
    event.waitUntil(
        clients.openWindow('/pwa/')
    );
});

// ============================================
// LOGGING
// ============================================

console.log('🔧 Service Worker cargado - BPG Consultas v2.1');
