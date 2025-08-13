#include "MutatorUniversal.h"
#include <algorithm>
#include <cmath>

// ===== Perlin1D =====
void Perlin1D::reseed(uint32_t seed) {
    // Permutación clásica Perlin
    std::array<int, 256> perm;
    for (int i=0;i<256;++i) perm[i] = i;
    std::mt19937 gen(seed);
    std::shuffle(perm.begin(), perm.end(), gen);
    for (int i=0;i<256;++i) p_[i] = perm[i];
}

float Perlin1D::noise(float x) const {
    int X = static_cast<int>(std::floor(x)) & 255;
    float xf = x - std::floor(x);
    float u = fade(xf);
    float n0 = grad(p_[X],     xf);
    float n1 = grad(p_[(X+1)&255], xf-1.0f);
    return lerp(n0, n1, u) * 0.188f; // normalización aprox. para ~[-1,1]
}

// ===== MutatorUniversal =====
MutatorUniversal::MutatorUniversal(uint64_t seed) : rng_(seed ? seed : std::random_device{}()) {
    // Semillas distintas para cada canal de ruido
    pnFreq_.reseed(static_cast<uint32_t>(rng_()));
    pnShift_.reseed(static_cast<uint32_t>(rng_()));
    pnAngle_.reseed(static_cast<uint32_t>(rng_()));
    pnPhase_.reseed(static_cast<uint32_t>(rng_()));
    pnZoom_.reseed(static_cast<uint32_t>(rng_()));
    pnOffX_.reseed(static_cast<uint32_t>(rng_()));
    pnOffY_.reseed(static_cast<uint32_t>(rng_()));
    pnCRe_.reseed(static_cast<uint32_t>(rng_()));
    pnCIm_.reseed(static_cast<uint32_t>(rng_()));
}

float MutatorUniversal::smoothstep(float x) const {
    // suaviza la lerp A->B para evitar acelerones
    x = clampf(x, 0.f, 1.f);
    return x*x*(3.f - 2.f*x);
}

float MutatorUniversal::randIn(float a, float b) {
    return a + (b - a) * unif01_(rng_);
}

void MutatorUniversal::pickNewTarget() {
    target_.freq   = randIn(ranges_.freqMin,  ranges_.freqMax);
    target_.shift  = randIn(ranges_.shiftMin, ranges_.shiftMax);
    target_.angle  = randIn(ranges_.angleMin, ranges_.angleMax);
    target_.phase  = randIn(ranges_.phaseMin, ranges_.phaseMax);
    target_.zoom   = randIn(ranges_.zoomMin,  ranges_.zoomMax);
    target_.offsetX= randIn(ranges_.offMin,   ranges_.offMax);
    target_.offsetY= randIn(ranges_.offMin,   ranges_.offMax);
    target_.cRe    = randIn(ranges_.cMin,     ranges_.cMax);
    target_.cIm    = randIn(ranges_.cMin,     ranges_.cMax);

    // Duración de interpolación y “hold” aleatorios (dentro de rangos de config)
    segDur_ = clampf(randIn(cfg_.targetLerpTime*0.7f, cfg_.targetLerpTime*1.3f), 1.5f, 10.0f);
    hold_   = cfg_.autoTargets ? randIn(cfg_.minHold, cfg_.maxHold) : 0.0f;
    seg_ = 0.0f;
}

void MutatorUniversal::randomize(FractalParams& params) {
    pickNewTarget();
    current_ = target_; // arranca en un estado aleatorio válido
    params = current_;
    // y busca un siguiente objetivo para empezar a moverse
    pickNewTarget();
}

void MutatorUniversal::newTarget() {
    pickNewTarget();
}

void MutatorUniversal::setCurrent(const FractalParams& p) {
    current_ = p;
}

FractalParams MutatorUniversal::lerpParams(const FractalParams& a, const FractalParams& b, float k) {
    FractalParams r{};
    auto L = [&](float x, float y){ return x + (y - x) * k; };
    r.freq   = L(a.freq,   b.freq);
    r.shift  = L(a.shift,  b.shift);
    r.angle  = L(a.angle,  b.angle);
    r.phase  = L(a.phase,  b.phase);
    r.zoom   = L(a.zoom,   b.zoom);
    r.offsetX= L(a.offsetX,b.offsetX);
    r.offsetY= L(a.offsetY,b.offsetY);
    r.cRe    = L(a.cRe,    b.cRe);
    r.cIm    = L(a.cIm,    b.cIm);
    return r;
}

// Mezcla seno + Perlin limitada por rangos
float MutatorUniversal::modulate(float base, float t, float lfoHz, float noiseAmp, float perlinPhase,
                                 float minV, float maxV)
{
    // Seno lento centrado en 0
    float s = std::sin(2.0f * 3.14159265f * lfoHz * t);

    // Perlin 1D también centrado en 0
    float n = 0.0f;
    // Avance del perlin con el tiempo y un desfase por canal
    float perlinX = t * cfg_.perlinRate + perlinPhase;
    // Ruido en [-1,1]
    n = pnFreq_.noise(perlinX); // NOTA: la instancia concreta se sustituye fuera

    // Mezcla: (1 - mix)*seno + mix*ruido
    float mixed = (1.0f - cfg_.noiseMix) * s + (cfg_.noiseMix) * n;

    float outV = base + mixed * noiseAmp;
    return clampf(outV, minV, maxV);
}

FractalParams MutatorUniversal::update(float dt) {
    t_   += dt;

    // Fase de interpolación A->B + hold
    FractalParams base = current_;
    if (seg_ < segDur_) {
        seg_ += dt;
        float k = smoothstep(seg_ / segDur_);
        base = lerpParams(current_, target_, k);
        if (seg_ >= segDur_ && hold_ <= 0.0f && cfg_.autoTargets) {
            // acabamos de llegar: programar hold
            hold_ = std::max(0.0f, hold_);
        }
    } else if (hold_ > 0.0f) {
        hold_ -= dt;
        if (hold_ <= 0.0f && cfg_.autoTargets) {
            // nuevo objetivo tras hold
            current_ = base; // fija el actual
            pickNewTarget();
        }
    } else if (cfg_.autoTargets) {
        current_ = base;
        pickNewTarget();
    }

    // Modulación continua (sine + perlin). Usamos instancias diferentes por canal:
    // Truco: para reutilizar modulate cambiando la fuente de ruido, reasignamos temporalmente pnFreq_.
    auto swapNoise = [&](Perlin1D& src, auto f){
        Perlin1D backup = pnFreq_;
        pnFreq_ = src;
        float out = f();
        pnFreq_ = backup;
        return out;
    };

    FractalParams out = base;

    out.freq   = swapNoise(pnFreq_,   [&]{ return modulate(base.freq,   t_, cfg_.lfo_freq,  cfg_.noiseAmp_freq,  0.0f, ranges_.freqMin,  ranges_.freqMax); });
    out.shift  = swapNoise(pnShift_,  [&]{ return modulate(base.shift,  t_, cfg_.lfo_shift, cfg_.noiseAmp_shift, 0.0f, ranges_.shiftMin, ranges_.shiftMax); });
    out.angle  = swapNoise(pnAngle_,  [&]{ return modulate(base.angle,  t_, cfg_.lfo_angle, cfg_.noiseAmp_angle, 0.0f, ranges_.angleMin, ranges_.angleMax); });
    out.phase  = swapNoise(pnPhase_,  [&]{ return modulate(base.phase,  t_, cfg_.lfo_phase, cfg_.noiseAmp_phase, 0.0f, ranges_.phaseMin, ranges_.phaseMax); });
    out.zoom   = swapNoise(pnZoom_,   [&]{ return modulate(base.zoom,   t_, cfg_.lfo_zoom,  cfg_.noiseAmp_zoom,  0.0f, ranges_.zoomMin,  ranges_.zoomMax); });
    out.offsetX= swapNoise(pnOffX_,   [&]{ return modulate(base.offsetX,t_, cfg_.lfo_off,   cfg_.noiseAmp_off,   0.0f, ranges_.offMin,   ranges_.offMax); });
    out.offsetY= swapNoise(pnOffY_,   [&]{ return modulate(base.offsetY,t_, cfg_.lfo_off,   cfg_.noiseAmp_off,   0.0f, ranges_.offMin,   ranges_.offMax); });
    out.cRe    = swapNoise(pnCRe_,    [&]{ return modulate(base.cRe,    t_, cfg_.lfo_c,     cfg_.noiseAmp_c,     0.0f, ranges_.cMin,     ranges_.cMax); });
    out.cIm    = swapNoise(pnCIm_,    [&]{ return modulate(base.cIm,    t_, cfg_.lfo_c,     cfg_.noiseAmp_c,     0.0f, ranges_.cMin,     ranges_.cMax); });

    return out;
}
