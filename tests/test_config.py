"""
Tests para verificar que la configuración funciona correctamente
"""

import sys
import os

# ✨ ARREGLADO: Agregar la raíz del proyecto al path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from config.settings import (
    RAGConfig, 
    DEFAULT_CONFIG, 
    DEV_CONFIG, 
    FAST_CONFIG,
    TECHNICAL_CONFIG,
    get_config,
    print_config
)


def test_default_config():
    """Probar configuración por defecto"""
    print("\n🧪 TEST 1: Configuración por defecto")
    print("-" * 50)
    
    config = DEFAULT_CONFIG
    
    assert config.chroma_db_path == "models/chroma_db"
    assert config.ollama_model == "llama3.2"
    assert config.default_k == 5
    assert config.default_temperature == 0.7
    
    print("✅ Configuración por defecto OK")
    print(f"   • DB: {config.chroma_db_path}")
    print(f"   • Model: {config.ollama_model}")


def test_custom_config():
    """Probar crear configuración personalizada"""
    print("\n🧪 TEST 2: Configuración personalizada")
    print("-" * 50)
    
    custom_config = RAGConfig(
        ollama_model="mistral",
        default_temperature=0.5,
        default_k=10,
        enable_validation=True
    )
    
    assert custom_config.ollama_model == "mistral"
    assert custom_config.default_temperature == 0.5
    assert custom_config.default_k == 10
    assert custom_config.enable_validation == True
    
    print("✅ Configuración personalizada OK")
    print(f"   • Model: {custom_config.ollama_model}")
    print(f"   • K: {custom_config.default_k}")


def test_validation():
    """Probar validaciones de configuración"""
    print("\n🧪 TEST 3: Validaciones")
    print("-" * 50)
    
    # Temperatura fuera de rango
    try:
        bad_config = RAGConfig(default_temperature=1.5)
        print("❌ ERROR: Debería haber fallado con temperature > 1")
    except ValueError as e:
        print(f"✅ Validación OK: {e}")
    
    # K negativo
    try:
        bad_config = RAGConfig(default_k=-1)
        print("❌ ERROR: Debería haber fallado con k < 1")
    except ValueError as e:
        print(f"✅ Validación OK: {e}")


def test_get_config_by_name():
    """Probar obtener configs por nombre"""
    print("\n🧪 TEST 4: Obtener configs por nombre")
    print("-" * 50)
    
    configs = {
        "default": get_config("default"),
        "dev": get_config("dev"),
        "fast": get_config("fast"),
        "technical": get_config("technical")
    }
    
    assert configs["default"].prompt_strategy == "standard"
    assert configs["dev"].enable_validation == True
    assert configs["fast"].default_k == 3
    assert configs["technical"].default_max_tokens == 700
    
    print("✅ Todas las configs disponibles:")
    for name, cfg in configs.items():
        print(f"   • {name}: strategy={cfg.prompt_strategy}, k={cfg.default_k}")


def test_to_dict():
    """Probar conversión a diccionario"""
    print("\n🧪 TEST 5: Conversión to_dict()")
    print("-" * 50)
    
    config = DEFAULT_CONFIG
    config_dict = config.to_dict()
    
    assert isinstance(config_dict, dict)
    assert config_dict['ollama_model'] == 'llama3.2'
    assert config_dict['default_k'] == 5
    
    print("✅ Conversión a dict OK")
    print(f"   • Keys: {len(config_dict)}")


def test_print_config():
    """Probar impresión de config"""
    print("\n🧪 TEST 6: Impresión de configuración")
    print("-" * 50)
    
    print_config(TECHNICAL_CONFIG)
    
    print("✅ Impresión OK")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 TESTS DE CONFIGURACIÓN RAG BPG")
    print("="*60)
    
    try:
        test_default_config()
        test_custom_config()
        test_validation()
        test_get_config_by_name()
        test_to_dict()
        test_print_config()
        
        print("\n" + "="*60)
        print("✅ TODOS LOS TESTS PASARON")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR EN TESTS: {e}")
        import traceback
        traceback.print_exc()