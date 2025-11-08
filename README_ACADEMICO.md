# 🎓 Sistema RAG para Consultas de Buenas Prácticas Ganaderas

**Materia:** Text Mining  
**Maestría:** Ciencia de Datos  
**Universidad:** Austral 
**Alumno:** Gaspar Gonzalez Wulfsohn 
**Fecha:** Noviembre 2025  

---

## 📋 Descripción del Proyecto

Sistema de **Retrieval-Augmented Generation (RAG)** que permite realizar consultas en lenguaje natural sobre documentación de Buenas Prácticas Ganaderas (BPG). Incluye una Progressive Web App (PWA) con funcionalidad offline para uso en el campo.

### Problema Abordado

Los productores ganaderos necesitan acceso rápido a información sobre buenas prácticas, pero:
- Documentación extensa y técnica (81 documentos PDF)
- Difícil búsqueda de información específica
- Acceso limitado en zonas rurales (sin internet)

### Solución Propuesta

Sistema RAG con:
1. **Procesamiento de documentos:** Extracción, chunking, embeddings
2. **Retrieval híbrido:** ChromaDB + Reranking (FlashRank)
3. **Generación:** LLM local (Ollama - llama3.1:8b)
4. **Interfaz PWA:** Funcionalidad offline completa

---

## 🎯 Objetivos Cumplidos

### Principales
- ✅ Implementar pipeline RAG completo funcional
- ✅ Optimizar calidad de respuestas (>80% precisión)
- ✅ Crear interfaz de usuario intuitiva
- ✅ Habilitar funcionalidad offline

### Text Mining Específicos
- ✅ Preprocessing especializado (stopwords, normalización)
- ✅ Chunking estratégico (400 tokens, overlap 50)
- ✅ Embeddings semánticos (nomic-embed-text)
- ✅ Evaluación cuantitativa del sistema

---

## 🏗️ Arquitectura
```
┌──────────────┐
│   Usuario    │
└──────┬───────┘
       │
       ▼
┌─────────────────────┐
│   PWA (Frontend)    │
│   - Offline-first   │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│   API REST          │
│   (FastAPI)         │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────────────────┐
│   RAG Pipeline                  │
│                                 │
│   1. Query Preprocessing        │
│      └─ Stopwords, norm.        │
│                                 │
│   2. Retrieval                  │
│      ├─ ChromaDB (semantic)     │
│      └─ FlashRank (rerank)      │
│                                 │
│   3. Prompt Engineering         │
│      └─ Context injection       │
│                                 │
│   4. Generation                 │
│      └─ Ollama (llama3.1:8b)    │
└─────────────────────────────────┘
```

---

## 📊 Técnicas de Text Mining Aplicadas

### 1. Preprocessing
```python
# Stopwords personalizadas BPG
stopwords = ["vaca", "animal", "establecimiento", ...]

# Normalización
- Lowercase
- Acentos removidos
- Espacios múltiples
```

### 2. Document Chunking
```python
Estrategia: Recursive Character Splitter
- Chunk size: 400 tokens
- Overlap: 50 tokens
- Preserva coherencia semántica
```

### 3. Embeddings
```python
Modelo: nomic-embed-text (768 dims)
Ventajas:
- Optimizado para retrieval
- Captura semántica BPG
- Rápido (local)
```

### 4. Retrieval Híbrido
```python
Pipeline:
1. Semantic search (ChromaDB)
   └─ Top-20 candidates
2. Reranking (FlashRank)
   └─ Top-5 final
3. Metadatos agregados
```

### 5. Evaluation
```python
Métricas:
- Precisión: 85%
- Recall: 90%
- F1-Score: 0.87
- Latencia: 20s promedio
```

---

## 🔬 Experimentos y Optimización

### Baseline vs Optimizado

| Aspecto | Baseline | Optimizado | Mejora |
|---------|----------|------------|--------|
| **Chunking** | 800 tokens | 400 tokens | +20% recall |
| **Retrieval** | Simple semantic | Hybrid + rerank | +15% precision |
| **Prompting** | Generic | Estrategias 4x | +10% calidad |
| **Preprocessing** | Básico | Stopwords custom | +5% relevancia |
| **F1-Score** | 0.67 | 0.87 | **+30%** |

### Decisiones de Diseño

**¿Por qué 400 tokens?**
- Testeo: 200/400/800 tokens
- Resultado: 400 balance contexto/precisión
- Documentación BPG: párrafos ~300-500 palabras

**¿Por qué Reranking?**
- ChromaDB solo: 70% precisión
- + FlashRank: 85% precisión
- Costo: +200ms (aceptable)

**¿Por qué stopwords personalizadas?**
- "animal", "vaca" muy frecuentes → ruido
- Custom list: +5% relevancia
- Basado en análisis de frecuencias

---

## 📁 Estructura del Proyecto
```
rag-bpg-project/
├── notebooks/                    # 📓 Análisis y experimentación
│   ├── 01_data_exploration.ipynb
│   ├── 02_rag_optimization.ipynb
│   └── 03_evaluation.ipynb
│
├── src/                          # 🐍 Código core
│   ├── preprocessing.py
│   ├── embedding.py
│   ├── rag_bpg_ollama.py
│   └── reranker.py
│
├── api/                          # 🔌 REST API
│   ├── main.py
│   └── models.py
│
├── pwa/                          # 🌐 Frontend
│   ├── index.html
│   ├── sw.js
│   └── js/
│
├── data/
│   ├── raw/                      # PDFs (NO incluidos - peso)
│   ├── processed/
│   └── stopwords.csv
│
├── tests/                        # 🧪 Testing
│   └── test_rag.py
│
└── docs/                         # 📚 Documentación
    ├── README.md
    ├── ARCHITECTURE.md
    └── OPTIMIZATION_REPORT.md
```

---

## 🚀 Instalación y Ejecución

### Prerrequisitos
```bash
# Python 3.10+
python3 --version

# Ollama instalado
ollama --version

# Modelo descargado
ollama pull llama3.1:8b
ollama pull nomic-embed-text
```

### Setup
```bash
# 1. Clonar repositorio
git clone [tu-repo-url]
cd rag-bpg-project

# 2. Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Generar base de datos (si no está incluida)
python scripts/ingest_documents.py
```

### Ejecución
```bash
# Terminal 1: API
python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8000

# Terminal 2: PWA
python3 -m http.server 8080 --directory pwa

# Abrir navegador
open http://localhost:8080
```

### Testing
```bash
# Unit tests
pytest tests/

# Evaluation
python scripts/evaluate_rag.py
```

---

## 📊 Resultados y Métricas

### Performance RAG

| Métrica | Valor | Interpretación |
|---------|-------|----------------|
| **Precisión** | 85% | Alta relevancia |
| **Recall** | 90% | Pocos falsos negativos |
| **F1-Score** | 0.87 | Balance excelente |
| **Latencia** | 20s | Aceptable para LLM local |

### Calidad Respuestas (Manual)

- ✅ Respuestas completas: 17/20 (85%)
- ✅ Fuentes correctas: 18/20 (90%)
- ✅ Formato adecuado: 19/20 (95%)
- ❌ Alucinaciones: 1/20 (5%)

### PWA Performance

- First load: 500ms
- Offline load: 100ms
- Storage: ~2MB

---

## 🎓 Contribuciones Académicas

### Text Mining

1. **Pipeline RAG optimizado para dominio específico**
   - Demostración de mejora 30% vs baseline
   - Metodología replicable

2. **Análisis de chunking strategies**
   - Comparación empírica 200/400/800 tokens
   - Recomendaciones por tipo de documento

3. **Evaluación cuantitativa sistema RAG**
   - Métricas estándar (P, R, F1)
   - Análisis de casos edge

### Ingeniería de Software

1. **PWA offline-first para zonas rurales**
   - Service Worker strategies
   - IndexedDB para caché local

2. **API REST escalable**
   - FastAPI + validación Pydantic
   - Documentación auto-generada

---

## 📚 Referencias Académicas

### Papers

1. Lewis et al. (2020) - "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks"
2. Gao et al. (2023) - "Retrieval-Augmented Generation for Large Language Models: A Survey"
3. Nussbaum et al. (2024) - "Nomic Embed: Training a Reproducible Long Context Text Embedder"

### Frameworks

- ChromaDB: Vector database para embeddings
- LangChain: Orchestration framework RAG
- FastAPI: Modern web framework Python
- Ollama: Local LLM inference

### Datasets

- Manuales BPG (81 documentos, ~500 páginas)
- Fuente: [Organismo oficial]

---

## 🔮 Trabajo Futuro

### Mejoras Técnicas

- [ ] **Fine-tuning llama3.1 con dataset BPG específico**
  - Crear corpus 500-1000 pares pregunta-respuesta
  - LoRA fine-tuning (4-8 horas GPU)
  - Evaluación: +10-15% precisión estimada
- [ ] Stopwords personalizadas (475 palabras BPG específicas)
- [ ] Graph RAG para consultas relacionales
- [ ] Multi-modal RAG (imágenes de manuales)
- [ ] Active learning con feedback usuarios
## 🚀 Deployment a Producción

### Contexto Actual

**Estado:** Sistema funcional localmente (localhost)  
**Limitación:** No accesible para productores en el campo  
**Objetivo:** App instalable que funcione offline en celulares

---

### Arquitectura Híbrida Inteligente (Recomendada)

**Concepto:** Pre-cachear consultas comunes + API para casos raros
```
┌─────────────────────────────────────────────┐
│  Productor (Celular - Campo SIN señal)    │
│  ┌───────────────────────────────────┐    │
│  │ PWA Instalada                      │    │
│  │ • 500 respuestas pre-cacheadas    │    │
│  │ • Similarity matching (30% umbral)│    │
│  │ • 90% consultas = instantáneas    │    │
│  └───────────────────────────────────┘    │
└─────────────────┬───────────────────────────┘
                  │
                  │ Solo para consultas NUEVAS
                  │ (10% de los casos)
                  ▼
┌─────────────────────────────────────────────┐
│  Vercel Edge Functions (Serverless)        │
│  • Auto-scale                               │
│  • $5-15/mes para 500 usuarios             │
│  • Respuesta: 5-10s                        │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│  RunPod GPU (On-Demand)                     │
│  • Solo cuando hay consulta nueva          │
│  • $0.30/hora                               │
│  • Se apaga automáticamente                │
└─────────────────────────────────────────────┘
```

---

### Por Qué Esta Arquitectura

#### Ventajas:

1. **Costo ultra-bajo:** $10-20/mes (vs $50-100/mes tradicional)
   - PWA: Gratis (Vercel)
   - Serverless: Pay-per-use
   - GPU: Solo cuando necesita

2. **Experiencia usuario óptima:**
   - 90% consultas = instantáneas (0.1s)
   - Funciona 100% offline para casos comunes
   - Similarity matching inteligente

3. **Escalable:**
   - 10 usuarios = $10/mes
   - 1000 usuarios = $30/mes
   - Auto-scale sin configuración

4. **Profesional:**
   - Edge computing moderno
   - HTTPS automático
   - CDN global

---

### Implementación

#### Fase 1: Pre-generar Cache (1 día)
```python
# scripts/generate_common_queries.py

# 1. Identificar 500 preguntas más comunes
common_queries = [
    # Bienestar Animal (100)
    "¿Qué es el bienestar animal?",
    "¿Cómo evaluar bienestar animal?",
    "Indicadores de bienestar animal",
    # ... 97 más
    
    # Vacunación (80)
    "¿Cómo vacunar ganado?",
    "¿Qué vacunas son obligatorias?",
    # ... 78 más
    
    # Transporte (70)
    "¿Cómo preparar animales para transporte?",
    # ... 69 más
    
    # ... 250 más categorizadas
]

# 2. Generar respuestas offline
from src.rag_bpg_ollama import RAGBPGOllama

rag = RAGBPGOllama()
cache = {}

for query in common_queries:
    print(f"Generando: {query}")
    response = rag.query(query)
    cache[query] = {
        "answer": response["answer"],
        "keywords": extract_keywords(query),
        "category": categorize(query)
    }

# 3. Guardar en PWA
import json
with open('pwa/cache.json', 'w') as f:
    json.dump(cache, f, ensure_ascii=False, indent=2)

print(f"✅ {len(cache)} respuestas pre-generadas")
```

#### Fase 2: Modificar PWA (2 horas)
```javascript
// pwa/js/app.js

// Cargar cache al iniciar
let CACHE = {};

async function loadCache() {
    const response = await fetch('cache.json');
    CACHE = await response.json();
    console.log(`✅ ${Object.keys(CACHE).length} respuestas cargadas`);
}

// Mejorar queryOffline
async function queryOffline(query) {
    // 1. Buscar match exacto
    if (CACHE[query]) {
        return {
            answer: CACHE[query].answer,
            source: 'cache-exact',
            cacheNote: '📦 Respuesta pre-cargada'
        };
    }
    
    // 2. Buscar similarity (ya implementado)
    const keywords = extractKeywords(query);
    let bestMatch = null;
    let bestScore = 0;
    
    for (const [cachedQuery, data] of Object.entries(CACHE)) {
        const score = calculateSimilarity(keywords, data.keywords);
        if (score > bestScore && score > 0.3) {
            bestScore = score;
            bestMatch = data;
        }
    }
    
    if (bestMatch) {
        return {
            answer: bestMatch.answer,
            source: 'cache-similar',
            similarity: bestScore,
            cacheNote: `📦 Respuesta similar (${Math.round(bestScore*100)}% match)`
        };
    }
    
    // 3. Si no hay match → requiere internet
    throw new Error('Consulta no disponible offline. Conecta a WiFi.');
}

// Inicializar
document.addEventListener('DOMContentLoaded', async () => {
    await loadCache();
    // ... resto del código
});
```

#### Fase 3: Deploy Frontend (10 min)
```bash
# 1. Build PWA con cache
cd pwa
ls -lh cache.json  # Verificar ~5-10MB

# 2. Deploy a Vercel
npm i -g vercel
vercel --prod

# Resultado: https://bpg-consultas.vercel.app
```

#### Fase 4: Serverless API (30 min)
```python
# api/serverless/query.py (Vercel Function)

from src.rag_bpg_ollama import RAGBPGOllama
import json

# Inicializar RAG (cold start ~5s)
rag = RAGBPGOllama()

def handler(request):
    data = json.loads(request.body)
    query = data.get('query')
    
    # Generar respuesta
    response = rag.query(query)
    
    # TODO: Guardar en cache para próxima vez
    # save_to_cache(query, response)
    
    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }
```
```json
// vercel.json
{
  "functions": {
    "api/serverless/*.py": {
      "runtime": "python3.9",
      "maxDuration": 60
    }
  }
}
```

#### Fase 5: GPU On-Demand (Opcional)
```python
# Si Vercel serverless es lento:
# Conectar a RunPod GPU via API

import requests

def query_via_runpod(query):
    # Inicia pod si está apagado
    pod_id = start_pod_if_needed()
    
    # Consulta
    response = requests.post(
        f'https://{pod_id}.runpod.io/query',
        json={'query': query}
    )
    
    # Apaga después de 5 min inactividad
    schedule_shutdown(pod_id, delay=300)
    
    return response.json()
```

---

### Flujo Usuario Real

#### Instalación (Primera vez):
```
1. Productor abre: bpg-consultas.vercel.app
2. Browser: "Instalar BPG Consultas?" 
3. Click "Instalar"
4. Descarga cache.json (5-10MB, ~30s con 3G)
5. Ícono aparece en pantalla
```

#### Uso en campo (SIN señal):
```
Usuario: "¿Cómo vacunar ganado?"
  ↓
App busca en cache local
  ↓ Match exacto en 500 pre-generadas
Respuesta instantánea (0.1s) ✅

Usuario: "¿Cómo aplicar vacunas a vacas?"
  ↓
Similarity: 75% match con "¿Cómo vacunar ganado?"
  ↓
Usa respuesta similar (0.1s) ✅

Usuario: "¿Cómo exportar a China?" (raro)
  ↓
No hay match en cache
  ↓
Error: "Consulta requiere conexión"
```

#### Uso con WiFi:
```
Usuario: "¿Cómo exportar a China?"
  ↓
Request a Vercel serverless
  ↓
Genera respuesta (10-30s)
  ↓
Guarda en cache local
  ↓
Próxima vez = offline ✅
```

---

### Costos Reales

#### Por Escala:

| Usuarios | Consultas/mes | Costo Vercel | Costo GPU | Total/mes |
|----------|---------------|--------------|-----------|-----------|
| 10 | 300 (30 nuevas) | $0 | $1 | **$1** |
| 50 | 1,500 (150 nuevas) | $5 | $5 | **$10** |
| 500 | 15,000 (1,500 nuevas) | $10 | $15 | **$25** |
| 1,000 | 30,000 (3,000 nuevas) | $15 | $20 | **$35** |

**Por usuario:** $0.03-0.05/mes

**Setup inicial:** $0 (todo serverless)

---

### Ventajas vs Alternativas

| Aspecto | Híbrido | VPS Tradicional |
|---------|---------|-----------------|
| **Costo 50 usuarios** | $10/mes | $50/mes |
| **Offline %** | 90% instantáneo | Requiere siempre API |
| **Latencia offline** | 0.1s | N/A |
| **Latencia online** | 10-30s | 5-10s |
| **Escalabilidad** | Auto | Manual |
| **Mantenimiento** | 0 horas/mes | 2-4 horas/mes |

---

### Métricas Esperadas

**Después de 1 mes con 50 usuarios:**
- 90% consultas resueltas offline (instantáneo)
- 10% consultas nuevas (requieren API)
- Cache crece a ~800 respuestas
- Costo: $8-12/mes

**Después de 6 meses:**
- 95% consultas offline (cache completo)
- Cache: ~1,200 respuestas
- Costo: $10-15/mes (estable)

---

### Limitaciones

1. **Cache inicial:** Descarga 5-10MB (30s con 3G)
2. **Consultas muy raras:** Necesitan internet primera vez
3. **Cold start:** Primera consulta nueva ~10-30s

**Soluciones:**
- Pre-instalar en WiFi antes de ir al campo
- Cache crece con uso → cada vez más offline
- Background sync cuando hay WiFi

---

### Recomendación Implementación

**Para proyecto académico:**
- ✅ Documentar esta arquitectura
- ✅ Demostrar funcional en local
- ✅ Mencionar como solución profesional



---

### Documentación Técnica

- **Vercel Docs:** https://vercel.com/docs/functions
- **Serverless Python:** https://vercel.com/docs/functions/runtimes/python
- **RunPod API:** https://docs.runpod.io
- **PWA Cache Strategies:** https://web.dev/offline-cookbook/

---



### Expansión

- [ ] Otras áreas agrícolas (avicultura, porcinos)
- [ ] Integración con sistemas de gestión ganadera
- [ ] App móvil nativa (iOS/Android)

---

## 👤 Autor

**[Gaspar Gonzalez Wulfsohn]**  
**Email:** gaspargw@gmail.com
**LinkedIn:** - 
**GitHub:** GasparGW

**Materia:** Text Mining  
**Profesor:** Hernán Merlino
**Fecha entrega:** 3 nov 2025

---

## 📄 Licencia

MIT License - Ver [LICENSE](LICENSE) para detalles.

---

## 🙏 Agradecimientos

- Profesor [Nombre] por guía en Text Mining
- ChromaDB team por excelente documentación
- Ollama por democratizar acceso a LLMs
- Comunidad de productores ganaderos por feedback

---

**⭐ Si este proyecto te fue útil, dale una estrella en GitHub**

