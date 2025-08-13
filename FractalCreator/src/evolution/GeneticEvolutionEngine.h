//=============================================================================
// GeneticFractalEvolution.h - Sistema de evolución genética para fractales
//=============================================================================
#pragma once
#include "../fractals/DeformableFractal.h"
#include <vector>
#include <functional>
#include <random>
#include <thread>
#include <mutex>
#include <atomic>
#include <chrono>
#include <map>

//=============================================================================
// FractalGenome - Representación genética de un fractal
//=============================================================================
struct FractalGenome {
    // Genes básicos
    struct Gene {
        float value;
        float mutationRate;
        float min, max;
        
        Gene(float v = 0.0f, float rate = 0.1f, float minVal = -10.0f, float maxVal = 10.0f)
            : value(v), mutationRate(rate), min(minVal), max(maxVal) {}
    };
    
    // Parámetros del fractal codificados genéticamente
    Gene juliaReal{0.355f, 0.05f, -2.0f, 2.0f};
    Gene juliaImag{0.355f, 0.05f, -2.0f, 2.0f};
    Gene escapeThreshold{4.0f, 0.02f, 2.0f, 10.0f};
    
    // Estado A
    Gene angleA{0.0f, 0.1f, -3.14159f, 3.14159f};
    Gene freqA{1.0f, 0.08f, 0.1f, 3.0f};
    Gene phaseA{0.0f, 0.1f, -3.14159f, 3.14159f};
    Gene functionA{0.0f, 0.3f, 0.0f, 10.0f};
    Gene edgeGlowA{1.0f, 0.05f, 0.1f, 2.0f};
    Gene edgeHueShiftA{1.0f, 0.05f, 0.1f, 2.0f};
    
    // Estado B
    Gene angleB{0.0f, 0.1f, -3.14159f, 3.14159f};
    Gene freqB{1.0f, 0.08f, 0.1f, 3.0f};
    Gene phaseB{0.0f, 0.1f, -3.14159f, 3.14159f};
    Gene functionB{1.0f, 0.3f, 0.0f, 10.0f};
    Gene edgeGlowB{1.0f, 0.05f, 0.1f, 2.0f};
    Gene edgeHueShiftB{1.0f, 0.05f, 0.1f, 2.0f};
    
    // Control de blending
    Gene functionBlend{0.0f, 0.03f, 0.0f, 1.0f};
    Gene deformMix{0.0f, 0.03f, 0.0f, 1.0f};
    Gene shift{0.0f, 0.05f, -2.0f, 2.0f};
    Gene edgeSaturation{1.0f, 0.02f, 0.0f, 2.0f};
    
    // Metadatos evolutivos
    float fitness = 0.0f;
    int generation = 0;
    int age = 0;
    std::vector<int> parentIDs;
    
    // Métodos (declaraciones solamente)
    void ApplyToFractal(DeformableFractal* fractal) const;
    void ExtractFromFractal(const DeformableFractal* fractal);
    void Mutate(std::mt19937& rng, float globalMutationRate = 1.0f);
    static FractalGenome Crossover(const FractalGenome& parent1, const FractalGenome& parent2, std::mt19937& rng);
    float CalculateDistance(const FractalGenome& other) const;
};

//=============================================================================
// FitnessEvaluator - Sistema de evaluación de fitness
//=============================================================================
class FitnessEvaluator {
public:
    // Tipos de criterios de fitness
    enum class FitnessCriterion {
        COMPLEXITY,
        SYMMETRY,
        COLOR_DIVERSITY,
        EDGE_DEFINITION,
        UNIQUENESS,
        AESTHETIC_APPEAL,
        STABILITY,
        PERFORMANCE
    };
    
    struct FitnessWeights {
        float complexity = 0.3f;
        float symmetry = 0.1f;
        float colorDiversity = 0.2f;
        float edgeDefinition = 0.15f;
        float uniqueness = 0.15f;
        float aestheticAppeal = 0.05f;
        float stability = 0.03f;
        float performance = 0.02f;
    };
    
    FitnessEvaluator(int imageSize = 512);
    ~FitnessEvaluator() = default;
    
    // Evaluación principal
    float EvaluateFitness(const DeformableFractal* fractal, const FitnessWeights& weights);
    float EvaluateFitness(const FractalGenome& genome, const FitnessWeights& weights);
    
    // Evaluaciones específicas (declaraciones solamente)
    float EvaluateComplexity(const std::vector<float>& imageData);
    float EvaluateSymmetry(const std::vector<float>& imageData);
    float EvaluateColorDiversity(const std::vector<float>& imageData);
    float EvaluateEdgeDefinition(const std::vector<float>& imageData);
    float EvaluateStability(const DeformableFractal* fractal);
    float EvaluatePerformance(const DeformableFractal* fractal);
    
    // Configuración
    void SetImageSize(int size) { m_imageSize = size; }
    int GetImageSize() const { return m_imageSize; }
    
    // Análisis de población para uniqueness
    void SetPopulationContext(const std::vector<FractalGenome>& population) {
        m_populationContext = &population;
    }
    
private:
    int m_imageSize;
    const std::vector<FractalGenome>* m_populationContext = nullptr;
    
    std::vector<float> RenderFractalToImage(const DeformableFractal* fractal);
    float CalculateImageVariance(const std::vector<float>& imageData);
    float CalculateImageEntropy(const std::vector<float>& imageData);
};

//=============================================================================
// GeneticEvolutionEngine - Motor principal de evolución
//=============================================================================
class GeneticEvolutionEngine {
public:
    struct EvolutionParameters {
        int populationSize = 50;
        int maxGenerations = 1000;
        float mutationRate = 0.15f;
        float crossoverRate = 0.7f;
        float elitePercentage = 0.1f;
        
        // Diversidad genética
        float diversityPressure = 0.2f;
        int speciesCount = 5;  // Cambiado de unsigned int a int
        float compatibilityThreshold = 2.0f;
        
        // Mutación adaptativa
        bool adaptiveMutation = true;
        float mutationDecay = 0.95f;
        float minMutationRate = 0.01f;
        
        // Criterios de parada
        float targetFitness = 0.95f;
        int stagnationGenerations = 50;
        
        // Paralelización
        int threadCount = static_cast<int>(std::thread::hardware_concurrency());
        
        // Fitness
        FitnessEvaluator::FitnessWeights fitnessWeights;
    };
    
    GeneticEvolutionEngine(const EvolutionParameters& params = EvolutionParameters{});
    ~GeneticEvolutionEngine();
    
    // Control de evolución
    void Initialize(unsigned int seed = 0);
    void StartEvolution();
    void StopEvolution();
    void PauseEvolution();
    void ResumeEvolution();
    
    bool IsRunning() const { return m_running; }
    bool IsPaused() const { return m_paused; }
    
    // Acceso a resultados
    std::vector<FractalGenome> GetCurrentGeneration() const;
    FractalGenome GetBestIndividual() const;
    std::vector<FractalGenome> GetBestIndividuals(int count) const;
    
    // Estadísticas
    struct EvolutionStats {
        int currentGeneration = 0;
        float bestFitness = 0.0f;
        float averageFitness = 0.0f;
        float diversityIndex = 0.0f;
        int stagnationCount = 0;
        float currentMutationRate = 0.0f;
        
        // Performance
        float generationsPerSecond = 0.0f;
        float evaluationsPerSecond = 0.0f;
    };
    
    EvolutionStats GetStats() const { return m_stats; }
    
    // Configuración dinámica
    void SetParameters(const EvolutionParameters& params);
    EvolutionParameters GetParameters() const { return m_params; }
    
    // Callbacks para eventos
    using GenerationCallback = std::function<void(int generation, const EvolutionStats&)>;
    using BestFoundCallback = std::function<void(const FractalGenome&, float fitness)>;
    
    void SetGenerationCallback(GenerationCallback callback) { m_generationCallback = callback; }
    void SetBestFoundCallback(BestFoundCallback callback) { m_bestFoundCallback = callback; }
    
    // Importar/Exportar población
    void ImportPopulation(const std::vector<FractalGenome>& population);
    std::vector<FractalGenome> ExportPopulation() const;
    
    // Seeding con fractales específicos
    void SeedWithFractal(const FractalGenome& genome, int copies = 5);
    void SeedWithFractals(const std::vector<FractalGenome>& genomes);
    
private:
    EvolutionParameters m_params;
    std::vector<FractalGenome> m_population;
    std::unique_ptr<FitnessEvaluator> m_fitnessEvaluator;
    
    // Threading
    std::atomic<bool> m_running{false};
    std::atomic<bool> m_paused{false};
    std::unique_ptr<std::thread> m_evolutionThread;
    mutable std::mutex m_populationMutex;
    
    // Estadísticas
    mutable EvolutionStats m_stats;
    std::chrono::high_resolution_clock::time_point m_lastStatsUpdate;
    
    // Callbacks
    GenerationCallback m_generationCallback;
    BestFoundCallback m_bestFoundCallback;
    
    // RNG
    std::mt19937 m_rng;
    
    // Especiación (NEAT-style)
    struct Species {
        std::vector<int> members;
        FractalGenome representative;
        float sharedFitness = 0.0f;
        int stagnationCount = 0;
    };
    std::vector<Species> m_species;
    
    // Métodos principales de evolución (declaraciones solamente)
    void EvolutionLoop();
    void EvaluatePopulation();
    void SelectParents(std::vector<int>& parents);
    void GenerateOffspring(const std::vector<int>& parents);
    void UpdateSpecies();
    void UpdateStats();
    
    // Selección
    int TournamentSelection(int tournamentSize = 3);
    int RouletteWheelSelection();
    std::vector<int> SelectElite();
    
    // Especiación
    void AssignToSpecies();
    float CalculateCompatibility(const FractalGenome& genome1, const FractalGenome& genome2);
    void AdjustFitnessForSharing();
    
    // Utilidades
    void InitializeRandomPopulation();
    void SortPopulationByFitness();
    float CalculateDiversityIndex();
    bool CheckStagnation();
};

//=============================================================================
// FractalGallery - Sistema de galería para mejores fractales
//=============================================================================
class FractalGallery {
public:
    struct GalleryEntry {
        FractalGenome genome;
        float fitness;
        std::string name;
        std::string description;
        int generation;
        std::chrono::system_clock::time_point creationTime;
        std::vector<uint8_t> thumbnail;
        
        // Metadata adicional
        std::map<std::string, float> fitnessBreakdown;
        std::string tags;
    };
    
    FractalGallery(const std::string& galleryPath = "fractal_gallery/");
    ~FractalGallery() = default;
    
    // Gestión de entradas
    void AddFractal(const FractalGenome& genome, float fitness, 
                   const std::string& name = "", const std::string& description = "");
    bool RemoveFractal(const std::string& name);
    GalleryEntry* FindFractal(const std::string& name);
    
    // Consultas
    std::vector<GalleryEntry> GetAllFractals() const;
    std::vector<GalleryEntry> GetTopFractals(int count) const;
    std::vector<GalleryEntry> SearchByTags(const std::string& tags) const;
    std::vector<GalleryEntry> GetFractalsByGeneration(int minGen, int maxGen) const;
    
    // Persistencia
    bool SaveToFile(const std::string& filename) const;
    bool LoadFromFile(const std::string& filename);
    bool ExportThumbnails(const std::string& directory) const;
    
    // Estadísticas
    int GetCount() const { return static_cast<int>(m_entries.size()); }
    float GetAverageFitness() const;
    GalleryEntry GetBestFractal() const;
    
private:
    std::string m_galleryPath;
    std::vector<GalleryEntry> m_entries;
    mutable std::mutex m_entriesMutex;
    
    void GenerateThumbnail(GalleryEntry& entry);
    std::string GenerateUniqueName(const std::string& baseName) const;
};