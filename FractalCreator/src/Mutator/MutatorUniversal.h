#pragma once
#include <random>
#include <cstdint>
#include <array>

// Estructura de parámetros que usará tu shader universal.
// Asegúrate de que los nombres de uniform coinciden con estos campos.
struct FractalParams {
    // Núcleo deformable
    float freq;      // _Freq
    float shift;     // _Shift
    float angle;     // _Angle  (rotación compleja)
    float phase;     // _Phase  (fase para animaciones internas, si la usas)
    // Navegación / cámara
    float zoom;      // _Zoom
    float offsetX;   // _OffsetX
    float offsetY;   // _OffsetY
    // Constante C (opcional si la usas en el núcleo)
    float cRe;       // _CRe
    float cIm;       // _CIm
};

// Utilidad: clamp
static inline float clampf(float v, float lo, float hi) {
    return v < lo ? lo : (v > hi ? hi : v);
}

// Ruido Perlin 1D ligero (suficiente para modulación lenta)
class Perlin1D {
public:
    explicit Perlin1D(uint32_t seed=123456u) { reseed(seed); }
    void reseed(uint32_t seed);
    // Devuelve ruido en [-1, 1]
    float noise(float x) const;
private:
    std::array<int, 256> p_;
    static inline float fade(float t) {
        // curva suave 6t^5 - 15t^4 + 10t^3
        return t*t*t*(t*(t*6.f - 15.f) + 10.f);
    }
    static inline float lerp(float a, float b, float t) { return a + t*(b-a); }
    static inline float grad(int hash, float x) {
        int h = hash & 15;
        float g = 1.0f + (h & 7); // [1,8]
        if (h & 8) g = -g;
        return g * x;
    }
};

// MutatorUniversal: genera objetivos aleatorios y transiciones suaves
class MutatorUniversal {
public:
    struct Ranges {
        // Límites prácticos (ajusta a tu gusto/estabilidad visual)
        float freqMin = 0.05f,  freqMax = 6.0f;
        float shiftMin = -6.2831853f, shiftMax = 6.2831853f; // ±2π
        float angleMin = -3.1415926f, angleMax = 3.1415926f; // ±π
        float phaseMin = 0.0f, phaseMax = 1000.0f; // libre si no lo usas
        float zoomMin  = 0.2f,  zoomMax  = 50.0f;
        float offMin   = -5.0f, offMax   = 5.0f;
        float cMin     = -2.0f, cMax     = 2.0f;
    };

    // Config de mutación y modulación continua
    struct Config {
        // Duración objetivo para interpolar A->B (segundos)
        float targetLerpTime = 4.0f;

        // Intensidad de ruido (mezcla con seno)
        float noiseAmp_freq  = 0.15f;
        float noiseAmp_shift = 0.25f;
        float noiseAmp_angle = 0.10f;
        float noiseAmp_phase = 0.20f;
        float noiseAmp_zoom  = 0.10f;
        float noiseAmp_off   = 0.25f;
        float noiseAmp_c     = 0.15f;

        // Frecuencias (Hz) del seno lento
        float lfo_freq  = 0.07f;
        float lfo_shift = 0.05f;
        float lfo_angle = 0.04f;
        float lfo_phase = 0.11f;
        float lfo_zoom  = 0.03f;
        float lfo_off   = 0.06f;
        float lfo_c     = 0.05f;

        // Velocidad del Perlin (cuánto avanza x por segundo)
        float perlinRate = 0.20f;

        // Cuándo disparar un nuevo objetivo (auto-rotate)
        bool autoTargets = true;
        float minHold = 2.5f;   // mantener un poco el estado al llegar
        float maxHold = 5.0f;

        // Mezcla seno/ruido [0..1] (0 = solo seno, 1 = solo ruido)
        float noiseMix = 0.45f;
    };

    explicit MutatorUniversal(uint64_t seed=0xC0FFEEu);

    // Establece rangos globales si quieres afinarlos
    void setRanges(const Ranges& r) { ranges_ = r; }
    void setConfig(const Config& c) { cfg_ = c; }

    // Inicializa con un estado aleatorio y su primer objetivo
    void randomize(FractalParams& params);

    // Llama cada frame: avanza interpolación + modulación (dt en segundos)
    // Devuelve los parámetros ya modulados/listos para setear en el shader.
    FractalParams update(float dt);

    // Permite forzar nuevo objetivo (por ejemplo, al activar tu toggle "Mutar")
    void newTarget();

    // Para fijar un estado inicial manual (opcional)
    void setCurrent(const FractalParams& p);

    // Consulta lectura
    const FractalParams& current() const { return current_; }
    const FractalParams& target()  const { return target_;  }

private:
    Ranges ranges_;
    Config cfg_;

    std::mt19937_64 rng_;
    std::uniform_real_distribution<float> unif01_{0.0f, 1.0f};

    // Ruido por-canal con seeds distintos
    Perlin1D pnFreq_, pnShift_, pnAngle_, pnPhase_, pnZoom_, pnOffX_, pnOffY_, pnCRe_, pnCIm_;

    // Estado A (current) -> B (target)
    FractalParams current_{};
    FractalParams target_{};

    // Timers
    float t_ = 0.0f;           // tiempo total vivo
    float seg_ = 0.0f;         // tiempo dentro del segmento actual
    float segDur_ = 4.0f;      // duración del segmento A->B
    float hold_ = 0.0f;        // tiempo de “descanso” al llegar a B

    // Internos
    float smoothstep(float x) const;
    float randIn(float a, float b);
    void pickNewTarget();
    float modulate(float base, float t, float lfoHz, float noiseAmp, float perlinPhase, float minV, float maxV);
    FractalParams lerpParams(const FractalParams& a, const FractalParams& b, float k);
};
