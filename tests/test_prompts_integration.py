"""
Tests de integración: verificar que las estrategias de prompts funcionan en el RAG
"""

import sys
import os

# ✨ ARREGLADO: Agregar la raíz del proyecto al path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)


def test_prompt_strategy_standard():
    """Test: RAG con estrategia Standard"""
    print("\n🧪 TEST 1: Estrategia STANDARD")
    print("-" * 50)
    
    try:
        from config.settings import RAGConfig
        from rag_bpg_ollama import RAGSystemBPG
        
        # Crear config con estrategia standard
        config = RAGConfig(prompt_strategy="standard")
        rag = RAGSystemBPG(config=config)
        
        # Verificar que la estrategia se cargó
        assert rag.prompt_strategy is not None
        assert rag.prompt_strategy.name == "Standard"
        
        print("✅ Estrategia Standard cargada")
        print(f"   • Nombre: {rag.prompt_strategy.name}")
        print(f"   • Max tokens: {rag.prompt_strategy.max_tokens_recommended}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise


def test_prompt_strategy_concise():
    """Test: RAG con estrategia Concise"""
    print("\n🧪 TEST 2: Estrategia CONCISE")
    print("-" * 50)
    
    try:
        from config.settings import RAGConfig
        from rag_bpg_ollama import RAGSystemBPG
        
        config = RAGConfig(prompt_strategy="concise")
        rag = RAGSystemBPG(config=config)
        
        assert rag.prompt_strategy is not None
        assert rag.prompt_strategy.name == "Concise"
        assert rag.prompt_strategy.max_tokens_recommended == 300
        
        print("✅ Estrategia Concise cargada")
        print(f"   • Nombre: {rag.prompt_strategy.name}")
        print(f"   • Max tokens: {rag.prompt_strategy.max_tokens_recommended}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise


def test_prompt_strategy_fewshot():
    """Test: RAG con estrategia Few-Shot"""
    print("\n🧪 TEST 3: Estrategia FEW-SHOT")
    print("-" * 50)
    
    try:
        from config.settings import RAGConfig
        from rag_bpg_ollama import RAGSystemBPG
        
        config = RAGConfig(prompt_strategy="fewshot")
        rag = RAGSystemBPG(config=config)
        
        assert rag.prompt_strategy is not None
        assert rag.prompt_strategy.name == "Few-Shot"
        assert rag.prompt_strategy.max_tokens_recommended == 600
        
        print("✅ Estrategia Few-Shot cargada")
        print(f"   • Nombre: {rag.prompt_strategy.name}")
        print(f"   • Max tokens: {rag.prompt_strategy.max_tokens_recommended}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise


def test_prompt_strategy_technical():
    """Test: RAG con estrategia Technical"""
    print("\n🧪 TEST 4: Estrategia TECHNICAL")
    print("-" * 50)
    
    try:
        from config.settings import RAGConfig
        from rag_bpg_ollama import RAGSystemBPG
        
        config = RAGConfig(prompt_strategy="technical")
        rag = RAGSystemBPG(config=config)
        
        assert rag.prompt_strategy is not None
        assert rag.prompt_strategy.name == "Technical"
        assert rag.prompt_strategy.max_tokens_recommended == 700
        
        print("✅ Estrategia Technical cargada")
        print(f"   • Nombre: {rag.prompt_strategy.name}")
        print(f"   • Max tokens: {rag.prompt_strategy.max_tokens_recommended}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise


def test_prompt_build():
    """Test: Construir prompt con cada estrategia"""
    print("\n🧪 TEST 5: Construcción de prompts")
    print("-" * 50)
    
    try:
        from config.settings import RAGConfig
        from rag_bpg_ollama import RAGSystemBPG
        
        context_mock = "La rampa debe tener 20° de pendiente."
        query_mock = "¿Qué pendiente debe tener la rampa?"
        
        strategies = ["standard", "concise", "fewshot", "technical"]
        
        for strategy_name in strategies:
            config = RAGConfig(prompt_strategy=strategy_name)
            rag = RAGSystemBPG(config=config)
            
            # Construir prompt
            prompt = rag.prompt_strategy.build(context_mock, query_mock)
            
            # Verificar que contiene elementos clave
            assert context_mock in prompt
            assert query_mock in prompt
            assert len(prompt) > 100
            
            print(f"✅ {rag.prompt_strategy.name}: {len(prompt)} chars")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise


def test_legacy_compatibility():
    """Test: Compatibilidad con modo legacy (sin estrategia)"""
    print("\n🧪 TEST 6: Modo legacy (sin estrategia)")
    print("-" * 50)
    
    try:
        from rag_bpg_ollama import RAGSystemBPG
        
        # Crear RAG sin config (modo legacy)
        rag = RAGSystemBPG(ollama_model="llama3.2")
        
        # En modo legacy, prompt_strategy debería funcionar igual
        print(f"✅ Modo legacy funciona")
        print(f"   • Estrategia: {rag.prompt_strategy.name if rag.prompt_strategy else 'None (Legacy)'}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise


def test_changing_strategies():
    """Test: Cambiar entre estrategias"""
    print("\n🧪 TEST 7: Cambio de estrategias")
    print("-" * 50)
    
    try:
        from config.settings import RAGConfig
        from rag_bpg_ollama import RAGSystemBPG
        
        strategies = ["standard", "concise", "fewshot", "technical"]
        results = []
        
        for strat in strategies:
            config = RAGConfig(prompt_strategy=strat)
            rag = RAGSystemBPG(config=config)
            results.append({
                'name': rag.prompt_strategy.name,
                'tokens': rag.prompt_strategy.max_tokens_recommended
            })
        
        # Verificar que se cargaron diferentes estrategias
        names = [r['name'] for r in results]
        assert len(set(names)) == 4  # 4 estrategias únicas
        
        print("✅ Cambio de estrategias funciona")
        for r in results:
            print(f"   • {r['name']}: {r['tokens']} tokens")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 TESTS DE INTEGRACIÓN: PROMPTS + RAG")
    print("="*60)
    
    try:
        test_prompt_strategy_standard()
        test_prompt_strategy_concise()
        test_prompt_strategy_fewshot()
        test_prompt_strategy_technical()
        test_prompt_build()
        test_legacy_compatibility()
        test_changing_strategies()
        
        print("\n" + "="*60)
        print("✅ TODOS LOS TESTS DE INTEGRACIÓN PASARON")
        print("="*60)
        print("\n💡 Tu RAG ahora:")
        print("   • Usa estrategias de prompts configurables")
        print("   • Cambia dinámicamente según configuración")
        print("   • Mantiene compatibilidad legacy")
        print("   • Está listo para validadores (PASO 6)\n")
        
    except Exception as e:
        print(f"\n❌ TESTS FALLARON: {e}")
        import traceback
        traceback.print_exc()