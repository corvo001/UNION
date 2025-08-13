#pragma once
#include "BaseFractal.h"

// IMPORTANTE: usar las definiciones centrales
#include "../generation/FractalTypes.h"   // ajusta la ruta si tu árbol difiere

class DeformableFractal : public BaseFractal {
public:
    DeformableFractal();

    // Implementación del fractal
    int   CalculateIterations(const Complex& point) const override;
    float CalculateSmooth    (const Complex& point) const override;
    void  Update(float dt) override;
    void  Randomize(uint32_t seed) override;

    // API usada por otros módulos
    void    SetJuliaConstant(const Complex& c);
    Complex GetJuliaConstant() const;

    void                 SetDeformStateA(const DeformState& s);
    void                 SetDeformStateB(const DeformState& s);
    const DeformState&   GetDeformStateA() const;
    const DeformState&   GetDeformStateB() const;

    void  SetFunctionBlend(float v);
    float GetFunctionBlend() const;

    void  SetDeformMix(float v);
    float GetDeformMix() const;

    void  SetShift(float v);
    float GetShift() const;// Breathing (animación rítmica del deformMix)

    void EnableBreathing(bool enable);
    bool IsBreathingEnabled() const { return m_breathingEnabled; }
    void SetBreathingDuration(float seconds);
    float GetBreathingDuration() const { return m_breathingDuration; }


private:
    // helpers
    Complex ApplyFunction(const Complex& z, DeformFunction func) const;
    Complex Deform       (const Complex& z, const DeformState& state, float time) const;
    Complex Rotate       (const Complex& z, float angle) const;
    float   GetBreathingPhase() const;

    // estado
    Complex     m_juliaConstant { -0.7f, 0.27015f };
    DeformState m_deformStateA  {};
    DeformState m_deformStateB  {};

    float m_functionBlend = 0.5f;
    float m_deformMix     = 0.5f;
    float m_shift         = 0.0f;

    // animaciones sencillas
    bool  m_breathingEnabled  = false;
    float m_breathingTime     = 0.0f;
    float m_breathingDuration = 4.0f;

    bool  m_mutating     = false;
    float m_mutationTime = 0.0f;
};


