#include "Mandelbrot.h"
#include <random>

Mandelbrot::Mandelbrot() {
    SetParameter("escape_radius", DEFAULT_ESCAPE_RADIUS);
    SetParameter("power", 2.0); // Para z^power + c
}

int Mandelbrot::ComputeIterations(const Complex& c) const {
    Complex z(0.0, 0.0);
    double escapeRadius = GetParameter("escape_radius");
    double power = GetParameter("power");
    double escapeRadiusSquared = escapeRadius * escapeRadius;
    
    for (int i = 0; i < m_maxIterations; ++i) {
        if (z.MagnitudeSquared() > escapeRadiusSquared) {
            return i;
        }
        
        // Fórmula básica: z = z^2 + c
        // TODO: Implementar potencias arbitrarias para más variedad
        z = z * z + c;
    }
    
    return m_maxIterations; // Punto está en el conjunto
}

std::unique_ptr<BaseFractal> Mandelbrot::Clone() const {
    auto clone = std::make_unique<Mandelbrot>();
    clone->m_parameters = this->m_parameters;
    clone->m_maxIterations = this->m_maxIterations;
    clone->m_seed = this->m_seed;
    return std::move(clone);
}

void Mandelbrot::Randomize(unsigned int seed) {
    BaseFractal::Randomize(seed);
    
    std::mt19937 rng(seed);
    std::uniform_real_distribution<double> radiusDist(1.5, 4.0);
    std::uniform_real_distribution<double> powerDist(1.5, 3.0);
    
    SetParameter("escape_radius", radiusDist(rng));
    SetParameter("power", powerDist(rng));
}

void Mandelbrot::SetEscapeRadius(double radius) {
    SetParameter("escape_radius", radius);