#pragma once

#include <string>
#include <map>
#include <vector>
#include <memory>
#include <fstream>
#include <sstream>
#include <complex>
#include <chrono>
#include <iomanip>

namespace FractalEcosystem {

/// Interfaz base para objetos serializables
class ISerializable {
public:
    virtual ~ISerializable() = default;
    virtual std::string serialize() const = 0;
    virtual bool deserialize(const std::string& data) = 0;
    virtual std::string getTypeName() const = 0;
};

/// Clase base para objetos del ecosistema
class EcosystemObject : public ISerializable {
protected:
    std::string id;
    std::chrono::system_clock::time_point timestamp;
    std::map<std::string, std::string> metadata;

public:
    EcosystemObject() : timestamp(std::chrono::system_clock::now()) {
        // Generar ID único
        auto now = std::chrono::system_clock::now();
        auto time_t = std::chrono::system_clock::to_time_t(now);
        std::ostringstream ss;
        ss << "obj_" << std::hex << time_t << "_" << std::rand() % 10000;
        id = ss.str();
    }

    const std::string& getId() const { return id; }
    void setId(const std::string& newId) { id = newId; }
    
    void addMetadata(const std::string& key, const std::string& value) {
        metadata[key] = value;
    }
    
    std::string getMetadata(const std::string& key) const {
        auto it = metadata.find(key);
        return it != metadata.end() ? it->second : "";
    }

protected:
    /// Serializar metadatos comunes
    std::string serializeBase() const {
        std::ostringstream json;
        json << std::fixed << std::setprecision(6);
        
        auto time_t = std::chrono::system_clock::to_time_t(timestamp);
        json << "\"id\": \"" << id << "\",\n";
        json << "\"timestamp\": \"" << std::put_time(std::gmtime(&time_t), "%Y-%m-%dT%H:%M:%SZ") << "\",\n";
        json << "\"type\": \"" << getTypeName() << "\",\n";
        
        if (!metadata.empty()) {
            json << "\"metadata\": {\n";
            bool first = true;
            for (const auto& [key, value] : metadata) {
                if (!first) json << ",\n";
                json << "  \"" << key << "\": \"" << value << "\"";
                first = false;
            }
            json << "\n},\n";
        }
        
        return json.str();
    }
};

/// Estado de parámetros fractales serializable
class SerializableFractalState : public EcosystemObject {
public:
    // Parámetros geométricos
    double zoom = 1.0;
    double centerX = 0.0;
    double centerY = 0.0;
    int maxIterations = 100;
    
    // Parámetros específicos de fractal
    std::complex<double> juliaC = {-0.7, 0.27015};
    double escapeRadius = 2.0;
    double power = 2.0;
    
    // Parámetros de color
    int colorScheme = 0;
    double colorSpeed = 1.0;
    double colorOffset = 0.0;
    double brightness = 1.0;
    double contrast = 1.0;
    bool smoothColoring = true;
    
    // Parámetros de mutación
    double mutationStrength = 0.1;
    bool autoMutate = false;
    double autoMutateSpeed = 0.01;
    
    // Tipo de fractal
    int fractalType = 0;

    std::string serialize() const override {
        std::ostringstream json;
        json << std::fixed << std::setprecision(6);
        json << "{\n";
        json << serializeBase();
        json << "\"parameters\": {\n";
        json << "  \"zoom\": " << zoom << ",\n";
        json << "  \"centerX\": " << centerX << ",\n";
        json << "  \"centerY\": " << centerY << ",\n";
        json << "  \"maxIterations\": " << maxIterations << ",\n";
        json << "  \"juliaC_real\": " << juliaC.real() << ",\n";
        json << "  \"juliaC_imag\": " << juliaC.imag() << ",\n";
        json << "  \"escapeRadius\": " << escapeRadius << ",\n";
        json << "  \"power\": " << power << ",\n";
        json << "  \"colorScheme\": " << colorScheme << ",\n";
        json << "  \"colorSpeed\": " << colorSpeed << ",\n";
        json << "  \"colorOffset\": " << colorOffset << ",\n";
        json << "  \"brightness\": " << brightness << ",\n";
        json << "  \"contrast\": " << contrast << ",\n";
        json << "  \"smoothColoring\": " << (smoothColoring ? "true" : "false") << ",\n";
        json << "  \"mutationStrength\": " << mutationStrength << ",\n";
        json << "  \"autoMutate\": " << (autoMutate ? "true" : "false") << ",\n";
        json << "  \"autoMutateSpeed\": " << autoMutateSpeed << "\n";
        json << "},\n";
        json << "\"fractalType\": " << fractalType << "\n";
        json << "}";
        return json.str();
    }
    
    bool deserialize(const std::string& data) override {
        // Parser JSON simple para este ejemplo
        // En producción usarías nlohmann/json o similar
        try {
            // Extraer valores usando parsing básico
            size_t pos;
            
            // Zoom
            pos = data.find("\"zoom\":");
            if (pos != std::string::npos) {
                pos = data.find(':', pos) + 1;
                zoom = std::stod(data.substr(pos));
            }
            
            // CenterX
            pos = data.find("\"centerX\":");
            if (pos != std::string::npos) {
                pos = data.find(':', pos) + 1;
                centerX = std::stod(data.substr(pos));
            }
            
            // CenterY
            pos = data.find("\"centerY\":");
            if (pos != std::string::npos) {
                pos = data.find(':', pos) + 1;
                centerY = std::stod(data.substr(pos));
            }
            
            // MaxIterations
            pos = data.find("\"maxIterations\":");
            if (pos != std::string::npos) {
                pos = data.find(':', pos) + 1;
                maxIterations = std::stoi(data.substr(pos));
            }
            
            // Julia C real
            pos = data.find("\"juliaC_real\":");
            if (pos != std::string::npos) {
                pos = data.find(':', pos) + 1;
                double real = std::stod(data.substr(pos));
                juliaC = std::complex<double>(real, juliaC.imag());
            }
            
            // Julia C imag
            pos = data.find("\"juliaC_imag\":");
            if (pos != std::string::npos) {
                pos = data.find(':', pos) + 1;
                double imag = std::stod(data.substr(pos));
                juliaC = std::complex<double>(juliaC.real(), imag);
            }
            
            // FractalType
            pos = data.find("\"fractalType\":");
            if (pos != std::string::npos) {
                pos = data.find(':', pos) + 1;
                fractalType = std::stoi(data.substr(pos));
            }
            
            return true;
        } catch (const std::exception&) {
            return false;
        }
    }
    
    std::string getTypeName() const override {
        return "FractalState";
    }
};

/// Snapshot completo del estado del ecosistema
class EcosystemSnapshot : public EcosystemObject {
public:
    std::vector<std::shared_ptr<ISerializable>> objects;
    std::string sessionId;
    double healthScore = 0.0;
    std::string activityLevel = "Unknown";
    
    void addObject(std::shared_ptr<ISerializable> obj) {
        objects.push_back(obj);
    }
    
    std::string serialize() const override {
        std::ostringstream json;
        json << "{\n";
        json << serializeBase();
        json << "\"sessionId\": \"" << sessionId << "\",\n";
        json << "\"healthScore\": " << healthScore << ",\n";
        json << "\"activityLevel\": \"" << activityLevel << "\",\n";
        json << "\"objects\": [\n";
        
        for (size_t i = 0; i < objects.size(); ++i) {
            if (i > 0) json << ",\n";
            json << objects[i]->serialize();
        }
        
        json << "\n]\n";
        json << "}";
        return json.str();
    }
    
    bool deserialize(const std::string& data) override {
        // Implementación simplificada
        try {
            size_t pos = data.find("\"sessionId\":");
            if (pos != std::string::npos) {
                pos = data.find('"', pos + 12);
                size_t end = data.find('"', pos + 1);
                sessionId = data.substr(pos + 1, end - pos - 1);
            }
            
            pos = data.find("\"healthScore\":");
            if (pos != std::string::npos) {
                pos = data.find(':', pos) + 1;
                healthScore = std::stod(data.substr(pos));
            }
            
            return true;
        } catch (const std::exception&) {
            return false;
        }
    }
    
    std::string getTypeName() const override {
        return "EcosystemSnapshot";
    }
};

/// Gestor de serialización del ecosistema
class SerializationManager {
private:
    std::string basePath;
    
public:
    SerializationManager(const std::string& path = "./serialized") : basePath(path) {
        // Crear directorio si no existe
        std::filesystem::create_directories(basePath);
    }
    
    /// Serializar objeto a archivo
    template<typename T>
    bool saveObject(const T& object, const std::string& filename) {
        static_assert(std::is_base_of_v<ISerializable, T>, "T must inherit from ISerializable");
        
        std::string filepath = basePath + "/" + filename;
        std::ofstream file(filepath);
        
        if (!file.is_open()) {
            return false;
        }
        
        file << object.serialize();
        file.close();
        
        std::cout << "💾 Objeto serializado: " << filepath << std::endl;
        return true;
    }
    
    /// Deserializar objeto desde archivo
    template<typename T>
    bool loadObject(T& object, const std::string& filename) {
        static_assert(std::is_base_of_v<ISerializable, T>, "T must inherit from ISerializable");
        
        std::string filepath = basePath + "/" + filename;
        std::ifstream file(filepath);
        
        if (!file.is_open()) {
            return false;
        }
        
        std::string content((std::istreambuf_iterator<char>(file)),
                           std::istreambuf_iterator<char>());
        file.close();
        
        bool success = object.deserialize(content);
        if (success) {
            std::cout << "📖 Objeto deserializado: " << filepath << std::endl;
        }
        
        return success;
    }
    
    /// Crear snapshot completo del ecosistema
    EcosystemSnapshot createSnapshot(const SerializableFractalState& fractalState) {
        EcosystemSnapshot snapshot;
        snapshot.sessionId = generateSessionId();
        snapshot.addMetadata("creator", "FractalMutator");
        snapshot.addMetadata("version", "1.0");
        
        // Añadir estado del fractal
        auto fractalPtr = std::make_shared<SerializableFractalState>(fractalState);
        snapshot.addObject(fractalPtr);
        
        // Calcular métricas del snapshot
        snapshot.healthScore = calculateHealthScore(fractalState);
        snapshot.activityLevel = determineActivityLevel(fractalState);
        
        std::cout << "📸 Snapshot creado: " << snapshot.getId() 
                  << " (salud: " << snapshot.healthScore << ")" << std::endl;
        
        return snapshot;
    }
    
    /// Guardar snapshot con timestamp
    bool saveTimestampedSnapshot(const EcosystemSnapshot& snapshot) {
        auto now = std::chrono::system_clock::now();
        auto time_t = std::chrono::system_clock::to_time_t(now);
        
        std::ostringstream filename;
        filename << "snapshot_" << std::put_time(std::gmtime(&time_t), "%Y%m%d_%H%M%S") << ".json";
        
        return saveObject(snapshot, filename.str());
    }
    
    /// Buscar snapshots por criterios
    std::vector<std::string> findSnapshots(double minHealth = 0.0, const std::string& activityLevel = "") {
        std::vector<std::string> results;
        
        // Implementar búsqueda en archivos
        // Por simplicidad, devolver lista vacía
        std::cout << "🔍 Búsqueda de snapshots con salud >= " << minHealth << std::endl;
        
        return results;
    }

private:
    std::string generateSessionId() {
        auto now = std::chrono::system_clock::now();
        auto time_t = std::chrono::system_clock::to_time_t(now);
        std::ostringstream ss;
        ss << "session_" << std::hex << time_t;
        return ss.str();
    }
    
    double calculateHealthScore(const SerializableFractalState& state) {
        double score = 1.0;
        
        // Penalizar valores extremos
        if (state.zoom > 1000.0 || state.zoom < 0.01) score *= 0.8;
        if (state.mutationStrength > 0.5) score *= 0.9;
        if (state.maxIterations < 50) score *= 0.7;
        
        return score;
    }
    
    std::string determineActivityLevel(const SerializableFractalState& state) {
        if (state.autoMutate && state.mutationStrength > 0.3) {
            return "High";
        } else if (state.mutationStrength > 0.1) {
            return "Moderate";
        } else {
            return "Low";
        }
    }
};

/// Factory para crear objetos serializables
class ObjectFactory {
public:
    static std::shared_ptr<ISerializable> createFromType(const std::string& typeName) {
        if (typeName == "FractalState") {
            return std::make_shared<SerializableFractalState>();
        } else if (typeName == "EcosystemSnapshot") {
            return std::make_shared<EcosystemSnapshot>();
        }
        
        return nullptr;
    }
    
    static std::shared_ptr<ISerializable> loadFromFile(const std::string& filepath) {
        std::ifstream file(filepath);
        if (!file.is_open()) {
            return nullptr;
        }
        
        std::string content((std::istreambuf_iterator<char>(file)),
                           std::istreambuf_iterator<char>());
        file.close();
        
        // Extraer tipo del JSON
        size_t pos = content.find("\"type\":");
        if (pos == std::string::npos) {
            return nullptr;
        }
        
        pos = content.find('"', pos + 7);
        size_t end = content.find('"', pos + 1);
        std::string typeName = content.substr(pos + 1, end - pos - 1);
        
        auto object = createFromType(typeName);
        if (object && object->deserialize(content)) {
            return object;
        }
        
        return nullptr;
    }
};

} // namespace FractalEcosystem