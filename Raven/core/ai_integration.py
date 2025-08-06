#!/usr/bin/env python3
"""
RAVEN AI INTEGRATION MODULE
Permite a Raven aprender de GPT-4 y Claude Sonnet 4 como fuentes de conocimiento
"""

import openai
import anthropic
import json
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class AIResponse:
    """Estructura para respuestas de modelos AI"""
    model: str
    response: str
    confidence: float
    metadata: Dict[str, Any]
    timestamp: str

class RavenAIIntegration:
    """
    Módulo de integración que permite a Raven consultar y aprender de otros modelos AI
    """
    
    def __init__(self, openai_key: Optional[str] = None, anthropic_key: Optional[str] = None):
        """
        Inicializa las conexiones con los modelos base
        
        Args:
            openai_key: API key para OpenAI GPT-4
            anthropic_key: API key para Anthropic Claude
        """
        self.gpt4_available = False
        self.claude_available = False
        
        # Configurar GPT-4
        if openai_key:
            try:
                openai.api_key = openai_key
                self.gpt4_available = True
                logger.info("✅ GPT-4 configurado correctamente")
            except Exception as e:
                logger.error(f"❌ Error configurando GPT-4: {e}")
        
        # Configurar Claude
        if anthropic_key:
            try:
                self.claude_client = anthropic.Anthropic(api_key=anthropic_key)
                self.claude_available = True
                logger.info("✅ Claude Sonnet 4 configurado correctamente")
            except Exception as e:
                logger.error(f"❌ Error configurando Claude: {e}")
        
        # Cache de respuestas para optimización
        self.response_cache = {}
        
        # Especialidades de cada modelo
        self.model_specialties = {
            'gpt4': ['code_analysis', 'mathematical_reasoning', 'pattern_recognition'],
            'claude': ['detailed_analysis', 'structured_thinking', 'fractal_theory']
        }
    
    async def query_gpt4(self, prompt: str, context: Dict = None) -> AIResponse:
        """
        Consulta GPT-4 con un prompt específico
        
        Args:
            prompt: Pregunta o solicitud para GPT-4
            context: Contexto adicional sobre el análisis actual de Raven
            
        Returns:
            AIResponse con la respuesta de GPT-4
        """
        if not self.gpt4_available:
            return AIResponse("gpt4", "No disponible", 0.0, {}, datetime.now().isoformat())
        
        try:
            # Construir prompt enriquecido con contexto de Raven
            enhanced_prompt = self._build_raven_context_prompt(prompt, context, "gpt4")
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Eres un experto en análisis fractal y matemáticas colaborando con el sistema Raven."},
                    {"role": "user", "content": enhanced_prompt}
                ],
                max_tokens=1500,
                temperature=0.3
            )
            
            content = response.choices[0].message.content
            confidence = self._estimate_confidence(content)
            
            return AIResponse(
                model="gpt4",
                response=content,
                confidence=confidence,
                metadata={
                    "tokens_used": response.usage.total_tokens,
                    "model_version": "gpt-4"
                },
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Error consultando GPT-4: {e}")
            return AIResponse("gpt4", f"Error: {str(e)}", 0.0, {}, datetime.now().isoformat())
    
    async def query_claude(self, prompt: str, context: Dict = None) -> AIResponse:
        """
        Consulta Claude Sonnet 4 con un prompt específico
        
        Args:
            prompt: Pregunta o solicitud para Claude
            context: Contexto adicional sobre el análisis actual de Raven
            
        Returns:
            AIResponse con la respuesta de Claude
        """
        if not self.claude_available:
            return AIResponse("claude", "No disponible", 0.0, {}, datetime.now().isoformat())
        
        try:
            # Construir prompt enriquecido con contexto de Raven
            enhanced_prompt = self._build_raven_context_prompt(prompt, context, "claude")
            
            message = await self.claude_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1500,
                temperature=0.3,
                messages=[{
                    "role": "user",
                    "content": enhanced_prompt
                }]
            )
            
            content = message.content[0].text
            confidence = self._estimate_confidence(content)
            
            return AIResponse(
                model="claude",
                response=content,
                confidence=confidence,
                metadata={
                    "tokens_used": message.usage.input_tokens + message.usage.output_tokens,
                    "model_version": "claude-sonnet-4"
                },
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Error consultando Claude: {e}")
            return AIResponse("claude", f"Error: {str(e)}", 0.0, {}, datetime.now().isoformat())
    
    def _build_raven_context_prompt(self, prompt: str, context: Dict, target_model: str) -> str:
        """
        Construye un prompt enriquecido con el contexto de Raven
        
        Args:
            prompt: Prompt original
            context: Contexto del análisis de Raven
            target_model: Modelo objetivo (gpt4/claude)
            
        Returns:
            Prompt enriquecido con contexto
        """
        raven_context = ""
        
        if context:
            raven_context = f"""
CONTEXTO DEL SISTEMA RAVEN:
- Análisis fractal en curso
- Dimensión Hausdorff detectada: {context.get('hausdorff_dimension', 'N/A')}
- Cluster identificado: {context.get('cluster_name', 'N/A')}
- Confianza actual: {context.get('confidence', 'N/A')}
- Características clave: {context.get('key_features', [])}

"""
        
        specialties_note = ""
        if target_model in self.model_specialties:
            specialties = ", ".join(self.model_specialties[target_model])
            specialties_note = f"\nNOTA: Aplica tu expertise en: {specialties}"
        
        return f"""{raven_context}CONSULTA DE RAVEN:
{prompt}
{specialties_note}

Por favor proporciona una respuesta detallada y técnicamente precisa que pueda ser integrada en el análisis de Raven."""
    
    def _estimate_confidence(self, response: str) -> float:
        """
        Estima la confianza de una respuesta basada en indicadores textuales
        
        Args:
            response: Respuesta del modelo
            
        Returns:
            Valor de confianza entre 0.0 y 1.0
        """
        confidence_indicators = {
            'high': ['definitivamente', 'claramente', 'precisamente', 'exactamente', 'sin duda'],
            'medium': ['probablemente', 'posiblemente', 'típicamente', 'generalmente'],
            'low': ['quizás', 'podría ser', 'incierto', 'difícil determinar', 'no está claro']
        }
        
        response_lower = response.lower()
        
        high_count = sum(1 for indicator in confidence_indicators['high'] if indicator in response_lower)
        medium_count = sum(1 for indicator in confidence_indicators['medium'] if indicator in response_lower)
        low_count = sum(1 for indicator in confidence_indicators['low'] if indicator in response_lower)
        
        # Calcular confianza basada en indicadores
        if high_count > low_count:
            base_confidence = 0.8
        elif medium_count > 0:
            base_confidence = 0.6
        else:
            base_confidence = 0.4
        
        # Ajustar por longitud y detalle de la respuesta
        length_factor = min(1.0, len(response) / 1000)
        
        return min(1.0, base_confidence + length_factor * 0.2)
    
    async def multi_model_consensus(self, prompt: str, context: Dict = None) -> Dict[str, Any]:
        """
        Obtiene consenso de múltiples modelos sobre una consulta
        
        Args:
            prompt: Pregunta para los modelos
            context: Contexto del análisis de Raven
            
        Returns:
            Dict con respuestas de todos los modelos y análisis de consenso
        """
        tasks = []
        
        if self.gpt4_available:
            tasks.append(self.query_gpt4(prompt, context))
        
        if self.claude_available:
            tasks.append(self.query_claude(prompt, context))
        
        if not tasks:
            return {
                'error': 'No hay modelos AI disponibles',
                'consensus': None,
                'responses': []
            }
        
        # Ejecutar consultas en paralelo
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filtrar respuestas válidas
        valid_responses = [r for r in responses if isinstance(r, AIResponse)]
        
        if not valid_responses:
            return {
                'error': 'No se obtuvieron respuestas válidas',
                'consensus': None,
                'responses': []
            }
        
        # Analizar consenso
        consensus_analysis = self._analyze_consensus(valid_responses)
        
        return {
            'responses': [r.__dict__ for r in valid_responses],
            'consensus': consensus_analysis,
            'recommendation': self._generate_recommendation(consensus_analysis, valid_responses)
        }
    
    def _analyze_consensus(self, responses: List[AIResponse]) -> Dict[str, Any]:
        """
        Analiza el consenso entre múltiples respuestas de modelos AI
        
        Args:
            responses: Lista de respuestas de diferentes modelos
            
        Returns:
            Análisis de consenso
        """
        if len(responses) < 2:
            return {
                'agreement_level': 'single_source',
                'confidence_avg': responses[0].confidence if responses else 0.0,
                'key_points': []
            }
        
        # Extraer palabras clave comunes
        all_words = []
        for response in responses:
            words = response.response.lower().split()
            # Filtrar palabras técnicas relevantes
            tech_words = [w for w in words if len(w) > 5 and any(term in w for term in 
                         ['fractal', 'dimensi', 'cluster', 'patron', 'analisis', 'estructura'])]
            all_words.extend(tech_words)
        
        # Encontrar consenso en palabras clave
        word_counts = {}
        for word in all_words:
            word_counts[word] = word_counts.get(word, 0) + 1
        
        common_concepts = [word for word, count in word_counts.items() if count >= len(responses)]
        
        # Calcular nivel de acuerdo basado en conceptos comunes
        agreement_score = len(common_concepts) / max(len(set(all_words)), 1)
        
        if agreement_score > 0.7:
            agreement_level = 'high'
        elif agreement_score > 0.4:
            agreement_level = 'medium'
        else:
            agreement_level = 'low'
        
        return {
            'agreement_level': agreement_level,
            'agreement_score': agreement_score,
            'confidence_avg': sum(r.confidence for r in responses) / len(responses),
            'common_concepts': common_concepts,
            'model_count': len(responses)
        }
    
    def _generate_recommendation(self, consensus: Dict, responses: List[AIResponse]) -> str:
        """
        Genera una recomendación basada en el consenso de los modelos
        
        Args:
            consensus: Análisis de consenso
            responses: Respuestas originales
            
        Returns:
            Recomendación para Raven
        """
        if consensus['agreement_level'] == 'high':
            highest_confidence = max(responses, key=lambda r: r.confidence)
            return f"Consenso alto detectado. Recomendación: {highest_confidence.response[:200]}..."
        
        elif consensus['agreement_level'] == 'medium':
            return f"Consenso moderado. Considerar múltiples perspectivas. Conceptos clave: {', '.join(consensus.get('common_concepts', [])[:5])}"
        
        else:
            return "Consenso bajo. Se recomienda análisis adicional o consulta de fuentes especializadas."
    
    def integrate_with_raven_classifier(self, cluster_analysis: Dict, features: Dict) -> Dict[str, Any]:
        """
        Integra el análisis AI con el clasificador de Raven
        
        Args:
            cluster_analysis: Análisis actual del cluster de Raven
            features: Características extraídas por Raven
            
        Returns:
            Análisis enriquecido con insights de modelos AI
        """
        # Construir consulta específica para el análisis fractal
        prompt = f"""
Analiza este patrón fractal clasificado por Raven:

Cluster: {cluster_analysis.get('cluster_name', 'Unknown')}
Dimensión Hausdorff: {features.get('hausdorff_dimension', 'N/A')}
Complejidad: {features.get('dimension_complexity', 'N/A')}
Confianza: {cluster_analysis.get('confidence', 'N/A')}

¿Confirmas esta clasificación? ¿Qué características adicionales deberían analizarse?
¿Hay patrones o propiedades que Raven podría haber pasado por alto?
"""
        
        context = {
            'cluster_name': cluster_analysis.get('cluster_name'),
            'hausdorff_dimension': features.get('hausdorff_dimension'),
            'confidence': cluster_analysis.get('confidence'),
            'key_features': list(features.keys())
        }
        
        # Esta función sería llamada de forma asíncrona en el contexto principal
        return {
            'ai_integration_ready': True,
            'suggested_prompt': prompt,
            'context': context,
            'next_steps': [
                'Ejecutar multi_model_consensus() con el prompt sugerido',
                'Integrar respuestas AI en el análisis de Raven',
                'Actualizar confidence score basado en consenso AI'
            ]
        }
    
    def export_learning_data(self, filename: str = None) -> str:
        """
        Exporta datos de aprendizaje e interacciones con modelos AI
        
        Args:
            filename: Nombre del archivo de exportación
            
        Returns:
            Ruta del archivo exportado
        """
        if filename is None:
            filename = f"raven_ai_learning_{datetime.now().strftime('%d%m%Y_%H%M%S')}.json"
        
        learning_data = {
            'system_info': {
                'raven_version': '2.1_ai_integrated',
                'gpt4_available': self.gpt4_available,
                'claude_available': self.claude_available,
                'export_timestamp': datetime.now().isoformat()
            },
            'model_specialties': self.model_specialties,
            'interaction_history': list(self.response_cache.values()),
            'integration_stats': {
                'total_queries': len(self.response_cache),
                'successful_integrations': sum(1 for r in self.response_cache.values() if r.get('success', False))
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(learning_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Datos de aprendizaje exportados: {filename}")
        return filename


# EJEMPLO DE INTEGRACIÓN CON EL MAIN.PY DE RAVEN

class EnhancedRavenWithAI:
    """
    Versión mejorada de Raven que integra capacidades de modelos AI externos
    """
    
    def __init__(self, openai_key: str = None, anthropic_key: str = None):
        # Importar componentes originales de Raven
        from core.knowledge_base import EnhancedKnowledgeBase
        from core.hausdorff_extractor import HausdorffDimensionExtractor
        
        self.knowledge_base = EnhancedKnowledgeBase()
        self.hausdorff_extractor = HausdorffDimensionExtractor()
        
        # Integrar módulo AI
        self.ai_integration = RavenAIIntegration(openai_key, anthropic_key)
        
        print("🤖 Raven mejorado con integración AI iniciado")
        print(f"   GPT-4: {'✅' if self.ai_integration.gpt4_available else '❌'}")
        print(f"   Claude: {'✅' if self.ai_integration.claude_available else '❌'}")
    
    async def analyze_with_ai_consensus(self, image_path: str) -> Dict[str, Any]:
        """
        Análisis fractal enriquecido con consenso de modelos AI
        
        Args:
            image_path: Ruta de la imagen a analizar
            
        Returns:
            Análisis completo con insights de múltiples modelos AI
        """
        # Análisis tradicional de Raven
        raven_analysis = self.perform_traditional_analysis(image_path)
        
        # Preparar consulta AI
        ai_integration_data = self.ai_integration.integrate_with_raven_classifier(
            raven_analysis['cluster_analysis'], 
            raven_analysis['features']
        )
        
        # Obtener consenso AI
        ai_consensus = await self.ai_integration.multi_model_consensus(
            ai_integration_data['suggested_prompt'],
            ai_integration_data['context']
        )
        
        # Combinar análisis
        enhanced_analysis = {
            'raven_analysis': raven_analysis,
            'ai_consensus': ai_consensus,
            'final_recommendation': self._combine_raven_and_ai_analysis(raven_analysis, ai_consensus),
            'confidence_boost': self._calculate_confidence_boost(raven_analysis, ai_consensus)
        }
        
        return enhanced_analysis
    
    def perform_traditional_analysis(self, image_path: str) -> Dict[str, Any]:
        """
        Realiza el análisis tradicional de Raven
        (Simplificado para el ejemplo)
        """
        # Aquí iría la lógica tradicional de Raven
        return {
            'cluster_analysis': {'cluster_name': 'Mandelbrot Clásico', 'confidence': 0.8},
            'features': {'hausdorff_dimension': 1.9, 'dimension_complexity': 0.6}
        }
    
    def _combine_raven_and_ai_analysis(self, raven_analysis: Dict, ai_consensus: Dict) -> str:
        """
        Combina el análisis de Raven con el consenso AI
        """
        if ai_consensus.get('consensus', {}).get('agreement_level') == 'high':
            return f"Análisis confirmado por consenso AI. {ai_consensus['recommendation']}"
        else:
            return f"Análisis de Raven mantiene validez. Consenso AI sugiere revisión adicional."
    
    def _calculate_confidence_boost(self, raven_analysis: Dict, ai_consensus: Dict) -> float:
        """
        Calcula el boost de confianza basado en el consenso AI
        """
        base_confidence = raven_analysis['cluster_analysis']['confidence']
        ai_confidence = ai_consensus.get('consensus', {}).get('confidence_avg', 0.5)
        agreement_level = ai_consensus.get('consensus', {}).get('agreement_level', 'low')
        
        if agreement_level == 'high':
            boost = min(0.2, ai_confidence * 0.3)
        elif agreement_level == 'medium':
            boost = min(0.1, ai_confidence * 0.2)
        else:
            boost = 0.0
        
        return min(1.0, base_confidence + boost)


# EJEMPLO DE USO
async def example_usage():
    """
    Ejemplo de cómo usar la integración AI con Raven
    """
    # Configurar claves API (en producción, usar variables de entorno)
    OPENAI_KEY = "tu_clave_openai_aqui"
    ANTHROPIC_KEY = "tu_clave_anthropic_aqui"
    
    # Crear instancia mejorada de Raven
    enhanced_raven = EnhancedRavenWithAI(OPENAI_KEY, ANTHROPIC_KEY)
    
    # Analizar imagen con consenso AI
    result = await enhanced_raven.analyze_with_ai_consensus("fractal_image.jpg")
    
    print("🔍 ANÁLISIS RAVEN + AI CONSENSUS")
    print("=" * 50)
    print(f"Análisis Raven: {result['raven_analysis']}")
    print(f"Consenso AI: {result['ai_consensus']['consensus']}")
    print(f"Recomendación final: {result['final_recommendation']}")
    print(f"Confianza mejorada: {result['confidence_boost']:.3f}")

if __name__ == "__main__":
    # Ejecutar ejemplo (requiere claves API válidas)
    # asyncio.run(example_usage())
    print("Módulo de integración AI para Raven listo para usar")
    print("Configura las claves API y ejecuta example_usage() para probar")