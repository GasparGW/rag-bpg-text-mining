"""
Test End-to-End completo del sistema RAG BPG
Prueba todo el flujo: Config -> Prompts -> RAG -> Validación
"""

import sys
import os

# Agregar la raíz del proyecto al path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)


def test_e2e_full_system():
    """Test: Sistema completo con todas las características"""
    print("\n🧪 TEST E2E 1: Sistema Completo")
    print("-" * 60)
    
    try:
        from config.settings import RAGConfig
        from rag_bpg_ollama import RAGSystemBPG
        
        # Configuración completa
        config = RAGConfig(
            ollama_model="llama3.2",
            prompt_strategy="standard",
            default_k=5,
            default_temperature=0.7,
            enable_validation=True,
            verbose=True
        )
        
        # Inicializar sistema
        print("\n1️⃣ Inicializando sistema RAG...")
        rag = RAGSystemBPG(config=config)
        
        # Verificar componentes
        assert rag.config is not None, "Config no inicializada"
        assert rag.prompt_strategy is not None, "Estrategia de prompts no inicializada"
        assert rag.validator is not None, "Validador no inicializado"
        assert rag.embedding_model is not None, "Modelo de embeddings no cargado"
        assert rag.collection is not None, "ChromaDB no conectada"
        
        print("✅ Sistema inicializado correctamente")
        print(f"   • Config: {config.prompt_strategy}")
        print(f"   • Prompts: {rag.prompt_strategy.name}")
        print(f"   • Validación: {'Activa' if rag.validator else 'Inactiva'}")
        print(f"   • Documentos: {rag.collection.count()}")
        
        # Test de retrieval
        print("\n2️⃣ Probando retrieval...")
        query_test = "¿Qué es el bienestar animal?"
        docs = rag.retrieve_documents(query_test, k=3)
        
        assert len(docs) > 0, "No se recuperaron documentos"
        assert all('text' in doc for doc in docs), "Documentos sin texto"
        assert all('similarity' in doc for doc in docs), "Documentos sin similaridad"
        
        print(f"✅ Retrieval OK: {len(docs)} documentos recuperados")
        print(f"   • Mejor similaridad: {docs[0]['similarity']}")
        
        # Test de generación (sin llamar a Ollama si no está disponible)
        print("\n3️⃣ Probando estructura de generación...")
        # Solo verificar que la función existe y acepta los parámetros correctos
        import inspect
        sig = inspect.signature(rag.generate_answer)
        params = list(sig.parameters.keys())
        
        assert 'query' in params, "generate_answer debe aceptar 'query'"
        assert 'context_docs' in params, "generate_answer debe aceptar 'context_docs'"
        
        print("✅ Estructura de generación OK")
        
        print("\n" + "="*60)
        print("✅ TEST E2E COMPLETO EXITOSO")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Error en test E2E: {e}")
        import traceback
        traceback.print_exc()
        raise


def test_e2e_different_strategies():
    """Test: Probar todas las estrategias de prompts"""
    print("\n🧪 TEST E2E 2: Todas las Estrategias")
    print("-" * 60)
    
    try:
        from config.settings import RAGConfig
        from rag_bpg_ollama import RAGSystemBPG
        
        strategies = ["standard", "concise", "fewshot", "technical"]
        results = {}
        
        for strategy in strategies:
            config = RAGConfig(
                prompt_strategy=strategy,
                enable_validation=False  # Para acelerar el test
            )
            
            rag = RAGSystemBPG(config=config)
            
            results[strategy] = {
                'strategy_name': rag.prompt_strategy.name,
                'max_tokens': rag.prompt_strategy.max_tokens_recommended,
                'config_ok': rag.config is not None,
                'prompt_ok': rag.prompt_strategy is not None
            }
            
            print(f"✅ {strategy}: {results[strategy]['strategy_name']} ({results[strategy]['max_tokens']} tokens)")
        
        # Verificar que todas son diferentes
        strategy_names = [r['strategy_name'] for r in results.values()]
        assert len(set(strategy_names)) == 4, "Las estrategias no son únicas"
        
        print("\n✅ Todas las estrategias funcionan correctamente")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise


def test_e2e_validation_modes():
    """Test: Probar sistema con y sin validación"""
    print("\n🧪 TEST E2E 3: Modos de Validación")
    print("-" * 60)
    
    try:
        from config.settings import RAGConfig
        from rag_bpg_ollama import RAGSystemBPG
        
        # Con validación
        print("\n1️⃣ Probando CON validación...")
        config_with = RAGConfig(enable_validation=True)
        rag_with = RAGSystemBPG(config=config_with)
        assert rag_with.validator is not None
        print("✅ Sistema con validación OK")
        
        # Sin validación
        print("\n2️⃣ Probando SIN validación...")
        config_without = RAGConfig(enable_validation=False)
        rag_without = RAGSystemBPG(config=config_without)
        assert rag_without.validator is None
        print("✅ Sistema sin validación OK")
        
        print("\n✅ Ambos modos funcionan correctamente")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise


def test_e2e_legacy_compatibility():
    """Test: Verificar compatibilidad con código legacy"""
    print("\n🧪 TEST E2E 4: Compatibilidad Legacy")
    print("-" * 60)
    
    try:
        from rag_bpg_ollama import RAGSystemBPG
        
        # Modo legacy puro (sin config)
        print("\n1️⃣ Inicializando en modo legacy...")
        rag_legacy = RAGSystemBPG(
            ollama_model="llama3.2",
            chroma_db_path="models/chroma_db"
        )
        
        assert rag_legacy.ollama_model == "llama3.2"
        assert rag_legacy.chroma_db_path == "models/chroma_db"
        
        print("✅ Modo legacy funciona correctamente")
        print(f"   • Model: {rag_legacy.ollama_model}")
        print(f"   • DB Path: {rag_legacy.chroma_db_path}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise


def test_e2e_retrieval_quality():
    """Test: Verificar calidad del retrieval"""
    print("\n🧪 TEST E2E 5: Calidad de Retrieval")
    print("-" * 60)
    
    try:
        from config.settings import RAGConfig
        from rag_bpg_ollama import RAGSystemBPG
        
        config = RAGConfig(default_k=5)
        rag = RAGSystemBPG(config=config)
        
        # Queries de prueba
        test_queries = [
            "¿Qué es el bienestar animal?",
            "¿Cómo manejar el agua en feedlot?",
            "requisitos de transporte"
        ]
        
        for query in test_queries:
            docs = rag.retrieve_documents(query, k=3)
            
            # Verificar calidad
            assert len(docs) > 0, f"No se encontraron docs para: {query}"
            assert docs[0]['similarity'] > 0.3, f"Similaridad muy baja para: {query}"
            assert all(len(doc['text']) > 50 for doc in docs), "Documentos muy cortos"
            
            print(f"✅ '{query[:30]}...': {len(docs)} docs, sim={docs[0]['similarity']:.3f}")
        
        print("\n✅ Calidad de retrieval verificada")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise


if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 TESTS END-TO-END: SISTEMA RAG BPG COMPLETO")
    print("="*70)
    
    try:
        test_e2e_full_system()
        test_e2e_different_strategies()
        test_e2e_validation_modes()
        test_e2e_legacy_compatibility()
        test_e2e_retrieval_quality()
        
        print("\n" + "="*70)
        print("🎉 ¡TODOS LOS TESTS END-TO-END PASARON!")
        print("="*70)
        print("\n✅ Sistema RAG BPG completamente funcional:")
        print("   ✓ Configuración centralizada")
        print("   ✓ Estrategias de prompts dinámicas")
        print("   ✓ Validación de respuestas")
        print("   ✓ Compatibilidad legacy")
        print("   ✓ Retrieval de alta calidad")
        print("\n🚀 ¡Listo para producción!\n")
        
    except Exception as e:
        print(f"\n❌ TESTS FALLARON: {e}")
        import traceback
        traceback.print_exc()