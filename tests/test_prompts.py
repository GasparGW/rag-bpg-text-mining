"""
Tests para verificar estrategias de prompts
"""

import sys
import os

# ✨ ARREGLADO: Agregar la raíz del proyecto al path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from prompts.strategies import (
    PromptFactory,
    PromptType,
    StandardPromptStrategy,
    ConcisePromptStrategy,
    FewShotPromptStrategy,
    TechnicalPromptStrategy
)


def test_factory_get_strategy():
    """Test: Obtener estrategias por tipo"""
    print("\n🧪 TEST 1: Factory - Get Strategy")
    print("-" * 50)
    
    standard = PromptFactory.get_strategy(PromptType.STANDARD)
    concise = PromptFactory.get_strategy(PromptType.CONCISE)
    fewshot = PromptFactory.get_strategy(PromptType.FEWSHOT)
    technical = PromptFactory.get_strategy(PromptType.TECHNICAL)
    
    assert isinstance(standard, StandardPromptStrategy)
    assert isinstance(concise, ConcisePromptStrategy)
    assert isinstance(fewshot, FewShotPromptStrategy)
    assert isinstance(technical, TechnicalPromptStrategy)
    
    print("✅ Todas las estrategias se obtienen correctamente")
    print(f"   • Standard: {standard.name}")
    print(f"   • Concise: {concise.name}")
    print(f"   • FewShot: {fewshot.name}")
    print(f"   • Technical: {technical.name}")


def test_factory_get_by_name():
    """Test: Obtener estrategias por nombre (string)"""
    print("\n🧪 TEST 2: Factory - Get by Name")
    print("-" * 50)
    
    standard = PromptFactory.get_strategy_by_name("standard")
    concise = PromptFactory.get_strategy_by_name("concise")
    
    assert standard.name == "Standard"
    assert concise.name == "Concise"
    
    # Test con nombre inválido (debe devolver standard)
    invalid = PromptFactory.get_strategy_by_name("noexiste")
    assert invalid.name == "Standard"
    
    print("✅ Get by name funciona correctamente")
    print(f"   • 'standard' -> {standard.name}")
    print(f"   • 'concise' -> {concise.name}")
    print(f"   • 'noexiste' -> {invalid.name} (fallback)")


def test_list_strategies():
    """Test: Listar estrategias"""
    print("\n🧪 TEST 3: Listar Estrategias")
    print("-" * 50)
    
    strategies = PromptFactory.list_strategies()
    
    assert len(strategies) == 4
    assert "standard" in strategies
    assert "concise" in strategies
    assert "fewshot" in strategies
    assert "technical" in strategies
    
    print("✅ Lista de estrategias:")
    for name, desc in strategies.items():
        print(f"   • {name}: {desc}")


def test_build_prompts():
    """Test: Construir prompts reales"""
    print("\n🧪 TEST 4: Construcción de Prompts")
    print("-" * 50)
    
    context = "La rampa debe tener 20° de pendiente máxima."
    query = "¿Qué pendiente debe tener la rampa?"
    
    # Test cada estrategia
    for pt in PromptType:
        strategy = PromptFactory.get_strategy(pt)
        prompt = strategy.build(context, query)
        
        # Verificar que el prompt contiene elementos clave
        assert context in prompt
        assert query in prompt
        assert len(prompt) > 100  # Prompt debe ser sustancial
        
        print(f"✅ {strategy.name}: {len(prompt)} caracteres")


def test_max_tokens():
    """Test: Verificar max_tokens recomendados"""
    print("\n🧪 TEST 5: Max Tokens Recomendados")
    print("-" * 50)
    
    expected_tokens = {
        PromptType.STANDARD: 500,
        PromptType.CONCISE: 300,
        PromptType.FEWSHOT: 600,
        PromptType.TECHNICAL: 700
    }
    
    for pt, expected in expected_tokens.items():
        strategy = PromptFactory.get_strategy(pt)
        actual = strategy.max_tokens_recommended
        assert actual == expected, f"{pt.value}: esperaba {expected}, obtuvo {actual}"
        print(f"✅ {strategy.name}: {actual} tokens")


def test_print_strategies():
    """Test: Imprimir estrategias"""
    print("\n🧪 TEST 6: Print Strategies")
    print("-" * 50)
    
    PromptFactory.print_strategies()
    
    print("✅ Print strategies OK")


def test_prompt_content():
    """Test: Verificar contenido de prompts"""
    print("\n🧪 TEST 7: Verificar Contenido de Prompts")
    print("-" * 50)
    
    context = "Ejemplo de contexto BPG"
    query = "¿Cómo hacer algo?"
    
    # Standard debe tener instrucciones detalladas
    standard = PromptFactory.get_strategy(PromptType.STANDARD)
    standard_prompt = standard.build(context, query)
    assert "INSTRUCCIONES" in standard_prompt
    assert "REGLAS ESTRICTAS" in standard_prompt
    print("✅ Standard: tiene instrucciones detalladas")
    
    # Concise debe ser más corto
    concise = PromptFactory.get_strategy(PromptType.CONCISE)
    concise_prompt = concise.build(context, query)
    assert len(concise_prompt) < len(standard_prompt)
    print("✅ Concise: es más corto que Standard")
    
    # FewShot debe tener ejemplos
    fewshot = PromptFactory.get_strategy(PromptType.FEWSHOT)
    fewshot_prompt = fewshot.build(context, query)
    assert "EJEMPLOS" in fewshot_prompt
    assert "Pregunta:" in fewshot_prompt
    print("✅ FewShot: contiene ejemplos")
    
    # Technical debe mencionar normativas
    technical = PromptFactory.get_strategy(PromptType.TECHNICAL)
    technical_prompt = technical.build(context, query)
    assert "NORMATIV" in technical_prompt.upper()
    assert "TÉCNIC" in technical_prompt.upper()
    print("✅ Technical: enfoque en normativas")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 TESTS DE ESTRATEGIAS DE PROMPTS")
    print("="*60)
    
    try:
        test_factory_get_strategy()
        test_factory_get_by_name()
        test_list_strategies()
        test_build_prompts()
        test_max_tokens()
        test_print_strategies()
        test_prompt_content()
        
        print("\n" + "="*60)
        print("✅ TODOS LOS TESTS PASARON")
        print("="*60 + "\n")
        
    except AssertionError as e:
        print(f"\n❌ TEST FALLÓ: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()