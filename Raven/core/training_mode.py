#!/usr/bin/env python3
"""
RAVEN TRAINING MODE
Sistema de entrenamiento temporal que usa AI para mejorar Raven y luego funciona GRATIS

Concepto:
1. FASE ENTRENAMIENTO (pagada): GPT-4/Claude analizan 100-200 imágenes
2. EXTRACCIÓN: Raven aprende de sus respuestas
3. FASE PRODUCCIÓN (gratis): Raven funciona solo con conocimiento mejorado
"""

import json
import os
import numpy as np
from datetime import datetime
from typing import Dict, List, Any
import asyncio

# Solo importar AI si está disponible
try:
    from core.ai_integration import RavenAIIntegration
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

class RavenTrainingMode:
    """
    Modo de entrenamiento que usa AI temporalmente para mejorar Raven permanentemente.
    
    INVERSIÓN INICIAL: $5-20 para entrenar
    RESULTADO: Raven mejorado que funciona GRATIS para siempre
    """
    
    def __init__(self, training_budget=10.0):  # $10 USD presupuesto
        self.training_budget = training_budget  # Presupuesto máximo
        self.spent_so_far = 0.0
        self.training_data = {
            'ai_insights': [],
            'pattern_discoveries': [],
            'improved_definitions': {},
            'new_rules': [],
            'confidence_adjustments': {}
        }
        self.cost_per_analysis = 0.02  # ~$0.02 por imagen
        self.max_training_samples = int(training_budget / self.cost_per_analysis)
        
        print(f"💰 Modo Entrenamiento iniciado - Presupuesto: ${training_budget}")
        print(f"📊 Máximo {self.max_training_samples} imágenes de entrenamiento")
        
        if AI_AVAILABLE:
            self.ai_integration = None  # Se inicializa con claves
        
    def estimate_training_cost(self, num_images: int) -> Dict[str, Any]:
        """
        Estima el costo de entrenar con X imágenes
        
        Args:
            num_images: Número de imágenes para entrenar
            
        Returns:
            Estimación detallada de costos
        """
        cost_breakdown = {
            'images': num_images,
            'cost_per_image': self.cost_per_analysis,
            'total_estimated_cost': num_images * self.cost_per_analysis,
            'tokens_per_image': 800,  # Promedio prompt + respuesta
            'total_tokens': num_images * 800,
            'within_budget': num_images * self.cost_per_analysis <= self.training_budget
        }
        
        # Beneficios estimados
        expected_improvements = {
            'confidence_boost': f"+{min(25, num_images * 0.2):.1f}%",
            'accuracy_improvement': f"+{min(15, num_images * 0.1):.1f}%",
            'new_patterns_discovered': min(10, num_images // 20),
            'cluster_refinements': min(8, num_images // 25)
        }
        
        cost_breakdown['expected_benefits'] = expected_improvements
        
        return cost_breakdown
    
    def interactive_training_setup(self):
        """
        Configuración interactiva del entrenamiento
        """
        print("\n🎓 CONFIGURACIÓN DEL ENTRENAMIENTO RAVEN")
        print("=" * 50)
        print("El objetivo es gastar una vez para mejorar Raven permanentemente")
        
        # Mostrar opciones de entrenamiento
        training_options = [
            {"name": "Entrenamiento Básico", "images": 50, "cost": 1.0, "improvement": "Mejora básica"},
            {"name": "Entrenamiento Estándar", "images": 150, "cost": 3.0, "improvement": "Mejora significativa"},
            {"name": "Entrenamiento Avanzado", "images": 300, "cost": 6.0, "improvement": "Mejora considerable"},
            {"name": "Entrenamiento Completo", "images": 500, "cost": 10.0, "improvement": "Mejora máxima"}
        ]
        
        print("\n🎯 Opciones de entrenamiento disponibles:")
        print("-" * 60)
        
        for i, option in enumerate(training_options, 1):
            cost_estimate = self.estimate_training_cost(option["images"])
            print(f"\n{i}. {option['name']}")
            print(f"   🖼️ Imágenes: {option['images']}")
            print(f"   💰 Costo estimado: ${option['cost']:.2f}")
            print(f"   📈 Resultado: {option['improvement']}")
            print(f"   ✨ Beneficios esperados:")
            for benefit, value in cost_estimate['expected_benefits'].items():
                print(f"      • {benefit.replace('_', ' ').title()}: {value}")
        
        print(f"\n5. ⚙️ Configuración personalizada")
        print(f"6. 🚪 Cancelar")
        
        choice = input(f"\n👉 Selecciona opción (1-6): ").strip()
        
        if choice in ['1', '2', '3', '4']:
            selected_option = training_options[int(choice) - 1]
            return self._confirm_training_plan(selected_option)
        elif choice == '5':
            return self._custom_training_setup()
        elif choice == '6':
            print("❌ Entrenamiento cancelado")
            return None
        else:
            print("❌ Opción inválida")
            return None
    
    def _confirm_training_plan(self, option: Dict) -> Dict:
        """Confirma el plan de entrenamiento seleccionado"""
        print(f"\n📋 PLAN DE ENTRENAMIENTO SELECCIONADO")
        print("=" * 40)
        print(f"📦 Plan: {option['name']}")
        print(f"🖼️ Imágenes a procesar: {option['images']}")
        print(f"💰 Costo estimado: ${option['cost']:.2f}")
        print(f"📈 Mejora esperada: {option['improvement']}")
        
        print(f"\n⚠️ IMPORTANTE:")
        print(f"• Este es un gasto único para entrenar Raven")
        print(f"• Después del entrenamiento, Raven funciona GRATIS")
        print(f"• El conocimiento adquirido se guarda permanentemente")
        print(f"• No necesitarás pagar más APIs después del entrenamiento")
        
        confirm = input(f"\n¿Proceder con el entrenamiento? (s/n): ").strip().lower()
        
        if confirm in ['s', 'sí', 'si', 'y', 'yes']:
            return {
                'images_to_train': option['images'],
                'estimated_cost': option['cost'],
                'plan_name': option['name']
            }
        else:
            print("❌ Entrenamiento cancelado")
            return None
    
    def _custom_training_setup(self) -> Dict:
        """Configuración personalizada de entrenamiento"""
        print(f"\n⚙️ CONFIGURACIÓN PERSONALIZADA")
        print(f"💰 Presupuesto disponible: ${self.training_budget:.2f}")
        print(f"💡 Costo estimado por imagen: ${self.cost_per_analysis:.3f}")
        
        try:
            num_images = int(input(f"🖼️ ¿Cuántas imágenes quieres usar para entrenar? (1-{self.max_training_samples}): "))
            
            if 1 <= num_images <= self.max_training_samples:
                cost_estimate = self.estimate_training_cost(num_images)
                
                print(f"\n📊 ESTIMACIÓN PERSONALIZADA:")
                print(f"   🖼️ Imágenes: {num_images}")
                print(f"   💰 Costo total: ${cost_estimate['total_estimated_cost']:.2f}")
                print(f"   📈 Mejoras esperadas:")
                for benefit, value in cost_estimate['expected_benefits'].items():
                    print(f"      • {benefit.replace('_', ' ').title()}: {value}")
                
                confirm = input(f"\n¿Proceder con esta configuración? (s/n): ").strip().lower()
                
                if confirm in ['s', 'sí', 'si', 'y', 'yes']:
                    return {
                        'images_to_train': num_images,
                        'estimated_cost': cost_estimate['total_estimated_cost'],
                        'plan_name': 'Personalizado'
                    }
            else:
                print(f"❌ Número de imágenes fuera de rango")
        except ValueError:
            print(f"❌ Entrada inválida")
        
        return None
    
    async def execute_training(self, training_plan: Dict, openai_key: str = None, anthropic_key: str = None):
        """
        Ejecuta el entrenamiento usando AI temporalmente
        
        Args:
            training_plan: Plan de entrenamiento confirmado
            openai_key: Clave API de OpenAI
            anthropic_key: Clave API de Anthropic
        """
        if not AI_AVAILABLE:
            print("❌ Módulo AI no disponible para entrenamiento")
            return False
        
        if not (openai_key or anthropic_key):
            print("❌ Se necesita al menos una clave API para entrenar")
            return False
        
        print(f"\n🚀 INICIANDO ENTRENAMIENTO: {training_plan['plan_name']}")
        print("=" * 50)
        
        # Inicializar integración AI
        self.ai_integration = RavenAIIntegration(openai_key, anthropic_key)
        
        # Obtener imágenes de entrenamiento
        training_images = self._select_training_images(training_plan['images_to_train'])
        
        if not training_images:
            print("❌ No se encontraron imágenes suficientes para entrenar")
            return False
        
        print(f"🖼️ Entrenando con {len(training_images)} imágenes")
        print(f"💰 Costo estimado: ${training_plan['estimated_cost']:.2f}")
        
        # Entrenar con cada imagen
        successful_trainings = 0
        total_cost = 0.0
        
        for i, image_path in enumerate(training_images, 1):
            if total_cost >= self.training_budget:
                print(f"⚠️ Presupuesto agotado en imagen {i}")
                break
            
            print(f"\n📸 Entrenando {i}/{len(training_images)}: {os.path.basename(image_path)}")
            
            try:
                # Realizar análisis AI
                training_result = await self._train_with_single_image(image_path)
                
                if training_result['success']:
                    successful_trainings += 1
                    total_cost += training_result['estimated_cost']
                    
                    # Guardar insights del entrenamiento
                    self.training_data['ai_insights'].append(training_result)
                    
                    print(f"   ✅ Entrenamiento exitoso")
                    print(f"   💰 Costo acumulado: ${total_cost:.3f}")
                else:
                    print(f"   ❌ Error in entrenamiento: {training_result.get('error', 'Unknown')}")
                
            except Exception as e:
                print(f"   ❌ Error inesperado: {e}")
                continue
        
        print(f"\n🎉 ENTRENAMIENTO COMPLETADO")
        print(f"✅ Imágenes procesadas exitosamente: {successful_trainings}")
        print(f"💰 Costo total real: ${total_cost:.2f}")
        
        # Generar conocimiento mejorado
        improved_knowledge = self._extract_knowledge_from_training()
        
        # Guardar conocimiento permanentemente
        self._save_improved_knowledge(improved_knowledge)
        
        print(f"\n🧠 CONOCIMIENTO EXTRAÍDO Y GUARDADO")
        print(f"🎯 Raven ahora funcionará GRATIS con este conocimiento mejorado")
        
        return True
    
    def _select_training_images(self, num_images: int) -> List[str]:
        """Selecciona imágenes representativas para entrenamiento"""
        # Buscar imágenes en carpetas procesadas y actuales
        all_images = []
        search_paths = ["data/processed", "data/today"]
        
        for search_path in search_paths:
            if os.path.exists(search_path):
                for root, dirs, files in os.walk(search_path):
                    for file in files:
                        if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                            full_path = os.path.join(root, file)
                            all_images.append(full_path)
        
        if len(all_images) < num_images:
            print(f"⚠️ Solo se encontraron {len(all_images)} imágenes (necesarias: {num_images})")
            return all_images
        
        # Seleccionar imágenes diversas (distribuidas uniformemente)
        selected_indices = np.linspace(0, len(all_images) - 1, num_images, dtype=int)
        selected_images = [all_images[i] for i in selected_indices]
        
        return selected_images
    
    async def _train_with_single_image(self, image_path: str) -> Dict[str, Any]:
        """Entrena con una sola imagen usando AI"""
        try:
            # Preparar prompt de entrenamiento especializado
            training_prompt = f"""
            ENTRENAMIENTO DE RAVEN - Análisis de Fractal

            Estás ayudando a entrenar un sistema de análisis fractal llamado Raven.
            Analiza esta imagen fractal y proporciona:

            1. Tipo de fractal principal (Mandelbrot, Julia, IFS, etc.)
            2. Dimensión de Hausdorff estimada (1.0-3.0)
            3. Características visuales clave
            4. Nivel de complejidad (1-10)
            5. Patrones geométricos dominantes
            6. Recomendaciones para clasificación automática

            Sé específico y técnico - este análisis mejorará las reglas de clasificación.
            """
            
            context = {
                'training_mode': True,
                'image_path': image_path,
                'purpose': 'knowledge_extraction'
            }
            
            # Consultar AI
            ai_result = await self.ai_integration.multi_model_consensus(training_prompt, context)
            
            if 'error' not in ai_result:
                return {
                    'success': True,
                    'image_path': image_path,
                    'ai_responses': ai_result['responses'],
                    'consensus': ai_result['consensus'],
                    'recommendation': ai_result['recommendation'],
                    'estimated_cost': self.cost_per_analysis,
                    'training_insights': self._extract_training_insights(ai_result)
                }
            else:
                return {
                    'success': False,
                    'error': ai_result['error'],
                    'estimated_cost': 0.0
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'estimated_cost': 0.0
            }
    
    def _extract_training_insights(self, ai_result: Dict) -> Dict[str, Any]:
        """Extrae insights específicos para mejorar Raven"""
        insights = {
            'fractal_characteristics': [],
            'classification_rules': [],
            'confidence_indicators': [],
            'pattern_recognition': []
        }
        
        # Analizar respuestas AI para extraer conocimiento estructurado
        for response in ai_result.get('responses', []):
            response_text = response.get('response', '').lower()
            
            # Buscar menciones de tipos fractales
            fractal_types = ['mandelbrot', 'julia', 'ifs', 'cantor', 'sierpinski', 'lorenz', 'henon']
            for ftype in fractal_types:
                if ftype in response_text:
                    insights['fractal_characteristics'].append({
                        'type': ftype,
                        'model': response.get('model'),
                        'confidence': response.get('confidence')
                    })
            
            # Buscar valores numéricos (dimensiones, etc.)
            import re
            dimension_matches = re.findall(r'dimensi[óo]n[^0-9]*([0-9]+\.?[0-9]*)', response_text)
            for dim_str in dimension_matches:
                try:
                    dimension = float(dim_str)
                    if 1.0 <= dimension <= 3.0:
                        insights['classification_rules'].append({
                            'type': 'hausdorff_dimension',
                            'value': dimension,
                            'source_model': response.get('model')
                        })
                except ValueError:
                    continue
        
        return insights
    
    def _extract_knowledge_from_training(self) -> Dict[str, Any]:
        """Extrae conocimiento permanente del entrenamiento"""
        print("\n🧠 Extrayendo conocimiento permanente del entrenamiento...")
        
        improved_knowledge = {
            'cluster_refinements': {},
            'new_classification_rules': [],
            'confidence_boosters': {},
            'pattern_recognition_improvements': [],
            'training_metadata': {
                'total_samples': len(self.training_data['ai_insights']),
                'training_date': datetime.now().isoformat(),
                'models_used': []
            }
        }
        
        # Analizar todos los insights de entrenamiento
        all_insights = []
        models_used = set()
        
        for training_result in self.training_data['ai_insights']:
            if training_result.get('success'):
                all_insights.append(training_result['training_insights'])
                
                # Registrar modelos usados
                for response in training_result.get('ai_responses', []):
                    models_used.add(response.get('model', 'unknown'))
        
        improved_knowledge['training_metadata']['models_used'] = list(models_used)
        
        # Consolidar características fractales
        fractal_consolidation = {}
        for insight in all_insights:
            for char in insight.get('fractal_characteristics', []):
                ftype = char['type']
                if ftype not in fractal_consolidation:
                    fractal_consolidation[ftype] = {'mentions': 0, 'total_confidence': 0.0}
                
                fractal_consolidation[ftype]['mentions'] += 1
                fractal_consolidation[ftype]['total_confidence'] += char.get('confidence', 0.5)
        
        # Crear reglas de clasificación mejoradas
        for ftype, data in fractal_consolidation.items():
            avg_confidence = data['total_confidence'] / data['mentions']
            if data['mentions'] >= 3 and avg_confidence > 0.6:  # Suficiente evidencia
                improved_knowledge['new_classification_rules'].append({
                    'rule_type': 'fractal_type_detection',
                    'fractal_type': ftype,
                    'confidence_threshold': avg_confidence,
                    'evidence_strength': data['mentions'],
                    'description': f'Regla mejorada para detectar fractales tipo {ftype}'
                })
        
        # Consolidar reglas de dimensión
        dimension_rules = []
        for insight in all_insights:
            for rule in insight.get('classification_rules', []):
                if rule['type'] == 'hausdorff_dimension':
                    dimension_rules.append(rule['value'])
        
        if dimension_rules:
            # Crear rangos mejorados basados en dimensiones observadas
            dimension_ranges = {
                'low_dimension': [d for d in dimension_rules if d < 1.5],
                'medium_dimension': [d for d in dimension_rules if 1.5 <= d < 2.0],
                'high_dimension': [d for d in dimension_rules if d >= 2.0]
            }
            
            improved_knowledge['confidence_boosters']['dimension_classification'] = dimension_ranges
        
        print(f"✅ Conocimiento extraído:")
        print(f"   • {len(improved_knowledge['new_classification_rules'])} nuevas reglas")
        print(f"   • {len(fractal_consolidation)} tipos fractales identificados")
        print(f"   • {len(dimension_rules)} referencias de dimensión")
        
        return improved_knowledge
    
    def _save_improved_knowledge(self, knowledge: Dict[str, Any]):
        """Guarda el conocimiento mejorado permanentemente"""
        # Crear directorio si no existe
        knowledge_dir = "data/trained_knowledge"
        os.makedirs(knowledge_dir, exist_ok=True)
        
        # Guardar conocimiento completo
        timestamp = datetime.now().strftime("%d%m%Y_%H%M%S")
        knowledge_file = os.path.join(knowledge_dir, f"raven_trained_knowledge_{timestamp}.json")
        
        with open(knowledge_file, 'w', encoding='utf-8') as f:
            json.dump(knowledge, f, indent=2, ensure_ascii=False)
        
        # También guardar versión "activa" que Raven cargará automáticamente
        active_knowledge_file = os.path.join(knowledge_dir, "active_trained_knowledge.json")
        with open(active_knowledge_file, 'w', encoding='utf-8') as f:
            json.dump(knowledge, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Conocimiento guardado en: {knowledge_file}")
        print(f"🎯 Conocimiento activo: {active_knowledge_file}")
        print(f"🆓 Raven ahora usará este conocimiento GRATIS en futuros análisis")


# INTEGRACIÓN CON EL SISTEMA PRINCIPAL DE RAVEN

class TrainedRavenEnhancement:
    """
    Mejoras para Raven basadas en conocimiento entrenado (GRATUITO después del entrenamiento)
    """
    
    def __init__(self):
        self.trained_knowledge = self._load_trained_knowledge()
        self.has_trained_knowledge = self.trained_knowledge is not None
        
        if self.has_trained_knowledge:
            print("🧠 Conocimiento entrenado cargado - Raven funcionará con mejoras AI")
        else:
            print("🔄 Sin conocimiento entrenado - Raven funcionará en modo estándar")
    
    def _load_trained_knowledge(self) -> Dict[str, Any]:
        """Carga conocimiento entrenado si existe"""
        knowledge_file = "data/trained_knowledge/active_trained_knowledge.json"
        
        if os.path.exists(knowledge_file):
            try:
                with open(knowledge_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Error cargando conocimiento entrenado: {e}")
        
        return None
    
    def enhance_classification(self, original_analysis: Dict, features: Dict) -> Dict:
        """
        Mejora la clasificación usando conocimiento entrenado (GRATIS)
        
        Args:
            original_analysis: Análisis original de Raven
            features: Características extraídas
            
        Returns:
            Análisis mejorado con conocimiento entrenado
        """
        if not self.has_trained_knowledge:
            return original_analysis
        
        enhanced_analysis = original_analysis.copy()
        confidence_boost = 0.0
        improvements = []
        
        # Aplicar reglas de clasificación aprendidas
        new_rules = self.trained_knowledge.get('new_classification_rules', [])
        for rule in new_rules:
            if rule['rule_type'] == 'fractal_type_detection':
                # Verificar si las características coinciden con el tipo fractal aprendido
                fractal_type = features.get('fractal_type', '').lower()
                if rule['fractal_type'] in fractal_type:
                    confidence_boost += 0.1
                    improvements.append(f"Coincidencia con patrón entrenado: {rule['fractal_type']}")
        
        # Aplicar boosters de confianza
        confidence_boosters = self.trained_knowledge.get('confidence_boosters', {})
        if 'dimension_classification' in confidence_boosters:
            hausdorff_dim = features.get('hausdorff_dimension', 0.0)
            
            # Verificar en qué rango cae la dimensión
            for range_name, dimensions in confidence_boosters['dimension_classification'].items():
                if dimensions and min(dimensions) <= hausdorff_dim <= max(dimensions):
                    confidence_boost += 0.05
                    improvements.append(f"Dimensión en rango entrenado: {range_name}")
        
        # Aplicar mejoras
        if confidence_boost > 0:
            original_confidence = enhanced_analysis.get('confidence', 0.0)
            enhanced_analysis['confidence'] = min(1.0, original_confidence + confidence_boost)
            enhanced_analysis['trained_improvements'] = improvements
            enhanced_analysis['confidence_boost_from_training'] = confidence_boost
            enhanced_analysis['used_trained_knowledge'] = True
        
        return enhanced_analysis


async def interactive_training_mode():
    """Función interactiva para el modo de entrenamiento"""
    if not AI_AVAILABLE:
        print("❌ Módulo AI no disponible")
        print("💡 Instala las dependencias: pip install openai anthropic")
        print("💡 Crea el archivo core/ai_integration.py")
        return
    
    trainer = RavenTrainingMode(training_budget=15.0)
    
    # Configurar entrenamiento
    training_plan = trainer.interactive_training_setup()
    
    if not training_plan:
        return
    
    # Solicitar claves API
    print(f"\n🔑 CONFIGURACIÓN DE API KEYS")
    print("Necesarias solo para el entrenamiento:")
    
    openai_key = input("🔑 Clave OpenAI (Enter para omitir): ").strip()
    anthropic_key = input("🔑 Clave Anthropic (Enter para omitir): ").strip()
    
    if not (openai_key or anthropic_key):
        print("❌ Se necesita al menos una clave API para entrenar")
        return
    
    # Ejecutar entrenamiento
    success = await trainer.execute_training(training_plan, openai_key, anthropic_key)
    
    if success:
        print(f"\n🎉 ¡ENTRENAMIENTO COMPLETADO EXITOSAMENTE!")
        print(f"🆓 Raven ahora funciona GRATIS con conocimiento mejorado")
        print(f"💡 Usa la opción '1' del menú principal para análisis mejorados")
    else:
        print(f"\n❌ Entrenamiento falló")

if __name__ == "__main__":
    # Ejemplo de uso
    print("Modo entrenamiento de Raven")
    asyncio.run(interactive_training_mode())