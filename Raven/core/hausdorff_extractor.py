import cv2
import numpy as np
from typing import Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class HausdorffDimensionExtractor:
    """
    Extractor de dimensión de Hausdorff usando el método box-counting.
    
    La dimensión de Hausdorff es fundamental para caracterizar fractales,
    ya que mide cómo la complejidad geométrica escala con la resolución.
    """
    
    def __init__(self, 
                 min_box_size: int = 2, 
                 max_box_size: int = 128,
                 edge_threshold1: int = 50,
                 edge_threshold2: int = 150):
        """
        Args:
            min_box_size: Tamaño mínimo de caja para box-counting
            max_box_size: Tamaño máximo de caja
            edge_threshold1: Umbral inferior para detección de bordes
            edge_threshold2: Umbral superior para detección de bordes
        """
        self.min_box_size = min_box_size
        self.max_box_size = max_box_size
        self.edge_threshold1 = edge_threshold1
        self.edge_threshold2 = edge_threshold2
    
    def _prepare_binary_image(self, image: np.ndarray) -> np.ndarray:
        """
        Prepara imagen binaria optimizada para análisis fractal.
        
        Args:
            image: Imagen en escala de grises
            
        Returns:
            Imagen binaria con contornos detectados
        """
        # Aplicar suavizado gaussiano para reducir ruido
        blurred = cv2.GaussianBlur(image, (3, 3), 0)
        
        # Detección de bordes con Canny
        edges = cv2.Canny(blurred, self.edge_threshold1, self.edge_threshold2)
        
        # Aplicar operaciones morfológicas para conectar bordes fragmentados
        kernel = np.ones((2, 2), np.uint8)
        edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
        
        return edges
    
    def _box_counting(self, binary_image: np.ndarray, box_size: int) -> int:
        """
        Cuenta el número de cajas de tamaño box_size que contienen píxeles activos.
        
        Args:
            binary_image: Imagen binaria
            box_size: Tamaño de la caja
            
        Returns:
            Número de cajas ocupadas
        """
        h, w = binary_image.shape
        count = 0
        
        # Iterar sobre todas las posibles cajas
        for i in range(0, h, box_size):
            for j in range(0, w, box_size):
                # Extraer la región de la caja
                box = binary_image[i:i+box_size, j:j+box_size]
                
                # Si hay al menos un píxel activo, contar la caja
                if np.any(box):
                    count += 1
        
        return count
    
    def _calculate_hausdorff_dimension(self, binary_image: np.ndarray) -> Tuple[float, Dict[str, Any]]:
        """
        Calcula la dimensión de Hausdorff usando box-counting.
        
        Args:
            binary_image: Imagen binaria
            
        Returns:
            Tuple con (dimensión, datos_adicionales)
        """
        # Generar tamaños de caja en escala logarítmica
        box_sizes = []
        size = self.max_box_size
        while size >= self.min_box_size:
            box_sizes.append(size)
            size //= 2
        
        box_sizes = sorted(box_sizes)
        
        # Calcular conteos para cada tamaño
        counts = []
        log_sizes = []
        
        for box_size in box_sizes:
            count = self._box_counting(binary_image, box_size)
            if count > 0:  # Evitar log(0)
                counts.append(count)
                log_sizes.append(1.0 / box_size)
        
        if len(counts) < 2:
            logger.warning("Insuficientes puntos para calcular dimensión de Hausdorff")
            return 0.0, {'error': 'insufficient_data'}
        
        # Regresión lineal en escala log-log
        log_counts = np.log(counts)
        log_scales = np.log(log_sizes)
        
        # y = mx + b, donde m es la dimensión de Hausdorff
        coeffs = np.polyfit(log_scales, log_counts, 1)
        hausdorff_dim = coeffs[0]
        
        # Calcular R² para medir calidad del ajuste
        y_pred = np.polyval(coeffs, log_scales)
        ss_res = np.sum((log_counts - y_pred) ** 2)
        ss_tot = np.sum((log_counts - np.mean(log_counts)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        
        additional_data = {
            'box_sizes': box_sizes,
            'counts': counts,
            'r_squared': r_squared,
            'log_regression_coeffs': coeffs.tolist(),
            'valid_points': len(counts)
        }
        
        return hausdorff_dim, additional_data
    
    def _calculate_local_dimensions(self, binary_image: np.ndarray, regions: int = 4) -> np.ndarray:
        """
        Calcula dimensiones de Hausdorff locales dividiendo la imagen en regiones.
        
        Args:
            binary_image: Imagen binaria
            regions: Número de regiones por lado (total = regions²)
            
        Returns:
            Array con dimensiones locales
        """
        h, w = binary_image.shape
        region_h = h // regions
        region_w = w // regions
        
        local_dims = []
        
        for i in range(regions):
            for j in range(regions):
                # Extraer región
                start_h = i * region_h
                end_h = start_h + region_h
                start_w = j * region_w
                end_w = start_w + region_w
                
                region = binary_image[start_h:end_h, start_w:end_w]
                
                # Calcular dimensión local si hay suficiente contenido
                if np.sum(region) > 50:  # Umbral mínimo de píxeles
                    local_dim, _ = self._calculate_hausdorff_dimension(region)
                    local_dims.append(max(0, min(3, local_dim)))  # Clamp entre 0-3
                else:
                    local_dims.append(0.0)
        
        return np.array(local_dims)
    
    def extract(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Extrae características basadas en dimensión de Hausdorff.
        
        Args:
            image: Imagen en escala de grises
            
        Returns:
            Dict con características de dimensión fractal
        """
        try:
            # Preparar imagen binaria
            binary_img = self._prepare_binary_image(image)
            
            # Verificar que hay contenido suficiente - UMBRAL REDUCIDO
            if np.sum(binary_img) < 30:  # Reducido de 100 a 30
                logger.warning("Imagen con muy poco contenido para análisis fractal")
                return {
                    'hausdorff_dimension': 0.0,
                    'local_dimensions': np.zeros(16),
                    'dimension_variance': 0.0,
                    'dimension_complexity': 0.0,
                    'fractal_type': 'insufficient_content',  # AGREGADO
                    'fractal_metadata': {'error': 'insufficient_content'}
                }
            
            # Calcular dimensión global
            hausdorff_dim, metadata = self._calculate_hausdorff_dimension(binary_img)
            
            # Calcular dimensiones locales
            local_dims = self._calculate_local_dimensions(binary_img, regions=4)
            
            # Métricas derivadas
            dimension_variance = np.var(local_dims)
            dimension_complexity = np.std(local_dims) / (np.mean(local_dims) + 1e-6)
            
            # Clasificación básica del tipo de fractal
            fractal_type = self._classify_fractal_type(hausdorff_dim, dimension_variance)
            
            return {
                'hausdorff_dimension': float(hausdorff_dim),
                'local_dimensions': local_dims,
                'dimension_variance': float(dimension_variance),
                'dimension_complexity': float(dimension_complexity),
                'fractal_type': fractal_type,
                'fractal_metadata': metadata
            }
            
        except Exception as e:
            logger.error(f"Error en extracción de dimensión de Hausdorff: {e}")
            return {
                'hausdorff_dimension': 0.0,
                'local_dimensions': np.zeros(16),
                'dimension_variance': 0.0,
                'dimension_complexity': 0.0,
                'fractal_type': 'error',  # AGREGADO
                'fractal_metadata': {'error': str(e)}
            }
    
    def _classify_fractal_type(self, hausdorff_dim: float, variance: float) -> str:
        """
        Clasificación básica del tipo de fractal basada en dimensión y varianza.
        
        Args:
            hausdorff_dim: Dimensión de Hausdorff global
            variance: Varianza de dimensiones locales
            
        Returns:
            Tipo de fractal estimado
        """
        if hausdorff_dim < 1.2:
            return "linear_sparse"
        elif hausdorff_dim < 1.5:
            if variance < 0.1:
                return "smooth_curve"
            else:
                return "branched_linear"
        elif hausdorff_dim < 1.8:
            if variance < 0.2:
                return "self_similar"
            else:
                return "irregular_branching"
        elif hausdorff_dim < 2.2:
            return "dense_fractal"
        else:
            return "space_filling"

# Extractor de contornos mejorado
class ContourAnalysisExtractor:
    """
    Extractor especializado en análisis de contornos para patrones fractales.
    """
    
    def __init__(self, min_contour_area: int = 50):
        """
        Args:
            min_contour_area: Área mínima para considerar un contorno
        """
        self.min_contour_area = min_contour_area
    
    def extract(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Extrae características de contornos.
        
        Args:
            image: Imagen en escala de grises
            
        Returns:
            Dict con características de contornos
        """
        try:
            # Preparar imagen para análisis de contornos
            blurred = cv2.GaussianBlur(image, (3, 3), 0)
            edges = cv2.Canny(blurred, 50, 150)
            
            # Encontrar contornos
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                return self._empty_contour_features()
            
            # Filtrar contornos por área
            valid_contours = [c for c in contours if cv2.contourArea(c) >= self.min_contour_area]
            
            if not valid_contours:
                return self._empty_contour_features()
            
            # Análisis de contornos
            features = self._analyze_contours(valid_contours, image.shape)
            
            return features
            
        except Exception as e:
            logger.error(f"Error en análisis de contornos: {e}")
            return self._empty_contour_features()
    
    def _empty_contour_features(self) -> Dict[str, Any]:
        """Retorna características vacías para casos sin contornos válidos."""
        return {
            'contour_count': 0,
            'total_perimeter': 0.0,
            'avg_area': 0.0,
            'contour_complexity': 0.0,
            'circularity_mean': 0.0,
            'circularity_std': 0.0,
            'convexity_mean': 0.0,
            'aspect_ratio_mean': 0.0,
            'contour_hierarchy_depth': 0
        }
    
    def _analyze_contours(self, contours: list, image_shape: Tuple[int, int]) -> Dict[str, Any]:
        """
        Analiza lista de contornos válidos.
        
        Args:
            contours: Lista de contornos
            image_shape: Forma de la imagen
            
        Returns:
            Dict con características de contornos
        """
        areas = []
        perimeters = []
        circularities = []
        convexities = []
        aspect_ratios = []
        
        total_perimeter = 0.0
        
        for contour in contours:
            # Área y perímetro
            area = cv2.contourArea(contour)
            perimeter = cv2.arcLength(contour, True)
            
            if area > 0 and perimeter > 0:
                areas.append(area)
                perimeters.append(perimeter)
                total_perimeter += perimeter
                
                # Circularidad: 4π*área/perímetro²
                circularity = 4 * np.pi * area / (perimeter ** 2)
                circularities.append(circularity)
                
                # Convexidad: área/área_convexa
                hull = cv2.convexHull(contour)
                hull_area = cv2.contourArea(hull)
                if hull_area > 0:
                    convexity = area / hull_area
                    convexities.append(convexity)
                
                # Relación de aspecto
                rect = cv2.minAreaRect(contour)
                width, height = rect[1]
                if height > 0:
                    aspect_ratio = width / height
                    aspect_ratios.append(aspect_ratio)
        
        # Calcular métricas agregadas
        contour_count = len(contours)
        avg_area = np.mean(areas) if areas else 0.0
        
        # Complejidad basada en la relación perímetro/área
        if areas and perimeters:
            complexity = np.mean([p / np.sqrt(a) for p, a in zip(perimeters, areas)])
        else:
            complexity = 0.0
        
        return {
            'contour_count': contour_count,
            'total_perimeter': total_perimeter,
            'avg_area': avg_area,
            'contour_complexity': complexity,
            'circularity_mean': np.mean(circularities) if circularities else 0.0,
            'circularity_std': np.std(circularities) if circularities else 0.0,
            'convexity_mean': np.mean(convexities) if convexities else 0.0,
            'aspect_ratio_mean': np.mean(aspect_ratios) if aspect_ratios else 0.0,
            'contour_hierarchy_depth': self._estimate_hierarchy_depth(contours, image_shape)
        }
    
    def _estimate_hierarchy_depth(self, contours: list, image_shape: Tuple[int, int]) -> int:
        """
        Estima la profundidad jerárquica de los contornos.
        
        Args:
            contours: Lista de contornos
            image_shape: Forma de la imagen
            
        Returns:
            Profundidad estimada
        """
        if len(contours) <= 1:
            return 0
        
        # Ordenar contornos por área (mayor a menor)
        sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)
        
        # Contar niveles de anidamiento aproximados
        hierarchy_levels = 0
        
        for i, outer_contour in enumerate(sorted_contours[:-1]):
            for inner_contour in sorted_contours[i+1:]:
                # Verificar si un contorno está dentro de otro
                if self._is_contour_inside(inner_contour, outer_contour):
                    hierarchy_levels = max(hierarchy_levels, i + 1)
                    break
        
        return hierarchy_levels
    
    def _is_contour_inside(self, inner_contour: np.ndarray, outer_contour: np.ndarray) -> bool:
        """
        Verifica si un contorno está dentro de otro.
        
        Args:
            inner_contour: Contorno interior
            outer_contour: Contorno exterior
            
        Returns:
            True si inner_contour está dentro de outer_contour
        """
        try:
            # Tomar un punto del contorno interior
            if len(inner_contour) > 0:
                # CORRECCIÓN: Convertir explícitamente a tipos correctos
                test_point = tuple(map(float, inner_contour[0][0]))
                
                # Usar pointPolygonTest para verificar si está dentro
                result = cv2.pointPolygonTest(outer_contour, test_point, False)
                return result >= 0
            return False
        except Exception as e:
            logger.error(f"Error verificando contorno interno: {e}")
            return False