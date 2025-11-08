"""
Validadores de calidad de respuestas RAG
Detectan problemas comunes: alucinaciones, respuestas incompletas, etc.
"""

from typing import Dict, List, Optional
import re


class ResponseValidator:
    """
    Validador de respuestas generadas por el sistema RAG
    Evalúa calidad, completitud y precisión de las respuestas
    """
    
    def __init__(
        self,
        min_length: int = 50,
        max_length: int = 2000,
        strict_mode: bool = False
    ):
        """
        Inicializar validador
        
        Args:
            min_length: Longitud mínima aceptable de respuesta
            max_length: Longitud máxima aceptable de respuesta
            strict_mode: Si True, aplica validaciones más estrictas
        """
        self.min_length = min_length
        self.max_length = max_length
        self.strict_mode = strict_mode
    
    def validate_response(
        self,
        response: str,
        context: str,
        query: str
    ) -> Dict:
        """
        Validar respuesta completa
        
        Args:
            response: Respuesta generada por el LLM
            context: Contexto usado (documentos recuperados)
            query: Pregunta original del usuario
            
        Returns:
            Dict con resultados de validación y score
        """
        validations = {
            'length_ok': self._check_length(response),
            'has_content': self._check_has_content(response),
            'has_structure': self._check_structure(response),
            'not_hallucinating': self._check_no_hallucination(response),
            'has_fallback': self._check_fallback_message(response),
            'no_code_blocks': self._check_no_code_blocks(response),
            'proper_spanish': self._check_spanish(response),
            'answers_question': self._check_relevance(response, query),
            'no_instructions_leaked': self._check_no_instructions_leaked(response),
            'contextual_relevance': self._check_contextual_relevance(response, query, context)
        }
        
        # En modo estricto, agregar validaciones adicionales
        if self.strict_mode:
            validations['no_vague_language'] = self._check_no_vague_language(response)
            validations['has_specifics'] = self._check_has_specifics(response)
        
        # Calcular score
        score = sum(validations.values()) / len(validations)
        
        # Determinar si es válida (umbral: 70%)
        is_valid = score >= 0.7
        
        # Generar recomendaciones
        recommendations = self._generate_recommendations(validations)
        
        return {
            'is_valid': is_valid,
            'score': round(score, 3),
            'validations': validations,
            'recommendations': recommendations,
            'details': self._get_validation_details(validations)
        }
    
    # ==================== VALIDACIONES INDIVIDUALES ====================
    
    def _check_length(self, response: str) -> bool:
        """Verificar que la longitud esté en el rango aceptable"""
        length = len(response.strip())
        return self.min_length <= length <= self.max_length
    
    def _check_has_content(self, response: str) -> bool:
        """Verificar que tiene contenido sustancial"""
        # Más de solo espacios en blanco
        return len(response.strip()) > 0 and len(response.split()) >= 10
    
    def _check_structure(self, response: str) -> bool:
        """Verificar que tiene estructura (viñetas, párrafos, etc.)"""
        indicators = [
            '•' in response,  # viñetas
            '\n-' in response or '\n*' in response,  # listas con guiones
            response.count('\n') >= 2,  # múltiples líneas
            ':' in response  # estructura con dos puntos
        ]
        return any(indicators)
    
    def _check_no_hallucination(self, response: str) -> bool:
        """
        Detectar frases que sugieren que el modelo está inventando información
        """
        hallucination_phrases = [
            'según mi conocimiento',
            'basándome en mi experiencia',
            'generalmente se recomienda',
            'es común que',
            'típicamente',
            'en mi opinión',
            'creo que',
            'probablemente',
            'suele ser',
            'normalmente se hace'
        ]
        
        response_lower = response.lower()
        return not any(phrase in response_lower for phrase in hallucination_phrases)
    
    def _check_fallback_message(self, response: str) -> bool:
        """
        Verificar que si no tiene info, lo dice claramente
        O que si tiene info, no usa mensajes de fallback
        """
        fallback_indicators = [
            'no encuentro',
            'no tengo',
            'no hay información',
            'no está en los manuales',
            'no puedo encontrar'
        ]
        
        response_lower = response.lower()
        has_fallback = any(indicator in response_lower for indicator in fallback_indicators)
        
        # Si tiene fallback, la respuesta debe ser corta
        if has_fallback:
            return len(response) < 300
        
        # Si no tiene fallback, debería tener contenido sustancial
        return len(response) > self.min_length
    
    def _check_no_code_blocks(self, response: str) -> bool:
        """Verificar que no tiene bloques de código markdown mal formateados"""
        return '```' not in response
    
    def _check_spanish(self, response: str) -> bool:
        """Verificar que está en español (usando voseo argentino idealmente)"""
        # Indicadores de español argentino
        voseo_indicators = ['sos', 'tenés', 'podés', 'debés', 'hacés', 'querés']
        spanish_words = ['el', 'la', 'los', 'las', 'que', 'para', 'con', 'en']
        
        response_lower = response.lower()
        
        # Al menos debe tener palabras en español
        has_spanish = any(word in response_lower for word in spanish_words)
        
        # Bonus si usa voseo
        has_voseo = any(word in response_lower for word in voseo_indicators)
        
        return has_spanish
    
    def _check_relevance(self, response: str, query: str) -> bool:
        """
        Verificar que la respuesta está relacionada con la pregunta
        """
        # Extraer palabras clave de la pregunta
        query_words = set(query.lower().split())
        response_words = set(response.lower().split())
        
        # Palabras comunes a ignorar
        stop_words = {'el', 'la', 'los', 'las', 'un', 'una', 'de', 'en', 'y', 'a', 'para', 
                     'con', 'por', 'que', 'del', 'al', 'es', 'como', 'se', '¿', '?'}
        
        query_keywords = query_words - stop_words
        
        # Al menos 30% de las palabras clave deberían aparecer en la respuesta
        if not query_keywords:
            return True
        
        overlap = len(query_keywords & response_words)
        relevance_ratio = overlap / len(query_keywords)
        
        return relevance_ratio >= 0.3
    
    def _check_no_vague_language(self, response: str) -> bool:
        """Verificar que no usa lenguaje vago (modo estricto)"""
        vague_phrases = [
            'puede ser',
            'tal vez',
            'quizás',
            'posiblemente',
            'eventualmente',
            'aproximadamente' # OK si está con números
        ]
        
        response_lower = response.lower()
        return not any(phrase in response_lower for phrase in vague_phrases)
    
    def _check_has_specifics(self, response: str) -> bool:
        """Verificar que tiene datos específicos: números, medidas, etc."""
        # Buscar números, porcentajes, medidas
        has_numbers = bool(re.search(r'\d+', response))
        has_units = bool(re.search(r'\d+\s*(°|m|cm|kg|%|grados|metros|centímetros)', response))
        
        return has_numbers or has_units
    
    def _check_no_instructions_leaked(self, response: str) -> bool:
        """
        Detectar si la respuesta incluye las instrucciones del prompt
        CRÍTICO: Indica que el LLM no entendió su tarea
        """
        instruction_indicators = [
            'ANÁLISIS PREVIO',
            'FORMATO DE RESPUESTA',
            'REGLAS ESTRICTAS',
            'INSTRUCCIONES:',
            'SI LA INFO NO ESTÁ',
            'ESTRUCTURA IDEAL',
            'respondé solo',
            'máximo 300 palabras',
            'comenzá directo',
            'usá viñetas'
        ]
        
        response_upper = response.upper()
        leaked = [ind for ind in instruction_indicators if ind.upper() in response_upper]
        
        if leaked:
            return False
        
        return True
    
    def _check_contextual_relevance(self, response: str, query: str, context: str) -> bool:
        """
        Verificar que la respuesta use palabras del contexto proporcionado
        Si responde sobre temas no mencionados en el contexto = problema
        """
        # Extraer palabras significativas de la respuesta (>4 letras)
        response_words = set(word.lower() for word in re.findall(r'\b\w{5,}\b', response))
        
        # Extraer palabras del contexto
        context_words = set(word.lower() for word in re.findall(r'\b\w{5,}\b', context))
        
        # Si es mensaje de fallback, es OK
        if any(phrase in response.lower() for phrase in ['no encuentro', 'no tengo', 'no hay información']):
            return True
        
        # Al menos 30% de las palabras significativas deben estar en el contexto
        if not response_words:
            return False
        
        overlap = len(response_words & context_words)
        relevance_ratio = overlap / len(response_words)
        
        return relevance_ratio >= 0.3
    
    # ==================== GENERACIÓN DE RECOMENDACIONES ====================
    
    def _generate_recommendations(self, validations: Dict[str, bool]) -> List[str]:
        """Generar recomendaciones basadas en validaciones fallidas"""
        recommendations = []
        
        if not validations['length_ok']:
            recommendations.append("Ajustar longitud de respuesta (muy corta o muy larga)")
        
        if not validations['has_content']:
            recommendations.append("Respuesta vacía o con contenido insuficiente")
        
        if not validations['has_structure']:
            recommendations.append("Mejorar estructura: usar viñetas o párrafos")
        
        if not validations['not_hallucinating']:
            recommendations.append("⚠️ CRÍTICO: Posible alucinación detectada")
        
        if not validations['no_code_blocks']:
            recommendations.append("Remover bloques de código markdown")
        
        if not validations['proper_spanish']:
            recommendations.append("Verificar que la respuesta esté en español")
        
        if not validations['answers_question']:
            recommendations.append("Respuesta no parece relacionada con la pregunta")
        
        # Validaciones de modo estricto
        if 'no_vague_language' in validations and not validations['no_vague_language']:
            recommendations.append("Evitar lenguaje vago, ser más específico")
        
        if 'has_specifics' in validations and not validations['has_specifics']:
            recommendations.append("Incluir datos específicos (números, medidas)")
        
        if 'no_instructions_leaked' in validations and not validations['no_instructions_leaked']:
            recommendations.append("🚨 CRÍTICO: El LLM está repitiendo las instrucciones del prompt. Revisar diseño del prompt.")
        
        if 'contextual_relevance' in validations and not validations['contextual_relevance']:
            recommendations.append("⚠️ IMPORTANTE: La respuesta parece no usar el contexto proporcionado. Posible alucinación.")
        
        if not recommendations:
            recommendations.append("✅ Respuesta cumple con todos los criterios de calidad")
        
        return recommendations
    
    def _get_validation_details(self, validations: Dict[str, bool]) -> Dict[str, str]:
        """Obtener detalles de cada validación"""
        details = {}
        
        for key, passed in validations.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            details[key] = status
        
        return details


class ValidationReport:
    """Generador de reportes de validación"""
    
    @staticmethod
    def print_report(validation_result: Dict):
        """Imprimir reporte de validación de forma legible"""
        print("\n" + "="*60)
        print("📊 REPORTE DE VALIDACIÓN DE RESPUESTA")
        print("="*60)
        
        # Score general
        score = validation_result['score']
        is_valid = validation_result['is_valid']
        
        status_emoji = "✅" if is_valid else "⚠️"
        print(f"\n{status_emoji} Score de Calidad: {score:.1%}")
        print(f"   Estado: {'VÁLIDA' if is_valid else 'REQUIERE ATENCIÓN'}")
        
        # Detalles de validaciones
        print("\n📋 Detalle de Validaciones:")
        for check, status in validation_result['details'].items():
            check_name = check.replace('_', ' ').title()
            print(f"   {status} {check_name}")
        
        # Recomendaciones
        if validation_result['recommendations']:
            print("\n💡 Recomendaciones:")
            for rec in validation_result['recommendations']:
                print(f"   • {rec}")
        
        print("="*60 + "\n")