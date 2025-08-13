#!/usr/bin/env python3
"""
RAVEN UNIVERSAL ANALYZER
Expansión del sistema Raven para análisis universal de datos

Integra las capacidades fractales existentes con nuevos módulos de análisis
para texto, audio, datos numéricos, archivos, URLs y más.
"""

import numpy as np
import pandas as pd
import cv2
import json
import re
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any, Union
import logging
from urllib.parse import urlparse
import mimetypes
from collections import Counter
import statistics

# ARREGLO DE IMPORTS - usar imports absolutos con try/except
try:
    from .knowledge_base import EnhancedKnowledgeBase
    from .hausdorff_extractor import HausdorffDimensionExtractor, ContourAnalysisExtractor
except ImportError:
    try:
        from knowledge_base import EnhancedKnowledgeBase
        from hausdorff_extractor import HausdorffDimensionExtractor, ContourAnalysisExtractor
    except ImportError:
        print("Advertencia: Módulos fractales no disponibles")
        EnhancedKnowledgeBase = None
        HausdorffDimensionExtractor = None
        ContourAnalysisExtractor = None

logger = logging.getLogger(__name__)

class RavenUniversalAnalyzer:
    """
    Analizador Universal basado en la arquitectura de Raven.
    
    Mantiene las capacidades fractales existentes y añade nuevos
    módulos especializados para diferentes tipos de datos.
    """
    
    def __init__(self):
        """Inicializa todos los módulos de análisis."""
        # Módulos originales de Raven (si están disponibles)
        self.fractal_available = all([
            EnhancedKnowledgeBase is not None,
            HausdorffDimensionExtractor is not None,
            ContourAnalysisExtractor is not None
        ])
        
        if self.fractal_available:
            self.knowledge_base = EnhancedKnowledgeBase()
            self.hausdorff_extractor = HausdorffDimensionExtractor()
            self.contour_extractor = ContourAnalysisExtractor()
        
        # Nuevos módulos de análisis universal
        self.text_analyzer = TextAnalysisModule()
        self.numeric_analyzer = NumericAnalysisModule()
        self.file_analyzer = FileAnalysisModule()
        self.url_analyzer = URLAnalysisModule()
        self.data_analyzer = DataStructureModule()
        
        # Historial de análisis
        self.analysis_history = {}
        
        # Configuración de detección automática de tipos
        self.type_detectors = {
            'image': self._is_image_data,
            'fractal_image': self._is_fractal_image,
            'text': self._is_text_data,
            'numeric': self._is_numeric_data,
            'url': self._is_url_data,
            'email': self._is_email_data,
            'file_path': self._is_file_path,
            'json': self._is_json_data,
            'csv_data': self._is_csv_data,
            'time_series': self._is_time_series,
            'code': self._is_code_data
        }
    
    def analyze_universal(self, data: Any, analysis_type: str = None, 
                         custom_params: Dict = None) -> Dict[str, Any]:
        """
        Método principal de análisis universal.
        
        Args:
            data: Datos a analizar (cualquier tipo)
            analysis_type: Tipo específico de análisis (opcional)
            custom_params: Parámetros personalizados
            
        Returns:
            Resultados completos del análisis
        """
        start_time = datetime.now()
        
        try:
            # Detectar tipo automáticamente si no se especifica
            if analysis_type is None:
                analysis_type = self._detect_data_type(data)
            
            print(f"Analizando como: {analysis_type}")
            
            # Seleccionar método de análisis apropiado
            analysis_result = self._route_analysis(data, analysis_type, custom_params or {})
            
            # Enriquecer con metadatos
            analysis_result.update({
                'analysis_type': analysis_type,
                'timestamp': start_time.isoformat(),
                'processing_time': (datetime.now() - start_time).total_seconds(),
                'raven_version': '2.1_universal',
                'data_signature': self._generate_data_signature(data),
                'fractal_capabilities': self.fractal_available
            })
            
            # Guardar en historial
            self._save_to_history(analysis_result)
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error en análisis universal: {e}")
            return {
                'error': str(e),
                'analysis_type': analysis_type or 'unknown',
                'timestamp': start_time.isoformat(),
                'success': False
            }
    
    def _detect_data_type(self, data: Any) -> str:
        """Detecta automáticamente el tipo de datos."""
        
        # Probar cada detector en orden de especificidad
        for data_type, detector in self.type_detectors.items():
            if detector(data):
                return data_type
        
        # Tipo genérico por defecto
        return 'generic'
    
    def _route_analysis(self, data: Any, analysis_type: str, params: Dict) -> Dict[str, Any]:
        """Enruta el análisis al módulo apropiado."""
        
        if analysis_type in ['image', 'fractal_image']:
            return self._analyze_image_data(data, params)
        elif analysis_type == 'text':
            return self._analyze_text_data(data, params)
        elif analysis_type == 'numeric':
            return self._analyze_numeric_data(data, params)
        elif analysis_type == 'url':
            return self._analyze_url_data(data, params)
        elif analysis_type == 'file_path':
            return self._analyze_file_data(data, params)
        elif analysis_type == 'json':
            return self._analyze_json_data(data, params)
        elif analysis_type == 'csv_data':
            return self._analyze_csv_data(data, params)
        elif analysis_type == 'time_series':
            return self._analyze_time_series_data(data, params)
        elif analysis_type == 'code':
            return self._analyze_code_data(data, params)
        else:
            return self._analyze_generic_data(data, params)
    
    def _analyze_image_data(self, data: Any, params: Dict) -> Dict[str, Any]:
        """Análisis de imágenes usando las capacidades originales de Raven."""
        
        if not self.fractal_available:
            return {
                'error': 'Módulos fractales no disponibles',
                'suggestion': 'Instalar módulos de análisis fractal de Raven'
            }
        
        # Convertir datos a imagen si es necesario
        if isinstance(data, str) and os.path.exists(data):
            image = cv2.imread(data, cv2.IMREAD_GRAYSCALE)
        elif isinstance(data, np.ndarray):
            image = data if len(data.shape) == 2 else cv2.cvtColor(data, cv2.COLOR_BGR2GRAY)
        else:
            return {'error': 'Formato de imagen no válido'}
        
        # Extraer características usando módulos de Raven
        hausdorff_features = self.hausdorff_extractor.extract(image)
        contour_features = self.contour_extractor.extract(image)
        
        # Combinar características
        combined_features = {**hausdorff_features, **contour_features}
        
        # Clasificar usando base de conocimiento de Raven
        cluster_id, confidence, all_scores = self.knowledge_base.classify_by_features(combined_features)
        
        # Análisis detallado del cluster
        cluster_analysis = self.knowledge_base.get_cluster_analysis(cluster_id, combined_features)
        
        # Sugerir clusters similares
        similar_clusters = self.knowledge_base.suggest_similar_clusters(cluster_id, combined_features)
        
        return {
            'analysis_module': 'raven_fractal_core',
            'image_properties': {
                'shape': image.shape,
                'dtype': str(image.dtype),
                'pixel_stats': {
                    'min': float(np.min(image)),
                    'max': float(np.max(image)),
                    'mean': float(np.mean(image)),
                    'std': float(np.std(image))
                }
            },
            'fractal_features': combined_features,
            'classification': {
                'cluster_id': cluster_id,
                'cluster_name': self.knowledge_base.get_cluster_name(cluster_id),
                'confidence': confidence,
                'all_cluster_scores': all_scores
            },
            'detailed_analysis': cluster_analysis,
            'similar_patterns': similar_clusters,
            'recommendations': self._generate_fractal_recommendations(cluster_id, combined_features)
        }
    
    def _analyze_text_data(self, data: str, params: Dict) -> Dict[str, Any]:
        """Análisis de texto."""
        return self.text_analyzer.analyze(data, params)
    
    def _analyze_numeric_data(self, data: Any, params: Dict) -> Dict[str, Any]:
        """Análisis de datos numéricos."""
        return self.numeric_analyzer.analyze(data, params)
    
    def _analyze_url_data(self, data: str, params: Dict) -> Dict[str, Any]:
        """Análisis de URLs."""
        return self.url_analyzer.analyze(data, params)
    
    def _analyze_file_data(self, data: str, params: Dict) -> Dict[str, Any]:
        """Análisis de archivos."""
        return self.file_analyzer.analyze(data, params)
    
    def _analyze_json_data(self, data: str, params: Dict) -> Dict[str, Any]:
        """Análisis de JSON."""
        return self.data_analyzer.analyze_json(data, params)
    
    def _analyze_csv_data(self, data: Any, params: Dict) -> Dict[str, Any]:
        """Análisis de CSV."""
        return self.data_analyzer.analyze_csv(data, params)
    
    def _analyze_time_series_data(self, data: Any, params: Dict) -> Dict[str, Any]:
        """Análisis de series temporales."""
        return self.numeric_analyzer.analyze_time_series(data, params)
    
    def _analyze_code_data(self, data: str, params: Dict) -> Dict[str, Any]:
        """Análisis de código fuente."""
        return self.text_analyzer.analyze_code(data, params)
    
    def _analyze_generic_data(self, data: Any, params: Dict) -> Dict[str, Any]:
        """Análisis genérico para datos no clasificados."""
        return {
            'analysis_module': 'generic_analyzer',
            'data_type': type(data).__name__,
            'data_size': len(str(data)),
            'data_preview': str(data)[:200] + '...' if len(str(data)) > 200 else str(data),
            'properties': {
                'is_iterable': hasattr(data, '__iter__'),
                'is_numeric': isinstance(data, (int, float, complex)),
                'is_string': isinstance(data, str),
                'is_hashable': hasattr(data, '__hash__') and data.__hash__ is not None
            },
            'suggestions': [
                'Especifica el tipo de análisis deseado',
                'Convierte a formato estándar (texto, números, imagen)',
                'Proporciona contexto adicional sobre los datos'
            ]
        }
    
    # Detectores de tipo de datos
    def _is_image_data(self, data: Any) -> bool:
        """Detecta si los datos son una imagen."""
        if isinstance(data, np.ndarray) and len(data.shape) in [2, 3]:
            return True
        if isinstance(data, str) and os.path.exists(data):
            mime_type, _ = mimetypes.guess_type(data)
            return mime_type and mime_type.startswith('image/')
        return False
    
    def _is_fractal_image(self, data: Any) -> bool:
        """Detecta si es una imagen con características fractales."""
        if not self._is_image_data(data):
            return False
        return True  # Por ahora, todas las imágenes se consideran potencialmente fractales
    
    def _is_text_data(self, data: Any) -> bool:
        """Detecta datos de texto."""
        return isinstance(data, str) and not self._is_url_data(data) and not self._is_file_path(data)
    
    def _is_numeric_data(self, data: Any) -> bool:
        """Detecta datos numéricos."""
        if isinstance(data, (int, float, complex)):
            return True
        if isinstance(data, (list, np.ndarray)):
            try:
                return all(isinstance(x, (int, float, complex)) for x in data)
            except:
                return False
        return False
    
    def _is_url_data(self, data: Any) -> bool:
        """Detecta URLs."""
        if isinstance(data, str):
            return bool(re.match(r'https?://[^\s]+', data))
        return False
    
    def _is_email_data(self, data: Any) -> bool:
        """Detecta emails."""
        if isinstance(data, str):
            return bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', data))
        return False
    
    def _is_file_path(self, data: Any) -> bool:
        """Detecta rutas de archivo."""
        if isinstance(data, str):
            return os.path.exists(data) or bool(re.match(r'^[a-zA-Z]:\\|^/', data))
        return False
    
    def _is_json_data(self, data: Any) -> bool:
        """Detecta JSON."""
        if isinstance(data, str):
            try:
                json.loads(data)
                return True
            except:
                return False
        return False
    
    def _is_csv_data(self, data: Any) -> bool:
        """Detecta CSV."""
        if isinstance(data, str) and '\n' in data and ',' in data:
            lines = data.split('\n')
            if len(lines) > 1:
                first_row = lines[0].split(',')
                second_row = lines[1].split(',') if len(lines) > 1 else []
                return len(first_row) == len(second_row) and len(first_row) > 1
        return False
    
    def _is_time_series(self, data: Any) -> bool:
        """Detecta series temporales."""
        if isinstance(data, (list, np.ndarray)) and len(data) > 10:
            return self._is_numeric_data(data)
        return False
    
    def _is_code_data(self, data: Any) -> bool:
        """Detecta código fuente."""
        if isinstance(data, str):
            code_indicators = ['def ', 'function ', 'class ', 'import ', '#include', 'var ', 'let ', 'const ']
            return any(indicator in data for indicator in code_indicators)
        return False
    
    def _generate_data_signature(self, data: Any) -> str:
        """Genera una firma única para los datos."""
        data_str = str(data)[:1000]
        return f"{type(data).__name__}_{len(data_str)}_{hash(data_str) % 10000}"
    
    def _generate_fractal_recommendations(self, cluster_id: int, features: Dict) -> List[str]:
        """Genera recomendaciones específicas para análisis fractal."""
        recommendations = []
        
        hausdorff_dim = features.get('hausdorff_dimension', 0)
        complexity = features.get('dimension_complexity', 0)
        
        if hausdorff_dim < 1.5:
            recommendations.append("Considerar análisis de curvas fractales lineales")
            recommendations.append("Evaluar parámetros de generación IFS")
        elif hausdorff_dim > 2.0:
            recommendations.append("Analizar patrones de relleno del espacio")
            recommendations.append("Investigar propiedades multifractales")
        
        if complexity > 0.8:
            recommendations.append("Alta complejidad detectada - análisis multiresolución recomendado")
        
        if cluster_id in [0, 1]:
            recommendations.append("Optimizar parámetros de escape e iteraciones")
            recommendations.append("Explorar zoom en regiones de interés")
        elif cluster_id == 8:
            recommendations.append("Realizar espectro de singularidades completo")
            recommendations.append("Calcular dimensiones generalizadas Dq")
        
        return recommendations
    
    def _save_to_history(self, analysis_result: Dict) -> None:
        """Guarda análisis en el historial."""
        signature = analysis_result.get('data_signature', 'unknown')
        timestamp = analysis_result.get('timestamp', datetime.now().isoformat())
        
        self.analysis_history[f"{timestamp}_{signature}"] = {
            'analysis_type': analysis_result.get('analysis_type'),
            'success': analysis_result.get('success', True),
            'processing_time': analysis_result.get('processing_time'),
            'summary': self._generate_analysis_summary(analysis_result)
        }
    
    def _generate_analysis_summary(self, analysis_result: Dict) -> str:
        """Genera resumen del análisis."""
        analysis_type = analysis_result.get('analysis_type', 'unknown')
        
        if analysis_type in ['image', 'fractal_image']:
            cluster_name = analysis_result.get('classification', {}).get('cluster_name', 'Unknown')
            confidence = analysis_result.get('classification', {}).get('confidence', 0)
            return f"Fractal clasificado como: {cluster_name} (confianza: {confidence:.2f})"
        else:
            return f"Análisis de tipo: {analysis_type}"
    
    def get_analysis_history(self) -> Dict:
        """Obtiene el historial de análisis."""
        return self.analysis_history
    
    def export_analysis(self, filename: str = None) -> str:
        """Exporta resultados de análisis."""
        if filename is None:
            filename = f"raven_analysis_{datetime.now().strftime('%d%m%Y_%H%M%S')}.json"
        
        export_data = {
            'raven_version': '2.1_universal',
            'export_timestamp': datetime.now().isoformat(),
            'analysis_history': self.analysis_history,
            'fractal_available': self.fractal_available
        }
        
        if self.fractal_available:
            export_data['cluster_definitions'] = self.knowledge_base.get_all_cluster_info()
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        return filename


# CLASES DE MÓDULOS ESPECIALIZADOS

class TextAnalysisModule:
    """Módulo especializado en análisis de texto."""
    
    def analyze(self, text: str, params: Dict) -> Dict[str, Any]:
        """Análisis completo de texto."""
        return {
            'analysis_module': 'text_analyzer',
            'basic_stats': self._basic_text_stats(text),
            'language_analysis': self._analyze_language(text),
            'sentiment': self._analyze_sentiment(text),
            'complexity': self._analyze_complexity(text),
            'patterns': self._find_patterns(text),
            'keywords': self._extract_keywords(text),
            'readability': self._calculate_readability(text)
        }
    
    def analyze_code(self, code: str, params: Dict) -> Dict[str, Any]:
        """Análisis específico de código fuente."""
        return {
            'analysis_module': 'code_analyzer',
            'language_detected': self._detect_programming_language(code),
            'complexity_metrics': self._calculate_code_complexity(code),
            'structure_analysis': self._analyze_code_structure(code),
            'quality_metrics': self._assess_code_quality(code)
        }
    
    def _basic_text_stats(self, text: str) -> Dict:
        """Estadísticas básicas del texto."""
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        paragraphs = text.split('\n\n')
        
        return {
            'character_count': len(text),
            'word_count': len(words),
            'sentence_count': len([s for s in sentences if s.strip()]),
            'paragraph_count': len([p for p in paragraphs if p.strip()]),
            'avg_word_length': np.mean([len(word) for word in words]) if words else 0,
            'avg_sentence_length': len(words) / len(sentences) if sentences else 0
        }
    
    def _analyze_language(self, text: str) -> Dict:
        """Análisis básico de idioma."""
        spanish_indicators = ['el', 'la', 'de', 'que', 'y', 'es', 'en', 'un', 'se', 'no']
        english_indicators = ['the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'it']
        
        words = re.findall(r'\b\w+\b', text.lower())
        spanish_count = sum(1 for word in words if word in spanish_indicators)
        english_count = sum(1 for word in words if word in english_indicators)
        
        if spanish_count > english_count:
            detected_lang = 'spanish'
            confidence = spanish_count / len(words) if words else 0
        elif english_count > spanish_count:
            detected_lang = 'english'
            confidence = english_count / len(words) if words else 0
        else:
            detected_lang = 'unknown'
            confidence = 0
        
        return {
            'detected_language': detected_lang,
            'confidence': confidence,
            'spanish_indicators': spanish_count,
            'english_indicators': english_count
        }
    
    def _analyze_sentiment(self, text: str) -> Dict:
        """Análisis básico de sentimiento."""
        positive_words = ['bueno', 'excelente', 'genial', 'perfecto', 'fantástico', 'good', 'great', 'excellent', 'amazing', 'perfect']
        negative_words = ['malo', 'terrible', 'horrible', 'pésimo', 'awful', 'bad', 'terrible', 'horrible', 'worst', 'hate']
        
        words = re.findall(r'\b\w+\b', text.lower())
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        if positive_count > negative_count:
            sentiment = 'positive'
            score = (positive_count - negative_count) / len(words) if words else 0
        elif negative_count > positive_count:
            sentiment = 'negative'
            score = (negative_count - positive_count) / len(words) if words else 0
        else:
            sentiment = 'neutral'
            score = 0
        
        return {
            'sentiment': sentiment,
            'score': score,
            'positive_indicators': positive_count,
            'negative_indicators': negative_count
        }
    
    def _analyze_complexity(self, text: str) -> Dict:
        """Análisis de complejidad textual."""
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        
        avg_word_length = np.mean([len(word) for word in words]) if words else 0
        avg_sentence_length = len(words) / len(sentences) if sentences else 0
        
        unique_words = len(set(word.lower() for word in words))
        vocabulary_richness = unique_words / len(words) if words else 0
        
        if avg_sentence_length < 10 and avg_word_length < 5:
            complexity_level = 'simple'
        elif avg_sentence_length < 20 and avg_word_length < 7:
            complexity_level = 'moderate'
        else:
            complexity_level = 'complex'
        
        return {
            'complexity_level': complexity_level,
            'avg_word_length': avg_word_length,
            'avg_sentence_length': avg_sentence_length,
            'vocabulary_richness': vocabulary_richness,
            'unique_word_ratio': vocabulary_richness
        }
    
    def _find_patterns(self, text: str) -> Dict:
        """Encuentra patrones en el texto."""
        patterns = {
            'emails': re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text),
            'urls': re.findall(r'https?://[^\s]+', text),
            'phone_numbers': re.findall(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', text),
            'dates': re.findall(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', text),
            'numbers': re.findall(r'\b\d+\.?\d*\b', text),
            'hashtags': re.findall(r'#\w+', text),
            'mentions': re.findall(r'@\w+', text)
        }
        
        return {k: v for k, v in patterns.items() if v}
    
    def _extract_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """Extrae palabras clave del texto."""
        stop_words = {'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se', 'no', 'te', 'lo', 'le', 
                     'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i', 'it', 'for', 'not', 'on'}
        
        words = re.findall(r'\b\w+\b', text.lower())
        filtered_words = [word for word in words if word not in stop_words and len(word) > 3]
        
        word_freq = Counter(filtered_words)
        return [word for word, count in word_freq.most_common(top_n)]
    
    def _calculate_readability(self, text: str) -> Dict:
        """Calcula métricas de legibilidad."""
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        syllables = sum(self._count_syllables(word) for word in words)
        
        if not sentences or not words:
            return {'error': 'Insufficient text for readability analysis'}
        
        avg_sentence_length = len(words) / len(sentences)
        avg_syllables_per_word = syllables / len(words)
        
        flesch_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        
        if flesch_score >= 90:
            reading_level = 'very_easy'
        elif flesch_score >= 80:
            reading_level = 'easy'
        elif flesch_score >= 70:
            reading_level = 'fairly_easy'
        elif flesch_score >= 60:
            reading_level = 'standard'
        elif flesch_score >= 50:
            reading_level = 'fairly_difficult'
        elif flesch_score >= 30:
            reading_level = 'difficult'
        else:
            reading_level = 'very_difficult'
        
        return {
            'flesch_score': flesch_score,
            'reading_level': reading_level,
            'avg_sentence_length': avg_sentence_length,
            'avg_syllables_per_word': avg_syllables_per_word
        }
    
    def _count_syllables(self, word: str) -> int:
        """Cuenta sílabas de una palabra (aproximación)."""
        word = word.lower()
        vowels = 'aeiouáéíóúü'
        syllable_count = 0
        prev_was_vowel = False
        
        for char in word:
            if char in vowels:
                if not prev_was_vowel:
                    syllable_count += 1
                prev_was_vowel = True
            else:
                prev_was_vowel = False
        
        return max(1, syllable_count)
    
    def _detect_programming_language(self, code: str) -> str:
        """Detecta el lenguaje de programación."""
        patterns = {
            'python': [r'def\s+\w+', r'import\s+\w+', r'from\s+\w+\s+import', r'if\s+__name__\s*==\s*["\']__main__["\']'],
            'javascript': [r'function\s+\w+', r'var\s+\w+', r'let\s+\w+', r'const\s+\w+', r'=>'],
            'java': [r'public\s+class', r'private\s+\w+', r'public\s+static\s+void\s+main'],
            'c++': [r'#include\s*<\w+>', r'int\s+main\s*\(', r'std::', r'cout\s*<<'],
            'html': [r'<html>', r'<head>', r'<body>', r'<div>', r'<!DOCTYPE'],
            'css': [r'\{[^}]*\}', r'#\w+', r'\.\w+', r'@media']
        }
        
        for lang, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, code, re.IGNORECASE):
                    return lang
        
        return 'unknown'
    
    def _calculate_code_complexity(self, code: str) -> Dict:
        """Calcula métricas de complejidad del código."""
        lines = code.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        
        # Contar estructuras de control
        control_structures = len(re.findall(r'\b(if|for|while|switch|case)\b', code))
        functions = len(re.findall(r'\b(def|function|class)\b', code))
        
        return {
            'total_lines': len(lines),
            'code_lines': len(non_empty_lines),
            'control_structures': control_structures,
            'functions': functions,
            'complexity_score': control_structures + functions * 2
        }
    
    def _analyze_code_structure(self, code: str) -> Dict:
        """Analiza la estructura del código."""
        lines = code.split('\n')
        
        # Análisis básico de indentación
        indentation_levels = []
        for line in lines:
            if line.strip():
                leading_spaces = len(line) - len(line.lstrip())
                indentation_levels.append(leading_spaces)
        
        return {
            'max_nesting_level': max(indentation_levels) // 4 if indentation_levels else 0,
            'avg_indentation': np.mean(indentation_levels) if indentation_levels else 0,
            'consistent_indentation': len(set(indentation_levels)) <= 5
        }
    
    def _assess_code_quality(self, code: str) -> Dict:
        """Evalúa la calidad del código."""
        lines = code.split('\n')
        code_lines = [line for line in lines if line.strip()]
        
        # Métricas básicas de calidad
        avg_line_length = np.mean([len(line) for line in code_lines]) if code_lines else 0
        long_lines = sum(1 for line in code_lines if len(line) > 80)
        comments = sum(1 for line in lines if line.strip().startswith('#') or '//' in line)
        
        return {
            'avg_line_length': avg_line_length,
            'long_lines_count': long_lines,
            'comment_ratio': comments / len(code_lines) if code_lines else 0,
            'quality_score': max(0, 100 - long_lines * 5 - max(0, avg_line_length - 60))
        }


class NumericAnalysisModule:
    """Módulo especializado en análisis de datos numéricos."""
    
    def analyze(self, data: Any, params: Dict) -> Dict[str, Any]:
        """Análisis completo de datos numéricos."""
        try:
            # Convertir a array numpy si es necesario
            if isinstance(data, (list, tuple)):
                arr = np.array(data)
            elif isinstance(data, (int, float)):
                arr = np.array([data])
            else:
                arr = data
            
            return {
                'analysis_module': 'numeric_analyzer',
                'basic_stats': self._basic_statistics(arr),
                'distribution': self._analyze_distribution(arr),
                'outliers': self._detect_outliers(arr),
                'trends': self._analyze_trends(arr),
                'patterns': self._find_numeric_patterns(arr)
            }
        except Exception as e:
            return {'error': f'Error en análisis numérico: {str(e)}'}
    
    def analyze_time_series(self, data: Any, params: Dict) -> Dict[str, Any]:
        """Análisis específico de series temporales."""
        try:
            arr = np.array(data) if not isinstance(data, np.ndarray) else data
            
            return {
                'analysis_module': 'time_series_analyzer',
                'basic_stats': self._basic_statistics(arr),
                'trend_analysis': self._analyze_time_trends(arr),
                'seasonality': self._detect_seasonality(arr),
                'stationarity': self._test_stationarity(arr),
                'forecasting_metrics': self._calculate_forecasting_metrics(arr)
            }
        except Exception as e:
            return {'error': f'Error en análisis de series temporales: {str(e)}'}
    
    def _basic_statistics(self, arr: np.ndarray) -> Dict:
        """Estadísticas básicas."""
        return {
            'count': len(arr),
            'mean': float(np.mean(arr)),
            'median': float(np.median(arr)),
            'std': float(np.std(arr)),
            'min': float(np.min(arr)),
            'max': float(np.max(arr)),
            'range': float(np.ptp(arr)),
            'skewness': float(statistics.median(arr) - np.mean(arr)),
            'variance': float(np.var(arr))
        }
    
    def _analyze_distribution(self, arr: np.ndarray) -> Dict:
        """Análisis de distribución."""
        # Análisis básico de distribución
        hist, bins = np.histogram(arr, bins=10)
        
        return {
            'histogram': hist.tolist(),
            'bins': bins.tolist(),
            'is_normal_like': abs(statistics.median(arr) - np.mean(arr)) < np.std(arr) * 0.1,
            'distribution_type': self._classify_distribution(arr)
        }
    
    def _classify_distribution(self, arr: np.ndarray) -> str:
        """Clasifica el tipo de distribución."""
        mean_val = np.mean(arr)
        median_val = np.median(arr)
        std_val = np.std(arr)
        
        if abs(mean_val - median_val) < std_val * 0.1:
            return 'normal_like'
        elif mean_val > median_val:
            return 'right_skewed'
        else:
            return 'left_skewed'
    
    def _detect_outliers(self, arr: np.ndarray) -> Dict:
        """Detección de valores atípicos."""
        q1 = np.percentile(arr, 25)
        q3 = np.percentile(arr, 75)
        iqr = q3 - q1
        
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        outliers = arr[(arr < lower_bound) | (arr > upper_bound)]
        
        return {
            'outlier_count': len(outliers),
            'outlier_percentage': len(outliers) / len(arr) * 100,
            'outlier_values': outliers.tolist(),
            'bounds': {'lower': lower_bound, 'upper': upper_bound}
        }
    
    def _analyze_trends(self, arr: np.ndarray) -> Dict:
        """Análisis de tendencias."""
        if len(arr) < 3:
            return {'trend': 'insufficient_data'}
        
        # Calcular tendencia simple usando regresión lineal básica
        x = np.arange(len(arr))
        slope = np.corrcoef(x, arr)[0, 1] * (np.std(arr) / np.std(x))
        
        if abs(slope) < np.std(arr) * 0.1:
            trend = 'stable'
        elif slope > 0:
            trend = 'increasing'
        else:
            trend = 'decreasing'
        
        return {
            'trend': trend,
            'slope': float(slope),
            'trend_strength': abs(float(slope))
        }
    
    def _find_numeric_patterns(self, arr: np.ndarray) -> Dict:
        """Encuentra patrones numéricos."""
        patterns = {}
        
        # Patrón de repetición
        if len(arr) > 4:
            diffs = np.diff(arr)
            if len(set(diffs)) <= 3:
                patterns['arithmetic_sequence'] = True
                patterns['common_difference'] = float(np.mean(diffs))
        
        # Patrón de multiplicación
        if len(arr) > 2 and all(x != 0 for x in arr[:-1]):
            ratios = arr[1:] / arr[:-1]
            if len(set(np.round(ratios, 2))) <= 2:
                patterns['geometric_sequence'] = True
                patterns['common_ratio'] = float(np.mean(ratios))
        
        return patterns
    
    def _analyze_time_trends(self, arr: np.ndarray) -> Dict:
        """Análisis de tendencias temporales."""
        return self._analyze_trends(arr)
    
    def _detect_seasonality(self, arr: np.ndarray) -> Dict:
        """Detección básica de estacionalidad."""
        if len(arr) < 12:
            return {'seasonality': 'insufficient_data'}
        
        # Análisis simple de autocorrelación
        autocorr_12 = np.corrcoef(arr[:-12], arr[12:])[0, 1] if len(arr) >= 24 else 0
        
        return {
            'seasonal_strength': abs(float(autocorr_12)),
            'likely_seasonal': abs(autocorr_12) > 0.3,
            'period_estimate': 12 if abs(autocorr_12) > 0.3 else None
        }
    
    def _test_stationarity(self, arr: np.ndarray) -> Dict:
        """Test básico de estacionariedad."""
        if len(arr) < 10:
            return {'stationarity': 'insufficient_data'}
        
        # Test simple: comparar varianza de primera y segunda mitad
        mid = len(arr) // 2
        var1 = np.var(arr[:mid])
        var2 = np.var(arr[mid:])
        
        variance_ratio = var2 / var1 if var1 != 0 else float('inf')
        
        return {
            'is_stationary': 0.5 <= variance_ratio <= 2.0,
            'variance_ratio': float(variance_ratio),
            'stationarity_score': 1.0 - abs(1.0 - variance_ratio)
        }
    
    def _calculate_forecasting_metrics(self, arr: np.ndarray) -> Dict:
        """Métricas básicas para forecasting."""
        if len(arr) < 5:
            return {'error': 'insufficient_data'}
        
        # Predicción simple: media móvil
        window = min(3, len(arr) // 2)
        moving_avg = np.convolve(arr, np.ones(window)/window, mode='valid')
        
        return {
            'predictability_score': 1.0 - (np.std(arr) / (np.mean(arr) + 1e-6)),
            'recommended_method': 'moving_average' if len(arr) < 50 else 'trend_analysis',
            'data_points': len(arr),
            'last_value': float(arr[-1]),
            'moving_average': float(moving_avg[-1]) if len(moving_avg) > 0 else float(arr[-1])
        }


class FileAnalysisModule:
    """Módulo especializado en análisis de archivos."""
    
    def analyze(self, file_path: str, params: Dict) -> Dict[str, Any]:
        """Análisis completo de archivos."""
        try:
            if not os.path.exists(file_path):
                return {'error': 'Archivo no encontrado'}
            
            file_stats = os.stat(file_path)
            mime_type, encoding = mimetypes.guess_type(file_path)
            
            return {
                'analysis_module': 'file_analyzer',
                'file_info': {
                    'name': os.path.basename(file_path),
                    'size': file_stats.st_size,
                    'extension': os.path.splitext(file_path)[1],
                    'mime_type': mime_type,
                    'encoding': encoding,
                    'created': datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
                    'modified': datetime.fromtimestamp(file_stats.st_mtime).isoformat()
                },
                'content_analysis': self._analyze_file_content(file_path, mime_type),
                'security_check': self._basic_security_check(file_path)
            }
        except Exception as e:
            return {'error': f'Error analizando archivo: {str(e)}'}
    
    def _analyze_file_content(self, file_path: str, mime_type: str) -> Dict:
        """Análisis del contenido del archivo."""
        try:
            if mime_type and mime_type.startswith('text'):
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(10000)  # Primeros 10KB
                return {
                    'type': 'text',
                    'preview': content[:500],
                    'line_count': content.count('\n'),
                    'character_count': len(content)
                }
            elif mime_type and mime_type.startswith('image'):
                return {
                    'type': 'image',
                    'analysis': 'Usar módulo de análisis de imágenes para detalles'
                }
            else:
                return {
                    'type': 'binary',
                    'analysis': 'Archivo binario - análisis limitado'
                }
        except Exception as e:
            return {'error': f'Error leyendo contenido: {str(e)}'}
    
    def _basic_security_check(self, file_path: str) -> Dict:
        """Verificación básica de seguridad."""
        dangerous_extensions = ['.exe', '.bat', '.cmd', '.scr', '.pif', '.com']
        ext = os.path.splitext(file_path)[1].lower()
        
        return {
            'potentially_dangerous': ext in dangerous_extensions,
            'extension_risk': 'high' if ext in dangerous_extensions else 'low',
            'recommendations': ['Escanear con antivirus'] if ext in dangerous_extensions else []
        }


class URLAnalysisModule:
    """Módulo especializado en análisis de URLs."""
    
    def analyze(self, url: str, params: Dict) -> Dict[str, Any]:
        """Análisis completo de URLs."""
        try:
            parsed = urlparse(url)
            
            return {
                'analysis_module': 'url_analyzer',
                'url_structure': {
                    'scheme': parsed.scheme,
                    'domain': parsed.netloc,
                    'path': parsed.path,
                    'query': parsed.query,
                    'fragment': parsed.fragment
                },
                'domain_analysis': self._analyze_domain(parsed.netloc),
                'security_analysis': self._analyze_url_security(url, parsed),
                'categorization': self._categorize_url(url, parsed)
            }
        except Exception as e:
            return {'error': f'Error analizando URL: {str(e)}'}
    
    def _analyze_domain(self, domain: str) -> Dict:
        """Análisis del dominio."""
        parts = domain.split('.')
        
        return {
            'subdomain_count': len(parts) - 2 if len(parts) > 2 else 0,
            'domain_length': len(domain),
            'tld': parts[-1] if parts else '',
            'is_ip': self._is_ip_address(domain)
        }
    
    def _is_ip_address(self, domain: str) -> bool:
        """Verifica si es una dirección IP."""
        try:
            parts = domain.split('.')
            return len(parts) == 4 and all(0 <= int(part) <= 255 for part in parts)
        except:
            return False
    
    def _analyze_url_security(self, url: str, parsed) -> Dict:
        """Análisis de seguridad de la URL."""
        suspicious_indicators = [
            'bit.ly', 'tinyurl', 'goo.gl',  # Acortadores
            'login', 'verify', 'secure', 'update'  # Palabras sospechosas
        ]
        
        is_suspicious = any(indicator in url.lower() for indicator in suspicious_indicators)
        
        return {
            'uses_https': parsed.scheme == 'https',
            'potentially_suspicious': is_suspicious,
            'suspicious_keywords': [word for word in suspicious_indicators if word in url.lower()],
            'security_score': 100 - (50 if not parsed.scheme == 'https' else 0) - (30 if is_suspicious else 0)
        }
    
    def _categorize_url(self, url: str, parsed) -> Dict:
        """Categorización de la URL."""
        categories = {
            'social': ['facebook.com', 'twitter.com', 'instagram.com', 'linkedin.com'],
            'search': ['google.com', 'bing.com', 'yahoo.com'],
            'shopping': ['amazon.com', 'ebay.com', 'aliexpress.com'],
            'news': ['bbc.com', 'cnn.com', 'reuters.com']
        }
        
        for category, domains in categories.items():
            if any(domain in parsed.netloc for domain in domains):
                return {'category': category, 'confidence': 0.9}
        
        return {'category': 'unknown', 'confidence': 0.0}


class DataStructureModule:
    """Módulo especializado en análisis de estructuras de datos."""
    
    def analyze_json(self, data: str, params: Dict) -> Dict[str, Any]:
        """Análisis de datos JSON."""
        try:
            parsed = json.loads(data)
            
            return {
                'analysis_module': 'json_analyzer',
                'structure': self._analyze_json_structure(parsed),
                'statistics': self._json_statistics(parsed),
                'schema': self._infer_json_schema(parsed)
            }
        except json.JSONDecodeError as e:
            return {'error': f'JSON inválido: {str(e)}'}
    
    def analyze_csv(self, data: Any, params: Dict) -> Dict[str, Any]:
        """Análisis de datos CSV."""
        try:
            if isinstance(data, str):
                lines = data.strip().split('\n')
                if len(lines) < 2:
                    return {'error': 'CSV debe tener al menos encabezados y una fila'}
                
                headers = lines[0].split(',')
                rows = [line.split(',') for line in lines[1:]]
            else:
                return {'error': 'Formato CSV no válido'}
            
            return {
                'analysis_module': 'csv_analyzer',
                'structure': {
                    'columns': len(headers),
                    'rows': len(rows),
                    'headers': headers
                },
                'column_analysis': self._analyze_csv_columns(headers, rows),
                'data_quality': self._assess_csv_quality(rows)
            }
        except Exception as e:
            return {'error': f'Error analizando CSV: {str(e)}'}
    
    def _analyze_json_structure(self, obj, depth=0) -> Dict:
        """Análisis de estructura JSON."""
        if depth > 10:  # Evitar recursión infinita
            return {'type': 'deep_nesting', 'depth_exceeded': True}
        
        if isinstance(obj, dict):
            return {
                'type': 'object',
                'keys': list(obj.keys()),
                'key_count': len(obj),
                'nested_structures': {k: self._analyze_json_structure(v, depth+1) for k, v in obj.items()}
            }
        elif isinstance(obj, list):
            return {
                'type': 'array',
                'length': len(obj),
                'element_types': list(set(type(item).__name__ for item in obj[:10]))  # Primeros 10 elementos
            }
        else:
            return {
                'type': type(obj).__name__,
                'value': str(obj)[:100]  # Primeros 100 caracteres
            }
    
    def _json_statistics(self, obj) -> Dict:
        """Estadísticas del JSON."""
        def count_elements(obj):
            if isinstance(obj, dict):
                return 1 + sum(count_elements(v) for v in obj.values())
            elif isinstance(obj, list):
                return 1 + sum(count_elements(item) for item in obj)
            else:
                return 1
        
        return {
            'total_elements': count_elements(obj),
            'max_depth': self._calculate_max_depth(obj),
            'total_size': len(json.dumps(obj))
        }
    
    def _calculate_max_depth(self, obj, current_depth=0):
        """Calcula la profundidad máxima del JSON."""
        if isinstance(obj, dict):
            return max([self._calculate_max_depth(v, current_depth + 1) for v in obj.values()], default=current_depth)
        elif isinstance(obj, list):
            return max([self._calculate_max_depth(item, current_depth + 1) for item in obj], default=current_depth)
        else:
            return current_depth
    
    def _infer_json_schema(self, obj) -> Dict:
        """Infiere un esquema básico del JSON."""
        if isinstance(obj, dict):
            return {
                'type': 'object',
                'properties': {k: self._infer_json_schema(v) for k, v in obj.items()}
            }
        elif isinstance(obj, list):
            if obj:
                return {
                    'type': 'array',
                    'items': self._infer_json_schema(obj[0])  # Esquema del primer elemento
                }
            else:
                return {'type': 'array', 'items': {}}
        else:
            return {'type': type(obj).__name__}
    
    def _analyze_csv_columns(self, headers: List[str], rows: List[List[str]]) -> Dict:
        """Análisis de columnas CSV."""
        column_analysis = {}
        
        for i, header in enumerate(headers):
            column_data = [row[i] if i < len(row) else '' for row in rows]
            
            # Intentar detectar tipo de datos
            numeric_count = sum(1 for val in column_data if self._is_numeric_string(val))
            date_count = sum(1 for val in column_data if self._is_date_string(val))
            
            total_count = len([val for val in column_data if val.strip()])
            
            if total_count == 0:
                data_type = 'empty'
            elif numeric_count / total_count > 0.8:
                data_type = 'numeric'
            elif date_count / total_count > 0.8:
                data_type = 'date'
            else:
                data_type = 'text'
            
            column_analysis[header] = {
                'data_type': data_type,
                'null_count': len(column_data) - total_count,
                'unique_values': len(set(column_data)),
                'sample_values': column_data[:5]
            }
        
        return column_analysis
    
    def _is_numeric_string(self, s: str) -> bool:
        """Verifica si una cadena representa un número."""
        try:
            float(s.strip())
            return True
        except:
            return False
    
    def _is_date_string(self, s: str) -> bool:
        """Verifica si una cadena representa una fecha."""
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}/\d{2}/\d{4}',  # DD/MM/YYYY
            r'\d{2}-\d{2}-\d{4}'   # DD-MM-YYYY
        ]
        return any(re.match(pattern, s.strip()) for pattern in date_patterns)
    
    def _assess_csv_quality(self, rows: List[List[str]]) -> Dict:
        """Evalúa la calidad de los datos CSV."""
        if not rows:
            return {'quality_score': 0, 'issues': ['No data rows']}
        
        expected_columns = len(rows[0]) if rows else 0
        inconsistent_rows = sum(1 for row in rows if len(row) != expected_columns)
        empty_cells = sum(sum(1 for cell in row if not cell.strip()) for row in rows)
        total_cells = sum(len(row) for row in rows)
        
        quality_score = max(0, 100 - 
                           (inconsistent_rows / len(rows) * 50) - 
                           (empty_cells / total_cells * 30 if total_cells > 0 else 30))
        
        issues = []
        if inconsistent_rows > 0:
            issues.append(f'{inconsistent_rows} filas con número inconsistente de columnas')
        if empty_cells / total_cells > 0.1:
            issues.append(f'Alto porcentaje de celdas vacías ({empty_cells/total_cells*100:.1f}%)')
        
        return {
            'quality_score': quality_score,
            'inconsistent_rows': inconsistent_rows,
            'empty_cells': empty_cells,
            'issues': issues
        }


# FUNCIÓN INTERACTIVA PRINCIPAL

def interactive_raven_universal():
    """Función interactiva principal para el analizador universal."""
    analyzer = RavenUniversalAnalyzer()
    
    print("\n" + "="*60)
    print("RAVEN UNIVERSAL ANALYZER - MODO INTERACTIVO")
    print("="*60)
    print(f"Capacidades fractales: {'Disponibles' if analyzer.fractal_available else 'No disponibles'}")
    print("\nTipos de datos soportados:")
    print("- Texto y código fuente")
    print("- Números y series temporales") 
    print("- URLs y rutas de archivos")
    print("- JSON y CSV")
    if analyzer.fractal_available:
        print("- Imágenes con análisis fractal completo")
    else:
        print("- Imágenes (análisis básico)")
    
    while True:
        print("\n" + "-"*40)
        print("OPCIONES:")
        print("1. Analizar texto")
        print("2. Analizar números")
        print("3. Analizar URL")
        print("4. Analizar archivo")
        print("5. Análisis automático (detectar tipo)")
        print("6. Ver historial")
        print("7. Salir")
        
        try:
            choice = input("\nSelecciona una opción (1-7): ").strip()
            
            if choice == '1':
                text = input("Introduce el texto a analizar: ")
                result = analyzer.analyze_universal(text, 'text')
                print_analysis_result(result)
                
            elif choice == '2':
                numbers_input = input("Introduce números separados por comas: ")
                try:
                    numbers = [float(x.strip()) for x in numbers_input.split(',')]
                    result = analyzer.analyze_universal(numbers, 'numeric')
                    print_analysis_result(result)
                except ValueError:
                    print("Error: Formato de números inválido")
                    
            elif choice == '3':
                url = input("Introduce la URL a analizar: ")
                result = analyzer.analyze_universal(url, 'url')
                print_analysis_result(result)
                
            elif choice == '4':
                file_path = input("Introduce la ruta del archivo: ")
                result = analyzer.analyze_universal(file_path, 'file_path')
                print_analysis_result(result)
                
            elif choice == '5':
                data_input = input("Introduce los datos (detección automática): ")
                result = analyzer.analyze_universal(data_input)
                print_analysis_result(result)
                
            elif choice == '6':
                history = analyzer.get_analysis_history()
                print(f"\nHistorial de análisis ({len(history)} entradas):")
                for key, entry in list(history.items())[-5:]:  # Últimas 5 entradas
                    print(f"- {entry['analysis_type']}: {entry['summary']}")
                    
            elif choice == '7':
                print("Saliendo del analizador universal...")
                break
                
            else:
                print("Opción no válida")
                
        except KeyboardInterrupt:
            print("\n\nSalida interrumpida")
            break
        except Exception as e:
            print(f"\nError: {e}")


def print_analysis_result(result: Dict[str, Any]):
    """Imprime los resultados del análisis de forma formateada."""
    print("\n" + "="*50)
    print("RESULTADOS DEL ANÁLISIS")
    print("="*50)
    
    if 'error' in result:
        print(f"ERROR: {result['error']}")
        return