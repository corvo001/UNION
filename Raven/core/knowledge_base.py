import numpy as np
from typing import Dict, List, Tuple, Any
import logging

logger = logging.getLogger(__name__)

class EnhancedKnowledgeBase:
    """
    Base de conocimiento expandida con 10 clusters especializados para patrones fractales.
    
    Cada cluster está definido por características específicas de dimensión de Hausdorff,
    características de contornos y patrones visuales distintivos.
    """
    
    def __init__(self):
        """Inicializa la base de conocimiento con definiciones de clusters."""
        self.cluster_definitions = self._initialize_cluster_definitions()
        self.feature_weights = self._initialize_feature_weights()
    
    def _initialize_cluster_definitions(self) -> Dict[int, Dict[str, Any]]:
        """
        Define las características de cada cluster especializado.
        
        Returns:
            Dict con definiciones detalladas de cada cluster
        """
        return {
            0: {
                'name': 'Mandelbrot Clásico',
                'description': 'Formas circulares concéntricas con estructura de bulbo principal y cardioide',
                'hausdorff_range': (1.8, 2.2),
                'complexity_range': (0.3, 0.7),
                'circularity_range': (0.6, 0.9),
                'visual_pattern': 'concentric_circular',
                'typical_features': {
                    'main_bulb': True,
                    'cardioid_shape': True,
                    'spiral_tendrils': True,
                    'self_similarity': 'high'
                }
            },
            
            1: {
                'name': 'Julia Set Conectado',
                'description': 'Conjuntos de Julia conectados con simetría axial y estructura fractal coherente',
                'hausdorff_range': (1.5, 1.9),
                'complexity_range': (0.2, 0.5),
                'circularity_range': (0.4, 0.8),
                'visual_pattern': 'symmetric_connected',
                'typical_features': {
                    'axial_symmetry': True,
                    'connected_structure': True,
                    'smooth_boundary': True,
                    'self_similarity': 'medium'
                }
            },
            
            2: {
                'name': 'Julia Set Desconectado (Polvo de Cantor)',
                'description': 'Conjuntos de Julia desconectados con estructura de polvo fractal',
                'hausdorff_range': (0.8, 1.4),
                'complexity_range': (0.1, 0.3),
                'circularity_range': (0.1, 0.4),
                'visual_pattern': 'disconnected_dust',
                'typical_features': {
                    'disconnected_points': True,
                    'cantor_dust': True,
                    'sparse_distribution': True,
                    'self_similarity': 'high'
                }
            },
            
            3: {
                'name': 'Fractal Arborescente (IFS)',
                'description': 'Estructuras tipo árbol, helecho o sistema vascular generadas por IFS',
                'hausdorff_range': (1.2, 1.7),
                'complexity_range': (0.4, 0.8),
                'circularity_range': (0.1, 0.3),
                'visual_pattern': 'branching_tree',
                'typical_features': {
                    'branching_structure': True,
                    'hierarchical_levels': True,
                    'organic_appearance': True,
                    'self_similarity': 'high'
                }
            },
            
            4: {
                'name': 'Fractales de Escape Divergente',
                'description': 'Patrones con escape rápido, bordes difusos y transiciones graduales',
                'hausdorff_range': (1.6, 2.0),
                'complexity_range': (0.5, 0.9),
                'circularity_range': (0.2, 0.6),
                'visual_pattern': 'divergent_escape',
                'typical_features': {
                    'blurred_boundaries': True,
                    'gradient_transitions': True,
                    'escape_patterns': True,
                    'self_similarity': 'low'
                }
            },
            
            5: {
                'name': 'Fractales Lineales y Curvas',
                'description': 'Curvas fractales como Koch, Peano, y curvas de relleno del espacio',
                'hausdorff_range': (1.0, 1.6),
                'complexity_range': (0.3, 0.6),
                'circularity_range': (0.1, 0.4),
                'visual_pattern': 'linear_curve',
                'typical_features': {
                    'curve_dominated': True,
                    'space_filling': False,
                    'linear_segments': True,
                    'self_similarity': 'very_high'
                }
            },
            
            6: {
                'name': 'Fractales de Atractor Extraño',
                'description': 'Atractores caóticos como Lorenz, Rössler, con trayectorias complejas',
                'hausdorff_range': (1.4, 2.1),
                'complexity_range': (0.6, 1.0),
                'circularity_range': (0.3, 0.7),
                'visual_pattern': 'chaotic_attractor',
                'typical_features': {
                    'chaotic_trajectory': True,
                    'strange_attractor': True,
                    'phase_space': True,
                    'self_similarity': 'medium'
                }
            },
            
            7: {
                'name': 'Fractales Cristalinos',
                'description': 'Estructuras con simetría cristalina, agregados de difusión limitada (DLA)',
                'hausdorff_range': (1.5, 1.8),
                'complexity_range': (0.4, 0.7),
                'circularity_range': (0.5, 0.8),
                'visual_pattern': 'crystalline_dla',
                'typical_features': {
                    'crystalline_symmetry': True,
                    'dla_growth': True,
                    'radial_structure': True,
                    'self_similarity': 'medium'
                }
            },
            
            8: {
                'name': 'Fractales Multifractales',
                'description': 'Patrones con múltiples dimensiones fractales, estructuras heterogéneas',
                'hausdorff_range': (1.3, 2.3),
                'complexity_range': (0.7, 1.2),
                'circularity_range': (0.2, 0.8),
                'visual_pattern': 'multifractal',
                'typical_features': {
                    'multiple_dimensions': True,
                    'heterogeneous_scaling': True,
                    'varying_density': True,
                    'self_similarity': 'variable'
                }
            },
            
            9: {
                'name': 'Fractales de Percolación',
                'description': 'Estructuras de percolación, redes complejas y clusters conectados',
                'hausdorff_range': (1.6, 2.0),
                'complexity_range': (0.5, 0.9),
                'circularity_range': (0.3, 0.6),
                'visual_pattern': 'percolation_network',
                'typical_features': {
                    'percolation_clusters': True,
                    'network_topology': True,
                    'connectivity_patterns': True,
                    'self_similarity': 'low'
                }
            }
        }
    
    def _initialize_feature_weights(self) -> Dict[str, float]:
        """
        Define pesos para diferentes características en la clasificación.
        
        Returns:
            Dict con pesos de características
        """
        return {
            'hausdorff_dimension': 0.3,
            'dimension_complexity': 0.2,
            'circularity_mean': 0.15,
            'contour_complexity': 0.15,
            'local_dimension_variance': 0.1,
            'convexity_mean': 0.05,
            'contour_count': 0.05
        }
    
    def describe_cluster(self, cluster_id: int) -> str:
        """
        Obtiene la descripción de un cluster.
        
        Args:
            cluster_id: ID del cluster (0-9)
            
        Returns:
            Descripción del cluster
        """
        if cluster_id in self.cluster_definitions:
            cluster = self.cluster_definitions[cluster_id]
            return f"{cluster['name']}: {cluster['description']}"
        else:
            return f"Cluster {cluster_id}: Sin descripción asignada."
    
    def get_cluster_name(self, cluster_id: int) -> str:
        """
        Obtiene el nombre de un cluster.
        
        Args:
            cluster_id: ID del cluster
            
        Returns:
            Nombre del cluster
        """
        if cluster_id in self.cluster_definitions:
            return self.cluster_definitions[cluster_id]['name']
        else:
            return f"Cluster {cluster_id}"
    
    def classify_by_features(self, features: Dict[str, Any]) -> Tuple[int, float, Dict[int, float]]:
        """
        Clasifica un patrón basado en sus características extraídas.
        
        Args:
            features: Dict con características extraídas
            
        Returns:
            Tuple con (cluster_id, confidence, scores_all_clusters)
        """
        try:
            cluster_scores = {}
            
            for cluster_id, cluster_def in self.cluster_definitions.items():
                score = self._calculate_cluster_score(features, cluster_def)
                cluster_scores[cluster_id] = float(score)  # CORRECCIÓN: Convertir a float
            
            # Encontrar el cluster con mayor score
            best_cluster = max(cluster_scores, key=cluster_scores.get)
            best_score = float(cluster_scores[best_cluster])  # CORRECCIÓN: Convertir a float
            
            # Calcular confianza (diferencia con el segundo mejor)
            sorted_scores = sorted(cluster_scores.values(), reverse=True)
            if len(sorted_scores) > 1:
                confidence = float(sorted_scores[0] - sorted_scores[1])  # CORRECCIÓN: Convertir a float
            else:
                confidence = float(best_score)
                
            confidence = max(0.0, min(1.0, confidence))  # Normalizar entre 0 y 1
            
            return int(best_cluster), confidence, cluster_scores
            
        except Exception as e:
            logger.error(f"Error en clasificación por características: {e}")
            return 0, 0.0, {i: 0.0 for i in range(10)}
    
    def _calculate_cluster_score(self, features: Dict[str, Any], cluster_def: Dict[str, Any]) -> float:
        """
        Calcula el score de similitud con un cluster específico.
        
        Args:
            features: Características extraídas
            cluster_def: Definición del cluster
            
        Returns:
            Score de similitud (0-1)
        """
        total_score = 0.0
        total_weight = 0.0
        
        # Score por dimensión de Hausdorff
        if 'hausdorff_dimension' in features:
            hausdorff_score = self._score_in_range(
                features['hausdorff_dimension'],
                cluster_def['hausdorff_range']
            )
            weight = self.feature_weights['hausdorff_dimension']
            total_score += hausdorff_score * weight
            total_weight += weight
        
        # Score por complejidad dimensional
        if 'dimension_complexity' in features:
            complexity_score = self._score_in_range(
                features['dimension_complexity'],
                cluster_def['complexity_range']
            )
            weight = self.feature_weights['dimension_complexity']
            total_score += complexity_score * weight
            total_weight += weight
        
        # Score por circularidad
        if 'circularity_mean' in features:
            circularity_score = self._score_in_range(
                features['circularity_mean'],
                cluster_def['circularity_range']
            )
            weight = self.feature_weights['circularity_mean']
            total_score += circularity_score * weight
            total_weight += weight
        
        # Score por complejidad de contornos
        if 'contour_complexity' in features:
            # Normalizar complejidad de contornos (típicamente 0-20)
            normalized_complexity = min(1.0, features['contour_complexity'] / 10.0)
            complexity_score = self._score_feature_compatibility(
                normalized_complexity, cluster_def['visual_pattern']
            )
            weight = self.feature_weights['contour_complexity']
            total_score += complexity_score * weight
            total_weight += weight
        
        # Score por varianza de dimensiones locales
        if 'dimension_variance' in features:
            variance_score = self._score_variance_compatibility(
                features['dimension_variance'], cluster_def['visual_pattern']
            )
            weight = self.feature_weights['local_dimension_variance']
            total_score += variance_score * weight
            total_weight += weight
        
        # Score por convexidad
        if 'convexity_mean' in features:
            convexity_score = self._score_convexity_compatibility(
                features['convexity_mean'], cluster_def['visual_pattern']
            )
            weight = self.feature_weights['convexity_mean']
            total_score += convexity_score * weight
            total_weight += weight
        
        # Score por número de contornos
        if 'contour_count' in features:
            count_score = self._score_contour_count_compatibility(
                features['contour_count'], cluster_def['visual_pattern']
            )
            weight = self.feature_weights['contour_count']
            total_score += count_score * weight
            total_weight += weight
        
        # Normalizar por el peso total usado
        final_score = total_score / total_weight if total_weight > 0 else 0.0
        
        return max(0.0, min(1.0, final_score))
    
    def _score_in_range(self, value: float, range_tuple: Tuple[float, float]) -> float:
        """
        Calcula score basado en si un valor está dentro de un rango.
        
        Args:
            value: Valor a evaluar
            range_tuple: (min, max) del rango esperado
            
        Returns:
            Score entre 0 y 1
        """
        min_val, max_val = range_tuple
        
        if min_val <= value <= max_val:
            # Valor dentro del rango, score alto
            center = (min_val + max_val) / 2
            distance_from_center = abs(value - center)
            range_width = max_val - min_val
            
            if range_width > 0:
                return 1.0 - (distance_from_center / (range_width / 2)) * 0.2
            else:
                return 1.0
        else:
            # Valor fuera del rango, penalizar por distancia
            if value < min_val:
                distance = min_val - value
                return max(0.0, 0.5 - distance * 0.1)
            else:
                distance = value - max_val
                return max(0.0, 0.5 - distance * 0.1)
    
    def _score_feature_compatibility(self, feature_value: float, visual_pattern: str) -> float:
        """
        Evalúa compatibilidad de una característica con un patrón visual.
        
        Args:
            feature_value: Valor de la característica (0-1)
            visual_pattern: Tipo de patrón visual
            
        Returns:
            Score de compatibilidad
        """
        compatibility_map = {
            'concentric_circular': {
                'high_complexity': 0.7,
                'medium_complexity': 1.0,
                'low_complexity': 0.3
            },
            'symmetric_connected': {
                'high_complexity': 0.4,
                'medium_complexity': 1.0,
                'low_complexity': 0.6
            },
            'disconnected_dust': {
                'high_complexity': 0.2,
                'medium_complexity': 0.4,
                'low_complexity': 1.0
            },
            'branching_tree': {
                'high_complexity': 1.0,
                'medium_complexity': 0.7,
                'low_complexity': 0.3
            },
            'divergent_escape': {
                'high_complexity': 1.0,
                'medium_complexity': 0.8,
                'low_complexity': 0.2
            },
            'linear_curve': {
                'high_complexity': 0.3,
                'medium_complexity': 1.0,
                'low_complexity': 0.8
            },
            'chaotic_attractor': {
                'high_complexity': 1.0,
                'medium_complexity': 0.6,
                'low_complexity': 0.1
            },
            'crystalline_dla': {
                'high_complexity': 0.6,
                'medium_complexity': 1.0,
                'low_complexity': 0.4
            },
            'multifractal': {
                'high_complexity': 1.0,
                'medium_complexity': 0.5,
                'low_complexity': 0.1
            },
            'percolation_network': {
                'high_complexity': 0.8,
                'medium_complexity': 1.0,
                'low_complexity': 0.3
            }
        }
        
        # Determinar nivel de complejidad
        if feature_value < 0.3:
            complexity_level = 'low_complexity'
        elif feature_value < 0.7:
            complexity_level = 'medium_complexity'
        else:
            complexity_level = 'high_complexity'
        
        if visual_pattern in compatibility_map:
            return compatibility_map[visual_pattern].get(complexity_level, 0.5)
        else:
            return 0.5
    
    def _score_variance_compatibility(self, variance: float, visual_pattern: str) -> float:
        """
        Evalúa compatibilidad de varianza dimensional con patrón visual.
        
        Args:
            variance: Varianza de dimensiones locales
            visual_pattern: Tipo de patrón visual
            
        Returns:
            Score de compatibilidad
        """
        variance_preferences = {
            'concentric_circular': 0.3,      # Media varianza
            'symmetric_connected': 0.2,      # Baja varianza
            'disconnected_dust': 0.1,        # Muy baja varianza
            'branching_tree': 0.6,           # Alta varianza
            'divergent_escape': 0.8,         # Muy alta varianza
            'linear_curve': 0.4,             # Media varianza
            'chaotic_attractor': 0.9,        # Muy alta varianza
            'crystalline_dla': 0.5,          # Media-alta varianza
            'multifractal': 1.0,             # Máxima varianza
            'percolation_network': 0.7       # Alta varianza
        }
        
        preferred_variance = variance_preferences.get(visual_pattern, 0.5)
        
        # Calcular score basado en cercanía al valor preferido
        difference = abs(variance - preferred_variance)
        return max(0.0, 1.0 - difference * 2.0)
    
    def _score_convexity_compatibility(self, convexity: float, visual_pattern: str) -> float:
        """
        Evalúa compatibilidad de convexidad con patrón visual.
        
        Args:
            convexity: Convexidad promedio de contornos
            visual_pattern: Tipo de patrón visual
            
        Returns:
            Score de compatibilidad
        """
        convexity_preferences = {
            'concentric_circular': 0.8,      # Alta convexidad
            'symmetric_connected': 0.7,      # Media-alta convexidad
            'disconnected_dust': 0.9,        # Muy alta convexidad
            'branching_tree': 0.3,           # Baja convexidad
            'divergent_escape': 0.4,         # Baja-media convexidad
            'linear_curve': 0.6,             # Media convexidad
            'chaotic_attractor': 0.2,        # Muy baja convexidad
            'crystalline_dla': 0.6,          # Media convexidad
            'multifractal': 0.4,             # Baja-media convexidad
            'percolation_network': 0.3       # Baja convexidad
        }
        
        preferred_convexity = convexity_preferences.get(visual_pattern, 0.5)
        
        # Calcular score basado en cercanía al valor preferido
        difference = abs(convexity - preferred_convexity)
        return max(0.0, 1.0 - difference * 1.5)
    
    def _score_contour_count_compatibility(self, count: int, visual_pattern: str) -> float:
        """
        Evalúa compatibilidad del número de contornos con patrón visual.
        
        Args:
            count: Número de contornos
            visual_pattern: Tipo de patrón visual
            
        Returns:
            Score de compatibilidad
        """
        # Normalizar count a un rango 0-1 (asumiendo máximo de 100 contornos)
        normalized_count = min(1.0, count / 100.0)
        
        count_preferences = {
            'concentric_circular': 0.3,      # Pocos contornos
            'symmetric_connected': 0.2,      # Muy pocos contornos
            'disconnected_dust': 0.8,        # Muchos contornos
            'branching_tree': 0.6,           # Bastantes contornos
            'divergent_escape': 0.4,         # Contornos medios
            'linear_curve': 0.1,             # Muy pocos contornos
            'chaotic_attractor': 0.7,        # Muchos contornos
            'crystalline_dla': 0.5,          # Contornos medios
            'multifractal': 0.9,             # Muchos contornos
            'percolation_network': 0.8       # Muchos contornos
        }
        
        preferred_count = count_preferences.get(visual_pattern, 0.5)
        
        # Calcular score basado en cercanía al valor preferido
        difference = abs(normalized_count - preferred_count)
        return max(0.0, 1.0 - difference * 1.2)
    
    def get_cluster_analysis(self, cluster_id: int, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Proporciona análisis detallado de por qué un patrón fue clasificado en un cluster.
        
        Args:
            cluster_id: ID del cluster asignado
            features: Características del patrón
            
        Returns:
            Dict con análisis detallado
        """
        if cluster_id not in self.cluster_definitions:
            return {'error': f'Cluster {cluster_id} no definido'}
        
        cluster_def = self.cluster_definitions[cluster_id]
        analysis = {
            'cluster_name': cluster_def['name'],
            'cluster_description': cluster_def['description'],
            'feature_matches': {},
            'confidence_factors': {},
            'recommendations': []
        }
        
        # Analizar cada característica
        if 'hausdorff_dimension' in features:
            dim = features['hausdorff_dimension']
            expected_range = cluster_def['hausdorff_range']
            in_range = expected_range[0] <= dim <= expected_range[1]
            
            analysis['feature_matches']['hausdorff_dimension'] = {
                'value': dim,
                'expected_range': expected_range,
                'matches': in_range,
                'score': self._score_in_range(dim, expected_range)
            }
        
        if 'dimension_complexity' in features:
            complexity = features['dimension_complexity']
            expected_range = cluster_def['complexity_range']
            in_range = expected_range[0] <= complexity <= expected_range[1]
            
            analysis['feature_matches']['dimension_complexity'] = {
                'value': complexity,
                'expected_range': expected_range,
                'matches': in_range,
                'score': self._score_in_range(complexity, expected_range)
            }
        
        # Generar recomendaciones basadas en el análisis
        if cluster_id in [0, 1]:  # Mandelbrot/Julia
            analysis['recommendations'].append(
                "Verificar parámetros de iteración para mejor resolución de detalles fractales"
            )
        elif cluster_id in [3, 6]:  # Arborescente/Caótico
            analysis['recommendations'].append(
                "Considerar análisis de ramificación y puntos de bifurcación"
            )
        elif cluster_id == 8:  # Multifractal
            analysis['recommendations'].append(
                "Realizar análisis multifractal completo con espectro de singularidades"
            )
        
        return analysis
    
    def get_all_cluster_info(self) -> Dict[int, Dict[str, Any]]:
        """
        Retorna información completa de todos los clusters.
        
        Returns:
            Dict con información de todos los clusters
        """
        return self.cluster_definitions.copy()
    
    def suggest_similar_clusters(self, cluster_id: int, features: Dict[str, Any]) -> List[Tuple[int, float]]:
        """
        Sugiere clusters similares basados en características.
        
        Args:
            cluster_id: Cluster principal asignado
            features: Características del patrón
            
        Returns:
            Lista de (cluster_id, similarity_score) ordenada por similitud
        """
        _, _, all_scores = self.classify_by_features(features)
        
        # Remover el cluster principal y ordenar por score
        similar_clusters = [(cid, score) for cid, score in all_scores.items() 
                          if cid != cluster_id]
        similar_clusters.sort(key=lambda x: x[1], reverse=True)
        
        return similar_clusters[:3]  # Top 3 similares