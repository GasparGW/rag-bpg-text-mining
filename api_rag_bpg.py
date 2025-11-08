"""
API REST para Sistema RAG BPG - Backend para PWA
Arquitectura: FastAPI + ChromaDB + Ollama
Puerto: 8000 (configurable)
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import uvicorn
from datetime import datetime
import logging

# Importar sistema RAG
from rag_bpg_ollama import RAGSystemBPG

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar FastAPI
app = FastAPI(
    title="API RAG BPG",
    description="Sistema de consultas sobre Buenas Prácticas Ganaderas usando RAG",
    version="1.0.0"
)

# Configurar CORS para PWA
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios exactos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar sistema RAG (global)
logger.info("Inicializando sistema RAG...")
try:
    rag_system = RAGSystemBPG(
        chroma_db_path="models/chroma_db",
        ollama_model="llama3.2"
    )
    logger.info("✅ Sistema RAG inicializado correctamente")
except Exception as e:
    logger.error(f"❌ Error inicializando RAG: {str(e)}")
    rag_system = None


# Modelos Pydantic para request/response
class QueryRequest(BaseModel):
    """Request para consulta RAG"""
    pregunta: str = Field(..., description="Pregunta del productor", min_length=5)
    k: int = Field(5, description="Número de documentos a recuperar", ge=1, le=10)
    temperature: float = Field(0.7, description="Temperatura del modelo", ge=0, le=1)
    
    class Config:
        json_schema_extra = {
            "example": {
                "pregunta": "¿Cuáles son las buenas prácticas para el manejo del agua?",
                "k": 5,
                "temperature": 0.7
            }
        }


class DocumentoRecuperado(BaseModel):
    """Documento recuperado del retriever"""
    rank: int
    text: str
    similarity: float
    metadata: Dict


class QueryResponse(BaseModel):
    """Response de consulta RAG"""
    respuesta: str = Field(..., description="Respuesta generada")
    pregunta: str = Field(..., description="Pregunta original")
    num_docs_usados: int = Field(..., description="Documentos usados como contexto")
    tiempo_generacion: float = Field(..., description="Tiempo en segundos")
    modelo: str = Field(..., description="Modelo LLM usado")
    documentos_recuperados: Optional[List[DocumentoRecuperado]] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    success: bool = True


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    rag_disponible: bool
    ollama_conectado: bool
    num_documentos_indexados: int
    timestamp: str


# Endpoints
@app.get("/", tags=["General"])
async def root():
    """Endpoint raíz"""
    return {
        "mensaje": "API RAG BPG - Sistema de Consultas sobre Buenas Prácticas Ganaderas",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health_check():
    """
    Health check del sistema
    Verifica que todos los componentes estén funcionando
    """
    if rag_system is None:
        raise HTTPException(status_code=503, detail="Sistema RAG no inicializado")
    
    try:
        # Verificar ChromaDB
        num_docs = rag_system.collection.count()
        
        # Verificar Ollama
        import requests
        ollama_response = requests.get(f"{rag_system.ollama_base_url}/api/tags", timeout=2)
        ollama_ok = ollama_response.status_code == 200
        
        return HealthResponse(
            status="healthy" if ollama_ok else "degraded",
            rag_disponible=True,
            ollama_conectado=ollama_ok,
            num_documentos_indexados=num_docs,
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        logger.error(f"Error en health check: {str(e)}")
        return HealthResponse(
            status="unhealthy",
            rag_disponible=False,
            ollama_conectado=False,
            num_documentos_indexados=0,
            timestamp=datetime.now().isoformat()
        )


@app.post("/query", response_model=QueryResponse, tags=["RAG"])
async def query_rag(request: QueryRequest):
    """
    Realizar consulta al sistema RAG
    
    - **pregunta**: Pregunta del productor sobre BPG
    - **k**: Número de documentos a recuperar (1-10)
    - **temperature**: Creatividad del modelo (0-1)
    
    Returns respuesta generada con metadata
    """
    if rag_system is None:
        raise HTTPException(
            status_code=503, 
            detail="Sistema RAG no disponible. Verifica que Ollama esté corriendo."
        )
    
    try:
        logger.info(f"Nueva consulta: {request.pregunta}")
        
        # Ejecutar consulta RAG
        resultado = rag_system.query(
            pregunta=request.pregunta,
            k=request.k,
            temperature=request.temperature,
            verbose=False
        )
        
        if not resultado['success']:
            raise HTTPException(
                status_code=500,
                detail=f"Error generando respuesta: {resultado['answer']}"
            )
        
        # Formatear documentos recuperados
        docs_recuperados = [
            DocumentoRecuperado(
                rank=doc['rank'],
                text=doc['text'],
                similarity=doc['similarity'],
                metadata=doc['metadata']
            )
            for doc in resultado['retrieved_docs']
        ]
        
        # Construir response
        response = QueryResponse(
            respuesta=resultado['answer'],
            pregunta=request.pregunta,
            num_docs_usados=resultado['num_docs_used'],
            tiempo_generacion=resultado['total_eval_duration'],
            modelo=resultado['model'],
            documentos_recuperados=docs_recuperados
        )
        
        logger.info(f"Consulta exitosa - {resultado['total_eval_duration']:.2f}s")
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/search", tags=["RAG"])
async def search_documents(query: str, k: int = 5):
    """
    Buscar documentos sin generar respuesta (solo retrieval)
    
    - **query**: Texto a buscar
    - **k**: Número de documentos a retornar
    """
    if rag_system is None:
        raise HTTPException(status_code=503, detail="Sistema RAG no disponible")
    
    try:
        docs = rag_system.retrieve_documents(query, k=k)
        
        return {
            "query": query,
            "num_resultados": len(docs),
            "documentos": docs
        }
    
    except Exception as e:
        logger.error(f"Error en búsqueda: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats", tags=["General"])
async def get_stats():
    """
    Obtener estadísticas del sistema
    """
    if rag_system is None:
        raise HTTPException(status_code=503, detail="Sistema RAG no disponible")
    
    try:
        num_docs = rag_system.collection.count()
        
        # Intentar obtener info de Ollama
        import requests
        try:
            ollama_response = requests.get(f"{rag_system.ollama_base_url}/api/tags", timeout=2)
            modelos = ollama_response.json().get('models', []) if ollama_response.status_code == 200 else []
            modelos_nombres = [m['name'] for m in modelos]
        except:
            modelos_nombres = []
        
        return {
            "documentos_indexados": num_docs,
            "modelo_embeddings": rag_system.embedding_model.get_sentence_embedding_dimension(),
            "dimension_vectores": 768,
            "ollama_url": rag_system.ollama_base_url,
            "modelo_llm_activo": rag_system.ollama_model,
            "modelos_disponibles": modelos_nombres,
            "base_datos": "ChromaDB",
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error obteniendo stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Función para iniciar servidor
def start_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """
    Iniciar servidor FastAPI
    
    Args:
        host: Host (0.0.0.0 para acceso desde red local)
        port: Puerto
        reload: Auto-reload en desarrollo
    """
    uvicorn.run(
        "api_rag_bpg:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


if __name__ == "__main__":
    # Iniciar servidor en desarrollo
    print("\n" + "="*60)
    print("🚀 Iniciando API RAG BPG")
    print("="*60)
    print(f"📍 URL: http://localhost:8000")
    print(f"📚 Docs: http://localhost:8000/docs")
    print(f"🔍 Health: http://localhost:8000/health")
    print("="*60 + "\n")
    
    start_server(
        host="0.0.0.0",  # Accesible desde red local
        port=8000,
        reload=True  # Auto-reload en desarrollo
    )
