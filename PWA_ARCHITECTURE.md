# 🏗️ BPG Consultas PWA - Arquitectura Técnica

Documentación técnica detallada de la Progressive Web App.

---

## 📐 Diagrama de Arquitectura
```
┌─────────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              index.html (UI)                         │  │
│  │  - Form handlers                                     │  │
│  │  - Display logic                                     │  │
│  │  - Event listeners                                   │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                   APPLICATION LAYER                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                app.js                                │  │
│  │  ┌────────────────────────────────────────────────┐ │  │
│  │  │ State Management                               │ │  │
│  │  │ - isOnline, isProcessing                       │ │  │
│  │  └────────────────────────────────────────────────┘ │  │
│  │  ┌────────────────────────────────────────────────┐ │  │
│  │  │ Query Handler                                  │ │  │
│  │  │ - handleQuerySubmit()                          │ │  │
│  │  │ - queryAPI() / queryOffline()                  │ │  │
│  │  └────────────────────────────────────────────────┘ │  │
│  │  ┌────────────────────────────────────────────────┐ │  │
│  │  │ UI Controller                                  │ │  │
│  │  │ - displayResponse()                            │ │  │
│  │  │ - updateOnlineStatus()                         │ │  │
│  │  └────────────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────┘  │
└───────────────────┬─────────────────┬───────────────────────┘
                    │                 │
        ┌───────────▼──────┐    ┌────▼──────────┐
        │                  │    │               │
┌───────▼──────────┐  ┌────▼────────────┐  ┌───▼──────────────┐
│  SERVICE WORKER  │  │   INDEXEDDB     │  │   API REST       │
│     (sw.js)      │  │    (db.js)      │  │  (Backend)       │
│                  │  │                 │  │                  │
│ ┌──────────────┐ │  │ ┌─────────────┐ │  │ FastAPI + RAG    │
│ │ Cache First  │ │  │ │ BPGConsultas│ │  │                  │
│ │ (Statics)    │ │  │ │  Database   │ │  │ - /query         │
│ └──────────────┘ │  │ │             │ │  │ - /health        │
│ ┌──────────────┐ │  │ │ Store:      │ │  │ - /config        │
│ │Network First │ │  │ │ - history   │ │  │                  │
│ │ (API calls)  │ │  │ └─────────────┘ │  │ ChromaDB         │
│ └──────────────┘ │  │                 │  │ + Ollama         │
└──────────────────┘  └─────────────────┘  └──────────────────┘
```

---

## 🔄 Flujo de Consulta Detallado

### Online Flow
```
1. User submits query
   ↓
2. app.js: handleQuerySubmit()
   - Validar input
   - Setear UI loading state
   ↓
3. app.js: queryAPI(query, k)
   - fetch() a http://localhost:8000/api/v1/query
   - Timeout: 120s
   ↓
4. Service Worker intercepta request
   - Intenta network first
   - Si falla → busca en API_CACHE
   ↓
5. API Backend procesa
   - RAG pipeline: retrieve + generate
   - Retorna JSON con answer + metadata
   ↓
6. Service Worker cachea respuesta exitosa
   - Guarda en API_CACHE_NAME
   ↓
7. app.js recibe respuesta
   - displayResponse(data)
   - saveToHistory(data)
   ↓
8. IndexedDB guarda en tabla 'history'
   ↓
9. UI actualiza
   - Muestra respuesta
   - Agrega a historial visual
   - Toast de éxito
```

### Offline Flow
```
1. User submits query (sin conexión)
   ↓
2. app.js detecta STATE.isOnline === false
   ↓
3. app.js: queryOffline(query)
   - DB.getHistory() → obtiene todas las queries
   - Similarity matching simple:
     * Split query en palabras (> 3 letras)
     * Busca overlaps con queries guardadas
     * Score = matches / total_words
   - Retorna bestMatch si score > 0.3
   ↓
4. Si encuentra match:
   - displayResponse(cachedData)
   - Banner: "📦 Respuesta recuperada de caché"
   ↓
5. Si NO encuentra:
   - displayResponse(error)
   - "No hay datos en caché para esta consulta"
   ↓
6. Toast notifica resultado
```

---

## 🗄️ IndexedDB Schema

### Database: `BPGConsultas`
**Version:** 1

### Object Store: `history`
```javascript
{
  keyPath: 'id',
  autoIncrement: true
}
```

**Índices:**
```javascript
- 'timestamp': unique=false
- 'query': unique=false
```

**Estructura:**
```typescript
interface HistoryItem {
  id: number;
  query: string;
  answer: string;
  strategy: string;
  timestamp: string;
  source: 'api' | 'cache';
  metadata: {
    model?: string;
    total_time?: number;
    num_docs_used?: number;
  }
}
```

---

## ⚙️ Service Worker Strategies

### Cache First (Estáticos)
```javascript
async function cacheFirstStrategy(request) {
  const cached = await caches.match(request);
  if (cached) return cached;
  
  const response = await fetch(request);
  if (response.ok) {
    const cache = await caches.open(CACHE_NAME);
    cache.put(request, response.clone());
  }
  return response;
}
```

### Network First (API)
```javascript
async function networkFirstStrategy(request) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(API_CACHE_NAME);
      cache.put(request, response.clone());
    }
    return response;
  } catch (error) {
    const cached = await caches.match(request);
    if (cached) return cached;
    
    return new Response(
      JSON.stringify({ offline: true }),
      { status: 503 }
    );
  }
}
```

---

## 🎨 CSS Architecture

**Variables CSS + Responsive:**
```css
:root {
  --primary: #2D5016;
  --accent: #FFD700;
  --shadow: 0 2px 8px rgba(0,0,0,0.1);
}

@media (max-width: 768px) {
  /* Tablet/Mobile */
}
```

---

## 🔒 Security

- ✅ XSS Prevention (escapeHtml)
- ✅ CORS configurado
- ✅ Input validation
- ✅ HTTPS requerido (producción)

---

## 📊 Performance Metrics

| Métrica | Valor | Objetivo |
|---------|-------|----------|
| First Load | ~500ms | < 1s |
| Offline Load | ~100ms | < 200ms |
| Query (online) | 5-60s | LLM dependent |
| Query (offline) | ~50ms | < 100ms |

---

## 🚀 Deployment

### Producción

1. HTTPS obligatorio
2. Actualizar `API_BASE_URL`
3. Actualizar `manifest.json`
4. Deploy a servidor web

### Vercel/Netlify
```bash
cd pwa
vercel --prod
```

---

## 📈 Future Optimizations

- Background Sync
- Push Notifications
- Web Share API
- Virtual Scrolling

---

**BPG Consultas PWA v2.1 - Documentación Técnica**
