"""
RAG System para Consultas de Buenas Prácticas Ganaderas (BPG)
Arquitectura: ChromaDB (vectores) + Ollama (generación)
Autor: Sistema RAG BPG
Versión: 2.0 - Con Configuración, Estrategias de Prompts y Validadores
"""

import os
import sys
from typing import List, Dict, Tuple, Optional
import chromadb
from sentence_transformers import SentenceTransformer
import requests
import json
from datetime import datetime

# ✨ Importar sistema de configuración
try:
    from config.settings import RAGConfig, DEFAULT_CONFIG
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False
    print("⚠️  Sistema de configuración no disponible, usando parámetros legacy")

# ✨ Importar estrategias de prompts
try:
    from prompts.strategies import PromptFactory, PromptType
    PROMPTS_AVAILABLE = True
except ImportError:
    PROMPTS_AVAILABLE = False
    print("⚠️  Sistema de prompts no disponible, usando prompt por defecto")


class RAGSystemBPG:
    """Sistema RAG completo para consultas sobre Buenas Prácticas Ganaderas"""
    
    def __init__(
        self, 
        # ✨ Parámetro principal de configuración
        config: Optional['RAGConfig'] = None,
        
        # Legacy parameters (para compatibilidad hacia atrás)
        chroma_db_path: Optional[str] = None,
        embedding_model_name: Optional[str] = None,
        ollama_base_url: Optional[str] = None,
        ollama_model: Optional[str] = None
    ):
        """
        Inicializar sistema RAG con configuración flexible
        
        Args:
            config: Objeto RAGConfig (recomendado) - Si se proporciona, ignora otros parámetros
            chroma_db_path: [LEGACY] Ruta a ChromaDB
            embedding_model_name: [LEGACY] Modelo de embeddings
            ollama_base_url: [LEGACY] URL de Ollama
            ollama_model: [LEGACY] Modelo de Ollama
            
        Ejemplos:
            # Forma nueva (recomendada):
            >>> from config.settings import RAGConfig
            >>> config = RAGConfig(ollama_model="mistral", prompt_strategy="fewshot")
            >>> rag = RAGSystemBPG(config=config)
            
            # Forma antigua (sigue funcionando):
            >>> rag = RAGSystemBPG(ollama_model="llama3.2")
        """
        print("🚀 Inicializando Sistema RAG BPG...")
        
        # ===== MANEJO DE CONFIGURACIÓN =====
        if config is not None:
            # Usar configuración nueva
            self.config = config
            print("✅ Usando configuración centralizada")
        elif CONFIG_AVAILABLE:
            # Crear config desde parámetros legacy
            config_kwargs = {}
            if chroma_db_path is not None:
                config_kwargs['chroma_db_path'] = chroma_db_path
            if embedding_model_name is not None:
                config_kwargs['embedding_model'] = embedding_model_name
            if ollama_base_url is not None:
                config_kwargs['ollama_base_url'] = ollama_base_url
            if ollama_model is not None:
                config_kwargs['ollama_model'] = ollama_model
            
            if config_kwargs:
                self.config = RAGConfig(**config_kwargs)
                print("✅ Configuración creada desde parámetros legacy")
            else:
                self.config = DEFAULT_CONFIG
                print("✅ Usando configuración por defecto")
        else:
            # Fallback: usar parámetros directos (modo legacy puro)
            print("⚠️  Modo legacy: sin sistema de configuración")
            self.chroma_db_path = chroma_db_path or "models/chroma_db"
            self.embedding_model_name = embedding_model_name or "paraphrase-multilingual-mpnet-base-v2"
            self.ollama_base_url = ollama_base_url or "http://localhost:11434"
            self.ollama_model = ollama_model or "llama3.2"
            self.config = None
        
        # ===== EXTRAER PARÁMETROS DE CONFIG =====
        if self.config:
            self.chroma_db_path = self.config.chroma_db_path
            self.embedding_model_name = self.config.embedding_model
            self.ollama_base_url = self.config.ollama_base_url
            self.ollama_model = self.config.ollama_model
        
        # ===== INICIALIZACIÓN DE COMPONENTES =====
        # Cargar modelo de embeddings
        print(f"📦 Cargando modelo de embeddings: {self.embedding_model_name}")
        self.embedding_model = SentenceTransformer(self.embedding_model_name)
        print("✅ Modelo de embeddings cargado")
        
        # Conectar a ChromaDB
        print(f"🗄️  Conectando a ChromaDB: {self.chroma_db_path}")
        self.chroma_client = chromadb.PersistentClient(path=self.chroma_db_path)
        
        # Usar collection_name de config si está disponible
        collection_name = self.config.collection_name if self.config else "bpg_manuals"
        self.collection = self.chroma_client.get_collection(name=collection_name)
        print(f"✅ Conectado a ChromaDB - {self.collection.count()} documentos disponibles")
        
        # Verificar conexión con Ollama
        self._verificar_ollama()
        
        # ✨ Inicializar estrategia de prompts
        if PROMPTS_AVAILABLE and self.config:
            strategy_name = self.config.prompt_strategy
            self.prompt_strategy = PromptFactory.get_strategy_by_name(strategy_name)
            print(f"📝 Estrategia de prompt: {self.prompt_strategy.name}")
        else:
            self.prompt_strategy = None
            print("📝 Usando prompt por defecto (legacy)")
        
        # ✨ NUEVO: Inicializar validador de respuestas
        if self.config and self.config.enable_validation:
            try:
                from utils.validators import ResponseValidator
                self.validator = ResponseValidator(
                    min_length=self.config.min_answer_length,
                    max_length=self.config.max_answer_length,
                    strict_mode=False  # Modo normal por defecto
                )
                print(f"🔍 Validación de respuestas: ACTIVADA")
            except ImportError:
                self.validator = None
                print("⚠️  Validador no disponible")
        else:
            self.validator = None
            if self.config:
                print(f"🔍 Validación de respuestas: DESACTIVADA")
        
        print("✅ Sistema RAG inicializado correctamente\n")
    
    def _verificar_ollama(self):
        """Verificar que Ollama esté corriendo y el modelo disponible"""
        try:
            response = requests.get(f"{self.ollama_base_url}/api/tags")
            if response.status_code == 200:
                modelos = response.json().get('models', [])
                modelos_nombres = [m['name'] for m in modelos]
                print(f"✅ Ollama conectado - Modelos disponibles: {modelos_nombres}")
                
                if self.ollama_model not in modelos_nombres:
                    print(f"⚠️  ADVERTENCIA: Modelo '{self.ollama_model}' no encontrado")
                    print(f"   Ejecuta: ollama pull {self.ollama_model}")
            else:
                print(f"❌ Error conectando a Ollama (status: {response.status_code})")
        except Exception as e:
            print(f"❌ Error: Ollama no está corriendo en {self.ollama_base_url}")
            print(f"   Inicia Ollama con: ollama serve")
            print(f"   Error detallado: {str(e)}")
    
    def retrieve_documents(
        self, 
        query: str, 
        k: int = 5,
        min_similarity: float = 0.0
    ) -> List[Dict]:
        """
        Recuperar documentos relevantes de ChromaDB
        
        Args:
            query: Pregunta del usuario
            k: Número de chunks a recuperar
            min_similarity: Similaridad mínima (0-1)
            
        Returns:
            Lista de documentos relevantes con metadata
        """
        print(f"\n🔍 Buscando documentos relevantes para: '{query}'")
        
        # Generar embedding de la query
        query_embedding = self.embedding_model.encode([query])[0].tolist()
        
        # Buscar en ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k
        )
        
        # Procesar resultados
        documentos_relevantes = []
        if results['documents'] and results['documents'][0]:
            for i, (doc, metadata, distance) in enumerate(zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            )):
                # Convertir distancia a similaridad (ChromaDB usa distancia L2)
                similarity = 1 / (1 + distance)
                
                if similarity >= min_similarity:
                    documentos_relevantes.append({
                        'rank': i + 1,
                        'text': doc,
                        'metadata': metadata,
                        'similarity': round(similarity, 4),
                        'distance': round(distance, 4)
                    })
        
        print(f"✅ Recuperados {len(documentos_relevantes)} documentos relevantes")
        return documentos_relevantes
    
    def generate_answer(
        self, 
        query: str, 
        context_docs: List[Dict],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Dict:
        """
        Generar respuesta usando Ollama con contexto recuperado
        
        Args:
            query: Pregunta del usuario
            context_docs: Documentos recuperados del retriever
            temperature: Creatividad del modelo (0-1) - usa config si es None
            max_tokens: Máximo de tokens en respuesta - usa recomendación de estrategia si es None
            
        Returns:
            Diccionario con respuesta y metadata
        """
        print(f"\n🤖 Generando respuesta con Ollama ({self.ollama_model})...")
        
        # ===== DETERMINAR PARÁMETROS DE GENERACIÓN =====
        if self.config:
            temperature = temperature if temperature is not None else self.config.default_temperature
            # Si hay estrategia, usar sus tokens recomendados, sino usar de config
            if self.prompt_strategy and max_tokens is None:
                max_tokens = self.prompt_strategy.max_tokens_recommended
            else:
                max_tokens = max_tokens if max_tokens is not None else self.config.default_max_tokens
        else:
            # Legacy fallback
            temperature = temperature if temperature is not None else 0.7
            max_tokens = max_tokens if max_tokens is not None else 500
        
        # ===== CONSTRUIR CONTEXTO =====
        context = "\n\n---\n\n".join([
            f"Fragmento {doc['rank']} (Similaridad: {doc['similarity']}):\n{doc['text']}"
            for doc in context_docs
        ])
        
        # ===== CONSTRUIR PROMPT USANDO ESTRATEGIA O FALLBACK =====
        if self.prompt_strategy:
            # Usar estrategia configurada
            prompt = self.prompt_strategy.build(context, query)
            strategy_used = self.prompt_strategy.name
            print(f"📝 Usando estrategia: {strategy_used}")
        else:
            # Prompt legacy (el original)
            prompt = f"""Eres un experto en Buenas Prácticas Ganaderas (BPG) para ganado vacuno de carne. 

Tu tarea es responder preguntas de productores ganaderos basándote ÚNICAMENTE en la información proporcionada en los documentos de referencia.

DOCUMENTOS DE REFERENCIA:
{context}

PREGUNTA DEL PRODUCTOR:
{query}

INSTRUCCIONES:
1. Responde SOLO con información de los documentos de referencia
2. Si la información no está en los documentos, di "No tengo información suficiente en los manuales"
3. Sé específico, práctico y directo
4. Usa un lenguaje profesional pero accesible
5. Si hay normativas o números específicos, cítalos exactamente

RESPUESTA:"""
            strategy_used = "Legacy"
            print(f"📝 Usando prompt: Legacy (por defecto)")
        
        # ===== LLAMAR A OLLAMA API =====
        try:
            response = requests.post(
                f"{self.ollama_base_url}/api/generate",
                json={
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens
                    }
                },
                timeout=120  # 2 minutos timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                answer_text = result.get('response', '').strip()
                
                print(f"✅ Respuesta generada ({len(answer_text)} caracteres)")
                
                # ✨ NUEVO: Validar respuesta si el validador está activo
                validation_result = None
                if self.validator:
                    validation_result = self.validator.validate_response(
                        response=answer_text,
                        context=context,
                        query=query
                    )
                    
                    if self.config and self.config.verbose and not validation_result['is_valid']:
                        print(f"⚠️  Validación: Score {validation_result['score']:.1%}")
                        print(f"   Recomendaciones: {validation_result['recommendations'][0]}")
                
                return {
                    'answer': answer_text,
                    'model': self.ollama_model,
                    'strategy': strategy_used,
                    'temperature': temperature,
                    'max_tokens': max_tokens,
                    'num_docs_used': len(context_docs),
                    'total_eval_duration': result.get('total_duration', 0) / 1e9,
                    'timestamp': datetime.now().isoformat(),
                    'validation': validation_result,  # ✨ NUEVO
                    'success': True
                }
            else:
                error_msg = f"Error de Ollama (status {response.status_code})"
                print(f"❌ {error_msg}")
                return {
                    'answer': error_msg,
                    'success': False
                }
                
        except Exception as e:
            error_msg = f"Error al generar respuesta: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                'answer': error_msg,
                'success': False
            }
    
    def query(
        self, 
        pregunta: str, 
        k: Optional[int] = None,
        temperature: Optional[float] = None,
        verbose: bool = True
    ) -> Dict:
        """
        Ejecutar consulta completa RAG (Retrieve + Generate)
        
        Args:
            pregunta: Pregunta del usuario
            k: Número de chunks a recuperar (usa config si es None)
            temperature: Creatividad de la respuesta (usa config si es None)
            verbose: Mostrar documentos recuperados
            
        Returns:
            Respuesta completa con metadata
        """
        print("\n" + "="*60)
        print("📋 CONSULTA RAG BPG")
        print("="*60)
        
        # Usar valores de configuración si están disponibles y no se especificaron
        if self.config:
            k = k if k is not None else self.config.default_k
            temperature = temperature if temperature is not None else self.config.default_temperature
        else:
            k = k if k is not None else 5
            temperature = temperature if temperature is not None else 0.7
        
        # 1. RETRIEVAL
        docs_relevantes = self.retrieve_documents(pregunta, k=k)
        
        if verbose and docs_relevantes:
            print("\n📄 Documentos recuperados:")
            for doc in docs_relevantes[:3]:  # Mostrar top 3
                print(f"\n  Rank {doc['rank']} - Similaridad: {doc['similarity']}")
                print(f"  {doc['text'][:200]}...")
        
        # 2. GENERATION
        resultado = self.generate_answer(
            query=pregunta,
            context_docs=docs_relevantes,
            temperature=temperature
        )
        
        # Agregar información de retrieval al resultado
        resultado['retrieved_docs'] = docs_relevantes
        resultado['query'] = pregunta
        resultado['k_used'] = k
        
        return resultado
    
    def chat_interactivo(self):
        """Modo chat interactivo para pruebas"""
        print("\n" + "="*60)
        print("💬 CHAT INTERACTIVO RAG BPG")
        print("="*60)
        
        # Mostrar configuración actual
        if self.prompt_strategy:
            print(f"📝 Estrategia actual: {self.prompt_strategy.name}")
        if self.config:
            print(f"⚙️  Temperature: {self.config.default_temperature}")
            print(f"⚙️  K documentos: {self.config.default_k}")
        if self.validator:
            print(f"🔍 Validación: ACTIVADA")
        
        print("\nEscribe 'salir' para terminar")
        print("Escribe 'reporte' después de una respuesta para ver validación detallada\n")
        
        last_validation = None
        
        while True:
            try:
                pregunta = input("\n🧑‍🌾 Productor: ").strip()
                
                if pregunta.lower() in ['salir', 'exit', 'quit']:
                    print("👋 Hasta luego!")
                    break
                
                if pregunta.lower() == 'reporte':
                    if last_validation and self.validator:
                        from utils.validators import ValidationReport
                        ValidationReport.print_report(last_validation)
                    else:
                        print("⚠️  No hay validación disponible para mostrar")
                    continue
                
                if not pregunta:
                    continue
                
                resultado = self.query(pregunta, verbose=False)
                
                if resultado['success']:
                    print(f"\n🤖 Asistente BPG: {resultado['answer']}")
                    print(f"\n⏱️  Tiempo: {resultado['total_eval_duration']:.2f}s")
                    print(f"📊 Docs: {resultado['num_docs_used']} | Estrategia: {resultado.get('strategy', 'N/A')}")
                    
                    # Guardar validación para comando 'reporte'
                    if resultado.get('validation'):
                        last_validation = resultado['validation']
                        score = resultado['validation']['score']
                        print(f"🔍 Calidad: {score:.1%}")
                else:
                    print(f"\n❌ Error: {resultado['answer']}")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Hasta luego!")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")


def main():
    """Función principal para pruebas"""
    
    print("\n" + "="*60)
    print("🎯 INICIANDO SISTEMA RAG BPG")
    print("="*60)
    
    # Usar configuración si está disponible
    if CONFIG_AVAILABLE:
        print("\n✅ Sistema de configuración disponible")
        print("✅ Sistema de prompts disponible") if PROMPTS_AVAILABLE else print("⚠️  Sistema de prompts NO disponible")
        
        # Por ahora usar DEFAULT
        rag = RAGSystemBPG(config=DEFAULT_CONFIG)
    else:
        print("\n⚠️  Modo legacy (sin configuración)")
        rag = RAGSystemBPG(
            chroma_db_path="models/chroma_db",
            embedding_model_name="paraphrase-multilingual-mpnet-base-v2",
            ollama_model="llama3.2"
        )
    
    # Ejemplos de consultas
    ejemplos = [
        "¿Cuáles son las buenas prácticas para el manejo del agua en feedlot?",
        "¿Qué requisitos debe cumplir el establecimiento ganadero?",
        "¿Cómo se debe manejar el bienestar animal durante el transporte?"
    ]
    
    print("\n" + "="*60)
    print("🧪 PROBANDO SISTEMA RAG CON CONSULTAS DE EJEMPLO")
    print("="*60)
    
    for i, pregunta in enumerate(ejemplos, 1):
        print(f"\n{'='*60}")
        print(f"EJEMPLO {i}")
        print(f"{'='*60}")
        
        resultado = rag.query(pregunta, k=3, verbose=True)
        
        if resultado['success']:
            print(f"\n📝 RESPUESTA FINAL:\n{resultado['answer']}")
            print(f"\n📊 METADATA:")
            print(f"   • Estrategia: {resultado.get('strategy', 'N/A')}")
            print(f"   • Tiempo: {resultado['total_eval_duration']:.2f}s")
            print(f"   • Docs usados: {resultado['num_docs_used']}")
            print(f"   • Temperature: {resultado.get('temperature', 'N/A')}")
            
            # Mostrar validación si existe
            if resultado.get('validation'):
                val = resultado['validation']
                print(f"   • Validación: {val['score']:.1%} ({'✅ VÁLIDA' if val['is_valid'] else '⚠️  REVISAR'})")
        
        print("\n" + "-"*60)
    
    # Modo interactivo
    print("\n\n¿Iniciar chat interactivo? (s/n): ", end="")
    try:
        if input().lower() == 's':
            rag.chat_interactivo()
    except:
        print("\nOK, hasta luego!")


if __name__ == "__main__":
    main()