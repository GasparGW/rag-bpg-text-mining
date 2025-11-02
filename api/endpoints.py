"""
Endpoints de la API REST del Sistema RAG BPG
"""

from fastapi import APIRouter, HTTPException, status
from datetime import datetime
from typing import Optional
import logging

from api.models import (
    QueryRequest, 
    QueryResponse, 
    HealthResponse, 
    ConfigResponse,
    ValidationResult
)
from rag_bpg_ollama import RAGSystemBPG
from config.settings import RAGConfig

logger = logging.getLogger(__name__)
router = APIRouter()
rag_system: Optional[RAGSystemBPG] = None


def set_rag_system(rag: RAGSystemBPG):
    global rag_system
    rag_system = rag


@router.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Health check del sistema"""
    if rag_system is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Sistema RAG no inicializado"
        )
    
    try:
        # Verificar Ollama - CORREGIDO (hacer llamada real)
        import requests
        ollama_available = False
        models_available = []
        try:
            response = requests.get(f"{rag_system.ollama_base_url}/api/tags", timeout=2)
            if response.status_code == 200:
                ollama_available = True
                models_available = [m['name'] for m in response.json().get('models', [])]
        except:
            ollama_available = False
        
        # Verificar ChromaDB
        chroma_available = rag_system.collection is not None
        total_docs = 0
        if chroma_available:
            try:
                total_docs = rag_system.collection.count()
            except:
                chroma_available = False
        
        return HealthResponse(
            status="healthy" if (ollama_available and chroma_available) else "degraded",
            version="2.1",
            rag_initialized=True,
            ollama_available=ollama_available,
            chroma_available=chroma_available,
            total_documents=total_docs,
            models_available=models_available,
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        logger.error(f"Error en health check: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error verificando salud del sistema: {str(e)}"
        )


@router.get("/config", response_model=ConfigResponse, tags=["System"])
async def get_config():
    """Obtener configuración actual del sistema"""
    if rag_system is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Sistema RAG no inicializado"
        )
    
    try:
        config = rag_system.config
        from prompts.strategies import PromptFactory
        available_strategies = list(PromptFactory.list_strategies().keys())
        
        return ConfigResponse(
            ollama_model=config.ollama_model,
            embedding_model=config.embedding_model,
            chroma_db_path=config.chroma_db_path,
            default_k=config.default_k,
            default_temperature=config.default_temperature,
            default_max_tokens=config.default_max_tokens,
            prompt_strategy=config.prompt_strategy,
            enable_validation=config.enable_validation,
            available_strategies=available_strategies
        )
    
    except Exception as e:
        logger.error(f"Error obteniendo config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo configuración: {str(e)}"
        )


@router.post("/query", response_model=QueryResponse, tags=["RAG"])
async def query_rag(request: QueryRequest):
    """Realizar consulta al sistema RAG"""
    if rag_system is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Sistema RAG no inicializado"
        )
    
    try:
        # Preparar parámetros - CORREGIDO: usar argumentos posicionales/keyword correctos
        query_params = {
            'verbose': False
        }
        
        # Parámetros opcionales
        if request.k is not None:
            query_params['k'] = request.k
        if request.temperature is not None:
            query_params['temperature'] = request.temperature
        if request.max_tokens is not None:
            query_params['max_tokens'] = request.max_tokens
        if request.strategy is not None:
            query_params['strategy'] = request.strategy
        if request.enable_validation is not None:
            query_params['enable_validation'] = request.enable_validation
        
        # Ejecutar query - CORREGIDO: query_text como primer argumento
        start_time = datetime.now()
        result = rag_system.query(request.query, **query_params)
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()
        
        # Parsear validación si existe
        validation = None
        if result.get('validation'):
            val = result['validation']
            validation = ValidationResult(
                is_valid=val['is_valid'],
                score=val['score'],
                validations=val['validations'],
                recommendations=val['recommendations']
            )
        
        # Construir respuesta
        return QueryResponse(
            success=result.get('success', True),
            answer=result['answer'],
            query=result['query'],
            model=result['model'],
            strategy=result['strategy'],
            temperature=result['temperature'],
            max_tokens=result['max_tokens'],
            num_docs_used=result['num_docs_used'],
            k_used=result['k_used'],
            total_time=total_time,
            timestamp=result['timestamp'],
            validation=validation,
            error=None
        )
    
    except Exception as e:
        logger.error(f"Error en query: {e}")
        
        # Retornar error estructurado
        return QueryResponse(
            success=False,
            answer="",
            query=request.query,
            model=rag_system.config.ollama_model,
            strategy=rag_system.config.prompt_strategy,
            temperature=request.temperature or rag_system.config.default_temperature,
            max_tokens=request.max_tokens or rag_system.config.default_max_tokens,
            num_docs_used=0,
            k_used=request.k or rag_system.config.default_k,
            total_time=0,
            timestamp=datetime.now().isoformat(),
            validation=None,
            error=str(e)
        )
