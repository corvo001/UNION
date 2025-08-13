import os
from datetime import datetime
import logging

# Configurar logging
logger = logging.getLogger(__name__)

class FolderAnalyzer:
    @staticmethod
    def _get_project_root():
        """
        Obtiene la ruta raíz del proyecto Raven, independientemente de desde dónde se ejecute
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Si estamos en la carpeta 'core', subir un nivel
        if os.path.basename(current_dir) == 'core':
            return os.path.dirname(current_dir)
        
        # Si ya estamos en la raíz del proyecto
        return current_dir
    
    @staticmethod
    def _resolve_data_path(base_path=None):
        """
        Resuelve la ruta correcta a la carpeta 'data'
        """
        if base_path is None:
            # Usar ruta relativa al proyecto
            project_root = FolderAnalyzer._get_project_root()
            data_path = os.path.join(project_root, 'data')
        else:
            # Usar ruta proporcionada
            if os.path.isabs(base_path):
                data_path = base_path
            else:
                project_root = FolderAnalyzer._get_project_root()
                data_path = os.path.join(project_root, base_path)
        
        logger.info(f"🎯 Ruta de datos resuelta: {data_path}")
        return data_path

    @staticmethod
    def get_todays_folder(base_path=None):
        """
        Identifica la carpeta con la fecha de hoy en formato DDMMYYYY
        
        Args:
            base_path: Ruta base donde buscar (None para autodetectar)
            
        Returns:
            str: Ruta completa a la carpeta de hoy, o None si no existe
        """
        try:
            # Resolver ruta correcta
            data_path = FolderAnalyzer._resolve_data_path(base_path)
            
            today = datetime.now().strftime("%d%m%Y")  # Formato: 27072025
            logger.info(f"🔍 Buscando carpeta para la fecha: {today}")
            
            today_path = os.path.join(data_path, 'today')  # Ruta a la carpeta 'today'
            
            # Verificar si existe la carpeta 'today'
            if not os.path.exists(today_path):
                logger.error(f"❌ No existe la carpeta '{today_path}'")
                logger.info(f"📁 Verificando estructura en: {data_path}")
                
                # Listar contenido del directorio base para debug
                if os.path.exists(data_path):
                    items = os.listdir(data_path)
                    logger.info(f"📂 Contenido de '{data_path}': {items}")
                else:
                    logger.error(f"❌ El directorio base '{data_path}' no existe")
                
                return None
            
            # Listar todas las carpetas en 'today' para debug
            logger.info("📁 Carpetas en 'today':")
            try:
                folders = os.listdir(today_path)
                for folder in folders:
                    folder_full_path = os.path.join(today_path, folder)
                    if os.path.isdir(folder_full_path):
                        logger.info(f"  📂 {folder}")
                    else:
                        logger.info(f"  📄 {folder} (archivo)")
                
                # Verificar si existe la carpeta de hoy
                today_folder_path = os.path.join(today_path, today)
                if os.path.exists(today_folder_path) and os.path.isdir(today_folder_path):
                    logger.info(f"✅ Carpeta de hoy encontrada: {today_folder_path}")
                    
                    # Verificar contenido de la carpeta del día
                    try:
                        content = os.listdir(today_folder_path)
                        logger.info(f"📋 Contenido de la carpeta del día ({len(content)} elementos):")
                        for item in content[:10]:  # Mostrar máximo 10 elementos
                            logger.info(f"  • {item}")
                        if len(content) > 10:
                            logger.info(f"  ... y {len(content) - 10} elementos más")
                    except Exception as e:
                        logger.warning(f"⚠️ No se pudo listar el contenido: {e}")
                    
                    return today_folder_path
                else:
                    logger.warning(f"❌ No se encontró la carpeta de hoy: {today}")
                    logger.info(f"💡 Sugerencia: Crear la carpeta '{today_folder_path}'")
                    return None
                    
            except Exception as e:
                logger.error(f"❌ Error listando carpetas en '{today_path}': {e}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error general en get_todays_folder: {e}")
            return None
    
    @staticmethod
    def create_todays_folder(base_path=None):
        """
        Crea la carpeta del día actual si no existe
        
        Args:
            base_path: Ruta base donde crear (None para autodetectar)
            
        Returns:
            str: Ruta a la carpeta creada, o None si hubo error
        """
        try:
            data_path = FolderAnalyzer._resolve_data_path(base_path)
            today = datetime.now().strftime("%d%m%Y")
            today_path = os.path.join(data_path, 'today')
            today_folder_path = os.path.join(today_path, today)
            
            # Crear estructura completa si no existe
            os.makedirs(today_folder_path, exist_ok=True)
            
            logger.info(f"✅ Carpeta creada/verificada: {today_folder_path}")
            return today_folder_path
            
        except Exception as e:
            logger.error(f"❌ Error creando carpeta del día: {e}")
            return None
    
    @staticmethod
    def get_or_create_todays_folder(base_path=None):
        """
        Obtiene la carpeta del día, creándola si no existe
        
        Args:
            base_path: Ruta base (None para autodetectar)
            
        Returns:
            str: Ruta a la carpeta del día
        """
        # Intentar obtener carpeta existente
        folder_path = FolderAnalyzer.get_todays_folder(base_path)
        
        if folder_path is None:
            logger.info("🛠️ Carpeta no encontrada, intentando crear...")
            folder_path = FolderAnalyzer.create_todays_folder(base_path)
        
        return folder_path
    
    @staticmethod
    def list_available_dates(base_path=None):
        """
        Lista todas las fechas disponibles en la carpeta 'today'
        
        Args:
            base_path: Ruta base (None para autodetectar)
            
        Returns:
            list: Lista de fechas disponibles
        """
        try:
            data_path = FolderAnalyzer._resolve_data_path(base_path)
            today_path = os.path.join(data_path, 'today')
            
            if not os.path.exists(today_path):
                return []
            
            items = os.listdir(today_path)
            dates = []
            
            for item in items:
                item_path = os.path.join(today_path, item)
                if os.path.isdir(item_path) and len(item) == 8 and item.isdigit():
                    # Formato DDMMYYYY
                    try:
                        # Validar que sea una fecha válida
                        datetime.strptime(item, "%d%m%Y")
                        dates.append(item)
                    except ValueError:
                        continue
            
            dates.sort(reverse=True)  # Más recientes primero
            return dates
            
        except Exception as e:
            logger.error(f"❌ Error listando fechas disponibles: {e}")
            return []
    
    @staticmethod
    def get_folder_stats(folder_path):
        """
        Obtiene estadísticas de una carpeta
        
        Args:
            folder_path: Ruta a la carpeta
            
        Returns:
            dict: Estadísticas de la carpeta
        """
        try:
            if not os.path.exists(folder_path):
                return {"error": "Carpeta no existe"}
            
            items = os.listdir(folder_path)
            
            stats = {
                "total_items": len(items),
                "files": 0,
                "directories": 0,
                "total_size": 0,
                "file_types": {}
            }
            
            for item in items:
                item_path = os.path.join(folder_path, item)
                
                if os.path.isfile(item_path):
                    stats["files"] += 1
                    
                    # Tamaño del archivo
                    try:
                        size = os.path.getsize(item_path)
                        stats["total_size"] += size
                    except:
                        pass
                    
                    # Tipo de archivo
                    ext = os.path.splitext(item)[1].lower()
                    if ext:
                        stats["file_types"][ext] = stats["file_types"].get(ext, 0) + 1
                    
                elif os.path.isdir(item_path):
                    stats["directories"] += 1
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo estadísticas: {e}")
            return {"error": str(e)}


# Función de utilidad para uso directo
def analyze_folder_structure(base_path=None):
    """
    Analiza la estructura completa de carpetas
    
    Args:
        base_path: Ruta base a analizar (None para autodetectar)
    """
    print(f"\n🔍 ANÁLISIS DE ESTRUCTURA DE CARPETAS - RAVEN 0.3/0.4")
    
    # Mostrar información de rutas
    project_root = FolderAnalyzer._get_project_root()
    resolved_path = FolderAnalyzer._resolve_data_path(base_path)
    
    print(f"📁 Directorio actual: {os.getcwd()}")
    print(f"🎯 Raíz del proyecto: {project_root}")
    print(f"📂 Ruta de datos: {resolved_path}")
    print("=" * 70)
    
    # Verificar carpeta del día
    today_folder = FolderAnalyzer.get_todays_folder(base_path)
    if today_folder:
        print(f"✅ Carpeta del día encontrada: {today_folder}")
        
        # Estadísticas
        stats = FolderAnalyzer.get_folder_stats(today_folder)
        if "error" not in stats:
            print(f"📊 Elementos totales: {stats['total_items']}")
            print(f"📄 Archivos: {stats['files']}")
            print(f"📁 Directorios: {stats['directories']}")
            print(f"💾 Tamaño total: {stats['total_size']:,} bytes")
            
            if stats['file_types']:
                print("📋 Tipos de archivo:")
                for ext, count in sorted(stats['file_types'].items()):
                    print(f"  {ext}: {count}")
    else:
        print("❌ No se encontró carpeta del día")
        
        # Intentar crear
        created_folder = FolderAnalyzer.create_todays_folder(base_path)
        if created_folder:
            print(f"✅ Carpeta creada: {created_folder}")
    
    # Listar fechas disponibles
    available_dates = FolderAnalyzer.list_available_dates(base_path)
    if available_dates:
        print(f"\n📅 Fechas disponibles ({len(available_dates)}):")
        for date in available_dates[:5]:  # Mostrar últimas 5
            formatted_date = f"{date[0:2]}/{date[2:4]}/{date[4:8]}"
            print(f"  • {date} ({formatted_date})")
        if len(available_dates) > 5:
            print(f"  ... y {len(available_dates) - 5} fechas más")
    else:
        print("\n📅 No hay fechas disponibles")


def test_from_anywhere():
    """
    Función de test que funciona desde cualquier ubicación
    """
    print("🚀 RAVEN FOLDER ANALYZER - TEST DESDE CUALQUIER UBICACIÓN")
    print("=" * 60)
    
    try:
        # Test con autodetección de rutas
        analyze_folder_structure()
        
        print(f"\n{'='*60}")
        print("✅ TEST COMPLETADO EXITOSAMENTE")
        
        # Mostrar información adicional útil
        today_folder = FolderAnalyzer.get_todays_folder()
        if today_folder:
            print(f"🎯 Carpeta del día: {today_folder}")
            print("💡 Puedes usar esta ruta en tu código Raven")
        else:
            print("💡 Ejecuta FolderAnalyzer.create_todays_folder() para crear la estructura")
        
    except Exception as e:
        print(f"❌ Error en test: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Configurar logging para pruebas
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    # Ejecutar test
    test_from_anywhere()