import json
import os
import re
import shutil
import numpy as np
from datetime import datetime
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import cv2
import asyncio  # NUEVO: Necesario para funciones async

# Importaciones del sistema existente
from core.fractal_interpreter import FractalInterpreter
from core.pattern_classifier import PatternClassifier

# *** IMPORTACIÓN CORREGIDA DEL FOLDER ANALYZER ***
try:
    from core.folder_analyzer import FolderAnalyzer
    print("✅ FolderAnalyzer importado correctamente")
except ImportError as e:
    print(f"❌ Error importando FolderAnalyzer: {e}")
    print("💡 Verifica que core/folder_analyzer.py exista y esté actualizado")
    exit(1)

# Nuevas importaciones para funcionalidades mejoradas
from core.hausdorff_extractor import HausdorffDimensionExtractor, ContourAnalysisExtractor
from core.knowledge_base import EnhancedKnowledgeBase

# *** IMPORTACIÓN DE RAVEN UNIVERSAL ***
try:
    from core.raven_universal import RavenUniversalAnalyzer, interactive_raven_universal
    UNIVERSAL_AVAILABLE = True
    print("✅ Analizador Universal importado correctamente")
except ImportError as e:
    print(f"⚠️ Raven Universal no encontrado - funcionando en modo clásico: {e}")
    UNIVERSAL_AVAILABLE = False
    # Crear función dummy para evitar errores
    def interactive_raven_universal():
        print("❌ Analizador Universal no disponible")
        print("💡 Instala el módulo raven_universal.py para habilitarlo")

# *** IMPORTACIONES PARA APRENDIZAJE GRATUITO ***
try:
    from core.free_learning import RavenFreeLearningSystem, interactive_free_learning
    FREE_LEARNING_AVAILABLE = True
    print("✅ Sistema de aprendizaje gratuito cargado")
except ImportError as e:
    print(f"⚠️ Aprendizaje gratuito no disponible: {e}")
    FREE_LEARNING_AVAILABLE = False
    def interactive_free_learning():
        print("❌ Sistema de aprendizaje gratuito no disponible")

# *** IMPORTACIONES PARA ENTRENAMIENTO AI ***
try:
    from core.training_mode import RavenTrainingMode, interactive_training_mode, TrainedRavenEnhancement
    TRAINING_MODE_AVAILABLE = True
    print("✅ Modo de entrenamiento AI cargado")
except ImportError as e:
    print(f"⚠️ Modo de entrenamiento no disponible: {e}")
    TRAINING_MODE_AVAILABLE = False
    async def interactive_training_mode():
        print("❌ Modo de entrenamiento AI no disponible")
    class TrainedRavenEnhancement:
        def __init__(self): self.has_trained_knowledge = False
        def enhance_classification(self, analysis, features): return analysis

# *** NUEVAS IMPORTACIONES PARA INTEGRACIÓN AI ***
try:
    from core.ai_integration import RavenAIIntegration, EnhancedRavenWithAI
    AI_INTEGRATION_AVAILABLE = True
    print("✅ Módulo de integración AI cargado correctamente")
except ImportError as e:
    print(f"⚠️ Integración AI no disponible: {e}")
    print("💡 Para habilitar AI: pip install openai anthropic")
    AI_INTEGRATION_AVAILABLE = False
    # Crear clases dummy para evitar errores
    class RavenAIIntegration:
        def __init__(self, *args, **kwargs):
            pass
    class EnhancedRavenWithAI:
        def __init__(self, *args, **kwargs):
            pass

# *** NUEVA FUNCIÓN PARA VERIFICAR AI EN TIEMPO REAL ***
def check_ai_integration_runtime():
    """
    Verificación mejorada en tiempo de ejecución para detectar si las dependencias de IA están disponibles.
    Esta función reemplaza la verificación estática y es más confiable.
    """
    ai_status = {
        'anthropic': False,
        'openai': False,
        'available': False
    }
    
    # Verificar Anthropic
    try:
        import anthropic
        # Test básico de funcionamiento
        try:
            # Solo test de importación sin crear cliente real
            ai_status['anthropic'] = True
            print("✅ Anthropic SDK disponible")
        except Exception:
            ai_status['anthropic'] = True  # Si se puede importar, está disponible
            print("✅ Anthropic SDK disponible")
    except ImportError:
        print("❌ Anthropic SDK no encontrado")
    except Exception as e:
        print(f"⚠️ Anthropic SDK con problema: {e}")
    
    # Verificar OpenAI
    try:
        import openai
        ai_status['openai'] = True
        print("✅ OpenAI SDK disponible")
    except ImportError:
        print("❌ OpenAI SDK no encontrado")
    except Exception as e:
        print(f"⚠️ OpenAI SDK con problema: {e}")
    
    # Determinar disponibilidad general
    ai_status['available'] = ai_status['anthropic'] or ai_status['openai']
    
    return ai_status

def natural_sort_key(s):
    """Función para ordenar numéricamente los nombres de archivo."""
    return [int(text) if text.isdigit() else text.lower() 
            for text in re.split('([0-9]+)', s)]

def save_enhanced_classification(image_path, cluster, description, features, analysis):
    """Guarda clasificación mejorada con análisis detallado en JSON"""
    json_path = os.path.splitext(image_path)[0] + '.json'
    
    # Convertir arrays numpy a listas para JSON serialization
    serializable_features = {}
    for key, value in features.items():
        if isinstance(value, np.ndarray):
            serializable_features[key] = value.tolist()
        elif isinstance(value, (np.integer, np.floating)):
            serializable_features[key] = float(value)
        else:
            serializable_features[key] = value
    
    classification_data = {
        'image_filename': os.path.basename(image_path),
        'cluster': int(cluster),
        'cluster_name': analysis.get('cluster_name', f'Cluster {cluster}'),
        'cluster_description': description,
        'confidence': float(analysis.get('confidence', 0.0)),
        'fractal_features': serializable_features,
        'feature_analysis': analysis.get('feature_matches', {}),
        'similar_clusters': analysis.get('similar_clusters', []),
        'recommendations': analysis.get('recommendations', []),
        'classification_method': {
            'kmeans_prediction': analysis.get('kmeans_prediction', cluster),
            'rule_prediction': analysis.get('rule_prediction', cluster),
            'final_method': analysis.get('final_method', 'hybrid')
        },
        'last_processed': datetime.now().strftime("%d-%m-%Y %H:%M:%S"), 
        'version': '2.1_complete_system'
    }
    
    # *** AÑADIR MEJORAS DE ENTRENAMIENTO SI ESTÁN DISPONIBLES ***
    if analysis.get('used_trained_knowledge'):
        classification_data['trained_enhancements'] = {
            'improvements': analysis.get('trained_improvements', []),
            'confidence_boost': analysis.get('confidence_boost_from_training', 0.0),
            'enhanced_by_training': True
        }
    
    try:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(classification_data, f, indent=4, ensure_ascii=False)
        print(f"📊 Análisis guardado: {os.path.basename(json_path)}")
        if analysis.get('used_trained_knowledge'):
            print(f"🧠 Incluye mejoras de entrenamiento AI")
    except Exception as e:
        print(f"❌ Error guardando JSON para {image_path}: {e}")

# *** NUEVA FUNCIÓN PARA GUARDAR CON AI INSIGHTS ***
def save_enhanced_classification_with_ai(image_path, cluster, description, features, analysis, ai_insights=None):
    """Guarda clasificación mejorada con análisis detallado en JSON + insights AI"""
    json_path = os.path.splitext(image_path)[0] + '.json'
    
    # Convertir arrays numpy a listas para JSON serialization
    serializable_features = {}
    for key, value in features.items():
        if isinstance(value, np.ndarray):
            serializable_features[key] = value.tolist()
        elif isinstance(value, (np.integer, np.floating)):
            serializable_features[key] = float(value)
        else:
            serializable_features[key] = value
    
    classification_data = {
        'image_filename': os.path.basename(image_path),
        'cluster': int(cluster),
        'cluster_name': analysis.get('cluster_name', f'Cluster {cluster}'),
        'cluster_description': description,
        'confidence': float(analysis.get('confidence', 0.0)),
        'fractal_features': serializable_features,
        'feature_analysis': analysis.get('feature_matches', {}),
        'similar_clusters': analysis.get('similar_clusters', []),
        'recommendations': analysis.get('recommendations', []),
        'classification_method': {
            'kmeans_prediction': analysis.get('kmeans_prediction', cluster),
            'rule_prediction': analysis.get('rule_prediction', cluster),
            'final_method': analysis.get('final_method', 'hybrid')
        },
        'last_processed': datetime.now().strftime("%d-%m-%Y %H:%M:%S"), 
        'version': '2.1_ai_integrated'
    }
    
    # *** AÑADIR INSIGHTS AI SI ESTÁN DISPONIBLES ***
    if ai_insights:
        classification_data['ai_analysis'] = {
            'consensus_level': ai_insights.get('consensus', {}).get('agreement_level', 'none'),
            'ai_confidence': ai_insights.get('consensus', {}).get('confidence_avg', 0.0),
            'ai_recommendation': ai_insights.get('recommendation', ''),
            'models_consulted': [r['model'] for r in ai_insights.get('responses', [])],
            'confidence_boost': ai_insights.get('confidence_boost', 0.0)
        }
    
    try:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(classification_data, f, indent=4, ensure_ascii=False)
        print(f"📊 Análisis guardado: {os.path.basename(json_path)}")
        if ai_insights:
            print(f"🤖 Incluye insights AI: {ai_insights.get('consensus', {}).get('agreement_level', 'none')} consensus")
    except Exception as e:
        print(f"❌ Error guardando JSON para {image_path}: {e}")

def extract_comprehensive_features(interpreter, hausdorff_extractor, contour_extractor, image_path):
    """
    Extrae características completas usando todos los extractores.
    """
    try:
        # Características básicas
        basic_features = interpreter.extract_features(image_path)
        
        # Cargar imagen para extractores adicionales
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            raise ValueError(f"No se pudo cargar la imagen: {image_path}")
        
        # Características de dimensión de Hausdorff
        hausdorff_features = hausdorff_extractor.extract(image)
        
        # Características de contornos
        contour_features = contour_extractor.extract(image)
        
        # Combinar todas las características
        comprehensive_features = {
            # Características básicas
            'histogram': basic_features.histogram,
            'hu_moments': basic_features.hu_moments,
            'edge_density': basic_features.edge_density,
            'total_pixels': basic_features.total_pixels,
            
            # Características de Hausdorff
            'hausdorff_dimension': hausdorff_features['hausdorff_dimension'],
            'local_dimensions': hausdorff_features['local_dimensions'],
            'dimension_variance': hausdorff_features['dimension_variance'],
            'dimension_complexity': hausdorff_features['dimension_complexity'],
            'fractal_type': hausdorff_features['fractal_type'],
            
            # Características de contornos
            'contour_count': contour_features['contour_count'],
            'total_perimeter': contour_features['total_perimeter'],
            'avg_area': contour_features['avg_area'],
            'contour_complexity': contour_features['contour_complexity'],
            'circularity_mean': contour_features['circularity_mean'],
            'circularity_std': contour_features['circularity_std'],
            'convexity_mean': contour_features['convexity_mean'],
            'aspect_ratio_mean': contour_features['aspect_ratio_mean'],
            'contour_hierarchy_depth': contour_features['contour_hierarchy_depth']
        }
        
        return comprehensive_features
        
    except Exception as e:
        print(f"❌ Error extrayendo características de {image_path}: {e}")
        return None

def create_feature_vector(features):
    """Crea vector de características para clustering."""
    try:
        vector_components = []
        
        # Características básicas (histograma reducido)
        if 'histogram' in features and len(features['histogram']) > 0:
            hist_reduced = features['histogram'][:20]
            vector_components.extend(hist_reduced)
        else:
            vector_components.extend([0.0] * 20)
        
        # Momentos de Hu
        if 'hu_moments' in features and len(features['hu_moments']) > 0:
            vector_components.extend(features['hu_moments'])
        else:
            vector_components.extend([0.0] * 7)
        
        # Características de Hausdorff
        vector_components.extend([
            features.get('hausdorff_dimension', 0.0),
            features.get('dimension_complexity', 0.0),
            features.get('dimension_variance', 0.0)
        ])
        
        # Características de contornos más importantes
        vector_components.extend([
            features.get('edge_density', 0.0),
            features.get('circularity_mean', 0.0),
            features.get('contour_complexity', 0.0),
            features.get('convexity_mean', 0.0),
            np.log1p(features.get('contour_count', 0))
        ])
        
        # Estadísticas de dimensiones locales
        local_dims = features.get('local_dimensions', np.zeros(16))
        if len(local_dims) > 0:
            vector_components.extend([
                np.mean(local_dims),
                np.std(local_dims),
                np.max(local_dims),
                np.min(local_dims)
            ])
        else:
            vector_components.extend([0.0, 0.0, 0.0, 0.0])
        
        return np.array(vector_components, dtype=np.float32)
        
    except Exception as e:
        print(f"❌ Error creando vector de características: {e}")
        return np.zeros(39, dtype=np.float32)

class FixedEnhancedPatternClassifier:
    """Clasificador mejorado CORREGIDO que funciona correctamente."""
    
    def __init__(self, n_clusters=10):
        self.n_clusters = n_clusters
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        self.knowledge_base = EnhancedKnowledgeBase()
        self.is_fitted = False
        
    def fit(self, feature_vectors, comprehensive_features_list):
        """Entrena el clasificador con vectores de características."""
        try:
            self.kmeans.fit(feature_vectors)
            self.is_fitted = True
            print(f"🤖 Clasificador entrenado con {len(feature_vectors)} muestras")
            
            # Mostrar estadísticas de clusters
            self._print_cluster_statistics(feature_vectors, comprehensive_features_list)
            
        except Exception as e:
            print(f"❌ Error entrenando clasificador: {e}")
    
    def predict_enhanced(self, feature_vector, comprehensive_features):
        """
        *** VERSIÓN CORREGIDA ***
        Predicción mejorada que funciona correctamente.
        """
        if not self.is_fitted:
            return 0, 0.0, {'error': 'Classifier not fitted'}
        
        try:
            # Predicción por K-means
            kmeans_cluster = self.kmeans.predict([feature_vector])[0]
            
            # *** CORRECIÓN PRINCIPAL ***
            # Análisis basado en reglas usando base de conocimiento
            rule_cluster, rule_confidence, all_scores = self.knowledge_base.classify_by_features(
                comprehensive_features
            )
            
            # Combinar ambos enfoques
            final_cluster, confidence, final_method = self._combine_predictions_fixed(
                kmeans_cluster, rule_cluster, rule_confidence, all_scores
            )
            
            # *** GENERAR ANÁLISIS DETALLADO ***
            analysis = self.knowledge_base.get_cluster_analysis(final_cluster, comprehensive_features)
            analysis['confidence'] = confidence
            analysis['kmeans_prediction'] = int(kmeans_cluster)
            analysis['rule_prediction'] = int(rule_cluster)
            analysis['final_method'] = final_method
            analysis['all_cluster_scores'] = {str(k): float(v) for k, v in all_scores.items()}
            analysis['similar_clusters'] = self.knowledge_base.suggest_similar_clusters(
                final_cluster, comprehensive_features
            )
            
            return final_cluster, confidence, analysis
            
        except Exception as e:
            print(f"❌ Error en predicción mejorada: {e}")
            return 0, 0.0, {'error': str(e)}
    
    def _combine_predictions_fixed(self, kmeans_cluster, rule_cluster, rule_confidence, all_scores):
        """
        *** VERSIÓN CORREGIDA ***
        Combina predicciones de manera más inteligente.
        """
        # Si la confianza de las reglas es muy alta, usar predicción por reglas
        if rule_confidence > 0.8:
            return rule_cluster, rule_confidence, 'rule_based_high_confidence'
        
        # Si las predicciones coinciden, aumentar confianza
        if kmeans_cluster == rule_cluster:
            combined_confidence = min(0.95, rule_confidence + 0.3)
            return rule_cluster, combined_confidence, 'hybrid_agreement'
        
        # Si no coinciden, evaluar cuál es más confiable basado en scores
        kmeans_confidence = 0.6  # Confianza base para K-means
        
        # Si la diferencia de scores es significativa, usar reglas
        sorted_scores = sorted(all_scores.values(), reverse=True)
        score_gap = sorted_scores[0] - sorted_scores[1] if len(sorted_scores) > 1 else 0
        
        if score_gap > 0.2:  # Gap significativo en scores de reglas
            return rule_cluster, rule_confidence + score_gap * 0.5, 'rule_based_significant_gap'
        
        # Si la confianza de reglas es mayor, usar reglas
        if rule_confidence > kmeans_confidence:
            return rule_cluster, rule_confidence, 'rule_based_higher_confidence'
        else:
            # Usar K-means pero con confianza reducida por el desacuerdo
            return kmeans_cluster, kmeans_confidence * 0.7, 'kmeans_with_disagreement'
    
    def _print_cluster_statistics(self, feature_vectors, comprehensive_features_list):
        """Imprime estadísticas de los clusters formados."""
        try:
            labels = self.kmeans.labels_
            
            print("\n📊 Estadísticas de Clustering:")
            for cluster_id in range(self.n_clusters):
                cluster_mask = labels == cluster_id
                cluster_count = np.sum(cluster_mask)
                percentage = (cluster_count / len(labels)) * 100
                
                cluster_name = self.knowledge_base.get_cluster_name(cluster_id)
                print(f"  Cluster {cluster_id} ({cluster_name}): {cluster_count} imágenes ({percentage:.1f}%)")
                
                if cluster_count > 0:
                    # Estadísticas de dimensión de Hausdorff para este cluster
                    hausdorff_dims = [
                        features.get('hausdorff_dimension', 0.0) 
                        for i, features in enumerate(comprehensive_features_list) 
                        if cluster_mask[i]
                    ]
                    if hausdorff_dims:
                        avg_hausdorff = np.mean(hausdorff_dims)
                        print(f"    - Dimensión Hausdorff promedio: {avg_hausdorff:.3f}")
                        
        except Exception as e:
            print(f"❌ Error calculando estadísticas: {e}")

def run_fractal_analysis():
    """Función que ejecuta el análisis fractal original."""
    print("🚀 Iniciando Raven v2.1 SISTEMA COMPLETO...")

    # Inicializar componentes
    interpreter = FractalInterpreter()
    hausdorff_extractor = HausdorffDimensionExtractor()
    contour_extractor = ContourAnalysisExtractor()
    
    # Añadir extractores al intérprete
    interpreter.add_extractor('hausdorff', hausdorff_extractor)
    interpreter.add_extractor('contours', contour_extractor)
    
    # *** USAR CLASIFICADOR CORREGIDO ***
    enhanced_classifier = FixedEnhancedPatternClassifier(n_clusters=10)
    scaler = StandardScaler()

    # *** BUSCAR CARPETA DEL DÍA CON FOLDER ANALYZER CORREGIDO ***
    print("🔍 Buscando carpeta del día con FolderAnalyzer corregido...")
    
    # Usar None para autodetección de rutas
    today_folder = FolderAnalyzer.get_todays_folder()

    if not today_folder:
        print("⚠️ No se encontró carpeta del día. Intentando crear...")
        today_folder = FolderAnalyzer.create_todays_folder()
        
        if not today_folder:
            print("❌ No se pudo crear carpeta del día.")
            print("💡 Verifica la estructura de carpetas o crea manualmente:")
            print("    data/today/DDMMYYYY")
            return
        else:
            print(f"✅ Carpeta creada: {today_folder}")

    print(f"✅ Carpeta de hoy encontrada: {today_folder}")

    # Verificar que la carpeta tenga contenido
    try:
        all_files = os.listdir(today_folder)
        print(f"📁 Total de archivos en carpeta: {len(all_files)}")
        
        if len(all_files) == 0:
            print("⚠️ La carpeta está vacía")
            print("💡 Copia imágenes fractales a la carpeta antes de ejecutar")
            return
        
        # Mostrar primeros archivos para debug
        print("📂 Primeros archivos encontrados:")
        for i, file in enumerate(all_files[:5]):
            print(f"   {i+1}. {file}")
        if len(all_files) > 5:
            print(f"   ... y {len(all_files) - 5} archivos más")
        
    except Exception as e:
        print(f"❌ Error accediendo a la carpeta: {e}")
        return

    # *** FILTRO CORREGIDO ***
    # Obtener y ordenar archivos (VERSIÓN CORREGIDA)
    image_files = sorted(
        [f for f in os.listdir(today_folder) if f.lower().endswith((".png", ".jpg", ".jpeg"))],
        key=natural_sort_key
    )
    
    if not image_files:
        print("❌ No se encontraron imágenes en la carpeta")
        print("💡 Formatos soportados: .png, .jpg, .jpeg")
        return

    print(f"🖼️ Encontradas {len(image_files)} imágenes para procesar")

    # Procesar imágenes y extraer características completas
    feature_vectors = []
    comprehensive_features_list = []
    processed_files = []

    print("\n🔍 Extrayendo características avanzadas...")
    for i, fname in enumerate(image_files):
        path = os.path.join(today_folder, fname)
        print(f"  Procesando {i+1}/{len(image_files)}: {fname}")
        
        try:
            # Extraer características completas
            comprehensive_features = extract_comprehensive_features(
                interpreter, hausdorff_extractor, contour_extractor, path
            )
            
            if comprehensive_features is not None:
                # Crear vector para clustering
                feature_vector = create_feature_vector(comprehensive_features)
                
                feature_vectors.append(feature_vector)
                comprehensive_features_list.append(comprehensive_features)
                processed_files.append(fname)
                
                # Mostrar dimensión de Hausdorff y tipo fractal
                hausdorff_dim = comprehensive_features.get('hausdorff_dimension', 0.0)
                fractal_type = comprehensive_features.get('fractal_type', 'unknown')
                print(f"     Dimensión Hausdorff: {hausdorff_dim:.3f} | Tipo: {fractal_type}")
                
        except Exception as e:
            print(f"     ❌ Error procesando {fname}: {e}")

    if not feature_vectors:
        print("❌ No se pudieron procesar imágenes válidas")
        return

    print(f"\n✅ Procesadas {len(feature_vectors)} imágenes exitosamente")

    # Escalado y entrenamiento del clasificador
    print("\n🤖 Entrenando clasificador híbrido corregido...")
    feature_vectors_np = np.array(feature_vectors)
    scaled_vectors = scaler.fit_transform(feature_vectors_np)
    enhanced_classifier.fit(scaled_vectors, comprehensive_features_list)

    # Clasificación y análisis detallado
    print("\n📊 Resultados de clasificación híbrida corregida:")
    print("=" * 80)
    
    classification_summary = {i: 0 for i in range(10)}
    
    for i, (feature_vector, comprehensive_features, fname) in enumerate(
        zip(feature_vectors_np, comprehensive_features_list, processed_files)
    ):
        img_path = os.path.join(today_folder, fname)
        scaled_vector = scaler.transform([feature_vector])[0]
        
        # *** PREDICCIÓN MEJORADA CORREGIDA CON ENTRENAMIENTO AI ***
        cluster, confidence, analysis = enhanced_classifier.predict_enhanced(
            scaled_vector, comprehensive_features
        )
        
        # Aplicar mejoras de conocimiento entrenado si está disponible
        if TRAINING_MODE_AVAILABLE:
            enhancement = TrainedRavenEnhancement()
            if enhancement.has_trained_knowledge:
                analysis = enhancement.enhance_classification(analysis, comprehensive_features)
                confidence = analysis.get('confidence', confidence)
        
        classification_summary[cluster] += 1
        
        # Descripción del cluster
        cluster_name = analysis.get('cluster_name', f'Cluster {cluster}')
        description = enhanced_classifier.knowledge_base.describe_cluster(cluster)
        
        # Mostrar resultado detallado
        print(f"\n🖼️ {fname}")
        print(f"     Cluster: {cluster} - {cluster_name}")
        print(f"    📝 {description}")
        print(f"    🎯 Confianza: {confidence:.3f} | Método: {analysis.get('final_method', 'hybrid')}")
        
        # Mostrar si hay mejoras de entrenamiento
        if analysis.get('used_trained_knowledge'):
            boost = analysis.get('confidence_boost_from_training', 0.0)
            print(f"    🧠 Mejorado con entrenamiento AI (+{boost:.3f} confianza)")
        
        # Mostrar características clave
        hausdorff_dim = comprehensive_features.get('hausdorff_dimension', 0.0)
        complexity = comprehensive_features.get('dimension_complexity', 0.0)
        contour_count = comprehensive_features.get('contour_count', 0)
        circularity = comprehensive_features.get('circularity_mean', 0.0)
        
        print(f"    📐 Dim. Hausdorff: {hausdorff_dim:.3f} | Complejidad: {complexity:.3f}")
        print(f"    🔍 Contornos: {contour_count} | Circularidad: {circularity:.3f}")
        
        # Mostrar predicciones de ambos métodos
        kmeans_pred = analysis.get('kmeans_prediction', cluster)
        rule_pred = analysis.get('rule_prediction', cluster)
        print(f"    🤖 K-means: {kmeans_pred} | Reglas: {rule_pred}")
        
        # Mostrar clusters similares
        similar_clusters = analysis.get('similar_clusters', [])
        if similar_clusters and len(similar_clusters) > 0:
            similar_info = similar_clusters[0]
            similar_name = enhanced_classifier.knowledge_base.get_cluster_name(similar_info[0])
            print(f"    🔗 Similar a: Cluster {similar_info[0]} ({similar_name}) - Score: {similar_info[1]:.3f}")
        
        # Mostrar recomendaciones
        recommendations = analysis.get('recommendations', [])
        if recommendations:
            print(f"    💡 Recomendación: {recommendations[0]}")
        
        # Guardar análisis completo
        save_enhanced_classification(img_path, cluster, description, 
                                   comprehensive_features, analysis)

    # Resumen final
    print("\n" + "=" * 80)
    print("📋 RESUMEN DE CLASIFICACIÓN COMPLETA")
    print("=" * 80)
    
    knowledge_base = enhanced_classifier.knowledge_base
    
    for cluster_id in range(10):
        count = classification_summary[cluster_id]
        if count > 0:
            percentage = (count / len(processed_files)) * 100
            cluster_name = knowledge_base.get_cluster_name(cluster_id)
            print(f"  Cluster {cluster_id} ({cluster_name}): {count} imágenes ({percentage:.1f}%)")
    
    # Estadísticas globales de dimensión de Hausdorff
    all_hausdorff_dims = [f.get('hausdorff_dimension', 0.0) for f in comprehensive_features_list]
    if all_hausdorff_dims:
        avg_hausdorff = np.mean(all_hausdorff_dims)
        std_hausdorff = np.std(all_hausdorff_dims)
        min_hausdorff = np.min(all_hausdorff_dims)
        max_hausdorff = np.max(all_hausdorff_dims)
        
        print(f"\n📊 ESTADÍSTICAS DE DIMENSIÓN DE HAUSDORFF:")
        print(f"   Promedio: {avg_hausdorff:.3f} ± {std_hausdorff:.3f}")
        print(f"   Rango: [{min_hausdorff:.3f}, {max_hausdorff:.3f}]")
    
    # Distribución de tipos fractales
    fractal_types = [f.get('fractal_type', 'unknown') for f in comprehensive_features_list]
    type_counts = {}
    for ftype in fractal_types:
        type_counts[ftype] = type_counts.get(ftype, 0) + 1
    
    print(f"\n🔬 DISTRIBUCIÓN DE TIPOS FRACTALES:")
    for ftype, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(fractal_types)) * 100
        print(f"   {ftype}: {count} imágenes ({percentage:.1f}%)")

    # *** MOVER CARPETA PROCESADA CON FOLDER ANALYZER ***
    print(f"\n📦 Moviendo carpeta procesada...")
    
    # Obtener ruta base del proyecto
    project_root = FolderAnalyzer._get_project_root()
    processed_dir = os.path.join(project_root, "data", "processed")
    
    if not os.path.exists(processed_dir):
        os.makedirs(processed_dir)
    
    # Obtener nombre base de la carpeta
    folder_name = datetime.now().strftime("%d%m%Y")
    
    # Buscar un nombre único con numeración automática
    counter = 1
    while True:
        new_folder_name = f"{folder_name}_analyzed_{counter}"
        destination = os.path.join(processed_dir, new_folder_name)
        
        # Si no existe esta carpeta, usar este nombre
        if not os.path.exists(destination):
            break
        
        # Si existe, incrementar contador y probar siguiente
        counter += 1
        
        # Prevenir bucle infinito (máximo 999 intentos)
        if counter > 999:
            print(f"⚠️ Demasiadas carpetas con la misma fecha. Usando timestamp.")
            timestamp = datetime.now().strftime("%d%m%Y_%H%M%S")
            new_folder_name = f"{folder_name}_analyzed_{timestamp}"
            destination = os.path.join(processed_dir, new_folder_name)
            break
    
    try:
        shutil.move(today_folder, destination)
        print(f"✅ Carpeta movida a procesados: {destination}")
        print(f"📁 Nombre asignado: {folder_name} → {new_folder_name}")
        if counter > 1:
            print(f"📊 Análisis #{counter} del día")
    except Exception as e:
        print(f"❌ Error moviendo carpeta: {e}")

    print(f"\n🎉 ¡Clasificación híbrida completada!")

# *** NUEVA FUNCIÓN PARA ANÁLISIS FRACTAL CON AI ***
async def run_fractal_analysis_with_ai(openai_key=None, anthropic_key=None):
    """Función que ejecuta el análisis fractal con integración AI."""
    print("🚀 Iniciando Raven v2.1 con INTEGRACIÓN AI...")
    
    # Verificar disponibilidad de AI
    if not AI_INTEGRATION_AVAILABLE:
        print("⚠️ Integración AI no disponible, ejecutando análisis clásico")
        run_fractal_analysis()  # Llamar función original
        return
    
    if not (openai_key or anthropic_key):
        print("⚠️ No se proporcionaron claves API, ejecutando análisis clásico")
        run_fractal_analysis()  # Llamar función original
        return
    
    # Crear instancia mejorada de Raven con AI
    try:
        enhanced_raven = EnhancedRavenWithAI(openai_key, anthropic_key)
        print("🤖 Raven con capacidades AI iniciado exitosamente")
    except Exception as e:
        print(f"❌ Error iniciando integración AI: {e}")
        print("🔄 Continuando con análisis clásico...")
        run_fractal_analysis()
        return
    
    print("🔍 Buscando carpeta del día...")
    today_folder = FolderAnalyzer.get_todays_folder()
    
    if not today_folder:
        print("❌ No se encontró carpeta del día")
        return
    
    # Obtener imágenes
    image_files = sorted(
        [f for f in os.listdir(today_folder) if f.lower().endswith((".png", ".jpg", ".jpeg"))],
        key=natural_sort_key
    )
    
    if not image_files:
        print("❌ No se encontraron imágenes")
        return
    
    print(f"🖼️ Encontradas {len(image_files)} imágenes para análisis AI-mejorado")
    
    # Procesar cada imagen con análisis AI (ejemplo para primeras 3 imágenes)
    for i, fname in enumerate(image_files[:3]):  # Procesar solo primeras 3 para demo
        img_path = os.path.join(today_folder, fname)
        print(f"\n🔍 Analizando con AI: {fname} ({i+1}/{min(3, len(image_files))})")
        
        try:
            # Análisis mejorado con consenso AI
            enhanced_analysis = await enhanced_raven.analyze_with_ai_consensus(img_path)
            
            # Mostrar resultados
            raven_cluster = enhanced_analysis['raven_analysis']['cluster_analysis']['cluster_name']
            ai_agreement = enhanced_analysis['ai_consensus']['consensus']['agreement_level']
            final_confidence = enhanced_analysis['confidence_boost']
            
            print(f"📊 Análisis Raven: {raven_cluster}")
            print(f"🤖 Consenso AI: {ai_agreement}")
            print(f"✨ Confianza final: {final_confidence:.3f}")
            
            # Guardar con insights AI
            save_enhanced_classification_with_ai(
                img_path,
                enhanced_analysis['raven_analysis']['cluster_analysis'].get('cluster_id', 0),
                enhanced_analysis['raven_analysis']['cluster_analysis'].get('cluster_name', ''),
                enhanced_analysis['raven_analysis']['features'],
                enhanced_analysis['raven_analysis']['cluster_analysis'],
                enhanced_analysis['ai_consensus']
            )
            
        except Exception as e:
            print(f"❌ Error en análisis AI para {fname}: {e}")
            continue
    
    print("\n🎉 ¡Análisis fractal con AI completado!")

# *** FUNCIÓN SHOW_MAIN_MENU CORREGIDA CON DETECCIÓN AI EN TIEMPO REAL ***
def show_main_menu():
    """Muestra el menú principal integrado con todas las opciones."""
    print("\n" + "=" * 70)
    print("🦅 RAVEN - SISTEMA DE ANÁLISIS FRACTAL INTEGRADO v2.1 COMPLETO")
    print("=" * 70)
    print("\n🎯 Selecciona el modo de análisis:")
    print("──────────────────────────────────")
    
    print("\n1. 📊 Análisis Fractal de Carpeta (Modo Clásico)")
    print("   └─ Procesamiento tradicional de Raven")
    print("   └─ Clasificación en 10 clusters especializados")
    print("   └─ Análisis de dimensión de Hausdorff avanzado")
    print("   └─ 100% GRATUITO")
    
    if FREE_LEARNING_AVAILABLE:
        print("\n2. 🧠 Aprendizaje Gratuito")
        print("   └─ Raven aprende de tus análisis históricos")
        print("   └─ Correcciones manuales para mejorar precisión")
        print("   └─ Auto-mejora basada en tus datos")
        print("   └─ 100% GRATUITO - Sin APIs externas")
    else:
        print("\n2. 🧠 Aprendizaje Gratuito (No disponible)")
        print("   └─ Falta core/free_learning.py")
    
    if TRAINING_MODE_AVAILABLE:
        print("\n3. 🎓 Entrenar Raven con AI (Una vez)")
        print("   └─ GPT-4 + Claude entrenan a Raven")
        print("   └─ Inversión única: $5-15")
        print("   └─ Después funciona GRATIS para siempre")
        print("   └─ Mejora permanente del sistema")
    else:
        print("\n3. 🎓 Entrenar Raven con AI (No disponible)")
        print("   └─ Falta core/training_mode.py o dependencias")
    
    # *** VERIFICACIÓN AI MEJORADA EN TIEMPO REAL ***
    print("\n🔍 Verificando dependencias AI...")
    ai_runtime_status = check_ai_integration_runtime()
    
    if ai_runtime_status['available']:
        print("\n4. 🤖 Análisis Fractal con AI (GPT-4 + Claude)")
        print("   └─ Análisis Raven + consenso de modelos AI")
        print("   └─ Clasificación verificada por GPT-4 y Claude")
        print("   └─ Confianza mejorada basada en consenso")
        print("   └─ ⚠️ Requiere claves API válidas")
        
        # Mostrar qué SDKs están disponibles
        available_models = []
        if ai_runtime_status['anthropic']:
            available_models.append("Claude")
        if ai_runtime_status['openai']:
            available_models.append("GPT-4")
        print(f"   └─ SDKs disponibles: {', '.join(available_models)}")
    else:
        print("\n4. ❌ Análisis Fractal con AI (No disponible)")
        print("   └─ Dependencias faltantes detectadas:")
        if not ai_runtime_status['anthropic']:
            print("       • pip install anthropic")
        if not ai_runtime_status['openai']:
            print("       • pip install openai")
    
    if UNIVERSAL_AVAILABLE:
        print("\n5. 🌟 Análisis Universal")
        print("   └─ Analiza CUALQUIER tipo de datos")
        print("   └─ Texto, números, URLs, archivos, JSON, CSV")
    else:
        print("\n5. 🌟 Análisis Universal (No disponible)")
        print("   └─ Falta core/raven_universal.py")
    
    print("\n6. 📋 Información del Sistema")
    print("7. 🚪 Salir")
    
    # *** MOSTRAR ESTADOS DE DISPONIBILIDAD ACTUALIZADOS ***
    print(f"\n📊 Estado de funcionalidades (verificado en tiempo real):")
    print(f"   🔄 Análisis Clásico: ✅ Siempre disponible")
    print(f"   🧠 Aprendizaje Gratuito: {'✅' if FREE_LEARNING_AVAILABLE else '❌'}")
    print(f"   🎓 Entrenamiento AI: {'✅' if TRAINING_MODE_AVAILABLE else '❌'}")
    print(f"   🤖 Integración AI: {'✅' if ai_runtime_status['available'] else '❌'}")
    print(f"   🌟 Análisis Universal: {'✅' if UNIVERSAL_AVAILABLE else '❌'}")
    
    # Guardar estado AI para uso en main()
    global AI_RUNTIME_AVAILABLE
    AI_RUNTIME_AVAILABLE = ai_runtime_status['available']

def show_system_info():
    """Muestra información completa del sistema."""
    print("\n" + "=" * 60)
    print("📋 INFORMACIÓN DEL SISTEMA RAVEN v2.1 COMPLETO")
    print("=" * 60)
    
    print("\n🔧 COMPONENTES PRINCIPALES:")
    components = [
        ("Intérprete Fractal", True),
        ("Clasificador de Patrones", True), 
        ("Analizador de Carpetas", True),
        ("Extractor Hausdorff", True),
        ("Base de Conocimiento (10 clusters)", True),
        ("Análisis Universal", UNIVERSAL_AVAILABLE),
        ("Aprendizaje Gratuito", FREE_LEARNING_AVAILABLE),
        ("Entrenamiento AI", TRAINING_MODE_AVAILABLE),
        ("Integración AI", AI_INTEGRATION_AVAILABLE)
    ]
    
    for name, available in components:
        status = "✅ Disponible" if available else "❌ No disponible"
        print(f"   {name}: {status}")
    
    print(f"\n🎯 CAPACIDADES ACTIVAS:")
    print(f"   • Análisis fractal especializado: ✅")
    print(f"   • Clasificación en 10 clusters: ✅")
    print(f"   • Dimensión de Hausdorff: ✅")
    print(f"   • Análisis de contornos: ✅")
    print(f"   • Base de conocimiento expandida: ✅")
    print(f"   • Aprendizaje de datos históricos: {'✅' if FREE_LEARNING_AVAILABLE else '❌'}")
    print(f"   • Entrenamiento con AI: {'✅' if TRAINING_MODE_AVAILABLE else '❌'}")
    print(f"   • Integración AI en tiempo real: {'✅' if AI_INTEGRATION_AVAILABLE else '❌'}")
    print(f"   • Análisis universal: {'✅' if UNIVERSAL_AVAILABLE else '❌'}")
    
    # Verificar si hay conocimiento entrenado
    if TRAINING_MODE_AVAILABLE:
        enhancement = TrainedRavenEnhancement()
        if enhancement.has_trained_knowledge:
            print(f"   🧠 Conocimiento AI entrenado: ✅ ACTIVO")
            print(f"       └─ Raven funcionará con mejoras AI automáticamente")
        else:
            print(f"   🧠 Conocimiento AI entrenado: ❌ Sin entrenar")
            print(f"       └─ Usa opción 3 para entrenar Raven con AI")
    
    print(f"\n📊 TIPOS DE FRACTALES RECONOCIDOS:")
    try:
        kb = EnhancedKnowledgeBase()
        for i in range(10):
            cluster_name = kb.get_cluster_name(i)
            print(f"   {i}. {cluster_name}")
    except Exception as e:
        print(f"   ❌ Error accediendo a la base de conocimiento: {e}")
    
    print(f"\n🗂️  ESTRUCTURA DE DATOS:")
    print(f"   📁 data/ - Carpetas de imágenes por fecha")
    print(f"   📁 data/processed/ - Análisis completados")
    print(f"   📁 data/trained_knowledge/ - Conocimiento AI entrenado")
    print(f"   📄 *.json - Metadatos de cada imagen")

    # Mostrar estado actual de carpetas
    print(f"\n📋 ESTADO ACTUAL:")
    try:
        # Verificar carpeta del día
        today_folder = FolderAnalyzer.get_todays_folder()
        if today_folder:
            print(f"   ✅ Carpeta del día: {os.path.basename(today_folder)}")
            stats = FolderAnalyzer.get_folder_stats(today_folder)
            if "error" not in stats:
                print(f"   📊 Archivos disponibles: {stats['files']}")
                if stats['file_types']:
                    for ext, count in stats['file_types'].items():
                        print(f"      {ext}: {count}")
        else:
            print(f"   ❌ No hay carpeta del día actual")
        
        # Fechas disponibles
        dates = FolderAnalyzer.list_available_dates()
        if dates:
            print(f"   📅 Fechas disponibles: {len(dates)}")
            for date in dates[:3]:
                formatted = f"{date[0:2]}/{date[2:4]}/{date[4:8]}"
                print(f"      • {date} ({formatted})")
            if len(dates) > 3:
                print(f"      ... y {len(dates) - 3} más")
        else:
            print(f"   📅 No hay fechas disponibles")
            
    except Exception as e:
        print(f"   ⚠️ Error verificando estado: {e}")

# *** FUNCIÓN MAIN CORREGIDA ***
def main():
    """Función principal con menú integrado completo."""
    
    print("🚀 INICIANDO RAVEN v2.1 - SISTEMA COMPLETO")
    print("=" * 60)
    
    # Verificar FolderAnalyzer al inicio
    try:
        test_result = FolderAnalyzer._get_project_root()
        print(f"✅ FolderAnalyzer funcionando - Proyecto en: {test_result}")
    except Exception as e:
        print(f"❌ Error en FolderAnalyzer: {e}")
        print("💡 Verifica que core/folder_analyzer.py esté actualizado")
        input("Presiona Enter para continuar de todos modos...")
    
    # *** VERIFICACIÓN INICIAL DE DEPENDENCIAS AI ***
    print("\n🔍 Verificación inicial de dependencias AI...")
    ai_initial_check = check_ai_integration_runtime()
    if ai_initial_check['available']:
        print("✅ Dependencias AI detectadas correctamente")
    else:
        print("⚠️ Algunas dependencias AI no están disponibles")
    
    while True:
        show_main_menu()
        
        try:
            choice = input("\n👉 Selecciona una opción (1-7): ").strip()
            
            if choice == '1':
                print("\n🔄 Iniciando análisis fractal clásico...")
                run_fractal_analysis()
                input("\n✨ Presiona Enter para continuar...")
                
            elif choice == '2':
                if FREE_LEARNING_AVAILABLE:
                    print("\n🧠 Iniciando sistema de aprendizaje gratuito...")
                    try:
                        interactive_free_learning()
                    except Exception as e:
                        print(f"❌ Error en aprendizaje gratuito: {e}")
                    input("\n✨ Presiona Enter para continuar...")
                else:
                    print("\n❌ Aprendizaje gratuito no disponible")
                    print("💡 Crea el archivo core/free_learning.py")
                    input("\n✨ Presiona Enter para continuar...")
                    
            elif choice == '3':
                if TRAINING_MODE_AVAILABLE:
                    print("\n🎓 Iniciando modo de entrenamiento AI...")
                    try:
                        # Verificar si ya está entrenado
                        enhancement = TrainedRavenEnhancement()
                        if enhancement.has_trained_knowledge:
                            print("🧠 Raven ya tiene conocimiento entrenado!")
                            print("✅ El sistema ya funciona con mejoras AI")
                            
                            retrain = input("¿Quieres volver a entrenar? (s/n): ").strip().lower()
                            if retrain not in ['s', 'sí', 'si', 'y', 'yes']:
                                continue
                        
                        # Ejecutar entrenamiento
                        asyncio.run(interactive_training_mode())
                    except Exception as e:
                        print(f"❌ Error en entrenamiento: {e}")
                    input("\n✨ Presiona Enter para continuar...")
                else:
                    print("\n❌ Modo de entrenamiento no disponible")
                    print("💡 Crea core/training_mode.py e instala: pip install openai anthropic")
                    input("\n✨ Presiona Enter para continuar...")
                    
            elif choice == '4':
                # *** VERIFICACIÓN AI CORREGIDA ***
                print("\n🔍 Verificando disponibilidad AI en tiempo real...")
                ai_check = check_ai_integration_runtime()
                
                if ai_check['available']:
                    print("✅ AI disponible - Continuando con configuración...")
                    print("\n🤖 CONFIGURACIÓN DE INTEGRACIÓN AI")
                    print("=" * 40)
                    print("Necesitas claves API para:")
                    if ai_check['openai']:
                        print("• ✅ OpenAI GPT-4: https://platform.openai.com/api-keys")
                    else:
                        print("• ❌ OpenAI no disponible")
                    if ai_check['anthropic']:
                        print("• ✅ Anthropic Claude: https://console.anthropic.com/")
                    else:
                        print("• ❌ Anthropic no disponible")
                    
                    print("\n⚠️ Las claves se usan solo para esta sesión (no se almacenan)")
                    
                    # Solicitar claves API solo para los SDKs disponibles
                    openai_key = ""
                    anthropic_key = ""
                    
                    if ai_check['openai']:
                        openai_key = input("\n🔑 Clave OpenAI (Enter para omitir): ").strip()
                    
                    if ai_check['anthropic']:
                        anthropic_key = input("🔑 Clave Anthropic (Enter para omitir): ").strip()
                    
                    if openai_key or anthropic_key:
                        print(f"\n🚀 Iniciando análisis AI...")
                        print(f"   GPT-4: {'✅' if openai_key and ai_check['openai'] else '❌'}")
                        print(f"   Claude: {'✅' if anthropic_key and ai_check['anthropic'] else '❌'}")
                        
                        # Ejecutar análisis AI de forma asíncrona
                        try:
                            if AI_INTEGRATION_AVAILABLE:  # Verificar que el módulo está importado
                                asyncio.run(run_fractal_analysis_with_ai(openai_key, anthropic_key))
                            else:
                                print("⚠️ Módulo AI no cargado, ejecutando análisis clásico")
                                run_fractal_analysis()
                        except Exception as e:
                            print(f"❌ Error en análisis AI: {e}")
                            print("🔄 Ejecutando análisis clásico...")
                            run_fractal_analysis()
                    else:
                        print("❌ No se proporcionaron claves, ejecutando análisis clásico")
                        run_fractal_analysis()
                    
                    input("\n✨ Presiona Enter para continuar...")
                else:
                    print("\n❌ Integración AI no disponible")
                    print("🔧 Dependencias faltantes:")
                    if not ai_check['anthropic']:
                        print("   pip install anthropic")
                    if not ai_check['openai']:
                        print("   pip install openai")
                    print("\n💡 Instala las dependencias y reinicia RAVEN")
                    input("\n✨ Presiona Enter para continuar...")
                    
            elif choice == '5':
                if UNIVERSAL_AVAILABLE:
                    print("\n🌟 Iniciando Raven Universal...")
                    try:
                        interactive_raven_universal()
                    except Exception as e:
                        print(f"❌ Error en análisis universal: {e}")
                    input("\n✨ Presiona Enter para continuar...")
                else:
                    print("\n❌ Análisis Universal no disponible")
                    print("💡 Instala core/raven_universal.py para habilitarlo")
                    input("\n✨ Presiona Enter para continuar...")
                    
            elif choice == '6':
                show_system_info()
                input("\n✨ Presiona Enter para continuar...")
                
            elif choice == '7':
                print("\n👋 ¡Gracias por usar Raven v2.1 Completo!")
                print("🦅 Sistema de análisis fractal con máximas capacidades")
                print("🔧 Aprendizaje gratuito + Entrenamiento AI disponibles")
                break
                
            else:
                print("❌ Opción no válida. Selecciona 1-7.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Salida interrumpida por el usuario")
            break
        except Exception as e:
            print(f"\n❌ Error inesperado: {e}")
            import traceback
            traceback.print_exc()
            input("✨ Presiona Enter para continuar...")

# *** INICIALIZAR VARIABLE GLOBAL ***
AI_RUNTIME_AVAILABLE = False

if __name__ == "__main__":
    main()