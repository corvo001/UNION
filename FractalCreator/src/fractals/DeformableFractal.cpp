#include "DeformableFractal.h"
#include <algorithm>
#include <random>
#include <cmath>

// Asegúrate de incluir también FractalTypes en el .cpp
#include "../generation/FractalTypes.h"

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

DeformableFractal::DeformableFractal() {
    // Estados por defecto
    m_deformStateA.angle    = 0.3f;
    m_deformStateA.freq     = 1.2f;
    m_deformStateA.phase    = 0.0f;
    m_deformStateA.function = DeformFunction::SIN;
    m_deformStateA.edgeGlow = 1.5f;
    m_deformStateA.edgeHueShift = 0.9f;

    m_deformStateB.angle    = -0.2f;
    m_deformStateB.freq     = 1.8f;
    m_deformStateB.phase    = 0.5f;
    m_deformStateB.function = DeformFunction::COS;
    m_deformStateB.edgeGlow = 1.1f;
    m_deformStateB.edgeHueShift = 1.3f;

    // Parámetros expuestos
    m_parameters["julia_real"]     = m_juliaConstant.real;
    m_parameters["julia_imag"]     = m_juliaConstant.imag;
    m_parameters["function_blend"] = m_functionBlend;
    m_parameters["deform_mix"]     = m_deformMix;
    m_parameters["shift"]          = m_shift;
    m_parameters["zoom"]           = 1.0;
    m_parameters["offset_x"]       = 0.0;
    m_parameters["offset_y"]       = 0.0;
}

int DeformableFractal::CalculateIterations(const Complex& point) const {
    Complex z = point;
    Complex c = m_juliaConstant;

    float currentDeformMix = m_deformMix;
    if (m_breathingEnabled) {
        currentDeformMix = 0.5f + 0.5f * std::sin(GetBreathingPhase());
    }

    for (int i = 0; i < m_maxIterations; ++i) {
        Complex deformA = Deform(z, m_deformStateA, m_breathingTime);
        Complex deformB = Deform(z, m_deformStateB, m_breathingTime);
        Complex blended = deformA * (1.0f - currentDeformMix) + deformB * currentDeformMix;

        z = blended * blended + c;

        if (z.MagnitudeSquared() > m_escapeThreshold) {
            return i;
        }
    }
    return m_maxIterations;
}

float DeformableFractal::CalculateSmooth(const Complex& point) const {
    Complex z = point;
    Complex c = m_juliaConstant;

    float currentDeformMix = m_deformMix;
    if (m_breathingEnabled) {
        currentDeformMix = 0.5f + 0.5f * std::sin(GetBreathingPhase());
    }

    for (int i = 0; i < m_maxIterations; ++i) {
        Complex deformA = Deform(z, m_deformStateA, m_breathingTime);
        Complex deformB = Deform(z, m_deformStateB, m_breathingTime);
        Complex blended = deformA * (1.0f - currentDeformMix) + deformB * currentDeformMix;

        z = blended * blended + c;

        if (z.MagnitudeSquared() > m_escapeThreshold) {
            float smooth = i + 1.0f - std::log2(std::log2(z.Magnitude()));
            return std::max(0.0f, smooth);
        }
    }
    return static_cast<float>(m_maxIterations);
}

void DeformableFractal::Update(float dt) {
    if (m_breathingEnabled) m_breathingTime += dt;

    if (m_mutating) {
        m_mutationTime += dt;
        if (m_mutationTime > 2.0f) {
            Randomize(static_cast<uint32_t>(m_mutationTime * 1000.0f));
            m_mutationTime = 0.0f;
        }
    }
}

void DeformableFractal::Randomize(uint32_t seed) {
    std::mt19937 gen(seed);
    std::uniform_real_distribution<float> dis(-1.0f, 1.0f);

    m_juliaConstant = Complex(dis(gen), dis(gen));

    m_deformStateA.angle = dis(gen) * static_cast<float>(M_PI);
    m_deformStateA.freq  = 0.5f + std::abs(dis(gen)) * 2.0f;
    m_deformStateA.phase = dis(gen) * static_cast<float>(M_PI);
    m_deformStateA.function = static_cast<DeformFunction>(
        std::uniform_int_distribution<int>(0, 10)(gen));

    m_deformStateB.angle = dis(gen) * static_cast<float>(M_PI);
    m_deformStateB.freq  = 0.5f + std::abs(dis(gen)) * 2.0f;
    m_deformStateB.phase = dis(gen) * static_cast<float>(M_PI);
    m_deformStateB.function = static_cast<DeformFunction>(
        std::uniform_int_distribution<int>(0, 10)(gen));

    m_parameters["julia_real"] = m_juliaConstant.real;
    m_parameters["julia_imag"] = m_juliaConstant.imag;
}

void DeformableFractal::EnableBreathing(bool enable) {
    m_breathingEnabled = enable;
    if (!enable) m_breathingTime = 0.0f; // opcional, reinicia tiempo
}

void DeformableFractal::SetBreathingDuration(float seconds) {
    m_breathingDuration = (seconds > 0.0f) ? seconds : 1.0f;
}

// ===== Helpers =====

Complex DeformableFractal::ApplyFunction(const Complex& z, DeformFunction func) const {
    switch (func) {
    case DeformFunction::SIN:
        return Complex(std::sin(z.real) * std::cosh(z.imag),
                       std::cos(z.real) * std::sinh(z.imag));
    case DeformFunction::COS:
        return Complex(std::cos(z.real) * std::cosh(z.imag),
                      -std::sin(z.real) * std::sinh(z.imag));
    case DeformFunction::ABS:
        return Complex(std::abs(z.real), std::abs(z.imag));
    case DeformFunction::SINH:
        return Complex(std::sinh(z.real) * std::cos(z.imag),
                       std::cosh(z.real) * std::sin(z.imag));
    case DeformFunction::COSH:
        return Complex(std::cosh(z.real) * std::cos(z.imag),
                       std::sinh(z.real) * std::sin(z.imag));
    case DeformFunction::ATAN:
        return Complex(std::atan(z.real), std::atan(z.imag));
    case DeformFunction::SQRT_ABS:
        return Complex(std::sqrt(std::abs(z.real)), std::sqrt(std::abs(z.imag)));
    case DeformFunction::ASIN:
        return Complex(std::asin(std::clamp(z.real, -1.0, 1.0)),
                       std::asin(std::clamp(z.imag, -1.0, 1.0)));
    case DeformFunction::TAN:
        return Complex(std::tan(z.real), std::tanh(z.imag));
    case DeformFunction::SIN_ABS:
        return Complex(std::sin(std::abs(z.real)), std::sin(std::abs(z.imag)));
    case DeformFunction::COS_SQUARE: {
        double cr = std::cos(z.real);
        double ci = std::cos(z.imag);
        return Complex(cr * cr, ci * ci);
    }
    default:
        return z;
    }
}

Complex DeformableFractal::Deform(const Complex& z, const DeformState& state, float /*time*/) const {
    Complex rotated = Rotate(z, state.angle);
    Complex scaled = z * state.freq + Complex(m_shift + state.phase, 0.0f);
    Complex transformed = ApplyFunction(scaled, state.function);
    return rotated + transformed * 0.5f;
}

Complex DeformableFractal::Rotate(const Complex& z, float angle) const {
    float c = std::cos(angle);
    float s = std::sin(angle);
    return Complex(c * z.real - s * z.imag, s * z.real + c * z.imag);
}

float DeformableFractal::GetBreathingPhase() const {
    return (m_breathingTime / m_breathingDuration) * 2.0f * static_cast<float>(M_PI);
}

// ===== Getters / Setters =====

void DeformableFractal::SetJuliaConstant(const Complex& c) {
    m_juliaConstant = c;
    m_parameters["julia_real"] = c.real;
    m_parameters["julia_imag"] = c.imag;
}

Complex DeformableFractal::GetJuliaConstant() const {
    return m_juliaConstant;
}

void DeformableFractal::SetDeformStateA(const DeformState& s) { m_deformStateA = s; }
void DeformableFractal::SetDeformStateB(const DeformState& s) { m_deformStateB = s; }

const DeformState& DeformableFractal::GetDeformStateA() const { return m_deformStateA; }
const DeformState& DeformableFractal::GetDeformStateB() const { return m_deformStateB; }

void  DeformableFractal::SetFunctionBlend(float v) { m_functionBlend = v; m_parameters["function_blend"] = v; }
float DeformableFractal::GetFunctionBlend() const  { return m_functionBlend; }

void  DeformableFractal::SetDeformMix(float v) { m_deformMix = v; m_parameters["deform_mix"] = v; }
float DeformableFractal::GetDeformMix() const  { return m_deformMix; }

void  DeformableFractal::SetShift(float v) { m_shift = v; m_parameters["shift"] = v; }
float DeformableFractal::GetShift() const  { return m_shift; }
