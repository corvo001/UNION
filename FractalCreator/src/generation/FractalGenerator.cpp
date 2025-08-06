#include "FractalGenerator.h"
#include "../Fractals/BaseFractal.h"
#include <chrono>

FractalGenerator::FractalGenerator(unsigned int seed) {
    if (seed == 0) {
        seed = static_cast<unsigned int>(
            std::chrono::high_resolution_clock::now().time_since_epoch().count()
        );
    }
    SetSeed(seed);
}

std::shared_ptr<BaseFractal> FractalGenerator::GenerateRandom() {
    // Por ahora retorna nullptr, implementaremos cuando tengamos fractales
    return nullptr;
}

void FractalGenerator::SetSeed(unsigned int seed) {
    m_currentSeed = seed;
    m_random.seed(seed);
}