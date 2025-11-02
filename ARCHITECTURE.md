# 🏗️ Arquitectura del Sistema RAG BPG

## 📋 Índice
- [Visión General](#visión-general)
- [Componentes del Sistema](#componentes-del-sistema)
- [Flujo de Datos](#flujo-de-datos)
- [Configuración](#configuración)
- [Uso del Sistema](#uso-del-sistema)
- [Testing](#testing)

---

## 🎯 Visión General

Sistema RAG (Retrieval-Augmented Generation) profesional para consultas sobre Buenas Prácticas Ganaderas (BPG) en Argentina. Combina:

- **ChromaDB**: Base de datos vectorial para retrieval semántico
- **Sentence Transformers**: Embeddings multilingües
- **Ollama**: Generación de respuestas con LLMs locales
- **Sistema de Configuración**: Parámetros centralizados
- **Estrategias de Prompts**: Prompts modulares y optimizados
- **Validación de Respuestas**: Control de calidad automático

---

## 🏛️ Componentes del Sistema

### 1. **Configuración (`config/`)**
```
config/
├── __init__.py
└── settings.py          # RAGConfig, DEFAULT_CONFIG, etc.
```

**Responsabilidades:**
- Centralizar todos los parámetros configurables
- Proveer configuraciones predefinidas (DEFAULT, DEV, FAST, TECHNICAL)
- Validar parámetros al instanciar

**Uso:**
```python
from config.settings import RAGConfig

config = RAGConfig(
    ollama_model="llama3.2",
    prompt_strategy="fewshot",
    enable_validation=True
)
```

---

### 2. **Estrategias de Prompts (`prompts/`)**
```
prompts/
├── __init__.py
└── strategies.py        # BasePromptStrategy, PromptFactory
```

**Estrategias Disponibles:**

| Estrategia | Tokens | Uso Recomendado |
|-----------|--------|-----------------|
| **Standard** | 500 | Consultas generales, balanceada |
| **Concise** | 300 | Respuestas rápidas y directas |
| **Few-Shot** | 600 | Queries complejas, necesita ejemplos |
| **Technical** | 700 | Normativas, especificaciones técnicas |

**Patrón de Diseño:** Strategy Pattern + Factory Pattern

**Uso:**
```python
from prompts.strategies import PromptFactory, PromptType

strategy = PromptFactory.get_strategy(PromptType.FEWSHOT)
prompt = strategy.build(context, query)
```

---

### 3. **Validadores (`utils/`)**
```
utils/
├── __init__.py
└── validators.py        # ResponseValidator, ValidationReport
```

**Validaciones Implementadas:**
- ✅ Longitud apropiada
- ✅ Contenido sustancial
- ✅ Estructura clara (viñetas, párrafos)
- ✅ Detección de alucinaciones
- ✅ Mensajes de fallback apropiados
- ✅ Español correcto (voseo argentino)
- ✅ Relevancia con la pregunta

**Uso:**
```python
from utils.validators import ResponseValidator

validator = ResponseValidator(min_length=50, max_length=2000)
result = validator.validate_response(response, context, query)

# result = {
#     'is_valid': True/False,
#     'score': 0.85,
#     'validations': {...},
#     'recommendations': [...]
# }
```

---

### 4. **Sistema RAG Principal (`rag_bpg_ollama.py`)**

**Clase Principal:** `RAGSystemBPG`

**Métodos Clave:**
```python
class RAGSystemBPG:
    def __init__(config=None, **legacy_params)
        # Inicializa todo el sistema
    
    def retrieve_documents(query, k=5, min_similarity=0.0)
        # Recupera documentos relevantes
    
    def generate_answer(query, context_docs, temperature, max_tokens)
        # Genera respuesta con LLM
    
    def query(pregunta, k, temperature, verbose)
        # Pipeline completo: retrieve + generate
    
    def chat_interactivo()
        # Modo chat para pruebas interactivas
```

---

## 🔄 Flujo de Datos
```
┌─────────────────┐
│  Usuario hace   │
│    pregunta     │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│           RAGSystemBPG.query()              │
└────────┬────────────────────────┬───────────┘
         │                        │
         ▼                        │
┌──────────────────┐              │
│   RETRIEVAL      │              │
│                  │              │
│ 1. Embedding     │              │
│    de la query   │              │
│                  │              │
│ 2. Búsqueda en   │              │
│    ChromaDB      │              │
│                  │              │
│ 3. Top-K docs    │              │
│    relevantes    │              │
└────────┬─────────┘              │
         │                        │
         ▼                        │
┌──────────────────┐              │
│   GENERATION     │              │
│                  │              │
│ 1. Construir     │              │
│    contexto      │              │
│                  │              │
│ 2. Seleccionar   │◄─────────────┘
│    estrategia    │   (config.prompt_strategy)
│    de prompt     │
│                  │
│ 3. Llamar a      │
│    Ollama        │
│                  │
│ 4. Validar       │
│    respuesta     │
└────────┬─────────┘
         │
         ▼
┌─────────────────┐
│   Respuesta +   │
│    metadata +   │
│   validación    │
└─────────────────┘
```

---

## ⚙️ Configuración

### Configuraciones Predefinidas
```python
from config.settings import (
    DEFAULT_CONFIG,    # Configuración estándar
    DEV_CONFIG,        # Para desarrollo (con validación)
    FAST_CONFIG,       # Respuestas rápidas (k=3, concise)
    TECHNICAL_CONFIG   # Consultas técnicas (k=7, technical)
)
```

### Configuración Personalizada
```python
config = RAGConfig(
    # ChromaDB
    chroma_db_path="models/chroma_db",
    collection_name="bpg_manuals",
    
    # Embeddings
    embedding_model="paraphrase-multilingual-mpnet-base-v2",
    
    # Ollama
    ollama_base_url="http://localhost:11434",
    ollama_model="llama3.2",
    ollama_timeout=120,
    
    # Retrieval
    default_k=5,
    min_similarity=0.0,
    
    # Generation
    default_temperature=0.7,
    default_max_tokens=500,
    prompt_strategy="standard",
    
    # Validación
    enable_validation=True,
    min_answer_length=50,
    max_answer_length=2000,
    
    # Logging
    verbose=True
)
```

---

## 🚀 Uso del Sistema

### Modo 1: Básico (Legacy)
```python
from rag_bpg_ollama import RAGSystemBPG

rag = RAGSystemBPG()
resultado = rag.query("¿Cómo manejar el agua en feedlot?")
print(resultado['answer'])
```

### Modo 2: Con Configuración
```python
from config.settings import RAGConfig
from rag_bpg_ollama import RAGSystemBPG

config = RAGConfig(
    prompt_strategy="fewshot",
    enable_validation=True
)

rag = RAGSystemBPG(config=config)
resultado = rag.query("¿Qué pendiente debe tener la rampa?")

print(resultado['answer'])
print(f"Calidad: {resultado['validation']['score']:.1%}")
```

### Modo 3: Chat Interactivo
```python
from rag_bpg_ollama import RAGSystemBPG

rag = RAGSystemBPG()
rag.chat_interactivo()
```

---

## 🧪 Testing

### Estructura de Tests
```
tests/
├── test_config.py                 # Tests de configuración
├── test_prompts.py               # Tests de estrategias
├── test_integration_simple.py     # Tests básicos de integración
├── test_prompts_integration.py    # Tests de prompts en RAG
├── test_validators.py            # Tests de validadores
└── test_end_to_end.py            # Tests E2E completos
```

### Ejecutar Tests
```bash
# Todos los tests
python3 tests/test_config.py
python3 tests/test_prompts.py
python3 tests/test_integration_simple.py
python3 tests/test_prompts_integration.py
python3 tests/test_validators.py
python3 tests/test_end_to_end.py

# O ejecutar verificación completa
python3 verify_system.py
```

---

## 📊 Métricas y Monitoreo

### Respuesta del Sistema

Cada llamada a `query()` retorna:
```python
{
    'answer': str,                    # Respuesta generada
    'query': str,                     # Pregunta original
    'model': str,                     # Modelo usado
    'strategy': str,                  # Estrategia de prompt
    'temperature': float,             # Temperatura usada
    'max_tokens': int,               # Max tokens
    'num_docs_used': int,            # Docs recuperados
    'k_used': int,                   # K usado
    'retrieved_docs': List[Dict],    # Docs recuperados
    'total_eval_duration': float,    # Tiempo de generación
    'timestamp': str,                # Timestamp ISO
    'validation': Dict,              # Resultado de validación
    'success': bool                  # Si fue exitoso
}
```

### Validación de Calidad
```python
validation = {
    'is_valid': True,
    'score': 0.875,  # 87.5% de calidad
    'validations': {
        'length_ok': True,
        'has_content': True,
        'has_structure': True,
        'not_hallucinating': True,
        'has_fallback': True,
        'no_code_blocks': True,
        'proper_spanish': True,
        'answers_question': True
    },
    'recommendations': ['✅ Respuesta cumple con todos los criterios']
}
```

---

## 🔧 Mantenimiento y Extensión

### Agregar Nueva Estrategia de Prompt

1. Crear clase que hereda de `BasePromptStrategy`
2. Implementar métodos abstractos
3. Registrar en `PromptFactory`
```python
class CustomPromptStrategy(BasePromptStrategy):
    @property
    def name(self) -> str:
        return "Custom"
    
    @property
    def max_tokens_recommended(self) -> int:
        return 400
    
    def build(self, context: str, query: str, metadata: Dict = None) -> str:
        return f"Custom prompt: {context}\n\nQuery: {query}"

# Registrar
PromptFactory._strategies[PromptType.CUSTOM] = CustomPromptStrategy()
```

### Agregar Nueva Validación

Modificar `ResponseValidator._check_*()` en `utils/validators.py`:
```python
def _check_custom_validation(self, response: str) -> bool:
    # Tu lógica aquí
    return True
```

---

## 📝 Notas Importantes

- **Compatibilidad Legacy**: El sistema mantiene compatibilidad completa con código anterior
- **Configuración por Defecto**: Si no se especifica config, usa DEFAULT_CONFIG
- **Validación Opcional**: Se puede activar/desactivar según necesidad
- **Estrategias Intercambiables**: Cambiar estrategia es tan simple como cambiar un parámetro

---

**Versión:** 2.0  
**Última Actualización:** Octubre 2025  
**Autor:** Sistema RAG BPG