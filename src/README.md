# Carpeta SRC - Código Fuente

## preprocessing/
Scripts para preparación de datos:
- `ocr_extractor.py` - Extrae texto de PDFs
- `text_cleaner.py` - Limpieza y normalización
- `chunker.py` - Divide texto en chunks
- `anonymizer.py` - Ofusca datos sensibles

## rag/
Core del sistema RAG:
- `embeddings.py` - Genera vectores de texto
- `vector_store.py` - Gestión ChromaDB
- `retriever.py` - Búsqueda de chunks relevantes
- `generator.py` - Generación respuestas con LLM
- `prompt_templates.py` - Templates de prompts

## pwa/
Progressive Web App para offline:
- `service_worker.js` - Cache y sincronización
- `app.py` - Backend FastAPI/Streamlit
- `offline_storage.py` - IndexedDB management

## utils/
Funciones auxiliares:
- `config.py` - Carga variables de entorno
- `logger.py` - Sistema de logging
- `validators.py` - Validación de datos
