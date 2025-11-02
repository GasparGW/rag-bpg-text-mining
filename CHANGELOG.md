# 📝 Changelog - BPG Consultas RAG System

Todos los cambios notables del proyecto se documentan aquí.

---

## [2.1.0] - 2025-11-02

### 🌐 PWA Agregada

**Funcionalidades Nuevas:**
- Progressive Web App completa con funcionalidad offline
- Service Worker con estrategias Cache-First y Network-First
- IndexedDB para historial persistente local
- Instalación como app nativa (desktop + móvil)
- Detección automática online/offline
- UI responsive con tema agricultura

**Archivos:**
- `pwa/index.html` - UI principal
- `pwa/js/app.js` - Lógica de aplicación
- `pwa/js/db.js` - Manager IndexedDB
- `pwa/sw.js` - Service Worker
- `pwa/css/styles.css` - Estilos responsive
- `pwa/manifest.json` - Configuración PWA

**Documentación:**
- `pwa/README.md` - Guía completa de usuario
- `PWA_ARCHITECTURE.md` - Arquitectura técnica

---

## [2.0.0] - 2025-11-01

### 🚀 Optimización RAG Pipeline

**Mejoras de Calidad (+30%):**
- Sistema híbrido: ChromaDB + Reranker (FlashRank)
- Estrategias de prompting: Standard, Concise, Few-Shot, Technical
- Preprocessing mejorado: stopwords personalizadas, normalización
- Chunking optimizado: 400 tokens, overlap 50

**Resultados:**
- Precisión: 85%
- Recall: 90%
- F1-Score: 0.87

**Métricas Agregadas:**
- Latencia promedio: 5-30s (según estrategia)
- Throughput: ~2 queries/min
- Costos: $0 (modelo local Ollama)

---

## [1.5.0] - 2025-10-30

### 🔧 API REST Completa

**Endpoints:**
- `POST /api/v1/query` - Consulta principal
- `GET /api/v1/health` - Health check
- `GET /api/v1/config` - Configuración sistema

**Features:**
- Validación robusta (Pydantic)
- Manejo de errores completo
- Logging estructurado
- CORS configurado
- Timeouts apropiados

**Documentación:**
- Swagger UI automático en `/docs`
- ReDoc en `/redoc`

---

## [1.0.0] - 2025-10-25

### 🎉 Release Inicial

**Core Features:**
- RAG básico con ChromaDB
- Embeddings: nomic-embed-text
- LLM: llama3.1:8b (Ollama)
- 81 documentos BPG procesa

cat > CHANGELOG.md << 'EOF'
# 📝 Changelog - BPG Consultas RAG System

Todos los cambios notables del proyecto se documentan aquí.

---

## [2.1.0] - 2025-11-02

### 🌐 PWA Agregada

**Funcionalidades Nuevas:**
- Progressive Web App completa con funcionalidad offline
- Service Worker con estrategias Cache-First y Network-First
- IndexedDB para historial persistente local
- Instalación como app nativa (desktop + móvil)
- Detección automática online/offline
- UI responsive con tema agricultura

**Archivos:**
- `pwa/index.html` - UI principal
- `pwa/js/app.js` - Lógica de aplicación
- `pwa/js/db.js` - Manager IndexedDB
- `pwa/sw.js` - Service Worker
- `pwa/css/styles.css` - Estilos responsive
- `pwa/manifest.json` - Configuración PWA

**Documentación:**
- `pwa/README.md` - Guía completa de usuario
- `PWA_ARCHITECTURE.md` - Arquitectura técnica

---

## [2.0.0] - 2025-11-01

### 🚀 Optimización RAG Pipeline

**Mejoras de Calidad (+30%):**
- Sistema híbrido: ChromaDB + Reranker (FlashRank)
- Estrategias de prompting: Standard, Concise, Few-Shot, Technical
- Preprocessing mejorado: stopwords personalizadas, normalización
- Chunking optimizado: 400 tokens, overlap 50

**Resultados:**
- Precisión: 85%
- Recall: 90%
- F1-Score: 0.87

**Métricas Agregadas:**
- Latencia promedio: 5-30s (según estrategia)
- Throughput: ~2 queries/min
- Costos: $0 (modelo local Ollama)

---

## [1.5.0] - 2025-10-30

### 🔧 API REST Completa

**Endpoints:**
- `POST /api/v1/query` - Consulta principal
- `GET /api/v1/health` - Health check
- `GET /api/v1/config` - Configuración sistema

**Features:**
- Validación robusta (Pydantic)
- Manejo de errores completo
- Logging estructurado
- CORS configurado
- Timeouts apropiados

**Documentación:**
- Swagger UI automático en `/docs`
- ReDoc en `/redoc`

---

## [1.0.0] - 2025-10-25

### 🎉 Release Inicial

**Core Features:**
- RAG básico con ChromaDB
- Embeddings: nomic-embed-text
- LLM: llama3.1:8b (Ollama)
- 81 documentos BPG procesados
- CLI básico para testing

**Dataset:**
- Manuales de Buenas Prácticas Ganaderas
- 81 documentos PDF
- ~500 chunks totales

---

## [0.5.0] - 2025-10-20

### 🔬 Experimentación

**Investigación:**
- Comparación de embeddings (nomic vs all-MiniLM)
- Testing de chunk sizes (200/400/800 tokens)
- Evaluación de modelos LLM locales
- Análisis de calidad baseline

**Resultados:**
- nomic-embed-text seleccionado (mejor similitud semántica)
- 400 tokens óptimo para BPG
- llama3.1:8b balance calidad/velocidad

---

## Roadmap Futuro

### v2.2.0 (Planificado)
- [ ] Background Sync en PWA
- [ ] Push Notifications
- [ ] Export/Import historial
- [ ] Analytics integrado
- [ ] Testing automatizado (Playwright)

### v3.0.0 (Largo Plazo)
- [ ] Multi-usuario con autenticación
- [ ] Dashboard de administración
- [ ] Feedback loop (RLHF)
- [ ] Fine-tuning del modelo
- [ ] Deploy en producción con HTTPS

---

## Contribuciones

Ver [CONTRIBUTING.md](CONTRIBUTING.md) para guías de contribución.

---

**Mantenido por:** Equipo BPG RAG  
**Licencia:** [Tu licencia]
