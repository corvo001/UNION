#!/usr/bin/env python3
"""
RAVEN FREE LEARNING SYSTEM
Sistema de aprendizaje gratuito que mejora sin APIs externas
"""

import json
import os
import numpy as np
from datetime import datetime
from collections import defaultdict
import statistics

class RavenFreeLearningSystem:
    """
    Sistema de aprendizaje gratuito para Raven que mejora sin APIs externas.
    
    - Aprende de tus correcciones manuales
    - Detecta patrones en análisis históricos
    - Auto-mejora la base de conocimiento
    - Sugiere nuevas características
    - TODO: 100% GRATUITO
    """
    
    def __init__(self, data_path="data/processed"):
        self.data_path = data_path
        self.learning_data = {
            'manual_corrections': [],
            'pattern_discoveries': [],
            'confidence_history': [],
            'cluster_refinements': {},
            'feature_importance': {}
        }
        self.load_learning_data()
    
    def load_learning_data(self):
        """Carga datos de aprendizaje acumulados"""
        learning_file = os.path.join(self.data_path, "raven_learning.json")
        if os.path.exists(learning_file):
            with open(learning_file, 'r', encoding='utf-8') as f:
                self.learning_data.update(json.load(f))
    
    def save_learning_data(self):
        """Guarda datos de aprendizaje"""
        os.makedirs(self.data_path, exist_ok=True)
        learning_file = os.path.join(self.data_path, "raven_learning.json")
        with open(learning_file, 'w', encoding='utf-8') as f:
            json.dump(self.learning_data, f, indent=2, ensure_ascii=False)
    
    def analyze_historical_data(self):
        """
        Analiza todos los JSONs históricos para encontrar patrones
        🆓 GRATUITO - Solo usa tus datos existentes
        """
        print("🔍 Analizando datos históricos para aprender patrones...")
        
        all_analyses = []
        
        # Buscar todos los JSONs en carpetas procesadas
        for root, dirs, files in os.walk(self.data_path):
            for file in files:
                if file.endswith('.json') and file != 'raven_learning.json':
                    json_path = os.path.join(root, file)
                    try:
                        with open(json_path, 'r', encoding='utf-8') as f:
                            analysis = json.load(f)
                            all_analyses.append(analysis)
                    except Exception as e:
                        continue
        
        if not all_analyses:
            print("⚠️ No se encontraron análisis históricos")
            return
        
        print(f"📊 Analizando {len(all_analyses)} análisis históricos...")
        
        # Análisis de patrones
        patterns_found = self._discover_patterns(all_analyses)
        
        # Análisis de confianza
        confidence_trends = self._analyze_confidence_trends(all_analyses)
        
        # Sugerencias de mejora
        improvements = self._suggest_improvements(patterns_found, confidence_trends)
        
        # Guardar aprendizajes
        self.learning_data['pattern_discoveries'].append({
            'timestamp': datetime.now().isoformat(),
            'total_analyses': len(all_analyses),
            'patterns_found': patterns_found,
            'confidence_trends': confidence_trends,
            'improvements': improvements
        })
        
        self.save_learning_data()
        
        return {
            'analyses_count': len(all_analyses),
            'patterns': patterns_found,
            'trends': confidence_trends,
            'suggestions': improvements
        }
    
    def _discover_patterns(self, analyses):
        """Descubre patrones en los datos históricos"""
        patterns = {
            'cluster_characteristics': defaultdict(list),
            'feature_correlations': {},
            'common_misclassifications': [],
            'high_confidence_indicators': [],
            'low_confidence_patterns': []
        }
        
        for analysis in analyses:
            cluster = analysis.get('cluster', 0)
            confidence = analysis.get('confidence', 0.0)
            features = analysis.get('fractal_features', {})
            
            # Agrupar características por cluster
            if features:
                for feature, value in features.items():
                    if isinstance(value, (int, float)):
                        patterns['cluster_characteristics'][cluster].append({
                            'feature': feature,
                            'value': value,
                            'confidence': confidence
                        })
            
            # Identificar patrones de alta/baja confianza
            if confidence > 0.8:
                patterns['high_confidence_indicators'].append({
                    'cluster': cluster,
                    'features': features,
                    'method': analysis.get('classification_method', {}).get('final_method', 'unknown')
                })
            elif confidence < 0.4:
                patterns['low_confidence_patterns'].append({
                    'cluster': cluster,
                    'features': features,
                    'reasons': 'Low confidence pattern detected'
                })
        
        return patterns
    
    def _analyze_confidence_trends(self, analyses):
        """Analiza tendencias de confianza"""
        confidence_by_cluster = defaultdict(list)
        confidence_by_method = defaultdict(list)
        
        for analysis in analyses:
            cluster = analysis.get('cluster', 0)
            confidence = analysis.get('confidence', 0.0)
            method = analysis.get('classification_method', {}).get('final_method', 'unknown')
            
            confidence_by_cluster[cluster].append(confidence)
            confidence_by_method[method].append(confidence)
        
        trends = {}
        
        # Confianza promedio por cluster
        for cluster, confidences in confidence_by_cluster.items():
            trends[f'cluster_{cluster}_avg_confidence'] = statistics.mean(confidences)
            trends[f'cluster_{cluster}_confidence_std'] = statistics.stdev(confidences) if len(confidences) > 1 else 0
        
        # Confianza por método
        for method, confidences in confidence_by_method.items():
            trends[f'method_{method}_avg_confidence'] = statistics.mean(confidences)
        
        return trends
    
    def _suggest_improvements(self, patterns, trends):
        """Sugiere mejoras basadas en patrones descubiertos"""
        suggestions = []
        
        # Sugerencias basadas en baja confianza
        low_confidence_clusters = []
        for key, value in trends.items():
            if 'avg_confidence' in key and 'cluster_' in key and value < 0.6:
                cluster_num = key.split('_')[1]
                low_confidence_clusters.append(cluster_num)
        
        if low_confidence_clusters:
            suggestions.append({
                'type': 'confidence_improvement',
                'priority': 'high',
                'clusters_affected': low_confidence_clusters,
                'suggestion': f'Refinar definiciones de clusters {", ".join(low_confidence_clusters)} - baja confianza promedio',
                'action': 'review_cluster_definitions'
            })
        
        # Sugerencias basadas en características
        for cluster, characteristics in patterns['cluster_characteristics'].items():
            if len(characteristics) > 5:  # Suficientes datos
                feature_values = defaultdict(list)
                for char in characteristics:
                    feature_values[char['feature']].append(char['value'])
                
                # Buscar características muy variables (posible ruido)
                for feature, values in feature_values.items():
                    if len(values) > 3:
                        std_dev = statistics.stdev(values)
                        mean_val = statistics.mean(values)
                        cv = std_dev / mean_val if mean_val != 0 else float('inf')
                        
                        if cv > 1.0:  # Coeficiente de variación alto
                            suggestions.append({
                                'type': 'feature_refinement',
                                'priority': 'medium',
                                'cluster': cluster,
                                'feature': feature,
                                'suggestion': f'Característica "{feature}" muy variable en cluster {cluster} (CV={cv:.2f})',
                                'action': 'review_feature_extraction'
                            })
        
        return suggestions
    
    def interactive_correction_learning(self):
        """
        Sistema interactivo para que corrijas clasificaciones y Raven aprenda
        🆓 GRATUITO - Tu conocimiento mejora el sistema
        """
        print("\n🎓 MODO APRENDIZAJE INTERACTIVO")
        print("=" * 50)
        print("Raven te mostrará clasificaciones recientes para que las valides")
        print("Tus correcciones mejorarán el sistema automáticamente")
        
        # Buscar análisis recientes con baja confianza
        recent_analyses = self._get_recent_low_confidence_analyses()
        
        if not recent_analyses:
            print("✅ No hay análisis recientes que necesiten validación")
            return
        
        corrections_made = 0
        
        for analysis in recent_analyses[:5]:  # Máximo 5 por sesión
            image_name = analysis.get('image_filename', 'unknown')
            current_cluster = analysis.get('cluster', 0)
            cluster_name = analysis.get('cluster_name', 'Unknown')
            confidence = analysis.get('confidence', 0.0)
            
            print(f"\n📸 Imagen: {image_name}")
            print(f"🤖 Raven clasificó como: Cluster {current_cluster} - {cluster_name}")
            print(f"🎯 Confianza: {confidence:.3f}")
            
            # Mostrar características principales
            features = analysis.get('fractal_features', {})
            hausdorff = features.get('hausdorff_dimension', 'N/A')
            complexity = features.get('dimension_complexity', 'N/A')
            print(f"📊 Hausdorff: {hausdorff} | Complejidad: {complexity}")
            
            print("\n¿Es correcta esta clasificación?")
            print("1. ✅ Correcta")
            print("2. ❌ Incorrecta")
            print("3. ⏭️ Saltar")
            print("4. 🚪 Salir")
            
            choice = input("Tu respuesta (1-4): ").strip()
            
            if choice == '1':
                self._record_positive_feedback(analysis)
                print("✅ Confirmación registrada - Raven aprende que esta clasificación es buena")
                corrections_made += 1
                
            elif choice == '2':
                correct_cluster = self._ask_correct_cluster()
                if correct_cluster is not None:
                    self._record_correction(analysis, correct_cluster)
                    print(f"📝 Corrección registrada: {current_cluster} → {correct_cluster}")
                    corrections_made += 1
                    
            elif choice == '3':
                continue
                
            elif choice == '4':
                break
        
        print(f"\n🎉 Sesión completada: {corrections_made} correcciones registradas")
        print("🧠 Raven ha mejorado con tu conocimiento!")
        
        self.save_learning_data()
    
    def _get_recent_low_confidence_analyses(self):
        """Obtiene análisis recientes con baja confianza"""
        recent_analyses = []
        
        for root, dirs, files in os.walk(self.data_path):
            for file in files:
                if file.endswith('.json') and file != 'raven_learning.json':
                    json_path = os.path.join(root, file)
                    try:
                        with open(json_path, 'r', encoding='utf-8') as f:
                            analysis = json.load(f)
                            
                        confidence = analysis.get('confidence', 0.0)
                        if confidence < 0.7:  # Solo baja confianza
                            recent_analyses.append(analysis)
                            
                    except Exception:
                        continue
        
        # Ordenar por confianza (más bajas primero)
        recent_analyses.sort(key=lambda x: x.get('confidence', 0.0))
        
        return recent_analyses
    
    def _ask_correct_cluster(self):
        """Pregunta cuál es el cluster correcto"""
        print("\n¿Cuál es el cluster correcto? (0-9)")
        print("0. Mandelbrot Clásico")
        print("1. Julia Set Conectado") 
        print("2. Julia Set Desconectado")
        print("3. Fractal Arborescente")
        print("4. Fractales de Escape Divergente")
        print("5. Fractales Lineales y Curvas")
        print("6. Fractales de Atractor Extraño")
        print("7. Fractales Cristalinos")
        print("8. Fractales Multifractales")
        print("9. Fractales de Percolación")
        
        try:
            cluster = int(input("Cluster correcto (0-9): ").strip())
            if 0 <= cluster <= 9:
                return cluster
            else:
                print("❌ Cluster inválido")
                return None
        except ValueError:
            print("❌ Entrada inválida")
            return None
    
    def _record_positive_feedback(self, analysis):
        """Registra feedback positivo"""
        self.learning_data['manual_corrections'].append({
            'timestamp': datetime.now().isoformat(),
            'type': 'positive_confirmation',
            'image': analysis.get('image_filename'),
            'cluster': analysis.get('cluster'),
            'confidence': analysis.get('confidence'),
            'features': analysis.get('fractal_features', {}),
            'method': analysis.get('classification_method', {}).get('final_method')
        })
    
    def _record_correction(self, analysis, correct_cluster):
        """Registra una corrección manual"""
        self.learning_data['manual_corrections'].append({
            'timestamp': datetime.now().isoformat(),
            'type': 'manual_correction',
            'image': analysis.get('image_filename'),
            'original_cluster': analysis.get('cluster'),
            'correct_cluster': correct_cluster,
            'original_confidence': analysis.get('confidence'),
            'features': analysis.get('fractal_features', {}),
            'original_method': analysis.get('classification_method', {}).get('final_method')
        })
    
    def generate_improvement_report(self):
        """
        Genera reporte de mejoras sugeridas
        🆓 GRATUITO - Análisis completo de tu sistema
        """
        print("\n📊 GENERANDO REPORTE DE MEJORAS GRATUITAS")
        print("=" * 50)
        
        # Analizar datos históricos
        historical_analysis = self.analyze_historical_data()
        
        # Análizar correcciones manuales
        corrections_analysis = self._analyze_manual_corrections()
        
        # Generar reporte
        report = {
            'timestamp': datetime.now().isoformat(),
            'historical_data': historical_analysis,
            'manual_corrections': corrections_analysis,
            'recommendations': self._generate_free_recommendations(historical_analysis, corrections_analysis)
        }
        
        # Mostrar reporte
        self._display_improvement_report(report)
        
        # Guardar reporte
        report_file = os.path.join(self.data_path, f"improvement_report_{datetime.now().strftime('%d%m%Y_%H%M%S')}.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Reporte guardado: {report_file}")
        
        return report
    
    def _analyze_manual_corrections(self):
        """Analiza las correcciones manuales realizadas"""
        corrections = self.learning_data.get('manual_corrections', [])
        
        if not corrections:
            return {'message': 'No hay correcciones manuales registradas'}
        
        analysis = {
            'total_corrections': len(corrections),
            'positive_confirmations': len([c for c in corrections if c['type'] == 'positive_confirmation']),
            'actual_corrections': len([c for c in corrections if c['type'] == 'manual_correction']),
            'most_corrected_clusters': {},
            'accuracy_by_method': {}
        }
        
        # Análisis de clusters más corregidos
        cluster_corrections = defaultdict(int)
        method_accuracy = defaultdict(list)
        
        for correction in corrections:
            if correction['type'] == 'manual_correction':
                original_cluster = correction['original_cluster']
                cluster_corrections[original_cluster] += 1
                method_accuracy[correction.get('original_method', 'unknown')].append(0)  # Error
            elif correction['type'] == 'positive_confirmation':
                method_accuracy[correction.get('method', 'unknown')].append(1)  # Correcto
        
        analysis['most_corrected_clusters'] = dict(cluster_corrections)
        
        # Calcular precisión por método
        for method, results in method_accuracy.items():
            if results:
                analysis['accuracy_by_method'][method] = sum(results) / len(results)
        
        return analysis
    
    def _generate_free_recommendations(self, historical_analysis, corrections_analysis):
        """Genera recomendaciones gratuitas para mejorar"""
        recommendations = []
        
        # Recomendaciones basadas en correcciones
        if corrections_analysis.get('most_corrected_clusters'):
            problematic_clusters = corrections_analysis['most_corrected_clusters']
            for cluster, count in problematic_clusters.items():
                recommendations.append({
                    'priority': 'HIGH' if count > 2 else 'MEDIUM',
                    'type': 'cluster_refinement',
                    'title': f'Refinar definiciones del Cluster {cluster}',
                    'description': f'Cluster {cluster} ha sido corregido {count} veces manualmente',
                    'action': f'Revisar rangos de características y patrones visuales del cluster {cluster}',
                    'cost': 'GRATIS - Solo requiere análisis manual'
                })
        
        # Recomendaciones basadas en precisión de métodos
        if corrections_analysis.get('accuracy_by_method'):
            for method, accuracy in corrections_analysis['accuracy_by_method'].items():
                if accuracy < 0.7:
                    recommendations.append({
                        'priority': 'MEDIUM',
                        'type': 'method_improvement',
                        'title': f'Mejorar método {method}',
                        'description': f'Precisión del método {method}: {accuracy:.2%}',
                        'action': f'Ajustar pesos o reglas del método {method}',
                        'cost': 'GRATIS - Ajuste de parámetros'
                    })
        
        # Recomendaciones basadas en patrones históricos
        if historical_analysis and historical_analysis.get('suggestions'):
            for suggestion in historical_analysis['suggestions']:
                recommendations.append({
                    'priority': suggestion.get('priority', 'LOW').upper(),
                    'type': 'pattern_based',
                    'title': suggestion.get('suggestion', 'Mejora sugerida'),
                    'description': f"Detectado en análisis de {historical_analysis.get('analyses_count', 0)} imágenes",
                    'action': suggestion.get('action', 'Revisar manualmente'),
                    'cost': 'GRATIS - Basado en tus datos existentes'
                })
        
        return recommendations
    
    def _display_improvement_report(self, report):
        """Muestra el reporte de mejoras de forma legible"""
        print("\n🎯 REPORTE DE MEJORAS GRATUITAS PARA RAVEN")
        print("=" * 60)
        
        # Datos históricos
        historical = report.get('historical_data', {})
        if historical:
            print(f"\n📊 ANÁLISIS HISTÓRICO:")
            print(f"   • Análisis procesados: {historical.get('analyses_count', 0)}")
            print(f"   • Patrones descubiertos: ✅")
            print(f"   • Tendencias de confianza: ✅")
        
        # Correcciones manuales
        corrections = report.get('manual_corrections', {})
        if corrections and corrections != {'message': 'No hay correcciones manuales registradas'}:
            print(f"\n🎓 APRENDIZAJE MANUAL:")
            print(f"   • Total correcciones: {corrections.get('total_corrections', 0)}")
            print(f"   • Confirmaciones positivas: {corrections.get('positive_confirmations', 0)}")
            print(f"   • Correcciones reales: {corrections.get('actual_corrections', 0)}")
        
        # Recomendaciones
        recommendations = report.get('recommendations', [])
        if recommendations:
            print(f"\n💡 RECOMENDACIONES GRATUITAS:")
            
            high_priority = [r for r in recommendations if r['priority'] == 'HIGH']
            medium_priority = [r for r in recommendations if r['priority'] == 'MEDIUM']
            low_priority = [r for r in recommendations if r['priority'] == 'LOW']
            
            for priority_list, priority_name in [(high_priority, '🔴 ALTA'), (medium_priority, '🟡 MEDIA'), (low_priority, '🟢 BAJA')]:
                if priority_list:
                    print(f"\n   {priority_name} PRIORIDAD:")
                    for i, rec in enumerate(priority_list, 1):
                        print(f"   {i}. {rec['title']}")
                        print(f"      📝 {rec['description']}")
                        print(f"      🔧 Acción: {rec['action']}")
                        print(f"      💰 Costo: {rec['cost']}")
                        print()
        else:
            print(f"\n✅ ¡Tu sistema Raven está funcionando muy bien!")
            print(f"   No se detectaron áreas críticas de mejora")


def interactive_free_learning():
    """Función interactiva para el sistema de aprendizaje gratuito"""
    learning_system = RavenFreeLearningSystem()
    
    print("\n🆓 SISTEMA DE APRENDIZAJE GRATUITO DE RAVEN")
    print("=" * 50)
    print("Mejora Raven sin costes usando tus propios datos")
    
    while True:
        print("\n🎯 Opciones disponibles:")
        print("1. 📊 Analizar datos históricos")
        print("2. 🎓 Modo aprendizaje interactivo")
        print("3. 📋 Generar reporte de mejoras")
        print("4. 🚪 Salir")
        
        choice = input("\nSelecciona opción (1-4): ").strip()
        
        if choice == '1':
            print("\n🔍 Analizando todos tus datos históricos...")
            result = learning_system.analyze_historical_data()
            print(f"✅ Análisis completo - {result['analyses_count']} archivos procesados")
            input("Presiona Enter para continuar...")
            
        elif choice == '2':
            learning_system.interactive_correction_learning()
            input("Presiona Enter para continuar...")
            
        elif choice == '3':
            learning_system.generate_improvement_report()
            input("Presiona Enter para continuar...")
            
        elif choice == '4':
            print("👋 ¡Gracias por usar el sistema de aprendizaje gratuito!")
            break
            
        else:
            print("❌ Opción inválida")


if __name__ == "__main__":
    interactive_free_learning()