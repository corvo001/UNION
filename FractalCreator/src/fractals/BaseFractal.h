#pragma once
#include "../Math/Complex.h"
#include <string>
#include <map>
#include <memory>

class BaseFractal {
public:
    virtual ~BaseFractal() = default;
    
    // Interfaz principal para cálculo
    virtual int ComputeIterations(const Complex& c) const = 0;
    virtual int GetMaxIterations() const { return m_maxIterations; }
    virtual std::string GetName() const = 0;
    
    // Sistema de parámetros
    virtual void SetParameter(const std::string& name, double value);
    virtual double GetParameter(const std::string& name) const;
    virtual std::map<std::string, double> GetAllParameters() const;
    
    // Generación procedural
    virtual void Randomize(unsigned int seed);
    virtual void Mutate(float strength = 0.1f);
    virtual std::unique_ptr<BaseFractal> Clone() const = 0;
    
    // Configuración básica
    void SetMaxIterations(int maxIter) { m_maxIterations = maxIter; }
    
protected:
    std::map<std::string, double> m_parameters;
    int m_maxIterations = 100;
    unsigned int m_seed = 0;
    
    // Utilidad para mutación aleatoria
    double RandomRange(double min, double max) const;
};
