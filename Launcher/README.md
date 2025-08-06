# UNION - Ecosistema de Fractales Unificado

**UNION** es el launcher unificado que conecta y gestiona todos los componentes del ecosistema de fractales, permitiendo una experiencia integrada y fluida.

## ✨ ¿Qué es UNION?

**UNION** actúa como el centro de control del ecosistema de fractales, proporcionando:

- **Gestión unificada**: Un punto central para acceder a todos los componentes
- **Ejecución directa**: Lanza programas del ecosistema con un clic
- **Monitoreo de estado**: Visualiza qué componentes están disponibles o en desarrollo
- **Interfaz elegante**: Diseño moderno con animaciones suaves
- **Arquitectura polyglot**: Conecta componentes escritos en diferentes lenguajes

## 🌐 Arquitectura del Ecosistema

```
UNION (Centro de Control)
├── FractalCreator (C++) ──────── Base matemática y renderizado
├── Nexo (Rust) ────────────────── Puente de integración seguro  
├── FractalExplorer (Julia) ───── Exploración interactiva y cálculo científico
└── Raven (Python) ──────────── Análisis y visualización
```

## 🛠 Prerrequisitos

### Windows:
- **MinGW-w64** o **Visual Studio 2019+**
- **CMake 3.16+**
- **SFML 2.5+**

### Instalación de SFML:

#### Opción 1: vcpkg (Recomendado)
```bash
# Instalar vcpkg
git clone https://github.com/Microsoft/vcpkg.git
cd vcpkg
./bootstrap-vcpkg.bat

# Instalar SFML
./vcpkg install sfml:x64-windows
```

## 🚀 Compilación y Ejecución

### Windows (Método fácil):
```bash
# Ejecutar el script automático
build.bat
```

### Manual:
```bash
# Crear directorio de build
mkdir build
cd build

# Configurar con CMake
cmake .. -G "MinGW Makefiles" -DCMAKE_BUILD_TYPE=Release

# Compilar
cmake --build . --config Release

# Ejecutar
./UNION.exe
```

## 📁 Estructura del Proyecto

```
UNION/
├── main.cpp              # Código principal de UNION
├── CMakeLists.txt         # Configuración de CMake
├── build.bat             # Script de compilación
├── README.md             # Este archivo
└── build/                # Directorio de compilación
    └── UNION.exe         # Ejecutable principal
```

## 🎮 Uso de UNION

1. **Compilar** usando `build.bat`
2. **Ejecutar** `UNION.exe`
3. **Interactuar** con los componentes:
   - 🟢 **Disponible**: Ejecuta directamente
   - 🟠 **En desarrollo**: Muestra información de progreso

### Componentes gestionados:

| Componente | Lenguaje | Estado | Función Principal |
|------------|----------|---------|-------------------|
| **FractalCreator** | C++ | ✅ Disponible | Base matemática y renderizado de alto rendimiento |
| **Nexo** | Rust | 🚧 En desarrollo | Puente de integración seguro con FFI |
| **FractalExplorer** | Julia | 🚧 En desarrollo | Exploración y cálculo científico avanzado |
| **Raven** | Python | 🚧 Planificado | Análisis de datos y visualización |

### Flujo de datos del ecosistema:

```
FractalCreator (C++) 
        ↓ (renderizado base)
    Nexo (Rust) 
        ↓ (integración segura)
FractalExplorer (Julia)
        ↓ (cálculos científicos)
    Raven (Python)
        ↓ (análisis y visualización)
```

## ⚙️ Configuración

### Personalizar rutas de ejecutables:
En `main.cpp`, modifica las rutas según tu configuración:
```cpp
// Línea ~185
"./FractalMutator.exe"  // Cambia por tu ruta
```

### Personalizar interfaz:
- **Colores**: Modifica valores RGB en las clases
- **Posiciones**: Ajusta coordenadas en `setupUI()`
- **Textos**: Cambia strings en los constructores

## 🎯 Filosofía de UNION

**UNION** representa la unificación de diferentes tecnologías y enfoques:

- **C++**: Potencia y control de bajo nivel
- **Go**: Simplicidad y concurrencia
- **Rust**: Seguridad y rendimiento
- **Python**: Flexibilidad y análisis

Todos trabajando juntos en un ecosistema cohesivo.

## 🔧 Dependencias por Componente

### UNION (Launcher):
- **SFML 2.5+**: Graphics, Window, System
- **Windows API**: Shell32, User32 (ejecución de programas)
- **C++17**: Estándar mínimo requerido

### Ecosistema completo (futuro):
- **Rust**: cargo, rustc 1.70+
- **Julia**: 1.9+, PackageCompiler.jl para binarios
- **Python**: 3.10+, NumPy, Matplotlib, PyQt/Tkinter

## 🐛 Solución de Problemas

### "No se pudo cargar la fuente"
```cpp
// Cambiar en main.cpp si es necesario
font.loadFromFile("C:/Windows/Fonts/arial.ttf")
```

### "SFML no encontrado"
```bash
# Usar vcpkg para instalación automática
vcpkg install sfml:x64-windows
```

### "No se puede ejecutar componentes"
- Verifica rutas de ejecutables
- Comprueba permisos
- Asegúrate de que los archivos existen

## 🚀 Roadmap

### Desarrollo evolutivo del ecosistema:

- [x] **v1.0**: UNION launcher con FractalCreator (C++)
- [ ] **v1.1**: Integración con Nexo (Rust) - FFI bridges
- [ ] **v1.2**: Soporte para FractalExplorer (Julia) - Cálculos científicos
- [ ] **v1.3**: Conexión con Raven (Python) - Análisis y visualización
- [ ] **v2.0**: Sistema de plugins dinámico multilenguaje
- [ ] **v2.1**: API unificada para intercambio de datos
- [ ] **v3.0**: Interfaz web con WebAssembly (Rust) + Observable (JS)

## 📝 Licencia

UNION es parte del ecosistema de fractales y mantiene coherencia con las licencias del proyecto principal.

## 🤝 Contribución

UNION es el punto de entrada al ecosistema. Las contribuciones son bienvenidas:

1. Fork del proyecto
2. Crear rama: `git checkout -b feature/union-feature`
3. Commit: `git commit -m 'Add UNION feature'`
4. Push: `git push origin feature/union-feature`
5. Pull Request

---

**UNION: Donde la matemática, el arte y la tecnología se encuentran en perfecta armonía. 🌀**