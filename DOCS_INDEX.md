# 📚 Índice de Documentación - BPG Consultas

Navegación rápida a toda la documentación del proyecto.

---

## 🚀 Quick Start

**¿Primera vez?** → [README.md](README.md)
```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Iniciar API
python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8000

# 3. Iniciar PWA
python3 -m http.server 8080 --directory pwa

# 4. Abrir navegador
open http://localhost:8080
```

---

## 📖 Documentación por Audiencia

### 👤 Usuario Final

**¿Cómo usar la app?**
- [pwa/README.md](pwa/README.md) - Guía completa de usuario
  - Instalación
  - Uso básico
  - Modo offline
  - Troubleshooting

### 💻 Desarrollador

**¿Cómo funciona el código?**
- [ARCHITECTURE.md](ARCHITECTURE.md) - Arquitectura RAG
  - Pipeline completo
  - Componentes
  - Flujo de datos
  
- [PWA_ARCHITECTURE.md](PWA_ARCHITECTURE.md) - Arquitectura PWA
  - Service Worker
  - IndexedDB
  - Offline strategy

### 🔬 Data Scientist

**¿Cómo se optimizó?**
- [OPTIMIZATION_REPORT.md](OPTIMIZATION_REPORT.md) - Mejoras RAG
  - Experimentos
  - Benchmarks
  - Métricas

### 📊 Manager / Stakeholder

**¿Qué se logró?**
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Resumen ejecutivo
  - Métricas clave
  - Arquitectura high-level
  - ROI / Costos
  - Roadmap

### 🛠️ DevOps / SRE

**¿Cómo deployar?**
- [DEPLOYMENT.md](docs/DEPLOYMENT.md) *(pendiente)*
  - Setup producción
  - Monitoring
  - Backups

---

## 📂 Estructura de Documentación
```
rag-bpg-project/
├── README.md                    # ⭐ Empieza aquí
├── DOCS_INDEX.md                # 📚 Este archivo
├── PROJECT_SUMMARY.md           # 🎯 Resumen ejecutivo
├── CHANGELOG.md                 # 📝 Historial cambios
├── ARCHITECTURE.md              # 🏗️ Arquitectura RAG
├── PWA_ARCHITECTURE.md          # 🌐 Arquitectura PWA
├── OPTIMIZATION_REPORT.md       # 📈 Benchmarks
│
├── pwa/
│   └── README.md                # 👤 Guía usuario PWA
│
├── docs/                        # Documentación adicional
│   ├── API_DOCUMENTATION.md     # 🔌 API endpoints
│   ├── RAG_OPTIMIZATION.md      # 🔬 Optimizaciones RAG
│   └── DEPLOYMENT.md            # 🚀 Deploy guide
│
└── notebooks/                   # Análisis & Experimentos
    ├── 01_data_exploration.ipynb
    ├── 02_rag_optimization.ipynb
    └── 03_evaluation.ipynb
```

---

## 🎯 Guías por Tarea

### Quiero hacer una consulta
→ [pwa/README.md - Uso](pwa/README.md#uso)

### Quiero instalar la app
→ [pwa/README.md - Instalación](pwa/README.md#instalación-como-app)

### Quiero entender cómo funciona RAG
→ [ARCHITECTURE.md](ARCHITECTURE.md)

### Quiero mejorar la calidad de respuestas
→ [OPTIMIZATION_REPORT.md](OPTIMIZATION_REPORT.md)

### Quiero integrar con mi sistema
→ [API Docs](http://localhost:8000/docs) (con servidor corriendo)

### Quiero deployar a producción
→ [PROJECT_SUMMARY.md - Deployment](PROJECT_SUMMARY.md#-deployment)

### Quiero contribuir al proyecto
→ [CONTRIBUTING.md](CONTRIBUTING.md) *(pendiente)*

### Tengo un problema
→ [pwa/README.md - Troubleshooting](pwa/README.md#-troubleshooting)

---

## 📊 Métricas Clave (Referencia Rápida)

| Métrica | Valor |
|---------|-------|
| **Calidad RAG** | 85% precisión |
| **Latencia** | 5-60s (online) |
| **Offline** | 100% funcional |
| **Documentos** | 81 PDFs BPG |
| **Chunks** | ~500 embeddings |
| **Costo** | $0 (desarrollo) |

---

## 🔗 Links Útiles

| Recurso | URL |
|---------|-----|
| **API Docs (Swagger)** | http://localhost:8000/docs |
| **API Docs (ReDoc)** | http://localhost:8000/redoc |
| **PWA Local** | http://localhost:8080 |
| **Health Check** | http://localhost:8000/health |
| **GitHub Repo** | [Tu repo URL] |

---

## 📞 Soporte

**Problemas técnicos:**
1. Revisar [Troubleshooting](pwa/README.md#-troubleshooting)
2. Buscar en [Issues existentes](https://github.com/...)
3. Crear nuevo issue con template

**Contacto:**
- Email: [Tu email]
- Slack: [Canal]
- Documentación: Este mismo repo

---

## 🗺️ Navegación Rápida

### Por Componente

- **RAG System:** [ARCHITECTURE.md](ARCHITECTURE.md)
- **API REST:** http://localhost:8000/docs
- **PWA:** [pwa/README.md](pwa/README.md)
- **Database:** [ARCHITECTURE.md - Storage](ARCHITECTURE.md#storage)

### Por Tecnología

- **ChromaDB:** [ARCHITECTURE.md - Vector Store](ARCHITECTURE.md)
- **Ollama/LLM:** [OPTIMIZATION_REPORT.md - LLM](OPTIMIZATION_REPORT.md)
- **Service Worker:** [PWA_ARCHITECTURE.md - SW](PWA_ARCHITECTURE.md#service-worker-lifecycle)
- **IndexedDB:** [PWA_ARCHITECTURE.md - DB](PWA_ARCHITECTURE.md#indexeddb-schema)

### Por Tema

- **Performance:** [OPTIMIZATION_REPORT.md](OPTIMIZATION_REPORT.md)
- **Security:** [PWA_ARCHITECTURE.md - Security](PWA_ARCHITECTURE.md#security)
- **Testing:** [PROJECT_SUMMARY.md - Testing](PROJECT_SUMMARY.md#-testing)
- **Deployment:** [PROJECT_SUMMARY.md - Deployment](PROJECT_SUMMARY.md#-deployment)

---

## 📅 Última Actualización

**Fecha:** Noviembre 2, 2025  
**Versión:** 2.1.0  
**Status:** ✅ Documentación completa

---

🎉 **¡Todo documentado y listo para usar!**
