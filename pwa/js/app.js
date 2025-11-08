/**
 * BPG Consultas - PWA Main Application
 * Handles UI, API calls, offline functionality
 */

// ============================================
// CONFIGURACIÓN
// ============================================

const CONFIG = {
    API_BASE_URL: 'http://localhost:8000',
    API_TIMEOUT: 120000, // 2 minutos
    MAX_HISTORY_ITEMS: 50
};

// ============================================
// ESTADO GLOBAL
// ============================================

const STATE = {
    isOnline: navigator.onLine,
    isProcessing: false,
    deferredPrompt: null
};

// ============================================
// ELEMENTOS DOM
// ============================================

const DOM = {
    queryForm: document.getElementById('query-form'),
    queryInput: document.getElementById('query-input'),
    charCount: document.getElementById('char-count'),
    submitBtn: document.getElementById('submit-btn'),
    btnText: document.querySelector('.btn-text'),
    btnLoader: document.querySelector('.btn-loader'),
    
    strategySelect: document.getElementById('strategy'),
    kInput: document.getElementById('k'),
    
    responseSection: document.getElementById('response-section'),
    responseContent: document.getElementById('response-content'),
    responseMeta: document.getElementById('response-meta'),
    
    historyList: document.getElementById('history-list'),
    clearHistoryBtn: document.getElementById('clear-history'),
    
    status: document.getElementById('status'),
    statusText: document.getElementById('status-text'),
    
    installBtn: document.getElementById('install-btn'),
    
    aboutModal: document.getElementById('about-modal'),
    aboutLink: document.getElementById('about-link'),
    helpLink: document.getElementById('help-link'),
    
    toastContainer: document.getElementById('toast-container')
};

// ============================================
// INICIALIZACIÓN
// ============================================

document.addEventListener('DOMContentLoaded', async () => {
    console.log('🚀 Iniciando BPG Consultas PWA');
    
    // Inicializar DB
    await DB.init();
    
    // Cargar historial
    loadHistory();
    
    // Setup event listeners
    setupEventListeners();
    
    // Check online status
    updateOnlineStatus();
    
    // Check for updates
    checkForUpdates();
    
    console.log('✅ PWA inicializada');
});

// ============================================
// EVENT LISTENERS
// ============================================

function setupEventListeners() {
    // Form submission
    DOM.queryForm.addEventListener('submit', handleQuerySubmit);
    
    // Character counter
    DOM.queryInput.addEventListener('input', updateCharCount);
    
    // Clear history
    DOM.clearHistoryBtn.addEventListener('click', handleClearHistory);
    
    // Online/Offline events
    window.addEventListener('online', updateOnlineStatus);
    window.addEventListener('offline', updateOnlineStatus);
    
    // PWA Install
    window.addEventListener('beforeinstallprompt', handleBeforeInstall);
    DOM.installBtn.addEventListener('click', handleInstallClick);
    
    // Modals
    DOM.aboutLink.addEventListener('click', (e) => {
        e.preventDefault();
        showModal(DOM.aboutModal);
    });
    
    document.querySelectorAll('.modal-close').forEach(btn => {
        btn.addEventListener('click', () => hideModal(btn.closest('.modal')));
    });
    
    DOM.aboutModal.addEventListener('click', (e) => {
        if (e.target === DOM.aboutModal) hideModal(DOM.aboutModal);
    });
    
    // Help
    DOM.helpLink.addEventListener('click', (e) => {
        e.preventDefault();
        showToast('💡 Tip: Esta app funciona sin conexión. Tus consultas se guardan localmente.', 'success');
    });
}

// ============================================
// QUERY HANDLING
// ============================================

async function handleQuerySubmit(e) {
    e.preventDefault();
    
    if (STATE.isProcessing) return;
    
    const query = DOM.queryInput.value.trim();
    if (!query) return;
    
    const k = parseInt(DOM.kInput.value);
    
    // UI Loading state
    setLoadingState(true);
    
    try {
        let result;
        
        if (STATE.isOnline) {
            // Online: llamar a API
            result = await queryAPI(query, k);  // ✅ CORREGIDO: sin strategy
        } else {
            // Offline: buscar en caché
            result = await queryOffline(query);
        }
        
        // Mostrar respuesta
        displayResponse(result);
        
        // Guardar en historial
        await saveToHistory({
            query,
            answer: result.answer,
            strategy: result.strategy || 'standard',  // ✅ CORREGIDO: valor por defecto
            timestamp: new Date().toISOString(),
            source: STATE.isOnline ? 'api' : 'cache'
        });
        
        // Recargar historial
        loadHistory();
        
        // Success toast
        showToast('✅ Consulta procesada', 'success');
        
    } catch (error) {
        console.error('Error en query:', error);
        showToast(`❌ Error: ${error.message}`, 'error');
        
        // Intentar respuesta genérica offline
        if (!STATE.isOnline) {
            displayResponse({
                answer: 'No hay conexión y no hay datos en caché para esta consulta. Por favor, intenta cuando tengas conexión.',
                query,
                source: 'offline-error'
            });
        }
    } finally {
        setLoadingState(false);
    }
}

async function queryAPI(query, k) {  // ✅ CORREGIDO: sin strategy
    const response = await fetch(`${CONFIG.API_BASE_URL}/api/v1/query`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            query,
            k
        }),
        signal: AbortSignal.timeout(CONFIG.API_TIMEOUT)
    });
    
    if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
    }
    
    const data = await response.json();
    
    if (!data.success) {
        throw new Error(data.error || 'Error desconocido');
    }
    
    return data;
}

async function queryOffline(query) {
    // Buscar en historial queries similares
    const history = await DB.getHistory();
    
    // Simple similarity: buscar query que contenga palabras clave
    const queryWords = query.toLowerCase().split(' ').filter(w => w.length > 3);
    
    let bestMatch = null;
    let bestScore = 0;
    
    for (const item of history) {
        const itemWords = item.query.toLowerCase().split(' ');
        const matches = queryWords.filter(w => itemWords.some(iw => iw.includes(w)));
        const score = matches.length / queryWords.length;
        
        if (score > bestScore && score > 0.3) {
            bestScore = score;
            bestMatch = item;
        }
    }
    
    if (bestMatch) {
        return {
            ...bestMatch,
            source: 'cache',
            cacheNote: '📦 Respuesta recuperada de caché (sin conexión)'
        };
    }
    
    throw new Error('No hay datos en caché para esta consulta');
}

// ============================================
// UI UPDATES
// ============================================

function displayResponse(data) {
    // Mostrar sección
    DOM.responseSection.style.display = 'block';
    
    // Contenido
    let content = data.answer;
    if (data.cacheNote) {
        content = `<div style="background: #fff3cd; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">${data.cacheNote}</div>\n\n${content}`;
    }
    DOM.responseContent.innerHTML = formatAnswer(content);
    
    // Metadata
    const meta = [];
    if (data.strategy) meta.push(`<span>📝 ${data.strategy}</span>`);
    if (data.model) meta.push(`<span>🤖 ${data.model}</span>`);
    if (data.total_time) meta.push(`<span>⏱️ ${data.total_time.toFixed(1)}s</span>`);
    if (data.num_docs_used) meta.push(`<span>📚 ${data.num_docs_used} docs</span>`);
    if (data.source) meta.push(`<span>🔗 ${data.source === 'api' ? 'Online' : 'Caché'}</span>`);
    
    DOM.responseMeta.innerHTML = meta.join('');
    
    // Scroll to response
    DOM.responseSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function formatAnswer(text) {
    // Convertir viñetas
    text = text.replace(/^[•·-]\s/gm, '<li>');
    
    // Detectar listas
    const lines = text.split('\n');
    let inList = false;
    const formatted = [];
    
    for (const line of lines) {
        if (line.startsWith('<li>')) {
            if (!inList) {
                formatted.push('<ul>');
                inList = true;
            }
            formatted.push(line + '</li>');
        } else {
            if (inList) {
                formatted.push('</ul>');
                inList = false;
            }
            if (line.trim()) {
                formatted.push(`<p>${line}</p>`);
            }
        }
    }
    
    if (inList) formatted.push('</ul>');
    
    return formatted.join('\n');
}

function setLoadingState(loading) {
    STATE.isProcessing = loading;
    DOM.submitBtn.disabled = loading;
    DOM.btnText.style.display = loading ? 'none' : 'inline';
    DOM.btnLoader.style.display = loading ? 'inline' : 'none';
    DOM.queryInput.disabled = loading;
}

function updateCharCount() {
    const count = DOM.queryInput.value.length;
    DOM.charCount.textContent = count;
    
    if (count > 450) {
        DOM.charCount.style.color = 'var(--error)';
    } else if (count > 400) {
        DOM.charCount.style.color = 'var(--warning)';
    } else {
        DOM.charCount.style.color = 'var(--text-secondary)';
    }
}

// ============================================
// HISTORIAL
// ============================================

async function loadHistory() {
    const history = await DB.getHistory();
    
    if (history.length === 0) {
        DOM.historyList.innerHTML = '<p class="empty-state">No hay consultas guardadas</p>';
        return;
    }
    
    DOM.historyList.innerHTML = history.map(item => `
        <div class="history-item" data-id="${item.id}">
            <div class="history-query">${escapeHtml(item.query)}</div>
            <div class="history-answer">${escapeHtml(item.answer.substring(0, 150))}...</div>
            <div class="history-date">${formatDate(item.timestamp)}</div>
        </div>
    `).join('');
    
    // Click handlers
    document.querySelectorAll('.history-item').forEach(item => {
        item.addEventListener('click', () => {
            const id = parseInt(item.dataset.id);
            loadHistoryItem(id);
        });
    });
}

async function loadHistoryItem(id) {
    const item = await DB.getHistoryItem(id);
    if (item) {
        displayResponse(item);
        showToast('📚 Cargado desde historial', 'success');
    }
}

async function saveToHistory(data) {
    await DB.addHistory(data);
}

async function handleClearHistory() {
    if (confirm('¿Seguro que quieres borrar todo el historial?')) {
        await DB.clearHistory();
        loadHistory();
        showToast('🗑️ Historial borrado', 'success');
    }
}

// ============================================
// ONLINE/OFFLINE
// ============================================

function updateOnlineStatus() {
    STATE.isOnline = navigator.onLine;
    
    if (STATE.isOnline) {
        DOM.status.className = 'status online';
        DOM.statusText.textContent = 'Conectado';
        showToast('✅ Conexión restaurada', 'success');
    } else {
        DOM.status.className = 'status offline';
        DOM.statusText.textContent = 'Sin conexión';
        showToast('📵 Modo offline - Se usará caché', 'warning');
    }
}

// ============================================
// PWA INSTALL
// ============================================

function handleBeforeInstall(e) {
    e.preventDefault();
    STATE.deferredPrompt = e;
    DOM.installBtn.style.display = 'inline-block';
}

async function handleInstallClick() {
    if (!STATE.deferredPrompt) return;
    
    STATE.deferredPrompt.prompt();
    const result = await STATE.deferredPrompt.userChoice;
    
    if (result.outcome === 'accepted') {
        showToast('✅ App instalada correctamente', 'success');
    }
    
    STATE.deferredPrompt = null;
    DOM.installBtn.style.display = 'none';
}

// ============================================
// MODALS & TOASTS
// ============================================

function showModal(modal) {
    modal.classList.add('show');
}

function hideModal(modal) {
    modal.classList.remove('show');
}

function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    
    DOM.toastContainer.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s ease-out reverse';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ============================================
// UTILIDADES
// ============================================

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(isoString) {
    const date = new Date(isoString);
    const now = new Date();
    const diff = now - date;
    
    if (diff < 60000) return 'Hace un momento';
    if (diff < 3600000) return `Hace ${Math.floor(diff / 60000)} min`;
    if (diff < 86400000) return `Hace ${Math.floor(diff / 3600000)} h`;
    
    return date.toLocaleDateString('es-AR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function checkForUpdates() {
    if ('serviceWorker' in navigator && navigator.serviceWorker.controller) {
        navigator.serviceWorker.controller.postMessage({ type: 'CHECK_UPDATE' });
    }
}

// ============================================
// EXPORT (para testing)
// ============================================

window.BPGApp = {
    queryAPI,
    queryOffline,
    loadHistory,
    STATE,
    CONFIG
};