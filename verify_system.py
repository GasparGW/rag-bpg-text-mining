"""
Script de verificación del sistema RAG BPG
Verifica que todos los componentes estén correctamente instalados y funcionando
"""

import sys
import os

def print_header(text):
    """Imprimir encabezado con formato"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def print_section(text):
    """Imprimir sección con formato"""
    print(f"\n📋 {text}")
    print("-" * 70)

def check_component(name, check_func):
    """Verificar un componente y mostrar resultado"""
    try:
        check_func()
        print(f"✅ {name}")
        return True
    except Exception as e:
        print(f"❌ {name}: {str(e)}")
        return False

def main():
    print_header("🔍 VERIFICACIÓN DEL SISTEMA RAG BPG")
    
    results = []
    
    # 1. Verificar estructura de carpetas
    print_section("Estructura del Proyecto")
    
    def check_folders():
        required = ['config', 'prompts', 'utils', 'tests', 'models']
        for folder in required:
            assert os.path.exists(folder), f"Falta carpeta: {folder}"
    
    results.append(check_component("Estructura de carpetas", check_folders))
    
    # 2. Verificar archivos principales
    print_section("Archivos Principales")
    
    def check_main_files():
        files = [
            'rag_bpg_ollama.py',
            'config/settings.py',
            'prompts/strategies.py',
            'utils/validators.py'
        ]
        for file in files:
            assert os.path.exists(file), f"Falta archivo: {file}"
    
    results.append(check_component("Archivos principales", check_main_files))
    
    # 3. Verificar imports
    print_section("Imports de Módulos")
    
    def check_imports():
        try:
            from config.settings import RAGConfig, DEFAULT_CONFIG
            print("  └─ config.settings: OK")
        except ImportError as e:
            raise ImportError(f"config.settings: {e}")
        
        try:
            from prompts.strategies import PromptFactory
            print("  └─ prompts.strategies: OK")
        except ImportError as e:
            raise ImportError(f"prompts.strategies: {e}")
        
        try:
            from utils.validators import ResponseValidator
            print("  └─ utils.validators: OK")
        except ImportError as e:
            raise ImportError(f"utils.validators: {e}")
        
        try:
            from rag_bpg_ollama import RAGSystemBPG
            print("  └─ rag_bpg_ollama: OK")
        except ImportError as e:
            raise ImportError(f"rag_bpg_ollama: {e}")
    
    results.append(check_component("Imports de módulos", check_imports))
    
    # 4. Verificar dependencias
    print_section("Dependencias de Python")
    
    def check_dependencies():
        deps = ['chromadb', 'sentence_transformers', 'requests']
        for dep in deps:
            try:
                __import__(dep)
                print(f"  └─ {dep}: OK")
            except ImportError:
                raise ImportError(f"{dep} no instalado")
    
    results.append(check_component("Dependencias", check_dependencies))
    
    # 5. Verificar ChromaDB
    print_section("Base de Datos ChromaDB")
    
    def check_chromadb():
        import chromadb
        client = chromadb.PersistentClient(path="models/chroma_db")
        collection = client.get_collection(name="bpg_manuals")
        count = collection.count()
        print(f"  └─ {count} documentos en la colección")
        assert count > 0, "La colección está vacía"
    
    results.append(check_component("ChromaDB", check_chromadb))
    
    # 6. Verificar configuraciones
    print_section("Configuraciones del Sistema")
    
    def check_configs():
        from config.settings import DEFAULT_CONFIG, DEV_CONFIG, FAST_CONFIG, TECHNICAL_CONFIG
        configs = {
            'DEFAULT': DEFAULT_CONFIG,
            'DEV': DEV_CONFIG,
            'FAST': FAST_CONFIG,
            'TECHNICAL': TECHNICAL_CONFIG
        }
        for name, config in configs.items():
            print(f"  └─ {name}: {config.prompt_strategy}, k={config.default_k}")
    
    results.append(check_component("Configuraciones", check_configs))
    
    # 7. Verificar estrategias de prompts
    print_section("Estrategias de Prompts")
    
    def check_strategies():
        from prompts.strategies import PromptFactory, PromptType
        strategies = list(PromptType)
        for pt in strategies:
            strategy = PromptFactory.get_strategy(pt)
            print(f"  └─ {strategy.name}: {strategy.max_tokens_recommended} tokens")
    
    results.append(check_component("Estrategias de prompts", check_strategies))
    
    # 8. Verificar inicialización del sistema
    print_section("Inicialización del Sistema RAG")
    
    def check_rag_init():
        from config.settings import RAGConfig
        from rag_bpg_ollama import RAGSystemBPG
        
        config = RAGConfig(
            prompt_strategy="standard",
            enable_validation=True
        )
        
        rag = RAGSystemBPG(config=config)
        
        print(f"  └─ Config: {rag.config is not None}")
        print(f"  └─ Estrategia: {rag.prompt_strategy.name if rag.prompt_strategy else 'None'}")
        print(f"  └─ Validador: {'Activo' if rag.validator else 'Inactivo'}")
        print(f"  └─ Embeddings: {rag.embedding_model is not None}")
        print(f"  └─ Documentos: {rag.collection.count()}")
    
    results.append(check_component("Sistema RAG", check_rag_init))
    
    # 9. Verificar Ollama (opcional)
    print_section("Ollama (Opcional)")
    
    def check_ollama():
        import requests
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                models = response.json().get('models', [])
                print(f"  └─ Ollama corriendo: {len(models)} modelos disponibles")
            else:
                raise Exception("Ollama no responde correctamente")
        except:
            raise Exception("Ollama no está corriendo (ejecuta: ollama serve)")
    
    ollama_ok = check_component("Ollama", check_ollama)
    if not ollama_ok:
        print("  ℹ️  Ollama es opcional para los tests, pero necesario para generar respuestas")
    
    # Resumen final
    print_header("📊 RESUMEN DE VERIFICACIÓN")
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n✅ Componentes verificados: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 ¡SISTEMA COMPLETAMENTE FUNCIONAL!")
        print("\n🚀 Próximos pasos:")
        print("   1. Ejecutar tests: python3 tests/test_end_to_end.py")
        print("   2. Probar el sistema: python3 rag_bpg_ollama.py")
        print("   3. Modo interactivo: ejecutar y elegir opción 's'")
    else:
        print("\n⚠️  Algunos componentes requieren atención")
        print("   Revisa los errores anteriores y corrige los problemas")
    
    print("\n" + "="*70 + "\n")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)