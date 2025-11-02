"""
Test de optimizaciones: prompt simplificado + validación mejorada
"""

from config.settings import RAGConfig
from rag_bpg_ollama import RAGSystemBPG

print("="*70)
print("🧪 TESTING OPTIMIZACIONES")
print("="*70)

# Configuración con validación activada
config = RAGConfig(
    prompt_strategy="standard",
    enable_validation=True,
    verbose=False
)

rag = RAGSystemBPG(config=config)

# Test 1: La query problemática original
print("\n" + "="*70)
print("TEST 1: Query ambigua que falló antes")
print("="*70)

resultado1 = rag.query("como vacuno a los animales y con que?", verbose=False)

print(f"\n📝 RESPUESTA:\n{resultado1['answer'][:500]}...")

if resultado1.get('validation'):
    val = resultado1['validation']
    print(f"\n🔍 VALIDACIÓN:")
    print(f"   Score: {val['score']:.1%}")
    print(f"   Válida: {'✅' if val['is_valid'] else '❌'}")
    print(f"\n🆕 NUEVAS VALIDACIONES:")
    print(f"   No instrucciones: {'✅' if val['validations']['no_instructions_leaked'] else '❌'}")
    print(f"   Relevancia: {'✅' if val['validations']['contextual_relevance'] else '❌'}")
    if not val['is_valid']:
        print(f"\n⚠️  Recomendación: {val['recommendations'][0]}")

# Test 2: Query normal
print("\n" + "="*70)
print("TEST 2: Query clara sobre bienestar animal")
print("="*70)

resultado2 = rag.query("¿Qué es el bienestar animal?", verbose=False)

print(f"\n📝 RESPUESTA:\n{resultado2['answer'][:300]}...")

if resultado2.get('validation'):
    val = resultado2['validation']
    print(f"\n🔍 VALIDACIÓN: Score {val['score']:.1%} - {'✅ Válida' if val['is_valid'] else '❌ Revisar'}")

# Test 3: Info no disponible
print("\n" + "="*70)
print("TEST 3: Info no disponible (debe reconocer que no sabe)")
print("="*70)

resultado3 = rag.query("¿Cómo criar alpacas en la Patagonia?", verbose=False)

print(f"\n📝 RESPUESTA:\n{resultado3['answer']}")

if resultado3.get('validation'):
    val = resultado3['validation']
    print(f"\n🔍 VALIDACIÓN: Score {val['score']:.1%}")
    print(f"   Tiene fallback apropiado: {'✅' if val['validations']['has_fallback'] else '❌'}")

print("\n" + "="*70)
print("✅ TESTING COMPLETADO")
print("="*70)
