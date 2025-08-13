#pragma once
#include <string>
#include <unordered_map>
#include "../Math/Complex.h"

class BaseFractal {
public:
    virtual ~BaseFractal() = default;

    // Núcleo que deben implementar los fractales concretos
    virtual int   CalculateIterations(const Complex& point) const = 0;
    virtual float CalculateSmooth    (const Complex& point) const = 0;

    // Hooks opcionales
    virtual void Update(float /*dt*/) {}
    virtual void Randomize(uint32_t /*seed*/) {}

    // Ajustes comunes
    void  SetMaxIterations(int it)          { m_maxIterations = it; }
    int   GetMaxIterations()          const { return m_maxIterations; }

    void  SetEscapeThreshold(float t)       { m_escapeThreshold = t; }
    float GetEscapeThreshold()        const { return m_escapeThreshold; }

    // Mapa genérico de parámetros (para UI / renderer)
    void   SetParameter (const std::string& name, double value);
    double GetParameter (const std::string& name) const;
    bool   HasParameter (const std::string& name) const;

protected:
    int   m_maxIterations   = 200;
    float m_escapeThreshold = 4.0f; // usualmente 2^2

    std::unordered_map<std::string, double> m_parameters;
};



