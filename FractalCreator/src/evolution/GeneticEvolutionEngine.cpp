#include "GeneticEvolutionEngine.h"
#include "../Fractals/DeformableFractal.h"
#include <algorithm>
#include <chrono>
#include <iostream>
#include "../generation/FractalTypes.h"

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

//=============================================================================
// FractalGenome Implementation
//=============================================================================
void FractalGenome::ApplyToFractal(DeformableFractal* fractal) const {
    // Aplicar genes básicos
    fractal->SetJuliaConstant(Complex(juliaReal.value, juliaImag.value));
    fractal->SetEscapeThreshold(escapeThreshold.value);
    
    // Estados de deformación
    DeformState stateA;
    stateA.angle = angleA.value;
    stateA.freq = freqA.value;
    stateA.phase = phaseA.value;
    stateA.function = static_cast<DeformFunction>(
        static_cast<int>(functionA.value) % static_cast<int>(DeformFunction::COUNT)
    );
    stateA.edgeGlow = edgeGlowA.value;
    stateA.edgeHueShift = edgeHueShiftA.value;
    
    DeformState stateB;
    stateB.angle = angleB.value;
    stateB.freq = freqB.value;
    stateB.phase = phaseB.value;
    stateB.function = static_cast<DeformFunction>(
        static_cast<int>(functionB.value) % static_cast<int>(DeformFunction::COUNT)
    );
    stateB.edgeGlow = edgeGlowB.value;
    stateB.edgeHueShift = edgeHueShiftB.value;
    
    fractal->SetDeformStateA(stateA);
    fractal->SetDeformStateB(stateB);
    
    // Control de blending
    fractal->SetFunctionBlend(functionBlend.value);
    fractal->SetDeformMix(deformMix.value);
    fractal->SetShift(shift.value);
    fractal->SetParameter("edge_saturation", edgeSaturation.value);
}

void FractalGenome::ExtractFromFractal(const DeformableFractal* fractal) {
    Complex julia = fractal->GetJuliaConstant();
    juliaReal.value = static_cast<float>(julia.real);
    juliaImag.value = static_cast<float>(julia.imag);
    escapeThreshold.value = fractal->GetEscapeThreshold();
    
    DeformState stateA = fractal->GetDeformStateA();
    angleA.value = stateA.angle;
    freqA.value = stateA.freq;
    phaseA.value = stateA.phase;
    functionA.value = static_cast<float>(stateA.function);
    edgeGlowA.value = stateA.edgeGlow;
    edgeHueShiftA.value = stateA.edgeHueShift;
    
    DeformState stateB = fractal->GetDeformStateB();
    angleB.value = stateB.angle;
    freqB.value = stateB.freq;
    phaseB.value = stateB.phase;
    functionB.value = static_cast<float>(stateB.function);
    edgeGlowB.value = stateB.edgeGlow;
    edgeHueShiftB.value = stateB.edgeHueShift;
    
    functionBlend.value = fractal->GetFunctionBlend();
    deformMix.value = fractal->GetDeformMix();
    shift.value = fractal->GetShift();
}

void FractalGenome::Mutate(std::mt19937& rng, float globalMutationRate) {
    auto mutateGene = [&](Gene& gene) {
        if (std::uniform_real_distribution<float>(0.0f, 1.0f)(rng) < gene.mutationRate * globalMutationRate) {
            std::normal_distribution<float> dist(0.0f, (gene.max - gene.min) * 0.1f);
            gene.value += dist(rng);
            gene.value = std::clamp(gene.value, gene.min, gene.max);
        }
    };
    
    // Mutar todos los genes
    mutateGene(juliaReal);
    mutateGene(juliaImag);
    mutateGene(escapeThreshold);
    
    mutateGene(angleA);
    mutateGene(freqA);
    mutateGene(phaseA);
    mutateGene(functionA);
    mutateGene(edgeGlowA);
    mutateGene(edgeHueShiftA);
    
    mutateGene(angleB);
    mutateGene(freqB);
    mutateGene(phaseB);
    mutateGene(functionB);
    mutateGene(edgeGlowB);
    mutateGene(edgeHueShiftB);
    
    mutateGene(functionBlend);
    mutateGene(deformMix);
    mutateGene(shift);
    mutateGene(edgeSaturation);
}

FractalGenome FractalGenome::Crossover(const FractalGenome& parent1, const FractalGenome& parent2, std::mt19937& rng) {
    FractalGenome child;
    std::uniform_real_distribution<float> dist(0.0f, 1.0f);
    
    auto crossoverGene = [&](const Gene& gene1, const Gene& gene2) -> Gene {
        Gene result = gene1;
        if (dist(rng) < 0.5f) {
            result.value = gene2.value;
        }
        // Heredar tasas de mutación promediadas
        result.mutationRate = (gene1.mutationRate + gene2.mutationRate) * 0.5f;
        return result;
    };
    
    // Crossover de todos los genes
    child.juliaReal = crossoverGene(parent1.juliaReal, parent2.juliaReal);
    child.juliaImag = crossoverGene(parent1.juliaImag, parent2.juliaImag);
    child.escapeThreshold = crossoverGene(parent1.escapeThreshold, parent2.escapeThreshold);
    
    child.angleA = crossoverGene(parent1.angleA, parent2.angleA);
    child.freqA = crossoverGene(parent1.freqA, parent2.freqA);
    child.phaseA = crossoverGene(parent1.phaseA, parent2.phaseA);
    child.functionA = crossoverGene(parent1.functionA, parent2.functionA);
    child.edgeGlowA = crossoverGene(parent1.edgeGlowA, parent2.edgeGlowA);
    child.edgeHueShiftA = crossoverGene(parent1.edgeHueShiftA, parent2.edgeHueShiftA);
    
    child.angleB = crossoverGene(parent1.angleB, parent2.angleB);
    child.freqB = crossoverGene(parent1.freqB, parent2.freqB);
    child.phaseB = crossoverGene(parent1.phaseB, parent2.phaseB);
    child.functionB = crossoverGene(parent1.functionB, parent2.functionB);
    child.edgeGlowB = crossoverGene(parent1.edgeGlowB, parent2.edgeGlowB);
    child.edgeHueShiftB = crossoverGene(parent1.edgeHueShiftB, parent2.edgeHueShiftB);
    
    child.functionBlend = crossoverGene(parent1.functionBlend, parent2.functionBlend);
    child.deformMix = crossoverGene(parent1.deformMix, parent2.deformMix);
    child.shift = crossoverGene(parent1.shift, parent2.shift);
    child.edgeSaturation = crossoverGene(parent1.edgeSaturation, parent2.edgeSaturation);
    
    child.parentIDs = {parent1.generation, parent2.generation};
    
    return child;
}

float FractalGenome::CalculateDistance(const FractalGenome& other) const {
    float distance = 0.0f;
    
    distance += std::abs(juliaReal.value - other.juliaReal.value);
    distance += std::abs(juliaImag.value - other.juliaImag.value);
    distance += std::abs(escapeThreshold.value - other.escapeThreshold.value);
    
    distance += std::abs(angleA.value - other.angleA.value);
    distance += std::abs(freqA.value - other.freqA.value);
    distance += std::abs(phaseA.value - other.phaseA.value);
    distance += std::abs(functionA.value - other.functionA.value);
    
    distance += std::abs(angleB.value - other.angleB.value);
    distance += std::abs(freqB.value - other.freqB.value);
    distance += std::abs(phaseB.value - other.phaseB.value);
    distance += std::abs(functionB.value - other.functionB.value);
    
    return distance;
}

//=============================================================================
// FitnessEvaluator Implementation
//=============================================================================
FitnessEvaluator::FitnessEvaluator(int imageSize) : m_imageSize(imageSize) {}

float FitnessEvaluator::EvaluateFitness(const DeformableFractal* fractal, const FitnessWeights& weights) {
    // Simplified fitness evaluation
    std::vector<float> imageData = RenderFractalToImage(fractal);
    
    float fitness = 0.0f;
    fitness += weights.complexity * EvaluateComplexity(imageData);
    fitness += weights.symmetry * EvaluateSymmetry(imageData);
    fitness += weights.colorDiversity * EvaluateColorDiversity(imageData);
    fitness += weights.edgeDefinition * EvaluateEdgeDefinition(imageData);
    fitness += weights.stability * EvaluateStability(fractal);
    fitness += weights.performance * EvaluatePerformance(fractal);
    
    return std::clamp(fitness, 0.0f, 1.0f);
}

float FitnessEvaluator::EvaluateFitness(const FractalGenome& genome, const FitnessWeights& weights) {
    DeformableFractal fractal;
    genome.ApplyToFractal(&fractal);
    return EvaluateFitness(&fractal, weights);
}

std::vector<float> FitnessEvaluator::RenderFractalToImage(const DeformableFractal* fractal) {
    std::vector<float> imageData(m_imageSize * m_imageSize);
    
    for (int y = 0; y < m_imageSize; y++) {
        for (int x = 0; x < m_imageSize; x++) {
            float u = (x - m_imageSize/2.0f) / (m_imageSize/2.0f) * 2.0f;
            float v = (y - m_imageSize/2.0f) / (m_imageSize/2.0f) * 2.0f;
            
            Complex point(u, v);
            float value = fractal->CalculateSmooth(point) / fractal->GetMaxIterations();
            imageData[y * m_imageSize + x] = value;
        }
    }
    
    return imageData;
}

float FitnessEvaluator::EvaluateComplexity(const std::vector<float>& imageData) {
    float complexity = 0.0f;
    int size = m_imageSize;
    
    for (int y = 1; y < size - 1; y++) {
        for (int x = 1; x < size - 1; x++) {
            float center = imageData[y * size + x];
            float variance = 0.0f;
            
            for (int dy = -1; dy <= 1; dy++) {
                for (int dx = -1; dx <= 1; dx++) {
                    float neighbor = imageData[(y + dy) * size + (x + dx)];
                    float diff = neighbor - center;
                    variance += diff * diff;
                }
            }
            
            complexity += std::sqrt(variance / 9.0f);
        }
    }
    
    return std::min(1.0f, complexity / (size * size * 0.1f));
}

float FitnessEvaluator::EvaluateSymmetry(const std::vector<float>& imageData) {
    float symmetryScore = 0.0f;
    int size = m_imageSize;
    int comparisons = 0;
    
    for (int y = 0; y < size; y++) {
        for (int x = 0; x < size / 2; x++) {
            float left = imageData[y * size + x];
            float right = imageData[y * size + (size - 1 - x)];
            symmetryScore += 1.0f - std::abs(left - right);
            comparisons++;
        }
    }
    
    return symmetryScore / comparisons;
}

float FitnessEvaluator::EvaluateColorDiversity(const std::vector<float>& imageData) {
    // Simple histogram-based diversity
    const int bins = 10;
    std::vector<int> histogram(bins, 0);
    
    for (float value : imageData) {
        int bin = std::min(bins - 1, static_cast<int>(value * bins));
        histogram[bin]++;
    }
    
    float diversity = 0.0f;
    int total = imageData.size();
    for (int count : histogram) {
        if (count > 0) {
            float p = static_cast<float>(count) / total;
            diversity -= p * std::log(p);
        }
    }
    
    return diversity / std::log(static_cast<float>(bins));
}

float FitnessEvaluator::EvaluateEdgeDefinition(const std::vector<float>& imageData) {
    float edgeStrength = 0.0f;
    int size = m_imageSize;
    
    for (int y = 1; y < size - 1; y++) {
        for (int x = 1; x < size - 1; x++) {
            float center = imageData[y * size + x];
            float dx = imageData[y * size + (x + 1)] - imageData[y * size + (x - 1)];
            float dy = imageData[(y + 1) * size + x] - imageData[(y - 1) * size + x];
            edgeStrength += std::sqrt(dx * dx + dy * dy);
        }
    }
    
    return std::min(1.0f, edgeStrength / (size * size * 0.5f));
}

float FitnessEvaluator::EvaluateStability(const DeformableFractal* fractal) {
    // Check if fractal parameters are in stable ranges
    Complex julia = fractal->GetJuliaConstant();
    float juliaMag = julia.Magnitude();
    return std::exp(-juliaMag * juliaMag / 4.0f);
}

float FitnessEvaluator::EvaluatePerformance(const DeformableFractal* fractal) {
    // Simple performance metric based on max iterations
    float iterScore = 1.0f - (fractal->GetMaxIterations() / 1000.0f);
    return std::max(0.0f, iterScore);
}

//=============================================================================
// GeneticEvolutionEngine Implementation
//=============================================================================
GeneticEvolutionEngine::GeneticEvolutionEngine(const EvolutionParameters& params)
    : m_params(params) {
    m_fitnessEvaluator = std::make_unique<FitnessEvaluator>(256);
}

GeneticEvolutionEngine::~GeneticEvolutionEngine() {
    StopEvolution();
}

void GeneticEvolutionEngine::Initialize(unsigned int seed) {
    m_rng.seed(seed);
    InitializeRandomPopulation();
}

void GeneticEvolutionEngine::StartEvolution() {
    if (!m_running) {
        m_running = true;
        m_evolutionThread = std::make_unique<std::thread>(&GeneticEvolutionEngine::EvolutionLoop, this);
    }
}

void GeneticEvolutionEngine::StopEvolution() {
    m_running = false;
    if (m_evolutionThread && m_evolutionThread->joinable()) {
        m_evolutionThread->join();
    }
}

void GeneticEvolutionEngine::PauseEvolution() {
    m_paused = true;
}

void GeneticEvolutionEngine::ResumeEvolution() {
    m_paused = false;
}

std::vector<FractalGenome> GeneticEvolutionEngine::GetCurrentGeneration() const {
    std::lock_guard<std::mutex> lock(m_populationMutex);
    return m_population;
}

FractalGenome GeneticEvolutionEngine::GetBestIndividual() const {
    std::lock_guard<std::mutex> lock(m_populationMutex);
    if (m_population.empty()) {
        return FractalGenome();
    }
    
    auto best = std::max_element(m_population.begin(), m_population.end(),
        [](const FractalGenome& a, const FractalGenome& b) {
            return a.fitness < b.fitness;
        });
    
    return *best;
}

void GeneticEvolutionEngine::InitializeRandomPopulation() {
    m_population.clear();
    m_population.reserve(m_params.populationSize);
    
    for (int i = 0; i < m_params.populationSize; i++) {
        FractalGenome genome;
        genome.Mutate(m_rng, 5.0f); // Strong initial mutation
        genome.generation = 0;
        m_population.push_back(genome);
    }
}

void GeneticEvolutionEngine::EvolutionLoop() {
    InitializeRandomPopulation();
    
    while (m_running && m_stats.currentGeneration < m_params.maxGenerations) {
        if (m_paused) {
            std::this_thread::sleep_for(std::chrono::milliseconds(100));
            continue;
        }
        
        EvaluatePopulation();
        UpdateStats();
        
        if (m_stats.bestFitness >= m_params.targetFitness || 
            m_stats.stagnationCount >= m_params.stagnationGenerations) {
            break;
        }
        
        std::vector<int> parents;
        SelectParents(parents);
        GenerateOffspring(parents);
        
        if (m_generationCallback) {
            m_generationCallback(m_stats.currentGeneration, m_stats);
        }
        
        m_stats.currentGeneration++;
    }
}

void GeneticEvolutionEngine::EvaluatePopulation() {
    for (auto& genome : m_population) {
        genome.fitness = m_fitnessEvaluator->EvaluateFitness(genome, m_params.fitnessWeights);
    }
}

void GeneticEvolutionEngine::SelectParents(std::vector<int>& parents) {
    parents.clear();
    int numParents = m_params.populationSize / 2;
    
    for (int i = 0; i < numParents; i++) {
        parents.push_back(TournamentSelection());
    }
}

void GeneticEvolutionEngine::GenerateOffspring(const std::vector<int>& parents) {
    std::vector<FractalGenome> newPopulation;
    newPopulation.reserve(m_params.populationSize);
    
    // Keep elite
    int eliteCount = static_cast<int>(m_params.populationSize * m_params.elitePercentage);
    SortPopulationByFitness();
    for (int i = 0; i < eliteCount; i++) {
        newPopulation.push_back(m_population[i]);
    }
    
    // Generate offspring
    while (newPopulation.size() < static_cast<size_t>(m_params.populationSize)) {
        int parent1Idx = parents[m_rng() % parents.size()];
        int parent2Idx = parents[m_rng() % parents.size()];
        
        FractalGenome child = FractalGenome::Crossover(
            m_population[parent1Idx], 
            m_population[parent2Idx], 
            m_rng
        );
        
        child.Mutate(m_rng, m_params.mutationRate);
        child.generation = m_stats.currentGeneration + 1;
        newPopulation.push_back(child);
    }
    
    m_population = newPopulation;
}

int GeneticEvolutionEngine::TournamentSelection(int tournamentSize) {
    int best = m_rng() % m_population.size();
    float bestFitness = m_population[best].fitness;
    
    for (int i = 1; i < tournamentSize; i++) {
        int candidate = m_rng() % m_population.size();
        if (m_population[candidate].fitness > bestFitness) {
            best = candidate;
            bestFitness = m_population[candidate].fitness;
        }
    }
    
    return best;
}

void GeneticEvolutionEngine::SortPopulationByFitness() {
    std::sort(m_population.begin(), m_population.end(),
        [](const FractalGenome& a, const FractalGenome& b) {
            return a.fitness > b.fitness;
        });
}

void GeneticEvolutionEngine::UpdateStats() {
    if (m_population.empty()) return;
    
    SortPopulationByFitness();
    m_stats.bestFitness = m_population[0].fitness;
    
    float sum = 0.0f;
    for (const auto& genome : m_population) {
        sum += genome.fitness;
    }
    m_stats.averageFitness = sum / m_population.size();
    
    if (m_bestFoundCallback && m_stats.bestFitness > 0.9f) {
        m_bestFoundCallback(m_population[0], m_stats.bestFitness);
    }
}

//=============================================================================
// FractalGallery Implementation (Simplified)
//=============================================================================
FractalGallery::FractalGallery(const std::string& galleryPath) 
    : m_galleryPath(galleryPath) {}

void FractalGallery::AddFractal(const FractalGenome& genome, float fitness,
                                const std::string& name, const std::string& description) {
    std::lock_guard<std::mutex> lock(m_entriesMutex);
    
    GalleryEntry entry;
    entry.genome = genome;
    entry.fitness = fitness;
    entry.name = name.empty() ? GenerateUniqueName("Fractal") : name;
    entry.description = description;
    entry.generation = genome.generation;
    entry.creationTime = std::chrono::system_clock::now();
    
    m_entries.push_back(entry);
}

std::vector<FractalGallery::GalleryEntry> FractalGallery::GetAllFractals() const {
    std::lock_guard<std::mutex> lock(m_entriesMutex);
    return m_entries;
}

std::vector<FractalGallery::GalleryEntry> FractalGallery::GetTopFractals(int count) const {
    std::lock_guard<std::mutex> lock(m_entriesMutex);
    
    std::vector<GalleryEntry> sorted = m_entries;
    std::sort(sorted.begin(), sorted.end(),
        [](const GalleryEntry& a, const GalleryEntry& b) {
            return a.fitness > b.fitness;
        });
    
    if (sorted.size() > static_cast<size_t>(count)) {
        sorted.resize(count);
    }
    
    return sorted;
}

std::string FractalGallery::GenerateUniqueName(const std::string& baseName) const {
    int counter = 1;
    std::string uniqueName = baseName;
    
    while (std::any_of(m_entries.begin(), m_entries.end(),
        [&uniqueName](const GalleryEntry& e) { return e.name == uniqueName; })) {
        uniqueName = baseName + "_" + std::to_string(counter++);
    }
    
    return uniqueName;
}