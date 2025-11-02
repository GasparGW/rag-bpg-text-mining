"""
Modelos de datos para API REST del Sistema RAG BPG
"""

from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Request para consulta al RAG"""
    query: str = Field(..., description="Pregunta del usuario", min_length=3)
    k: Optional[int] = Field(None, description="Número de documentos a recuperar (1-20)", ge=1, le=20)
    temperature: Optional[float] = Field(None, description="Temperatura del LLM (0-1)", ge=0, le=1)
    max_tokens: Optional[int] = Field(None, description="Máximo de tokens en respuesta", ge=50, le=2000)
    strategy: Optional[str] = Field(None, description="Estrategia de prompt: standard, concise, fewshot, technical")
    enable_validation: Optional[bool] = Field(None, description="Activar validación de respuesta")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "¿Qué es el bienestar animal?",
                "k": 5,
                "temperature": 0.7,
                "strategy": "standard"
            }
        }


class ValidationResult(BaseModel):
    """Resultado de validación de respuesta"""
    is_valid: bool
    score: float
    validations: Dict[str, bool]
    recommendations: List[str]


class QueryResponse(BaseModel):
    """Response de consulta al RAG"""
    success: bool
    answer: str
    query: str
    model: str
    strategy: str
    temperature: float
    max_tokens: int
    num_docs_used: int
    k_used: int
    total_time: float
    timestamp: str
    validation: Optional[ValidationResult] = None
    error: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "answer": "El bienestar animal se refiere a...",
                "query": "¿Qué es el bienestar animal?",
                "model": "llama3.1:8b",
                "strategy": "Standard",
                "temperature": 0.7,
                "max_tokens": 500,
                "num_docs_used": 5,
                "k_used": 5,
                "total_time": 6.5,
                "timestamp": "2025-11-01T17:30:00",
                "validation": None,
                "error": None
            }
        }


class HealthResponse(BaseModel):
    """Response de health check"""
    status: str
    version: str
    rag_initialized: bool
    ollama_available: bool
    chroma_available: bool
    total_documents: int
    models_available: List[str]
    timestamp: str


class ConfigResponse(BaseModel):
    """Response con configuración actual"""
    ollama_model: str
    embedding_model: str
    chroma_db_path: str
    default_k: int
    default_temperature: float
    default_max_tokens: int
    prompt_strategy: str
    enable_validation: bool
    available_strategies: List[str]
