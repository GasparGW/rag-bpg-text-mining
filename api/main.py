"""
Aplicación FastAPI principal para Sistema RAG BPG
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from contextlib import asynccontextmanager

from api.endpoints import router, set_rag_system
from rag_bpg_ollama import RAGSystemBPG
from config.settings import DEFAULT_CONFIG

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Variable global para RAG
rag_system = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle del sistema: inicialización y cleanup
    """
    global rag_system
    
    # Startup: Inicializar RAG
    logger.info("🚀 Inicializando Sistema RAG BPG...")
    try:
        rag_system = RAGSystemBPG(config=DEFAULT_CONFIG)
        set_rag_system(rag_system)
        logger.info("✅ Sistema RAG inicializado correctamente")
    except Exception as e:
        logger.error(f"❌ Error inicializando RAG: {e}")
        raise
    
    yield
    
    # Shutdown: Cleanup si es necesario
    logger.info("👋 Cerrando Sistema RAG BPG...")


# Crear aplicación FastAPI
app = FastAPI(
    title="API RAG BPG",
    description="API REST para consultas sobre Buenas Prácticas Ganaderas usando RAG",
    version="2.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware (permite peticiones desde frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción: especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar endpoints
app.include_router(router, prefix="/api/v1")


@app.get("/", tags=["Root"])
async def root():
    """
    Endpoint raíz - Información básica de la API
    """
    return {
        "message": "API RAG BPG - Sistema de consultas sobre Buenas Prácticas Ganaderas",
        "version": "2.1.0",
        "docs": "/docs",
        "health": "/api/v1/health",
        "config": "/api/v1/config",
        "query": "/api/v1/query"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
