#pragma once
#include <memory>
#include <random>
#include "FractalTypes.h"

// Forward declarations
class DeformableFractal;
class Complex;
struct DeformState;
enum class DeformFunction : int;

class FractalGenerator {
public:
    FractalGenerator(unsigned int seed = 0) : m_currentSeed(seed) {}
    virtual ~FractalGenerator() = default;

    virtual std::unique_ptr<DeformableFractal> GenerateRandom() = 0;
    virtual std::unique_ptr<DeformableFractal> GenerateFromSeed(unsigned int seed) = 0;
    
    void SetSeed(unsigned int seed) { m_currentSeed = seed; }
    unsigned int GetSeed() const { return m_currentSeed; }

protected:
    unsigned int m_currentSeed;
};

class ProceduralFractalGenerator : public FractalGenerator {
public:
    ProceduralFractalGenerator();
    
    std::unique_ptr<DeformableFractal> GenerateRandom() override;
    std::unique_ptr<DeformableFractal> GenerateFromSeed(unsigned int seed) override;
    
    struct GenerationParams {
        float complexityBias = 0.5f;
        float colorfulnessBias = 0.7f;
        bool allowWildFunctions = true;
        bool preferStableFractals = true;
    };
    
    void SetGenerationParams(const GenerationParams& params) { m_params = params; }
    
private:
    GenerationParams m_params;
    std::mt19937 m_rng;
    
    DeformFunction SelectRandomFunction(bool allowWild = true);
    Complex GenerateJuliaConstant();
    DeformState GenerateDeformState();
};