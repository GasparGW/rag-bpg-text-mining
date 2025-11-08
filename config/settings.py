"""
Configuración centralizada del sistema RAG BPG
Este archivo centraliza todos los parámetros configurables
"""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class PromptStrategy(Enum):
    """Estrategias de prompt disponibles"""
    STANDARD = "standard"
    CONCISE = "concise"
    FEWSHOT = "fewshot"
    TECHNICAL = "technical"


@dataclass
class RAGConfig:
    """
    Configuración completa del sistema RAG
    Usa dataclass para validación automática de tipos
    """
    
    # ==================== ChromaDB ====================
    chroma_db_path: str = "models/chroma_db"
    collection_name: str = "bpg_manuals"
    
    # ==================== Embeddings ====================
    embedding_model: str = "paraphrase-multilingual-mpnet-base-v2"
    
    # ==================== Ollama ====================
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"
    ollama_timeout: int = 120  # segundos
    
    # ==================== Retrieval ====================
    default_k: int = 5  # número de documentos a recuperar
    min_similarity: float = 0.0  # similaridad mínima (0-1)
    
    # ==================== Generation ====================
    default_temperature: float = 0.7  # creatividad del modelo (0-1)
    default_max_tokens: int = 500  # máximo tokens en respuesta
    prompt_strategy: str = "standard"  # estrategia de prompt a usar
    
    # ==================== Validación ====================
    enable_validation: bool = False  # activar validación de respuestas
    min_answer_length: int = 50  # longitud mínima de respuesta
    max_answer_length: int = 2000  # longitud máxima de respuesta
    
    # ==================== Logging ====================
    verbose: bool = True  # mostrar información detallada
    log_file: Optional[str] = None  # archivo de log (None = no guardar)
    
    def __post_init__(self):
        """Validaciones después de inicialización"""
        # Validar rangos
        if not 0 <= self.default_temperature <= 1:
            raise ValueError("Temperature debe estar entre 0 y 1")
        
        if not 0 <= self.min_similarity <= 1:
            raise ValueError("min_similarity debe estar entre 0 y 1")
        
        if self.default_k < 1:
            raise ValueError("default_k debe ser al menos 1")
    
    def to_dict(self) -> dict:
        """Convertir configuración a diccionario"""
        return {
            'chroma_db_path': self.chroma_db_path,
            'collection_name': self.collection_name,
            'embedding_model': self.embedding_model,
            'ollama_base_url': self.ollama_base_url,
            'ollama_model': self.ollama_model,
            'ollama_timeout': self.ollama_timeout,
            'default_k': self.default_k,
            'min_similarity': self.min_similarity,
            'default_temperature': self.default_temperature,
            'default_max_tokens': self.default_max_tokens,
            'prompt_strategy': self.prompt_strategy,
            'enable_validation': self.enable_validation,
            'verbose': self.verbose
        }
    
    @classmethod
    def from_dict(cls, config_dict: dict) -> 'RAGConfig':
        """Crear configuración desde diccionario"""
        return cls(**config_dict)


# ==================== CONFIGURACIONES PRE-DEFINIDAS ====================

# Configuración por defecto (para producción)
DEFAULT_CONFIG = RAGConfig()

# Configuración para desarrollo (más verbose, validación activa)
DEV_CONFIG = RAGConfig(
    enable_validation=True,
    verbose=True,
    log_file="rag_dev.log"
)

# Configuración para respuestas rápidas
FAST_CONFIG = RAGConfig(
    default_k=3,
    default_max_tokens=300,
    prompt_strategy="concise",
    ollama_timeout=60
)

# Configuración para consultas técnicas detalladas
TECHNICAL_CONFIG = RAGConfig(
    default_k=7,
    default_max_tokens=700,
    prompt_strategy="technical",
    default_temperature=0.3  # más determinístico
)


# ==================== FUNCIONES AUXILIARES ====================

def get_config(config_name: str = "default") -> RAGConfig:
    """
    Obtener configuración por nombre
    
    Args:
        config_name: Nombre de configuración ("default", "dev", "fast", "technical")
        
    Returns:
        Instancia de RAGConfig
    """
    configs = {
        "default": DEFAULT_CONFIG,
        "dev": DEV_CONFIG,
        "fast": FAST_CONFIG,
        "technical": TECHNICAL_CONFIG
    }
    
    return configs.get(config_name.lower(), DEFAULT_CONFIG)


def print_config(config: RAGConfig):
    """Imprimir configuración de forma legible"""
    print("\n" + "="*60)
    print("⚙️  CONFIGURACIÓN RAG BPG")
    print("="*60)
    
    print("\n📦 ChromaDB:")
    print(f"  • Path: {config.chroma_db_path}")
    print(f"  • Collection: {config.collection_name}")
    
    print("\n🤖 Ollama:")
    print(f"  • URL: {config.ollama_base_url}")
    print(f"  • Model: {config.ollama_model}")
    print(f"  • Timeout: {config.ollama_timeout}s")
    
    print("\n🔍 Retrieval:")
    print(f"  • K documentos: {config.default_k}")
    print(f"  • Min similarity: {config.min_similarity}")
    
    print("\n✨ Generation:")
    print(f"  • Temperature: {config.default_temperature}")
    print(f"  • Max tokens: {config.default_max_tokens}")
    print(f"  • Prompt strategy: {config.prompt_strategy}")
    
    print("\n🔧 Otros:")
    print(f"  • Validación: {'✅' if config.enable_validation else '❌'}")
    print(f"  • Verbose: {'✅' if config.verbose else '❌'}")
    print(f"  • Log file: {config.log_file or 'None'}")
    
    print("="*60 + "\n")