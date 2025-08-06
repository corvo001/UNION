#include "BaseFractal.h"
#include <random>
#include <stdexcept>

void BaseFractal::SetParameter(const std::string& name, double value) {
    m_parameters[name] = value;
}

double BaseFractal::GetParameter(const std::string& name) const {
    auto it = m_parameters.find(name);
    if (it != m_parameters.end()) {
        return it->second;
    }
    throw std::runtime_error("Parameter '" + name + "' not found");
}

std::map<std::string, double> BaseFractal::GetAllParameters() const {
    return m_parameters;
}

void BaseFractal::Randomize(unsigned int seed) {
    m_seed = seed;
    // Las clases derivadas sobrescribirán esto para randomizar sus parámetros
}

void BaseFractal::Mutate(float strength) {
    // Implementación base - las clases derivadas pueden sobrescribir
    std::mt19937 rng(m_seed);
    std::uniform_real_distribution<double> dist(-strength, strength);
    
    for (auto& param : m_parameters) {
        param.second += dist(rng);
    }
}

double BaseFractal::RandomRange(double min, double max) const {
    std::mt19937 rng(m_seed);
    std::uniform_real_distribution<double> dist(min, max);
    return dist(rng);
}