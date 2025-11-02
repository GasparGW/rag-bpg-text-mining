/**
 * BPG Consultas - IndexedDB Manager
 * Handles offline storage for queries and responses
 */

const DB = (() => {
    const DB_NAME = 'BPGConsultas';
    const DB_VERSION = 1;
    const STORE_HISTORY = 'history';
    
    let db = null;

    // ============================================
    // INICIALIZACIÓN
    // ============================================

    async function init() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open(DB_NAME, DB_VERSION);
            
            request.onerror = () => {
                console.error('❌ Error abriendo IndexedDB:', request.error);
                reject(request.error);
            };
            
            request.onsuccess = () => {
                db = request.result;
                console.log('✅ IndexedDB inicializado');
                resolve(db);
            };
            
            request.onupgradeneeded = (event) => {
                const db = event.target.result;
                
                // Crear store de historial
                if (!db.objectStoreNames.contains(STORE_HISTORY)) {
                    const historyStore = db.createObjectStore(STORE_HISTORY, {
                        keyPath: 'id',
                        autoIncrement: true
                    });
                    
                    // Índices para búsqueda eficiente
                    historyStore.createIndex('timestamp', 'timestamp', { unique: false });
                    historyStore.createIndex('query', 'query', { unique: false });
                    
                    console.log('✅ Store "history" creado');
                }
            };
        });
    }

    // ============================================
    // HISTORIAL - CREATE
    // ============================================

    async function addHistory(data) {
        return new Promise((resolve, reject) => {
            const transaction = db.transaction([STORE_HISTORY], 'readwrite');
            const store = transaction.objectStore(STORE_HISTORY);
            
            const historyItem = {
                query: data.query,
                answer: data.answer,
                strategy: data.strategy || 'standard',
                timestamp: data.timestamp || new Date().toISOString(),
                source: data.source || 'api',
                metadata: {
                    model: data.model,
                    total_time: data.total_time,
                    num_docs_used: data.num_docs_used
                }
            };
            
            const request = store.add(historyItem);
            
            request.onsuccess = () => {
                console.log('✅ Item guardado en historial:', request.result);
                
                // Limpiar historial viejo si supera el límite
                cleanOldHistory();
                
                resolve(request.result);
            };
            
            request.onerror = () => {
                console.error('❌ Error guardando en historial:', request.error);
                reject(request.error);
            };
        });
    }

    // ============================================
    // HISTORIAL - READ
    // ============================================

    async function getHistory(limit = 50) {
        return new Promise((resolve, reject) => {
            const transaction = db.transaction([STORE_HISTORY], 'readonly');
            const store = transaction.objectStore(STORE_HISTORY);
            const index = store.index('timestamp');
            
            const request = index.openCursor(null, 'prev'); // Más recientes primero
            const results = [];
            
            request.onsuccess = (event) => {
                const cursor = event.target.result;
                
                if (cursor && results.length < limit) {
                    results.push({
                        id: cursor.value.id,
                        ...cursor.value
                    });
                    cursor.continue();
                } else {
                    resolve(results);
                }
            };
            
            request.onerror = () => {
                console.error('❌ Error leyendo historial:', request.error);
                reject(request.error);
            };
        });
    }

    async function getHistoryItem(id) {
        return new Promise((resolve, reject) => {
            const transaction = db.transaction([STORE_HISTORY], 'readonly');
            const store = transaction.objectStore(STORE_HISTORY);
            const request = store.get(id);
            
            request.onsuccess = () => {
                resolve(request.result);
            };
            
            request.onerror = () => {
                console.error('❌ Error obteniendo item:', request.error);
                reject(request.error);
            };
        });
    }

    // ============================================
    // HISTORIAL - DELETE
    // ============================================

    async function deleteHistoryItem(id) {
        return new Promise((resolve, reject) => {
            const transaction = db.transaction([STORE_HISTORY], 'readwrite');
            const store = transaction.objectStore(STORE_HISTORY);
            const request = store.delete(id);
            
            request.onsuccess = () => {
                console.log('✅ Item eliminado del historial');
                resolve();
            };
            
            request.onerror = () => {
                console.error('❌ Error eliminando item:', request.error);
                reject(request.error);
            };
        });
    }

    async function clearHistory() {
        return new Promise((resolve, reject) => {
            const transaction = db.transaction([STORE_HISTORY], 'readwrite');
            const store = transaction.objectStore(STORE_HISTORY);
            const request = store.clear();
            
            request.onsuccess = () => {
                console.log('✅ Historial limpiado');
                resolve();
            };
            
            request.onerror = () => {
                console.error('❌ Error limpiando historial:', request.error);
                reject(request.error);
            };
        });
    }

    // ============================================
    // MANTENIMIENTO
    // ============================================

    async function cleanOldHistory(maxItems = 100) {
        const history = await getHistory(1000); // Obtener todos
        
        if (history.length > maxItems) {
            const toDelete = history.slice(maxItems); // Items más viejos
            
            for (const item of toDelete) {
                await deleteHistoryItem(item.id);
            }
            
            console.log(`🗑️ Limpiados ${toDelete.length} items viejos del historial`);
        }
    }

    async function getStorageSize() {
        if ('storage' in navigator && 'estimate' in navigator.storage) {
            const estimate = await navigator.storage.estimate();
            return {
                usage: estimate.usage,
                quota: estimate.quota,
                usagePercent: ((estimate.usage / estimate.quota) * 100).toFixed(2)
            };
        }
        return null;
    }

    // ============================================
    // BÚSQUEDA
    // ============================================

    async function searchHistory(searchTerm) {
        const history = await getHistory(100);
        const term = searchTerm.toLowerCase();
        
        return history.filter(item => 
            item.query.toLowerCase().includes(term) ||
            item.answer.toLowerCase().includes(term)
        );
    }

    // ============================================
    // ESTADÍSTICAS
    // ============================================

    async function getStats() {
        const history = await getHistory(1000);
        
        const totalQueries = history.length;
        const strategyCounts = {};
        const sourceCounts = { api: 0, cache: 0 };
        
        history.forEach(item => {
            // Estrategias
            strategyCounts[item.strategy] = (strategyCounts[item.strategy] || 0) + 1;
            
            // Fuentes
            if (item.source) {
                sourceCounts[item.source] = (sourceCounts[item.source] || 0) + 1;
            }
        });
        
        return {
            totalQueries,
            strategies: strategyCounts,
            sources: sourceCounts,
            oldestQuery: history[history.length - 1]?.timestamp,
            newestQuery: history[0]?.timestamp
        };
    }

    // ============================================
    // EXPORT/IMPORT (para backup)
    // ============================================

    async function exportHistory() {
        const history = await getHistory(1000);
        const dataStr = JSON.stringify(history, null, 2);
        const blob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `bpg-history-${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        
        URL.revokeObjectURL(url);
    }

    async function importHistory(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            
            reader.onload = async (e) => {
                try {
                    const data = JSON.parse(e.target.result);
                    
                    for (const item of data) {
                        await addHistory(item);
                    }
                    
                    resolve(data.length);
                } catch (error) {
                    reject(error);
                }
            };
            
            reader.onerror = () => reject(reader.error);
            reader.readAsText(file);
        });
    }

    // ============================================
    // API PÚBLICA
    // ============================================

    return {
        init,
        
        // CRUD Historial
        addHistory,
        getHistory,
        getHistoryItem,
        deleteHistoryItem,
        clearHistory,
        
        // Utilidades
        searchHistory,
        getStats,
        getStorageSize,
        
        // Backup
        exportHistory,
        importHistory
    };
})();

// Auto-inicializar si está disponible
if (typeof window !== 'undefined') {
    window.DB = DB;
}
