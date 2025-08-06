#pragma once
#include "BaseFractal.h"

class Mandelbrot : public BaseFractal {
public:
    Mandelbrot();
    
    int ComputeIterations(const Complex& c) const override;
    std::string GetName() const override { return "Mandelbrot"; }
    std::unique_ptr<BaseFractal> Clone() const override;
    
    void Randomize(unsigned int seed) override;
    
    // Parámetros específicos del Mandelbrot
    void SetEscapeRadius(double radius);
    double GetEscapeRadius() const;
    
private:
    static constexpr double DEFAULT_ESCAPE_RADIUS = 2.0;
};