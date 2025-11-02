"""
Tests para el sistema de validadores de respuestas
"""

import sys
import os

# Agregar la raíz del proyecto al path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from utils.validators import ResponseValidator, ValidationReport


def test_validator_good_response():
    """Test: Validar una respuesta buena"""
    print("\n🧪 TEST 1: Respuesta de buena calidad")
    print("-" * 50)
    
    validator = ResponseValidator()
    
    good_response = """La rampa de carga debe cumplir con los siguientes requisitos:

- Pendiente máxima de 20° (25° si no se usa para terneros)
- Cuanto menor sea la pendiente, más fácil será cargar los animales
- Orientación que evite el sol de frente al amanecer o atardecer
- Tramo final plano de más de 2 metros
- Piso antideslizante (cemento ranurado o con pestañas)

Estas especificaciones están en los manuales de BPG."""
    
    context = "La rampa debe tener 20° de pendiente máxima..."
    query = "¿Qué requisitos debe cumplir la rampa de carga?"
    
    result = validator.validate_response(good_response, context, query)
    
    assert result['is_valid'] == True
    assert result['score'] > 0.7
    
    print(f"✅ Respuesta válida")
    print(f"   Score: {result['score']:.1%}")
    print(f"   Recomendación: {result['recommendations'][0]}")


def test_validator_short_response():
    """Test: Respuesta muy corta"""
    print("\n🧪 TEST 2: Respuesta muy corta")
    print("-" * 50)
    
    validator = ResponseValidator(min_length=50)
    
    short_response = "Sí, es correcto."
    context = "..."
    query = "¿Está bien esto?"
    
    result = validator.validate_response(short_response, context, query)
    
    assert result['is_valid'] == False
    assert result['validations']['length_ok'] == False
    
    print(f"✅ Detectada respuesta corta")
    print(f"   Score: {result['score']:.1%}")
    print(f"   Fallas: {[k for k,v in result['validations'].items() if not v]}")


def test_validator_hallucination():
    """Test: Detectar posible alucinación"""
    print("\n🧪 TEST 3: Detectar alucinación")
    print("-" * 50)
    
    validator = ResponseValidator()
    
    hallucinated_response = """Según mi conocimiento y experiencia, generalmente se recomienda 
que las rampas tengan una pendiente de 15°. Es común que los productores usen cemento."""
    
    context = "..."
    query = "¿Qué pendiente debe tener la rampa?"
    
    result = validator.validate_response(hallucinated_response, context, query)
    
    assert result['validations']['not_hallucinating'] == False
    
    print(f"⚠️  Alucinación detectada")
    print(f"   Score: {result['score']:.1%}")
    print(f"   Recomendaciones: {result['recommendations']}")


def test_validator_fallback_message():
    """Test: Mensaje de fallback apropiado"""
    print("\n🧪 TEST 4: Mensaje de fallback")
    print("-" * 50)
    
    validator = ResponseValidator()
    
    fallback_response = "No encuentro esa información específica en los manuales BPG que tengo disponibles."
    
    context = "..."
    query = "¿Cómo prevenir la mastitis en feedlot?"
    
    result = validator.validate_response(fallback_response, context, query)
    
    assert result['validations']['has_fallback'] == True
    
    print(f"✅ Fallback apropiado")
    print(f"   Score: {result['score']:.1%}")


def test_validator_print_report():
    """Test: Generar reporte visual"""
    print("\n🧪 TEST 5: Reporte de validación")
    print("-" * 50)
    
    validator = ResponseValidator()
    
    response = """Para el manejo del agua en feedlot debés:

- Asegurar acceso constante a agua limpia y fresca
- Mantener los bebederos limpios y funcionales
- Calcular la demanda según el número de animales
- Verificar la calidad del agua regularmente

Según los manuales de BPG, el agua es fundamental para el bienestar animal."""
    
    context = "El agua es esencial..."
    query = "¿Cómo manejar el agua en feedlot?"
    
    result = validator.validate_response(response, context, query)
    
    ValidationReport.print_report(result)
    
    print("✅ Reporte generado correctamente")


def test_validator_integration_with_config():
    """Test: Integración con configuración"""
    print("\n🧪 TEST 6: Integración con RAGConfig")
    print("-" * 50)
    
    try:
        from config.settings import RAGConfig
        
        config = RAGConfig(
            enable_validation=True,
            min_answer_length=30,
            max_answer_length=1500
        )
        
        validator = ResponseValidator(
            min_length=config.min_answer_length,
            max_length=config.max_answer_length
        )
        
        print("✅ Validador creado con config")
        print(f"   Min length: {validator.min_length}")
        print(f"   Max length: {validator.max_length}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 TESTS DE VALIDADORES")
    print("="*60)
    
    try:
        test_validator_good_response()
        test_validator_short_response()
        test_validator_hallucination()
        test_validator_fallback_message()
        test_validator_print_report()
        test_validator_integration_with_config()
        
        print("\n" + "="*60)
        print("✅ TODOS LOS TESTS DE VALIDADORES PASARON")
        print("="*60)
        print("\n💡 Sistema de validación:")
        print("   • Detecta respuestas de baja calidad")
        print("   • Identifica posibles alucinaciones")
        print("   • Genera reportes detallados")
        print("   • Se integra con la configuración\n")
        
    except Exception as e:
        print(f"\n❌ TESTS FALLARON: {e}")
        import traceback
        traceback.print_exc()