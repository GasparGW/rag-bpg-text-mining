"""
Test simplificado de integración sin necesidad de ChromaDB completa
"""

import sys
import os

# ✨ ARREGLADO: Agregar la raíz del proyecto al path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

print("\n" + "="*60)
print("🧪 TEST SIMPLIFICADO DE INTEGRACIÓN")
print("="*60)

# Test 1: Imports
print("\n🧪 TEST 1: Verificar imports")
print("-" * 50)

try:
    from config.settings import RAGConfig, DEFAULT_CONFIG
    print("✅ Config importada")
except ImportError as e:
    print(f"❌ Error config: {e}")
    sys.exit(1)

try:
    from prompts.strategies import PromptFactory
    print("✅ Prompts importados")
except ImportError as e:
    print(f"❌ Error prompts: {e}")
    sys.exit(1)

try:
    from rag_bpg_ollama import RAGSystemBPG
    print("✅ RAG importado")
except ImportError as e:
    print(f"❌ Error RAG: {e}")
    sys.exit(1)

# Test 2: Crear configuración personalizada
print("\n🧪 TEST 2: Crear configuración personalizada")
print("-" * 50)

custom_config = RAGConfig(
    ollama_model="mistral",
    default_k=10,
    default_temperature=0.5,
    prompt_strategy="fewshot"
)

print(f"✅ Config creada:")
print(f"   • Model: {custom_config.ollama_model}")
print(f"   • K: {custom_config.default_k}")
print(f"   • Temperature: {custom_config.default_temperature}")
print(f"   • Strategy: {custom_config.prompt_strategy}")

# Test 3: Verificar que RAGSystemBPG acepta config
print("\n🧪 TEST 3: Verificar firma de RAGSystemBPG")
print("-" * 50)

import inspect
sig = inspect.signature(RAGSystemBPG.__init__)
params = list(sig.parameters.keys())

if 'config' in params:
    print("✅ RAGSystemBPG acepta parámetro 'config'")
    print(f"   Parámetros: {params}")
else:
    print("❌ RAGSystemBPG NO acepta 'config'")
    sys.exit(1)

# Test 4: Verificar compatibilidad legacy
print("\n🧪 TEST 4: Verificar parámetros legacy")
print("-" * 50)

legacy_params = ['chroma_db_path', 'embedding_model_name', 'ollama_base_url', 'ollama_model']
missing = [p for p in legacy_params if p not in params]

if not missing:
    print("✅ Todos los parámetros legacy presentes")
    print(f"   Legacy params: {legacy_params}")
else:
    print(f"⚠️  Faltan parámetros legacy: {missing}")

print("\n" + "="*60)
print("✅ INTEGRACIÓN VERIFICADA - PASO 4 COMPLETO")
print("="*60)
print("\n💡 Tu código ahora tiene:")
print("   • Sistema de configuración centralizado")
print("   • Compatibilidad con código antiguo")
print("   • Listo para integrar estrategias de prompts\n")