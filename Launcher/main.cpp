#include <SFML/Graphics.hpp>
#include <iostream>
#include <vector>
#include <string>
#include <cmath>
#include <windows.h>
#include <shellapi.h>
#include <locale>

class ComponentButton {
public:
    sf::RectangleShape shape;
    sf::Text title;
    sf::Text subtitle;
    sf::Text lang;
    sf::Text status;
    sf::RectangleShape statusBadge;
    std::string executablePath;
    bool isExecutable;
    bool isHovered;
    float animationTime;
    
    ComponentButton(sf::Vector2f pos, sf::Vector2f size, std::string titleStr, 
                   std::string subtitleStr, std::string langStr, std::string statusStr,
                   std::string execPath, bool executable) 
        : executablePath(execPath), isExecutable(executable), isHovered(false), animationTime(0.0f) {
        
        // Evitar warnings de parámetros no usados
        (void)titleStr; (void)subtitleStr; (void)langStr; (void)statusStr;
        
        // Configurar forma principal
        shape.setPosition(pos);
        shape.setSize(size);
        shape.setFillColor(sf::Color(45, 45, 55));
        shape.setOutlineThickness(2);
        shape.setOutlineColor(sf::Color(70, 70, 85));
        
        // Badge de estado
        statusBadge.setSize(sf::Vector2f(80, 20));
        statusBadge.setPosition(pos.x + size.x - 85, pos.y + 5);
        
        // Color del badge según estado
        if (statusStr == "Disponible") {
            statusBadge.setFillColor(sf::Color(46, 204, 113)); // Verde
        } else {
            statusBadge.setFillColor(sf::Color(230, 126, 34)); // Naranja
        }
    }
    
    void setupTexts(sf::Font& font) {
        // Título principal
        title.setFont(font);
        title.setString(executablePath.find("FractalCreator") != std::string::npos ? "FractalCreator" :
                       executablePath.find("nexo") != std::string::npos ? "Nexo" :
                       executablePath.find("main.jl") != std::string::npos ? "FractalExplorer" :
                       executablePath.find("Raven") != std::string::npos ? "Raven" : "Componente");
        title.setCharacterSize(18);
        title.setFillColor(sf::Color::White);
        title.setPosition(shape.getPosition().x + 15, shape.getPosition().y + 15);
        
        // Subtítulo/descripción
        subtitle.setFont(font);
        if (executablePath.find("FractalCreator") != std::string::npos) {
            subtitle.setString("Base matematica y renderizado");
        } else if (executablePath.find("nexo") != std::string::npos) {
            subtitle.setString("Puente de integracion");
        } else if (executablePath.find("main.jl") != std::string::npos) {
            subtitle.setString("Visualizacion y exportacion");
        } else if (executablePath.find("Raven") != std::string::npos) {
            subtitle.setString("Analisis avanzado con IA");
        } else {
            subtitle.setString("Componente del ecosistema");
        }
        subtitle.setCharacterSize(12);
        subtitle.setFillColor(sf::Color(180, 180, 190));
        subtitle.setPosition(shape.getPosition().x + 15, shape.getPosition().y + 45);
        
        // Lenguaje
        lang.setFont(font);
        if (executablePath.find("FractalCreator") != std::string::npos) {
            lang.setString("C++");
        } else if (executablePath.find("nexo") != std::string::npos) {
            lang.setString("Rust");
        } else if (executablePath.find("main.jl") != std::string::npos) {
            lang.setString("Julia");
        } else if (executablePath.find("Raven") != std::string::npos) {
            lang.setString("Python");
        } else {
            lang.setString("Unknown");
        }
        lang.setCharacterSize(14);
        lang.setFillColor(sf::Color(100, 149, 237));
        lang.setPosition(shape.getPosition().x + 15, shape.getPosition().y + 75);
        
        // Status
        status.setFont(font);
        status.setString(isExecutable ? "Disponible" : "En desarrollo");
        status.setCharacterSize(10);
        status.setFillColor(sf::Color::White);
        
        // Centrar texto en badge
        sf::FloatRect statusBounds = status.getLocalBounds();
        sf::Vector2f badgePos = statusBadge.getPosition();
        sf::Vector2f badgeSize = statusBadge.getSize();
        status.setPosition(
            badgePos.x + (badgeSize.x - statusBounds.width) / 2,
            badgePos.y + (badgeSize.y - statusBounds.height) / 2 - 2
        );
    }
    
    void update(float deltaTime) {
        if (isHovered) {
            animationTime += deltaTime * 3.0f;
        } else {
            animationTime -= deltaTime * 3.0f;
        }
        animationTime = std::max(0.0f, std::min(1.0f, animationTime));
        
        // Efecto hover
        float intensity = 45 + (animationTime * 15);
        shape.setFillColor(sf::Color(intensity, intensity, intensity + 10));
        shape.setOutlineColor(sf::Color(70 + animationTime * 30, 70 + animationTime * 30, 85 + animationTime * 40));
    }
    
    bool contains(sf::Vector2f point) {
        return shape.getGlobalBounds().contains(point);
    }
    
    void setHovered(bool hovered) {
        isHovered = hovered;
    }
    
    void draw(sf::RenderWindow& window) {
        window.draw(shape);
        window.draw(statusBadge);
        window.draw(title);
        window.draw(subtitle);
        window.draw(lang);
        window.draw(status);
    }
    
    // Funciones auxiliares para extraer directorio y nombre de archivo
    std::string extractDirectory(const std::string& path) {
        size_t lastSlash = path.find_last_of("/\\");
        if (lastSlash != std::string::npos) {
            return path.substr(0, lastSlash);
        }
        return ".";
    }
    
    std::string extractFileName(const std::string& path) {
        size_t lastSlash = path.find_last_of("/\\");
        if (lastSlash != std::string::npos) {
            return path.substr(lastSlash + 1);
        }
        return path;
    }
    
    bool fileExists(const std::string& path) {
        WIN32_FIND_DATAA findFileData;
        HANDLE hFind = FindFirstFileA(path.c_str(), &findFileData);
        
        if (hFind == INVALID_HANDLE_VALUE) {
            return false;
        }
        
        FindClose(hFind);
        return true;
    }
    
    void execute() {
        if (isExecutable && !executablePath.empty()) {
            // Verificar si el archivo existe
            if (!fileExists(executablePath)) {
                MessageBoxA(NULL, 
                    ("Archivo no encontrado: " + executablePath + "\n\nVerifica que el archivo exista en la ruta correcta.").c_str(),
                    "Archivo No Encontrado", 
                    MB_OK | MB_ICONWARNING);
                return;
            }
            
            // Obtener ruta absoluta del archivo
            char fullPath[MAX_PATH];
            GetFullPathNameA(executablePath.c_str(), MAX_PATH, fullPath, NULL);
            std::string absolutePath(fullPath);
            
            // Determinar el tipo de archivo y comando a ejecutar
            std::string command;
            std::string workingDir = extractDirectory(absolutePath);
            std::string execName = extractFileName(absolutePath);
            
            std::cout << "🚀 Ejecutando: " << absolutePath << std::endl;
            std::cout << "📂 Directorio: " << workingDir << std::endl;
            std::cout << "📄 Archivo: " << execName << std::endl;
            
            // Detectar tipo de archivo
            bool isPythonScript = (executablePath.find(".py") != std::string::npos);
            bool isJuliaScript = (executablePath.find(".jl") != std::string::npos);
            
            if (isPythonScript) {
                // Ejecutar script Python
                command = "python \"" + absolutePath + "\"";
                std::cout << "🐍 Comando Python: " << command << std::endl;
                
                HINSTANCE result = ShellExecuteA(NULL, "open", "cmd.exe", 
                    ("/k " + command).c_str(), 
                    workingDir.c_str(), SW_SHOWNORMAL);
                    
                if (reinterpret_cast<uintptr_t>(result) <= 32) {
                    // Intentar con py
                    command = "py \"" + absolutePath + "\"";
                    result = ShellExecuteA(NULL, "open", "cmd.exe", 
                        ("/k " + command).c_str(), 
                        workingDir.c_str(), SW_SHOWNORMAL);
                }
                
                if (reinterpret_cast<uintptr_t>(result) <= 32) {
                    std::string errorMsg = "No se pudo ejecutar el script Python.\n\n";
                    errorMsg += "Asegurate de tener Python instalado y en el PATH.\n\n";
                    errorMsg += "Archivo: " + absolutePath;
                    MessageBoxA(NULL, errorMsg.c_str(), "Python No Encontrado", MB_OK | MB_ICONERROR);
                } else {
                    std::cout << "✅ Python ejecutado correctamente" << std::endl;
                }
                
            } else if (isJuliaScript) {
                // Ejecutar script Julia
                command = "julia \"" + absolutePath + "\"";
                std::cout << "💜 Comando Julia: " << command << std::endl;
                
                HINSTANCE result = ShellExecuteA(NULL, "open", "cmd.exe", 
                    ("/k " + command).c_str(), 
                    workingDir.c_str(), SW_SHOWNORMAL);
                    
                if (reinterpret_cast<uintptr_t>(result) <= 32) {
                    std::string errorMsg = "No se pudo ejecutar el script Julia.\n\n";
                    errorMsg += "Asegurate de tener Julia instalado y en el PATH.\n\n";
                    errorMsg += "O ejecuta manualmente:\n";
                    errorMsg += "1. Abre cmd en: " + workingDir + "\n";
                    errorMsg += "2. Ejecuta: julia " + execName;
                    MessageBoxA(NULL, errorMsg.c_str(), "Julia No Encontrado", MB_OK | MB_ICONERROR);
                } else {
                    std::cout << "✅ Julia ejecutado correctamente" << std::endl;
                }
                
            } else {
                // Ejecutar ejecutable normal (C++, Rust, etc.)
                std::cout << "🎯 Ejecutando ejecutable: " << absolutePath << std::endl;
                
                HINSTANCE result = ShellExecuteA(NULL, "open", absolutePath.c_str(), 
                    NULL, workingDir.c_str(), SW_SHOWNORMAL);
                
                if (reinterpret_cast<uintptr_t>(result) <= 32) {
                    uintptr_t errorCode = reinterpret_cast<uintptr_t>(result);
                    std::string errorMsg = "Error ejecutando el archivo.\nCodigo de error: " + std::to_string(errorCode) + "\n\n";
                    
                    if (errorCode == 2) {
                        errorMsg += "Archivo no encontrado.";
                    } else if (errorCode == 3) {
                        errorMsg += "Ruta no encontrada.";
                    } else if (errorCode == 5) {
                        errorMsg += "Acceso denegado.";
                    } else if (errorCode == 8) {
                        errorMsg += "Memoria insuficiente.";
                    } else if (errorCode == 31) {
                        errorMsg += "No hay aplicacion asociada.";
                    } else {
                        errorMsg += "Error desconocido.";
                    }
                    
                    errorMsg += "\n\nRuta completa: " + absolutePath;
                    errorMsg += "\nDirectorio: " + workingDir;
                    errorMsg += "\n\nIntenta ejecutar manualmente desde: " + workingDir;
                    
                    MessageBoxA(NULL, errorMsg.c_str(), "Error de Ejecucion", MB_OK | MB_ICONERROR);
                } else {
                    std::cout << "✅ Ejecutable lanzado correctamente" << std::endl;
                }
            }
        } else {
            // Componente en desarrollo
            std::string errorMsg = "El componente esta en desarrollo.\n\nPronto estara disponible!";
            MessageBoxA(NULL, 
                errorMsg.c_str(),
                "Componente en Desarrollo", 
                MB_OK | MB_ICONINFORMATION);
        }
    }
};

class UNION {
private:
    sf::RenderWindow window;
    sf::Font font;
    std::vector<ComponentButton> components;
    sf::Text title;
    sf::Text subtitle;
    sf::Clock clock;
    
public:
    UNION() : window(sf::VideoMode(720, 600), "UNION - Ecosistema de Fractales", sf::Style::Titlebar | sf::Style::Close) {
        window.setFramerateLimit(60);
        
        if (!font.loadFromFile("C:/Windows/Fonts/arial.ttf")) {
            std::cout << "⚠️ No se pudo cargar la fuente, usando fuente por defecto" << std::endl;
        }
        
        setupUI();
    }
    
    std::string findFractalCreatorExecutable() {
        std::vector<std::string> possiblePaths = {
            "../FractalCreator/build/Release/FractalMutator.exe",
            "../FractalCreator/build/Debug/FractalMutator.exe",
            "FractalCreator/build/Release/FractalMutator.exe",
            "../FractalCreator/FractalMutator.exe",
            "FractalMutator.exe",
            "../FractalCreator.exe",
            "FractalCreator.exe",
            // Rutas adicionales basadas en tu estructura
            "../../FractalCreator/build/Release/FractalMutator.exe",
            "../../../FractalCreator/build/Release/FractalMutator.exe"
        };
        
        std::cout << "🔍 Buscando FractalCreator..." << std::endl;
        
        // Mostrar directorio actual para debug
        char currentDir[MAX_PATH];
        GetCurrentDirectoryA(MAX_PATH, currentDir);
        std::cout << "📂 Directorio actual: " << currentDir << std::endl;
        
        for (const auto& path : possiblePaths) {
            std::cout << "   Probando: " << path << std::endl;
            
            WIN32_FIND_DATAA findFileData;
            HANDLE hFind = FindFirstFileA(path.c_str(), &findFileData);
            
            if (hFind != INVALID_HANDLE_VALUE) {
                FindClose(hFind);
                std::cout << "✅ FractalCreator encontrado: " << path << std::endl;
                return path;
            }
        }
        
        std::cout << "❌ FractalCreator no encontrado en ninguna ruta" << std::endl;
        
        // Listar archivos en directorios comunes para debug
        std::cout << "📋 Archivos en ../:" << std::endl;
        WIN32_FIND_DATAA findFileData;
        HANDLE hFind = FindFirstFileA("../*", &findFileData);
        if (hFind != INVALID_HANDLE_VALUE) {
            do {
                if (findFileData.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) {
                    std::cout << "   📁 " << findFileData.cFileName << std::endl;
                } else {
                    std::cout << "   📄 " << findFileData.cFileName << std::endl;
                }
            } while (FindNextFileA(hFind, &findFileData) != 0);
            FindClose(hFind);
        }
        
        return "";
    }
    
    std::string findNexoExecutable() {
        std::vector<std::string> possiblePaths = {
            "../nexo-rust/target/release/nexo.exe",
            "../nexo-rust/target/debug/nexo.exe",
            "nexo-rust/target/release/nexo.exe",
            "../nexo/target/release/nexo.exe",
            "nexo.exe"
        };
        
        std::cout << "🔍 Buscando Nexo..." << std::endl;
        
        for (const auto& path : possiblePaths) {
            WIN32_FIND_DATAA findFileData;
            HANDLE hFind = FindFirstFileA(path.c_str(), &findFileData);
            
            if (hFind != INVALID_HANDLE_VALUE) {
                FindClose(hFind);
                std::cout << "✅ Nexo encontrado: " << path << std::endl;
                return path;
            }
        }
        
        std::cout << "❌ Nexo no encontrado" << std::endl;
        return "";
    }
    
    std::string findFractalExplorerExecutable() {
        std::vector<std::string> possiblePaths = {
            "../FractalExplorer/main.jl",
            "FractalExplorer/main.jl",
            "../FractalExplorer/FractalExplorer.exe",
            "FractalExplorer/FractalExplorer.exe",
            // Rutas adicionales
            "../../FractalExplorer/main.jl",
            "../../../FractalExplorer/main.jl"
        };
        
        std::cout << "🔍 Buscando FractalExplorer..." << std::endl;
        
        for (const auto& path : possiblePaths) {
            std::cout << "   Probando: " << path << std::endl;
            
            WIN32_FIND_DATAA findFileData;
            HANDLE hFind = FindFirstFileA(path.c_str(), &findFileData);
            
            if (hFind != INVALID_HANDLE_VALUE) {
                FindClose(hFind);
                std::cout << "✅ FractalExplorer encontrado: " << path << std::endl;
                return path;
            }
        }
        
        std::cout << "❌ FractalExplorer no encontrado" << std::endl;
        return "";
    }
    
    std::string findRavenExecutable() {
        std::vector<std::string> possiblePaths = {
            "../Raven/Raven/Raven.exe",
            "../Raven/Raven/main.py",
            "../Raven/Raven.exe",
            "../Raven/main.py",
            "Raven/Raven.exe",
            "Raven/main.py"
        };
        
        std::cout << "🔍 Buscando Raven..." << std::endl;
        
        for (const auto& path : possiblePaths) {
            WIN32_FIND_DATAA findFileData;
            HANDLE hFind = FindFirstFileA(path.c_str(), &findFileData);
            
            if (hFind != INVALID_HANDLE_VALUE) {
                FindClose(hFind);
                std::cout << "✅ Raven encontrado: " << path << std::endl;
                return path;
            }
        }
        
        std::cout << "❌ Raven no encontrado" << std::endl;
        return "";
    }
    
    void setupUI() {
        // Buscar todos los ejecutables
        std::string fractalCreatorPath = findFractalCreatorExecutable();
        bool fractalCreatorExists = !fractalCreatorPath.empty();
        
        std::string nexoExecutablePath = findNexoExecutable();
        bool nexoExists = !nexoExecutablePath.empty();
        
        std::string fractalExplorerPath = findFractalExplorerExecutable();
        bool fractalExplorerExists = !fractalExplorerPath.empty();
        
        std::string ravenExecutablePath = findRavenExecutable();
        bool ravenExists = !ravenExecutablePath.empty();

        // Crear componentes con roles corregidos
        components.clear();
        
        // FractalCreator - Genera fractales base
        components.push_back(ComponentButton(
            sf::Vector2f(80, 140), sf::Vector2f(240, 140),
            "FractalCreator", "Base matematica y renderizado", "C++",
            fractalCreatorExists ? "Disponible" : "En desarrollo", 
            fractalCreatorPath, fractalCreatorExists
        ));
        
        // Nexo - Coordina componentes
        components.push_back(ComponentButton(
            sf::Vector2f(380, 140), sf::Vector2f(240, 140),
            "Nexo", "Puente de integracion", "Rust",
            nexoExists ? "Disponible" : "En desarrollo", 
            nexoExecutablePath, nexoExists
        ));
        
        // Raven - Análisis con IA
        components.push_back(ComponentButton(
            sf::Vector2f(80, 380), sf::Vector2f(240, 140),
            "Raven", "Analisis avanzado con IA", "Python",
            ravenExists ? "Disponible" : "En desarrollo", 
            ravenExecutablePath, ravenExists
        ));
        
        // FractalExplorer - Visualización y exportación
        components.push_back(ComponentButton(
            sf::Vector2f(380, 380), sf::Vector2f(240, 140),
            "FractalExplorer", "Visualizacion y exportacion", "Julia",
            fractalExplorerExists ? "Disponible" : "En desarrollo", 
            fractalExplorerPath, fractalExplorerExists
        ));
        
        // Configurar textos de cada componente
        for (auto& component : components) {
            component.setupTexts(font);
        }
        
        // Título principal
        title.setFont(font);
        title.setString("UNION - Ecosistema de Fractales");
        title.setCharacterSize(24);
        title.setFillColor(sf::Color::White);
        title.setPosition(50, 30);
        
        // Subtítulo
        subtitle.setFont(font);
        subtitle.setString("Selecciona un componente para ejecutar");
        subtitle.setCharacterSize(14);
        subtitle.setFillColor(sf::Color(150, 150, 150));
        subtitle.setPosition(50, 65);
        
        // Estado de componentes
        std::cout << "📊 Estado del ecosistema:" << std::endl;
        std::cout << "  🔧 FractalCreator: " << (fractalCreatorExists ? "✅ Disponible" : "❌ No encontrado") << std::endl;
        std::cout << "  🦀 Nexo: " << (nexoExists ? "✅ Disponible" : "❌ No encontrado") << std::endl;
        std::cout << "  🐍 Raven: " << (ravenExists ? "✅ Disponible" : "❌ No encontrado") << std::endl;
        std::cout << "  💜 FractalExplorer: " << (fractalExplorerExists ? "✅ Disponible" : "❌ No encontrado") << std::endl;
    }
    
    void run() {
        while (window.isOpen()) {
            handleEvents();
            update();
            render();
        }
    }
    
private:
    void handleEvents() {
        sf::Event event;
        while (window.pollEvent(event)) {
            if (event.type == sf::Event::Closed) {
                window.close();
            }
            
            if (event.type == sf::Event::MouseButtonPressed) {
                if (event.mouseButton.button == sf::Mouse::Left) {
                    sf::Vector2f mousePos(event.mouseButton.x, event.mouseButton.y);
                    
                    for (auto& component : components) {
                        if (component.contains(mousePos)) {
                            component.execute();
                            break;
                        }
                    }
                }
            }
            
            if (event.type == sf::Event::MouseMoved) {
                sf::Vector2f mousePos(event.mouseMove.x, event.mouseMove.y);
                
                for (auto& component : components) {
                    component.setHovered(component.contains(mousePos));
                }
            }
        }
    }
    
    void update() {
        float deltaTime = clock.restart().asSeconds();
        
        for (auto& component : components) {
            component.update(deltaTime);
        }
    }
    
    void render() {
        window.clear(sf::Color(25, 25, 35));
        
        window.draw(title);
        window.draw(subtitle);
        
        for (auto& component : components) {
            component.draw(window);
        }
        
        window.display();
    }
};

int main() {
    std::cout << "🚀 INICIANDO ECOSISTEMA UNION..." << std::endl;
    std::cout << "====================================" << std::endl;
    
    // Crear directorio shared dentro de FractalExplorer para exportación
    std::string sharedDir = "../FractalExplorer/shared";
    if (!CreateDirectoryA(sharedDir.c_str(), NULL)) {
        if (GetLastError() != ERROR_ALREADY_EXISTS) {
            std::cout << "⚠️  No se pudo crear directorio compartido: " << sharedDir << std::endl;
        } else {
            std::cout << "📁 Directorio compartido ya existe: " << sharedDir << std::endl;
        }
    } else {
        std::cout << "📁 Directorio compartido creado: " << sharedDir << std::endl;
    }
    
    // Configurar consola para UTF-8
    SetConsoleOutputCP(CP_UTF8);
    
    UNION app;
    app.run();
    
    return 0;
}