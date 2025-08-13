#include "FractalGenerator.h"
#include "../Fractals/DeformableFractal.h"
#include <chrono>
#include <vector>
#include "../generation/FractalTypes.h"

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

// ProceduralFractalGenerator Implementation
ProceduralFractalGenerator::ProceduralFractalGenerator() : FractalGenerator() {
    auto seed = std::chrono::high_resolution_clock::now().time_since_epoch().count();
    m_rng.seed(static_cast<unsigned int>(seed));
}

std::unique_ptr<DeformableFractal> ProceduralFractalGenerator::GenerateRandom() {
    auto seed = std::chrono::high_resolution_clock::now().time_since_epoch().count();
    return GenerateFromSeed(static_cast<unsigned int>(seed));
}

std::unique_ptr<DeformableFractal> ProceduralFractalGenerator::GenerateFromSeed(unsigned int seed) {
    m_rng.seed(seed);
    m_currentSeed = seed;
    
    auto fractal = std::make_unique<DeformableFractal>();
    
    // Generate Julia constant
    fractal->SetJuliaConstant(GenerateJuliaConstant());
    
    // Generate deform states
    fractal->SetDeformStateA(GenerateDeformState());
    fractal->SetDeformStateB(GenerateDeformState());
    
    // Generate blending parameters
    std::uniform_real_distribution<float> dis(0.0f, 1.0f);
    fractal->SetFunctionBlend(dis(m_rng));
    fractal->SetDeformMix(dis(m_rng));
    fractal->SetShift(dis(m_rng) * 2.0f - 1.0f);
    
    // Set iterations based on complexity bias
    int iterations = 100 + static_cast<int>(m_params.complexityBias * 200);
    fractal->SetMaxIterations(iterations);
    
    return fractal;
}

Complex ProceduralFractalGenerator::GenerateJuliaConstant() {
    std::uniform_real_distribution<float> dis(-1.0f, 1.0f);
    
    // Some known good Julia constants with random variation
    std::vector<Complex> goodConstants = {
        Complex(-0.4, 0.6),
        Complex(-0.75, 0.11),
        Complex(-0.8, 0.156),
        Complex(-0.7269, 0.1889),
        Complex(0.285, 0.01),
        Complex(-0.835, -0.2321),
        Complex(-0.123, 0.745)
    };
    
    std::uniform_int_distribution<size_t> indexDis(0, goodConstants.size() - 1);
    Complex base = goodConstants[indexDis(m_rng)];
    
    // Add some variation
    float variation = 0.1f;
    base.real += dis(m_rng) * variation;
    base.imag += dis(m_rng) * variation;
    
    return base;
}

DeformState ProceduralFractalGenerator::GenerateDeformState() {
    DeformState state;
    
    std::uniform_real_distribution<float> angleDis(-static_cast<float>(M_PI), static_cast<float>(M_PI));
    std::uniform_real_distribution<float> freqDis(0.5f, 3.0f);
    std::uniform_real_distribution<float> phaseDis(0.0f, 2.0f * static_cast<float>(M_PI));
    std::uniform_real_distribution<float> glowDis(0.5f, 2.0f);
    std::uniform_real_distribution<float> hueDis(0.5f, 2.0f);
    
    state.angle = angleDis(m_rng);
    state.freq = freqDis(m_rng);
    state.phase = phaseDis(m_rng);
    state.function = SelectRandomFunction(m_params.allowWildFunctions);
    state.edgeGlow = glowDis(m_rng);
    state.edgeHueShift = hueDis(m_rng);
    
    return state;
}

DeformFunction ProceduralFractalGenerator::SelectRandomFunction(bool allowWild) {
    std::vector<DeformFunction> safeFunctions = {
        DeformFunction::SIN,
        DeformFunction::COS,
        DeformFunction::ABS,
        DeformFunction::ATAN
    };
    
    std::vector<DeformFunction> wildFunctions = {
        DeformFunction::SINH,
        DeformFunction::COSH,
        DeformFunction::SQRT_ABS,
        DeformFunction::TAN,
        DeformFunction::SIN_ABS,
        DeformFunction::COS_SQUARE
    };
    
    if (allowWild && std::uniform_real_distribution<float>(0.0f, 1.0f)(m_rng) < 0.3f) {
        std::uniform_int_distribution<size_t> dis(0, wildFunctions.size() - 1);
        return wildFunctions[dis(m_rng)];
    } else {
        std::uniform_int_distribution<size_t> dis(0, safeFunctions.size() - 1);
        return safeFunctions[dis(m_rng)];
    }
}