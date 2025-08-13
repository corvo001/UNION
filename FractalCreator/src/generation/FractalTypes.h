#pragma once

enum class DeformFunction {
    SIN = 0,
    COS,
    ABS,
    ATAN,
    SINH,
    COSH,
    SQRT_ABS,
    ASIN,
    TAN,
    SIN_ABS,
    COS_SQUARE,
    COUNT
}; // ← obligatorio


struct DeformState {
    float angle = 0.0f;
    float freq  = 1.0f;
    float phase = 0.0f;
    DeformFunction function = DeformFunction::SIN;
    float edgeGlow = 1.0f;
    float edgeHueShift = 1.0f;
};
