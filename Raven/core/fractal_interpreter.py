import cv2
import numpy as np
from dataclasses import dataclass
from typing import Optional, Dict, Any, Protocol
from abc import ABC, abstractmethod
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ImageFeatures:
    """
    Contenedor para las características extraídas de una imagen.
    
    Attributes:
        histogram: Histograma de niveles de gris (256 bins)
        hu_moments: Momentos de Hu normalizados logarítmicamente (7 valores)
        edge_density: Densidad de bordes (ratio de píxeles de borde)
        total_pixels: Número total de píxeles en la imagen
        metadata: Información adicional sobre la extracción
    """
    histogram: np.ndarray
    hu_moments: np.ndarray
    edge_density: float
    total_pixels: int
    metadata: Dict[str, Any]
    
    def __getitem__(self, key):
        """Permite acceso tipo diccionario para compatibilidad hacia atrás."""
        if key == 'histogram':
            return self.histogram
        elif key == 'hu_moments':
            return self.hu_moments
        elif key == 'edge_density':
            return self.edge_density
        elif key == 'total_pixels':
            return self.total_pixels
        elif key == 'metadata':
            return self.metadata
        elif key == 'edges':
            # Para compatibilidad, devolver información de bordes si existe
            return self.metadata.get('edges_info', None)
        else:
            raise KeyError(f"'{key}' no es una clave válida")
    
    def __contains__(self, key):
        """Permite usar 'in' para verificar si existe una clave."""
        valid_keys = ['histogram', 'hu_moments', 'edge_density', 'total_pixels', 'metadata', 'edges']
        return key in valid_keys
    
    def keys(self):
        """Devuelve las claves disponibles como si fuera un diccionario."""
        return ['histogram', 'hu_moments', 'edge_density', 'total_pixels', 'metadata']
    
    def to_dict(self):
        """Convierte a diccionario para compatibilidad completa."""
        return {
            'histogram': self.histogram,
            'hu_moments': self.hu_moments,
            'edge_density': self.edge_density,
            'total_pixels': self.total_pixels,
            'metadata': self.metadata
        }

class FeatureExtractorInterface(Protocol):
    """Interfaz para extractores de características."""
    def extract(self, image: np.ndarray) -> Dict[str, Any]:
        """Extrae características de una imagen."""
        ...

class EdgeExtractor:
    """Extractor de características basadas en bordes."""
    
    def __init__(self, threshold1: int = 100, threshold2: int = 200):
        """
        Args:
            threshold1: Umbral inferior para Canny
            threshold2: Umbral superior para Canny
        """
        self.threshold1 = threshold1
        self.threshold2 = threshold2
    
    def extract(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Extrae características de bordes.
        
        Returns:
            Dict con 'edges' (array binario) y 'edge_density' (float)
        """
        edges = cv2.Canny(image, self.threshold1, self.threshold2)
        edge_density = np.count_nonzero(edges) / image.size
        
        return {
            'edges': edges,
            'edge_density': edge_density
        }

class HistogramExtractor:
    """Extractor de histograma de niveles de gris."""
    
    def __init__(self, bins: int = 256):
        """
        Args:
            bins: Número de bins para el histograma
        """
        self.bins = bins
    
    def extract(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Extrae histograma normalizado.
        
        Returns:
            Dict con 'histogram' (array normalizado)
        """
        hist = cv2.calcHist([image], [0], None, [self.bins], [0, 256])
        histogram = hist.flatten()
        # Normalizar por el total de píxeles
        histogram = histogram / image.size
        
        return {
            'histogram': histogram
        }

class HuMomentsExtractor:
    """Extractor de momentos de Hu."""
    
    def __init__(self, use_log_transform: bool = True):
        """
        Args:
            use_log_transform: Si aplicar transformación logarítmica
        """
        self.use_log_transform = use_log_transform
    
    def extract(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Extrae momentos de Hu de los bordes de la imagen.
        
        Returns:
            Dict con 'hu_moments' (array de 7 valores)
        """
        # Calcular bordes para los momentos
        edges = cv2.Canny(image, 100, 200)
        moments = cv2.moments(edges)
        hu_moments = cv2.HuMoments(moments).flatten()
        
        if self.use_log_transform:
            # Transformación logarítmica para hacer los momentos más comparables
            hu_moments = -np.sign(hu_moments) * np.log10(np.abs(hu_moments) + 1e-10)
        
        return {
            'hu_moments': hu_moments
        }

class FractalInterpreter:
    """
    Interpretador de fractales mejorado con arquitectura modular.
    
    Permite añadir/quitar extractores de características de forma dinámica
    y mantiene separación de responsabilidades.
    """
    
    def __init__(self):
        """Inicializa con extractores por defecto."""
        self.extractors = {
            'edges': EdgeExtractor(),
            'histogram': HistogramExtractor(),
            'hu_moments': HuMomentsExtractor()
        }
        self._image_cache = {}
    
    def add_extractor(self, name: str, extractor: FeatureExtractorInterface):
        """
        Añade un nuevo extractor de características.
        
        Args:
            name: Nombre identificativo del extractor
            extractor: Instancia del extractor
        """
        self.extractors[name] = extractor
        logger.info(f"Extractor '{name}' añadido")
    
    def remove_extractor(self, name: str):
        """
        Remueve un extractor de características.
        
        Args:
            name: Nombre del extractor a remover
        """
        if name in self.extractors:
            del self.extractors[name]
            logger.info(f"Extractor '{name}' removido")
        else:
            logger.warning(f"Extractor '{name}' no encontrado")
    
    def _load_image(self, image_path: str) -> np.ndarray:
        """
        Carga una imagen desde archivo con caché.
        
        Args:
            image_path: Ruta a la imagen
            
        Returns:
            Imagen en escala de grises
            
        Raises:
            FileNotFoundError: Si la imagen no existe
        """
        if image_path in self._image_cache:
            return self._image_cache[image_path]
        
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise FileNotFoundError(f"Imagen no encontrada: {image_path}")
        
        self._image_cache[image_path] = img
        logger.info(f"Imagen cargada: {image_path} ({img.shape})")
        return img
    
    def extract_features(self, image_path: str, 
                        extractors: Optional[list] = None) -> ImageFeatures:
        """
        Extrae características de una imagen usando extractores especificados.
        
        Args:
            image_path: Ruta a la imagen
            extractors: Lista de nombres de extractores a usar (None = todos)
            
        Returns:
            ImageFeatures con todas las características extraídas
        """
        try:
            # Cargar imagen
            img = self._load_image(image_path)
            
            # Determinar qué extractores usar
            if extractors is None:
                active_extractors = self.extractors
            else:
                active_extractors = {name: self.extractors[name] 
                                   for name in extractors 
                                   if name in self.extractors}
            
            # Extraer características
            all_features = {}
            metadata = {
                'image_path': image_path,
                'image_shape': img.shape,
                'extractors_used': list(active_extractors.keys())
            }
            
            for name, extractor in active_extractors.items():
                try:
                    features = extractor.extract(img)
                    all_features.update(features)
                    logger.debug(f"Características extraídas por '{name}': {list(features.keys())}")
                except Exception as e:
                    logger.error(f"Error en extractor '{name}': {e}")
                    continue
            
            # Construir resultado final
            result = ImageFeatures(
                histogram=all_features.get('histogram', np.array([])),
                hu_moments=all_features.get('hu_moments', np.array([])),
                edge_density=all_features.get('edge_density', 0.0),
                total_pixels=int(img.size),
                metadata=metadata
            )
            
            logger.info(f"Características extraídas exitosamente de {image_path}")
            return result
            
        except Exception as e:
            logger.error(f"Error completo extrayendo características de {image_path}: {e}")
            raise
    
    def extract_batch(self, image_paths: list, 
                     extractors: Optional[list] = None) -> Dict[str, ImageFeatures]:
        """
        Extrae características de múltiples imágenes.
        
        Args:
            image_paths: Lista de rutas de imágenes
            extractors: Lista de extractores a usar
            
        Returns:
            Dict con path -> ImageFeatures
        """
        results = {}
        for path in image_paths:
            try:
                results[path] = self.extract_features(path, extractors)
            except Exception as e:
                logger.error(f"Error procesando {path}: {e}")
                continue
        
        return results
    
    def extract_features_legacy(self, image_path: str) -> Dict[str, Any]:
        """
        Método de compatibilidad que devuelve un diccionario como el código original.
        
        Args:
            image_path: Ruta a la imagen
            
        Returns:
            Dict con las características en formato original
        """
        features = self.extract_features(image_path)
        
        # Recrear formato original con edges incluidos
        img = self._load_image(image_path)
        edges = cv2.Canny(img, 100, 200)  # Usar valores por defecto
        
        return {
            "edges": edges,
            "histogram": features.histogram,
            "hu_moments": features.hu_moments,
            "edge_density": features.edge_density,
            "total_pixels": features.total_pixels
        }
        """
        Genera un resumen de las características extraídas.
        
        Args:
            features: Características extraídas
            
        Returns:
            Dict con estadísticas resumidas
        """
        summary = {
            'total_pixels': features.total_pixels,
            'edge_density': features.edge_density,
            'histogram_stats': {
                'mean': np.mean(features.histogram) if len(features.histogram) > 0 else 0,
                'std': np.std(features.histogram) if len(features.histogram) > 0 else 0,
                'max_bin': np.argmax(features.histogram) if len(features.histogram) > 0 else 0
            },
            'hu_moments_range': {
                'min': np.min(features.hu_moments) if len(features.hu_moments) > 0 else 0,
                'max': np.max(features.hu_moments) if len(features.hu_moments) > 0 else 0
            },
            'metadata': features.metadata
        }
        
        return summary

# Ejemplo de uso y extensión
if __name__ == "__main__":
    # Crear intérprete
    interpreter = FractalInterpreter()
    
    # Ejemplo de uso con nueva API (recomendado)
    try:
        features = interpreter.extract_features("imagen_fractal.jpg")
        print(f"Edge density: {features.edge_density}")
        print(f"Histogram shape: {features.histogram.shape}")
        print(f"Hu moments: {len(features.hu_moments)}")
        
        # También funciona como diccionario para compatibilidad
        print(f"Edge density (dict style): {features['edge_density']}")
        
        summary = interpreter.get_feature_summary(features)
        print(f"Resumen: {summary}")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
    
    # Ejemplo para código legacy que esperaba diccionario
    try:
        features_dict = interpreter.extract_features_legacy("imagen_fractal.jpg")
        print(f"Formato legacy - Edge density: {features_dict['edge_density']}")
        print(f"Formato legacy - Edges shape: {features_dict['edges'].shape}")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
    
    # Ejemplo de uso selectivo
    features_parcial = interpreter.extract_features(
        "imagen_fractal.jpg", 
        extractors=['histogram', 'edges']
    )
    
    # Ejemplo de extractor personalizado
    class CustomExtractor:
        def extract(self, image: np.ndarray) -> Dict[str, Any]:
            # Ejemplo: calcular entropía
            hist = cv2.calcHist([image], [0], None, [256], [0, 256])
            hist = hist.flatten() / image.size
            entropy = -np.sum(hist * np.log2(hist + 1e-10))
            return {'entropy': entropy}
    
    # Añadir extractor personalizado
    interpreter.add_extractor('entropy', CustomExtractor())