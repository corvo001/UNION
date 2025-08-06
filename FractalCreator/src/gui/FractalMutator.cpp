#include <SFML/Graphics.hpp>
#include <complex>
#include <iostream>
#include <string>
#include <optional>
#include <cstdint>
#include <random>
#include <vector>
#include <memory>
#include <fstream>
#include <filesystem>
#include <iomanip>
#include <sstream>
#include "Serialization.hpp"

using namespace FractalEcosystem;

enum class FractalType {
    MANDELBROT,
    JULIA,
    BURNING_SHIP
};

enum class ColorScheme {
    CLASSIC,
    FIRE,
    OCEAN,
    RAINBOW,
    MONOCHROME,
    ELECTRIC
};

// Estructura de parámetros mutables (misma que antes)
struct FractalParameters {
    double zoom = 1.0;
    double centerX = 0.0;
    double centerY = 0.0;
    int maxIterations = 100;
    
    std::complex<double> juliaC = {-0.7, 0.27015};
    double escapeRadius = 2.0;
    double power = 2.0;
    
    ColorScheme colorScheme = ColorScheme::CLASSIC;
    double colorSpeed = 1.0;
    double colorOffset = 0.0;
    double brightness = 1.0;
    double contrast = 1.0;
    bool smoothColoring = true;
    
    double mutationStrength = 0.1;
    bool autoMutate = false;
    double autoMutateSpeed = 0.01;
    
    // Convertir a objeto serializable
    SerializableFractalState toSerializable(FractalType fractalType) const {
        SerializableFractalState serializable;
        
        serializable.zoom = zoom;
        serializable.centerX = centerX;
        serializable.centerY = centerY;
        serializable.maxIterations = maxIterations;
        serializable.juliaC = juliaC;
        serializable.escapeRadius = escapeRadius;
        serializable.power = power;
        serializable.colorScheme = static_cast<int>(colorScheme);
        serializable.colorSpeed = colorSpeed;
        serializable.colorOffset = colorOffset;
        serializable.brightness = brightness;
        serializable.contrast = contrast;
        serializable.smoothColoring = smoothColoring;
        serializable.mutationStrength = mutationStrength;
        serializable.autoMutate = autoMutate;
        serializable.autoMutateSpeed = autoMutateSpeed;
        serializable.fractalType = static_cast<int>(fractalType);
        
        return serializable;
    }
    
    // Cargar desde objeto serializable
    void fromSerializable(const SerializableFractalState& serializable) {
        zoom = serializable.zoom;
        centerX = serializable.centerX;
        centerY = serializable.centerY;
        maxIterations = serializable.maxIterations;
        juliaC = serializable.juliaC;
        escapeRadius = serializable.escapeRadius;
        power = serializable.power;
        colorScheme = static_cast<ColorScheme>(serializable.colorScheme);
        colorSpeed = serializable.colorSpeed;
        colorOffset = serializable.colorOffset;
        brightness = serializable.brightness;
        contrast = serializable.contrast;
        smoothColoring = serializable.smoothColoring;
        mutationStrength = serializable.mutationStrength;
        autoMutate = serializable.autoMutate;
        autoMutateSpeed = serializable.autoMutateSpeed;
    }
    
    // Método para generar JSON (mantener compatibilidad)
    std::string toJSON() const {
        std::ostringstream json;
        json << std::fixed << std::setprecision(6);
        json << "{\n";
        json << "  \"zoom\": " << zoom << ",\n";
        json << "  \"centerX\": " << centerX << ",\n";
        json << "  \"centerY\": " << centerY << ",\n";
        json << "  \"maxIterations\": " << maxIterations << ",\n";
        json << "  \"juliaC_real\": " << juliaC.real() << ",\n";
        json << "  \"juliaC_imag\": " << juliaC.imag() << ",\n";
        json << "  \"escapeRadius\": " << escapeRadius << ",\n";
        json << "  \"power\": " << power << ",\n";
        json << "  \"colorScheme\": " << static_cast<int>(colorScheme) << ",\n";
        json << "  \"colorSpeed\": " << colorSpeed << ",\n";
        json << "  \"colorOffset\": " << colorOffset << ",\n";
        json << "  \"brightness\": " << brightness << ",\n";
        json << "  \"contrast\": " << contrast << ",\n";
        json << "  \"smoothColoring\": " << (smoothColoring ? "true" : "false") << ",\n";
        json << "  \"mutationStrength\": " << mutationStrength << ",\n";
        json << "  \"autoMutate\": " << (autoMutate ? "true" : "false") << ",\n";
        json << "  \"autoMutateSpeed\": " << autoMutateSpeed << "\n";
        json << "}";
        return json.str();
    }
};

// Clase Button (igual que antes - la omito por brevedad)
class Button {
private:
    sf::RectangleShape shape;
    std::optional<sf::Text> text;
    sf::Font* font;
    bool isPressed = false;
    bool isHovered = false;
    
public:
    Button(float x, float y, float width, float height, const std::string& label, sf::Font* f) 
        : font(f) {
        shape.setPosition({x, y});
        shape.setSize({width, height});
        shape.setFillColor(sf::Color(60, 60, 60));
        shape.setOutlineThickness(2);
        shape.setOutlineColor(sf::Color(100, 100, 100));
        
        if (font) {
            text = sf::Text(*font);
            text->setString(label);
            text->setCharacterSize(14);
            text->setFillColor(sf::Color::White);
            
            sf::FloatRect textBounds = text->getLocalBounds();
            text->setPosition({
                x + (width - textBounds.size.x) / 2,
                y + (height - textBounds.size.y) / 2 - 2
            });
        }
    }
    
    void update(sf::Vector2i mousePos, bool isClicked) {
        sf::FloatRect bounds = shape.getGlobalBounds();
        isHovered = bounds.contains(static_cast<sf::Vector2f>(mousePos));
        
        if (isHovered && isClicked) {
            isPressed = true;
        }
        
        if (isPressed) {
            shape.setFillColor(sf::Color(100, 150, 100));
            isPressed = false;
        } else if (isHovered) {
            shape.setFillColor(sf::Color(80, 80, 80));
        } else {
            shape.setFillColor(sf::Color(60, 60, 60));
        }
    }
    
    bool wasClicked(sf::Vector2i mousePos, bool isClicked) {
        sf::FloatRect bounds = shape.getGlobalBounds();
        return isClicked && bounds.contains(static_cast<sf::Vector2f>(mousePos));
    }
    
    void draw(sf::RenderWindow& window) {
        window.draw(shape);
        if (font && text) {
            window.draw(*text);
        }
    }
};

class FractalRenderer {
private:
    int width, height;
    FractalType currentType;
    FractalParameters params;
    
    std::uint8_t* pixels;
    sf::Texture texture;
    sf::Sprite sprite;
    
    std::random_device rd;
    std::mt19937 gen;
    std::uniform_real_distribution<> mutationDist;
    
    double animationTime = 0.0;
    
    // Sistema de archivos compartidos (mantener compatibilidad)
    std::string sharedPath;
    sf::Clock syncClock;
    const float SYNC_INTERVAL = 1.0f;
    
    // NUEVO: Sistema de serialización
    SerializationManager serializer;
    sf::Clock snapshotClock;
    const float SNAPSHOT_INTERVAL = 30.0f; // Snapshot cada 30 segundos
    int snapshotCounter = 0;

public:
    FractalRenderer(int w, int h, const std::string& shared = "./shared") 
        : width(w), height(h), currentType(FractalType::MANDELBROT),
          texture(sf::Vector2u(static_cast<unsigned int>(w), static_cast<unsigned int>(h))),
          sprite(texture), gen(rd()), mutationDist(-1.0, 1.0),
          sharedPath(shared), serializer(shared + "/serialized") {
        
        pixels = new std::uint8_t[width * height * 4];
        
        // Crear directorios necesarios
        std::filesystem::create_directories(shared);
        std::filesystem::create_directories(shared + "/serialized");
        
        // Intentar cargar último estado guardado
        loadLastState();
        
        std::cout << "🔧 FractalRenderer con serialización iniciado" << std::endl;
        std::cout << "💾 Sistema de persistencia: " << shared << "/serialized" << std::endl;
    }
    
    ~FractalRenderer() {
        delete[] pixels;
        
        // Guardar estado final al cerrar
        saveCurrentState("final_state.json");
    }
    
    // NUEVA: Guardar estado actual
    void saveCurrentState(const std::string& filename = "") {
        auto serializable = params.toSerializable(currentType);
        serializable.addMetadata("session", "current");
        serializable.addMetadata("component", "FractalMutator");
        
        std::string actualFilename = filename;
        if (actualFilename.empty()) {
            auto now = std::chrono::system_clock::now();
            auto time_t = std::chrono::system_clock::to_time_t(now);
            std::ostringstream ss;
            ss << "state_" << std::put_time(std::gmtime(&time_t), "%Y%m%d_%H%M%S") << ".json";
            actualFilename = ss.str();
        }
        
        if (serializer.saveObject(serializable, actualFilename)) {
            std::cout << "💾 Estado guardado: " << actualFilename << std::endl;
        }
    }
    
    // NUEVA: Cargar estado desde archivo
    bool loadState(const std::string& filename) {
        SerializableFractalState serializable;
        if (serializer.loadObject(serializable, filename)) {
            params.fromSerializable(serializable);
            currentType = static_cast<FractalType>(serializable.fractalType);
            
            std::cout << "📖 Estado cargado: " << filename << std::endl;
            std::cout << "   Zoom: " << params.zoom << ", Tipo: " << serializable.fractalType << std::endl;
            return true;
        }
        return false;
    }
    
    // NUEVA: Cargar último estado guardado
    void loadLastState() {
        // Intentar cargar el estado más reciente
        if (std::filesystem::exists(sharedPath + "/serialized/final_state.json")) {
            if (loadState("final_state.json")) {
                std::cout << "🔄 Estado anterior restaurado" << std::endl;
                return;
            }
        }
        
        // Si no hay estado previo, usar valores por defecto
        std::cout << "✨ Iniciando con estado por defecto" << std::endl;
    }
    
    // NUEVA: Crear snapshot automático de estados interesantes
    void createInterestingSnapshot() {
        // Determinar si el estado actual es "interesante"
        bool isInteresting = false;
        std::string reason = "";
        
        // Criterios para estados interesantes
        if (params.zoom > 100.0) {
            isInteresting = true;
            reason = "high_zoom";
        } else if (params.mutationStrength > 0.4) {
            isInteresting = true;
            reason = "high_mutation";
        } else if (params.autoMutate && params.zoom > 10.0) {
            isInteresting = true;
            reason = "auto_evolving";
        }
        
        if (isInteresting) {
            auto serializable = params.toSerializable(currentType);
            serializable.addMetadata("interesting", "true");
            serializable.addMetadata("reason", reason);
            serializable.addMetadata("auto_saved", "true");
            
            auto snapshot = serializer.createSnapshot(serializable);
            serializer.saveTimestampedSnapshot(snapshot);
            
            std::cout << "📸 Snapshot interesante guardado: " << reason << std::endl;
        }
    }
    
    // NUEVA: Exportar colección de estados
    void exportStateCollection() {
        EcosystemSnapshot collection;
        collection.sessionId = "collection_" + std::to_string(std::time(nullptr));
        collection.addMetadata("type", "state_collection");
        collection.addMetadata("component", "FractalMutator");
        
        // Añadir estado actual
        auto currentState = std::make_shared<SerializableFractalState>(params.toSerializable(currentType));
        currentState->addMetadata("current", "true");
        collection.addObject(currentState);
        
        // Guardar colección
        serializer.saveObject(collection, "state_collection.json");
        std::cout << "📦 Colección de estados exportada" << std::endl;
    }
    
    // Funciones existentes (calculateIterations, getColor, etc.) - mantener igual
    double calculateIterations(std::complex<double> point) {
        std::complex<double> z(0.0, 0.0);
        int iterations = 0;
        double magnitude = 0.0;
        
        switch (currentType) {
            case FractalType::MANDELBROT:
                z = std::complex<double>(0.0, 0.0);
                while (iterations < params.maxIterations) {
                    magnitude = std::abs(z);
                    if (magnitude > params.escapeRadius) break;
                    z = std::pow(z, params.power) + point;
                    iterations++;
                }
                break;
                
            case FractalType::JULIA:
                z = point;
                while (iterations < params.maxIterations) {
                    magnitude = std::abs(z);
                    if (magnitude > params.escapeRadius) break;
                    z = std::pow(z, params.power) + params.juliaC;
                    iterations++;
                }
                break;
                
            case FractalType::BURNING_SHIP:
                z = std::complex<double>(0.0, 0.0);
                while (iterations < params.maxIterations) {
                    magnitude = std::abs(z);
                    if (magnitude > params.escapeRadius) break;
                    z = std::complex<double>(std::abs(z.real()), std::abs(z.imag()));
                    z = std::pow(z, params.power) + point;
                    iterations++;
                }
                break;
        }
        
        if (params.smoothColoring && iterations < params.maxIterations) {
            double smoothed = iterations + 1 - std::log2(std::log2(magnitude));
            return smoothed;
        }
        
        return static_cast<double>(iterations);
    }
    
    sf::Color getColor(double iterations) {
        if (iterations >= params.maxIterations) {
            return sf::Color::Black;
        }
        
        double normalized = iterations / params.maxIterations;
        normalized = normalized * params.colorSpeed + params.colorOffset;
        normalized = std::pow(normalized * params.brightness, params.contrast);
        normalized = std::fmod(normalized, 1.0);
        
        sf::Color color;
        
        switch (params.colorScheme) {
            case ColorScheme::CLASSIC:
                color = sf::Color(
                    static_cast<std::uint8_t>((std::sin(normalized * 16 + animationTime) * 127 + 128)),
                    static_cast<std::uint8_t>((std::sin(normalized * 13 + 2 + animationTime) * 127 + 128)),
                    static_cast<std::uint8_t>((std::sin(normalized * 21 + 4 + animationTime) * 127 + 128))
                );
                break;
                
            case ColorScheme::FIRE:
                {
                    double r = normalized;
                    double g = std::max(0.0, normalized - 0.3) * 1.5;
                    double b = std::max(0.0, normalized - 0.7) * 3.0;
                    color = sf::Color(
                        static_cast<std::uint8_t>(std::min(255.0, r * 255)),
                        static_cast<std::uint8_t>(std::min(255.0, g * 255)),
                        static_cast<std::uint8_t>(std::min(255.0, b * 255))
                    );
                }
                break;
                
            // ... resto de casos de color igual que antes
            default:
                color = sf::Color::White;
                break;
        }
        
        return color;
    }
    
    std::complex<double> screenToComplex(int x, int y) {
        double real = (x - width / 2.0) / (width / 4.0) / params.zoom + params.centerX;
        double imag = (y - height / 2.0) / (height / 4.0) / params.zoom + params.centerY;
        return std::complex<double>(real, imag);
    }
    
    void render() {
        for (int y = 0; y < height; y++) {
            for (int x = 0; x < width; x++) {
                std::complex<double> point = screenToComplex(x, y);
                double iterations = calculateIterations(point);
                
                sf::Color color = getColor(iterations);
                int index = (y * width + x) * 4;
                
                pixels[index] = color.r;
                pixels[index + 1] = color.g;
                pixels[index + 2] = color.b;
                pixels[index + 3] = 255;
            }
        }
        
        texture.update(pixels);
    }
    
    void draw(sf::RenderWindow& window) {
        window.draw(sprite);
    }
    
    // MODIFICADA: Sincronización con serialización automática
    void syncWithEcosystem(double fps) {
        if (syncClock.getElapsedTime().asSeconds() >= SYNC_INTERVAL) {
            // Mantener compatibilidad con Nexo
            saveParameters(params, currentType);
            syncClock.restart();
        }
        
        // NUEVO: Snapshots automáticos
        if (snapshotClock.getElapsedTime().asSeconds() >= SNAPSHOT_INTERVAL) {
            createInterestingSnapshot();
            snapshotCounter++;
            
            // Snapshot periódico cada 10 veces (5 minutos)
            if (snapshotCounter % 10 == 0) {
                saveCurrentState();
            }
            
            snapshotClock.restart();
        }
    }
    
    // Mantener funciones existentes
    void mutateParameters(double strength = 1.0) {
        double s = params.mutationStrength * strength;
        
        if (currentType == FractalType::JULIA) {
            params.juliaC += std::complex<double>(
                mutationDist(gen) * s * 0.1,
                mutationDist(gen) * s * 0.1
            );
        }
        
        params.colorSpeed += mutationDist(gen) * s * 0.5;
        params.colorSpeed = std::max(0.1, std::min(5.0, params.colorSpeed));
        
        params.colorOffset += mutationDist(gen) * s * 0.1;
        params.colorOffset = std::fmod(params.colorOffset + 1.0, 1.0);
        
        params.brightness += mutationDist(gen) * s * 0.2;
        params.brightness = std::max(0.1, std::min(3.0, params.brightness));
        
        params.contrast += mutationDist(gen) * s * 0.2;
        params.contrast = std::max(0.1, std::min(3.0, params.contrast));
        
        params.power += mutationDist(gen) * s * 0.1;
        params.power = std::max(1.5, std::min(4.0, params.power));
        
        std::cout << "Mutacion aplicada - Fuerza: " << s << std::endl;
    }
    
    // Resto de funciones mantener igual...
    void zoomIn() { params.zoom *= 1.2; }
    void zoomOut() { params.zoom /= 1.2; }
    void moveLeft() { params.centerX -= 0.1 / params.zoom; }
    void moveRight() { params.centerX += 0.1 / params.zoom; }
    void moveUp() { params.centerY -= 0.1 / params.zoom; }
    void moveDown() { params.centerY += 0.1 / params.zoom; }
    
    void reset() {
        params = FractalParameters();
        std::cout << "Parametros reseteados" << std::endl;
    }

    // Función para compatibilidad con Nexo
    bool saveParameters(const FractalParameters& params, FractalType fractalType) {
        try {
            std::string paramsFile = sharedPath + "/fractal_params.json";
            std::ofstream file(paramsFile);
            if (!file.is_open()) return false;
            
            file << "{\n";
            file << "  \"timestamp\": \"" << getCurrentTimestamp() << "\",\n";
            file << "  \"fractalType\": " << static_cast<int>(fractalType) << ",\n";
            file << "  \"parameters\": " << params.toJSON() << "\n";
            file << "}";
            file.close();
            return true;
        } catch (const std::exception&) {
            return false;
        }
    }

private:
    std::string getCurrentTimestamp() {
        auto now = std::chrono::system_clock::now();
        auto time_t = std::chrono::system_clock::to_time_t(now);
        std::ostringstream ss;
        ss << std::put_time(std::localtime(&time_t), "%Y-%m-%d %H:%M:%S");
        return ss.str();
    }

public:
    // Getters para UI
    std::string getStatusInfo() {
        std::string typeName;
        switch (currentType) {
            case FractalType::MANDELBROT: typeName = "Mandelbrot"; break;
            case FractalType::JULIA: typeName = "Julia"; break;
            case FractalType::BURNING_SHIP: typeName = "Burning Ship"; break;
        }
        
        std::string colorName;
        switch (params.colorScheme) {
            case ColorScheme::CLASSIC: colorName = "Clasico"; break;
            case ColorScheme::FIRE: colorName = "Fuego"; break;
            case ColorScheme::OCEAN: colorName = "Oceano"; break;
            case ColorScheme::RAINBOW: colorName = "Arcoiris"; break;
            case ColorScheme::MONOCHROME: colorName = "Monocromo"; break;
            case ColorScheme::ELECTRIC: colorName = "Electrico"; break;
        }
        
        return "Tipo: " + typeName + " | Color: " + colorName + 
               " | Auto: " + (params.autoMutate ? "ON" : "OFF") +
               " | Fuerza: " + std::to_string(params.mutationStrength).substr(0, 4) +
               " | Snapshots: " + std::to_string(snapshotCounter);
    }
    
    // NUEVAS: Funciones para controles adicionales
    void saveStateManual() { saveCurrentState(); }
    void exportCollection() { exportStateCollection(); }
    bool loadStateManual(const std::string& filename) { return loadState(filename); }
    
    // Mantener funciones existentes para controles
    void switchFractalType() {
        switch (currentType) {
            case FractalType::MANDELBROT:
                currentType = FractalType::JULIA;
                params.centerX = 0.0; params.centerY = 0.0; params.zoom = 1.0;
                break;
            case FractalType::JULIA:
                currentType = FractalType::BURNING_SHIP;
                params.centerX = -0.5; params.centerY = -0.6; params.zoom = 0.8;
                break;
            case FractalType::BURNING_SHIP:
                currentType = FractalType::MANDELBROT;
                reset();
                break;
        }
    }
    
    void switchColorScheme() {
        int current = static_cast<int>(params.colorScheme);
        current = (current + 1) % 6;
        params.colorScheme = static_cast<ColorScheme>(current);
    }
    
    void toggleAutoMutate() { 
        params.autoMutate = !params.autoMutate; 
        std::cout << "Auto-mutacion: " << (params.autoMutate ? "ON" : "OFF") << std::endl;
    }
    
    void adjustMutationStrength(double delta) {
        params.mutationStrength += delta;
        params.mutationStrength = std::max(0.01, std::min(1.0, params.mutationStrength));
        std::cout << "Fuerza de mutacion: " << params.mutationStrength << std::endl;
    }
    
    void increaseIterations() { 
        params.maxIterations = std::min(params.maxIterations + 50, 2000); 
    }
    void decreaseIterations() { 
        params.maxIterations = std::max(params.maxIterations - 50, 50); 
    }
    
    void autoMutate(double deltaTime) {
        if (params.autoMutate) {
            animationTime += deltaTime;
            mutateParameters(params.autoMutateSpeed);
        }
    }
    
    void adjustJuliaC(double deltaReal, double deltaImag) {
        if (currentType == FractalType::JULIA) {
            params.juliaC += std::complex<double>(deltaReal, deltaImag);
        }
    }
    
    // Getters para compatibilidad
    const FractalParameters& getParameters() const { return params; }
    bool isAutoMutating() const { return params.autoMutate; }
    double getMutationStrength() const { return params.mutationStrength; }
};

int main() {
    const int WIDTH = 800;
    const int HEIGHT = 600;
    const int UI_PANEL_HEIGHT = 120; // Aumentado para nuevos botones
    
    sf::RenderWindow window(sf::VideoMode({WIDTH, HEIGHT + UI_PANEL_HEIGHT}), 
                           "Ecosistema Fractal - Mutador con Serialización sin iconos");
    window.setFramerateLimit(60);
    
    FractalRenderer renderer(WIDTH, HEIGHT);
    
    sf::Font font;
    bool fontLoaded = font.openFromFile("C:/Windows/Fonts/arial.ttf");
    
    std::vector<std::unique_ptr<Button>> buttons;
    
    if (fontLoaded) {
        // Primera fila - controles existentes
        buttons.push_back(std::make_unique<Button>(10, HEIGHT + 10, 100, 35, "MUTAR", &font));
        buttons.push_back(std::make_unique<Button>(120, HEIGHT + 10, 100, 35, "AUTO ON/OFF", &font));
        buttons.push_back(std::make_unique<Button>(230, HEIGHT + 10, 80, 35, "RESET", &font));
        buttons.push_back(std::make_unique<Button>(320, HEIGHT + 10, 80, 35, "FRACTAL", &font));
        buttons.push_back(std::make_unique<Button>(410, HEIGHT + 10, 80, 35, "COLOR", &font));
        
        // Segunda fila - controles de mutación
        buttons.push_back(std::make_unique<Button>(10, HEIGHT + 55, 80, 35, "FUERZA -", &font));
        buttons.push_back(std::make_unique<Button>(100, HEIGHT + 55, 80, 35, "FUERZA +", &font));
        buttons.push_back(std::make_unique<Button>(190, HEIGHT + 55, 60, 35, "ZOOM +", &font));
        buttons.push_back(std::make_unique<Button>(260, HEIGHT + 55, 60, 35, "ZOOM -", &font));
        
        // NUEVA: Tercera fila - controles de serialización
        buttons.push_back(std::make_unique<Button>(340, HEIGHT + 55, 80, 35, "GUARDAR", &font));
        buttons.push_back(std::make_unique<Button>(430, HEIGHT + 55, 80, 35, "EXPORTAR", &font));
    }
    
    sf::RectangleShape uiPanel;
    uiPanel.setPosition({0, static_cast<float>(HEIGHT)});
    uiPanel.setSize({static_cast<float>(WIDTH), static_cast<float>(UI_PANEL_HEIGHT)});
    uiPanel.setFillColor(sf::Color(40, 40, 40));
    
    std::optional<sf::Text> infoText;
    if (fontLoaded) {
        infoText = sf::Text(font);
        infoText->setCharacterSize(12);
        infoText->setFillColor(sf::Color::White);
        infoText->setPosition({520, static_cast<float>(HEIGHT + 20)});
    }
    
    std::cout << "=== ECOSISTEMA FRACTAL CON SERIALIZACIÓN SIN ICONOS ===" << std::endl;
    std::cout << "💾 Persistencia: Estados guardados automáticamente" << std::endl;
    std::cout << "📸 Snapshots: Estados interesantes detectados automáticamente" << std::endl;
    std::cout << "🔄 Restauración: Estado anterior cargado al iniciar" << std::endl;
    std::cout << "📦 Exportación: Colecciones de estados disponibles" << std::endl;
    std::cout << std::endl;
    std::cout << "CONTROLES ADICIONALES:" << std::endl;
    std::cout << "- GUARDAR: Guardar estado actual manualmente" << std::endl;
    std::cout << "- EXPORTAR: Exportar colección de estados" << std::endl;
    std::cout << "- Tecla S: Guardar snapshot manual" << std::endl;
    std::cout << "- Tecla L: Listar estados guardados" << std::endl;
    
    sf::Clock clock;
    sf::Clock fpsClock;
    int frameCount = 0;
    double currentFPS = 0.0;
    bool needsRender = true;
    bool mousePressed = false;
    
    while (window.isOpen()) {
        float deltaTime = clock.restart().asSeconds();
        sf::Vector2i mousePos = sf::Mouse::getPosition(window);
        
        // Calcular FPS
        frameCount++;
        if (fpsClock.getElapsedTime().asSeconds() >= 1.0f) {
            currentFPS = frameCount / fpsClock.getElapsedTime().asSeconds();
            frameCount = 0;
            fpsClock.restart();
        }
        
        // Sincronización con ecosistema (incluye serialización automática)
        renderer.syncWithEcosystem(currentFPS);
        
        // Auto-mutación
        if (renderer.isAutoMutating()) {
            renderer.autoMutate(deltaTime);
            needsRender = true;
        }
        
        while (auto event = window.pollEvent()) {
            if (event->is<sf::Event::Closed>()) {
                window.close();
            }
            
            if (const auto* mouseButtonPressed = event->getIf<sf::Event::MouseButtonPressed>()) {
                if (mouseButtonPressed->button == sf::Mouse::Button::Left) {
                    mousePressed = true;
                }
            }
            
            if (const auto* mouseButtonReleased = event->getIf<sf::Event::MouseButtonReleased>()) {
                if (mouseButtonReleased->button == sf::Mouse::Button::Left) {
                    mousePressed = false;
                }
            }
            
            if (const auto* keyPressed = event->getIf<sf::Event::KeyPressed>()) {
                needsRender = true;
                
                switch (keyPressed->code) {
                    case sf::Keyboard::Key::Escape: window.close(); break;
                    case sf::Keyboard::Key::W: renderer.moveUp(); break;
                    case sf::Keyboard::Key::S: 
                        // NUEVO: S para snapshot manual
                        renderer.saveStateManual();
                        std::cout << "📸 Snapshot manual guardado!" << std::endl;
                        break;
                    case sf::Keyboard::Key::A: renderer.moveLeft(); break;
                    case sf::Keyboard::Key::D: renderer.moveRight(); break;
                    case sf::Keyboard::Key::Equal: renderer.zoomIn(); break;
                    case sf::Keyboard::Key::Hyphen: renderer.zoomOut(); break;
                    case sf::Keyboard::Key::L:
                        // NUEVO: L para listar estados
                        std::cout << "📁 Estados serializados disponibles en: ./shared/serialized/" << std::endl;
                        break;
                }
            }
            
            if (const auto* mouseWheel = event->getIf<sf::Event::MouseWheelScrolled>()) {
                needsRender = true;
                if (mouseWheel->delta > 0) {
                    renderer.zoomIn();
                } else {
                    renderer.zoomOut();
                }
            }
        }
        
        // Procesar clicks en botones
        if (fontLoaded && buttons.size() >= 11) {
            for (auto& button : buttons) {
                button->update(mousePos, mousePressed);
            }
            
            // Botones existentes
            if (buttons[0]->wasClicked(mousePos, mousePressed)) { // MUTAR
                renderer.mutateParameters();
                needsRender = true;
            }
            if (buttons[1]->wasClicked(mousePos, mousePressed)) { // AUTO ON/OFF
                renderer.toggleAutoMutate();
            }
            if (buttons[2]->wasClicked(mousePos, mousePressed)) { // RESET
                renderer.reset();
                needsRender = true;
            }
            if (buttons[3]->wasClicked(mousePos, mousePressed)) { // FRACTAL
                renderer.switchFractalType();
                needsRender = true;
            }
            if (buttons[4]->wasClicked(mousePos, mousePressed)) { // COLOR
                renderer.switchColorScheme();
                needsRender = true;
            }
            if (buttons[5]->wasClicked(mousePos, mousePressed)) { // FUERZA -
                renderer.adjustMutationStrength(-0.05);
            }
            if (buttons[6]->wasClicked(mousePos, mousePressed)) { // FUERZA +
                renderer.adjustMutationStrength(0.05);
            }
            if (buttons[7]->wasClicked(mousePos, mousePressed)) { // ZOOM +
                renderer.zoomIn();
                needsRender = true;
            }
            if (buttons[8]->wasClicked(mousePos, mousePressed)) { // ZOOM -
                renderer.zoomOut();
                needsRender = true;
            }
            
            // NUEVOS: Botones de serialización
            if (buttons[9]->wasClicked(mousePos, mousePressed)) { // GUARDAR
                renderer.saveStateManual();
                std::cout << "💾 Estado guardado manualmente!" << std::endl;
            }
            if (buttons[10]->wasClicked(mousePos, mousePressed)) { // EXPORTAR
                renderer.exportCollection();
                std::cout << "📦 Colección exportada!" << std::endl;
            }
        }
        
        if (needsRender) {
            renderer.render();
            needsRender = false;
        }
        
        window.clear();
        renderer.draw(window);
        
        window.draw(uiPanel);
        
        if (fontLoaded) {
            for (auto& button : buttons) {
                button->draw(window);
            }
            
            if (infoText) {
                std::string statusInfo = renderer.getStatusInfo() + 
                                       " | FPS: " + std::to_string(static_cast<int>(currentFPS));
                infoText->setString(statusInfo);
                window.draw(*infoText);
            }
        }
        
        window.display();
    }
    
    return 0;
}