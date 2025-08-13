// src/rendering/FractalRenderer.cpp
#include "Rendering/FractalRenderer.h"
#include "fractals/BaseFractal.h"
#include "fractals/DeformableFractal.h"

#include <vector>
#include <string>
#include <cmath>
#include <ctime>
#include <cstdio>
#include <algorithm>   // <- necesario para std::clamp

// stb: asegúrate de tener external/stb/stb_image_write.h y la carpeta en include dirs
// Solo UN .cpp debe definir STB_IMAGE_WRITE_IMPLEMENTATION en todo el proyecto.
#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "stb/stb_image_write.h"

// ======================= Shaders embebidos =======================
static const char* kVS = R"(#version 330
const vec2 v[3] = vec2[3]( vec2(-1.0,-1.0), vec2(3.0,-1.0), vec2(-1.0,3.0) );
out vec2 uv;
void main(){
    gl_Position = vec4(v[gl_VertexID], 0.0, 1.0);
    uv = 0.5*(v[gl_VertexID]+1.0);
}
)";

// Paletas + deformación A/B + Mandel/Julia + SMOOTH COLORING
static const char* kFS = R"(#version 330
in vec2 uv;
out vec4 FragColor;

uniform vec2  uResolution;
uniform float uZoom;
uniform vec2  uOffset;
uniform vec2  uJulia;
uniform int   uFractalMode;   // 0 mandelbrot, 1 julia
uniform int   uMaxIter;
uniform float uEscape;

uniform int   uMode;          // paleta 0..3
uniform int   uUseSmooth;     // 0=normal, 1=smooth

// Deformación
uniform float uFunctionBlend; // 0..1
uniform float uDeformMix;     // 0..1
uniform float uShift;         // rad

uniform int   uFuncA;         // 0..10
uniform int   uFuncB;         // 0..10
uniform vec3  uA;             // angle, freq, phase
uniform vec3  uB;             // angle, freq, phase

// ---- Palettes ----
vec3 pal_gray(float t){ return vec3(t); }
vec3 pal_cosine(float t){
    const vec3 a=vec3(0.5), b=vec3(0.5), c=vec3(1.0), d=vec3(0.0,0.33,0.67);
    return a + b * cos(6.28318*(c*t + d));
}
vec3 pal_sinrgb(float t){
    return vec3(0.5+0.5*sin(6.28318*(t+0.00)),
                0.5+0.5*sin(6.28318*(t+0.33)),
                0.5+0.5*sin(6.28318*(t+0.67)));
}
vec3 pal_heat(float t){
    t = clamp(t, 0.0, 1.0);
    float r = smoothstep(0.0, 0.3, t);
    float g = smoothstep(0.3, 0.7, t);
    float b = smoothstep(0.7, 1.0, t);
    return vec3(r, 0.4*g + 0.6*t, 0.2*b);
}
vec3 pick_palette(int mode, float t){
    if(mode==0) return pal_gray(t);
    if(mode==1) return pal_cosine(t);
    if(mode==2) return pal_sinrgb(t);
    return pal_heat(t);
}

// ---- Complex helpers ----
mat2 rot(float a){ float c=cos(a), s=sin(a); return mat2(c,-s,s,c); }
vec2 apply_func(vec2 z, int fn, vec3 p, float shift){
    vec2 zr = rot(p.x) * z;
    float t = p.y * (zr.x + zr.y) + p.z + shift;
    if (fn==0)       return vec2(sin(t));
    else if (fn==1)  return vec2(cos(t));
    else if (fn==2)  return vec2(abs(zr.x), abs(zr.y));
    else if (fn==3)  return vec2(sinh(t));
    else if (fn==4)  return vec2(cosh(t));
    else if (fn==5)  return vec2(atan(t));
    else if (fn==6)  return vec2(sqrt(abs(zr.x)), sqrt(abs(zr.y)));
    else if (fn==7)  return vec2(asin(clamp(t,-1.0,1.0)));
    else if (fn==8)  return vec2(tan(t));
    else if (fn==9)  return vec2(abs(sin(t)));
    else if (fn==10) return vec2(cos(t)*cos(t));
    return zr;
}
vec2 deform(vec2 z){
    vec2 a = apply_func(z, uFuncA, uA, uShift);
    vec2 b = apply_func(z, uFuncB, uB, uShift);
    vec2 ab = mix(a, b, clamp(uFunctionBlend, 0.0, 1.0));
    return mix(z, ab, clamp(uDeformMix, 0.0, 1.0));
}

// ---- Iteración con modo "smooth" opcional ----
struct ItRes { float it; float zn2; };

ItRes iterate_raw(vec2 c){
    vec2 z = (uFractalMode==1) ? c : vec2(0.0);
    float i = 0.0;
    float esc2 = uEscape*uEscape;

    for (int k=0; k<100000; ++k){
        if (k >= uMaxIter) break;
        vec2 zd = deform(z);
        vec2 z2 = vec2(zd.x*zd.x - zd.y*zd.y, 2.0*zd.x*zd.y);
        z = z2 + (uFractalMode==1 ? uJulia : c);
        float r2 = dot(z,z);
        if (r2 > esc2){ i = float(k); return ItRes(i, r2); }
        i = float(k);
    }
    return ItRes(i, dot(z,z));
}

float iterate_smooth(vec2 c){
    ItRes r = iterate_raw(c);
    if (r.it >= float(uMaxIter)-1.0) return r.it; // interior
    float log_zn  = 0.5*log(r.zn2);
    float log_b   = log(uEscape);
    float nu = r.it + 1.0 - (log(log_zn / log_b) / 0.6931471805599453); // /ln2
    return max(nu, 0.0);
}

void main(){
    vec2 p = (uv*2.0 - 1.0);
    float ar = uResolution.x / max(uResolution.y, 1.0);
    p.x *= ar;
    vec2 c = p*uZoom + uOffset;

    float v = (uUseSmooth!=0) ? iterate_smooth(c) : iterate_raw(c).it;
    float t = clamp(v / float(uMaxIter), 0.0, 1.0);

    vec3 col = pick_palette(uMode, t);
    FragColor = vec4(col, 1.0);
}
)";

// ======================= Implementación =======================
FractalRenderer::FractalRenderer() {}
FractalRenderer::~FractalRenderer() { Shutdown(); }

bool FractalRenderer::Initialize(int width, int height) {
    m_width = width; m_height = height;

    if (!createFullscreenTri()) return false;
    if (!createShader())        return false;

    glUseProgram(m_prog);
    uResolution  = glGetUniformLocation(m_prog, "uResolution");
    uZoom        = glGetUniformLocation(m_prog, "uZoom");
    uOffset      = glGetUniformLocation(m_prog, "uOffset");
    uJulia       = glGetUniformLocation(m_prog, "uJulia");
    uProc        = glGetUniformLocation(m_prog, "uProc"); // opcional
    uMode        = glGetUniformLocation(m_prog, "uMode");
    uMaxIter     = glGetUniformLocation(m_prog, "uMaxIter");
    uEscape      = glGetUniformLocation(m_prog, "uEscape");
    uFractalMode = glGetUniformLocation(m_prog, "uFractalMode");
    // uUseSmooth y deform uniforms se resuelven por nombre en RenderFractal

    glViewport(0, 0, m_width, m_height);
    return true;
}

void FractalRenderer::Shutdown() { destroyGLObjects(); }

void FractalRenderer::Clear() {
    glClearColor(0.f, 0.f, 0.f, 1.f);
    glClear(GL_COLOR_BUFFER_BIT);
}

void FractalRenderer::RenderFractal(BaseFractal* fractal) {
    if (!m_prog) return;

    // ---- getters robustos (sin depender de excepciones) ----
    auto get_raw = [&](const char* key)->float {
        try { return static_cast<float>(fractal->GetParameter(key)); }
        catch (...) { return NAN; }
    };
    auto get = [&](const char* key, float def)->float {
        float v = get_raw(key);
        if (std::isnan(v) || std::isinf(v)) return def;
        // Si tu GetParameter devuelve 0 cuando no existe, aplica defaults críticos:
        if ((std::strcmp(key, "max_iterations") == 0 || std::strcmp(key, "maxIter") == 0) && v <= 0.0f) return def;
        if (std::strcmp(key, "escape") == 0 && v <= 0.0f) return def;
        if (std::strcmp(key, "zoom") == 0 && (v <= 0.0f || !std::isfinite(v))) return def;
        return v;
    };
    auto get_or = [&](const char* k1, const char* k2, float def)->float {
        float v1 = get(k1, NAN);
        if (!std::isnan(v1)) return v1;
        return get(k2, def);
    };

    // ---- lectura con fallback + clamps ----
    float zoom   = std::max(1e-9f, get_or("zoom", "Zoom", 1.0f));
    float offx   = get_or("offset_x", "OffsetX", 0.0f);
    float offy   = get_or("offset_y", "OffsetY", 0.0f);

    float miterf = get_or("max_iterations", "maxIter", 300.0f);
    int   miter  = (int)std::max(1.0f, miterf);

    float escape = std::max(2.0f, get_or("escape", "bailout", 4.0f));

    int fmode = (int)std::round(get_or("fractal_mode", "fractalMode", 0.0f));
    fmode = (fmode != 0) ? 1 : 0;

    float jr = get_or("julia_r", "juliaRe", 0.0f);
    float ji = get_or("julia_i", "juliaIm", 0.0f);

    float fblend = std::clamp(get_or("function_blend", "funcBlend", 0.5f), 0.0f, 1.0f);
    float dmix   = std::clamp(get_or("deform_mix",     "deformMix", 0.5f), 0.0f, 1.0f);
    float shift  = get_or("shift", "phaseShift", 0.0f);

    int   funcA  = (int)std::round(get_or("funcA", "functionA", 0.0f));
    int   funcB  = (int)std::round(get_or("funcB", "functionB", 0.0f));
    float Aang   = get_or("A_angle","Aangle",0.0f);
    float Afreq  = get_or("A_freq", "Afreq", 1.0f);
    float Aphase = get_or("A_phase","Aphase",0.0f);
    float Bang   = get_or("B_angle","Bangle",0.0f);
    float Bfreq  = get_or("B_freq", "Bfreq", 1.0f);
    float Bphase = get_or("B_phase","Bphase",0.0f);

    // Si es DeformableFractal, sobreescribe con su API (más fiable)
    if (auto* df = dynamic_cast<DeformableFractal*>(fractal)) {
        fblend = df->GetFunctionBlend();
        dmix   = df->GetDeformMix();
        shift  = df->GetShift();
        const DeformState& A = df->GetDeformStateA();
        const DeformState& B = df->GetDeformStateB();
        funcA  = (int)A.function; funcB = (int)B.function;
        Aang=A.angle; Afreq=A.freq; Aphase=A.phase;
        Bang=B.angle; Bfreq=B.freq; Bphase=B.phase;
        // Si DF expone GetJuliaConstant, puedes leer jr/ji aquí.
    }

    int useSmooth = (int)std::round(get_or("use_smooth", "smooth", 1.0f));
    useSmooth = useSmooth ? 1 : 0;

    glUseProgram(m_prog);
    glUniform2f(uResolution, (float)m_width, (float)m_height);
    glUniform1f(uZoom, zoom);
    glUniform2f(uOffset, offx, offy);
    glUniform2f(uJulia, jr, ji);
    glUniform1i(uMode, m_mode);
    glUniform1i(uMaxIter, miter);
    glUniform1f(uEscape, escape);
    glUniform1i(uFractalMode, fmode);

    // Uniforms extra (por nombre)
    GLint uFunctionBlendLoc = glGetUniformLocation(m_prog, "uFunctionBlend");
    GLint uDeformMixLoc     = glGetUniformLocation(m_prog, "uDeformMix");
    GLint uShiftLoc         = glGetUniformLocation(m_prog, "uShift");
    GLint uFuncALoc         = glGetUniformLocation(m_prog, "uFuncA");
    GLint uFuncBLoc         = glGetUniformLocation(m_prog, "uFuncB");
    GLint uALoc             = glGetUniformLocation(m_prog, "uA");
    GLint uBLoc             = glGetUniformLocation(m_prog, "uB");
    GLint uUseSmoothLoc     = glGetUniformLocation(m_prog, "uUseSmooth");

    if (uFunctionBlendLoc >= 0) glUniform1f(uFunctionBlendLoc, fblend);
    if (uDeformMixLoc     >= 0) glUniform1f(uDeformMixLoc,     dmix);
    if (uShiftLoc         >= 0) glUniform1f(uShiftLoc,         shift);
    if (uFuncALoc         >= 0) glUniform1i(uFuncALoc,         funcA);
    if (uFuncBLoc         >= 0) glUniform1i(uFuncBLoc,         funcB);
    if (uALoc             >= 0) glUniform3f(uALoc, Aang, Afreq, Aphase);
    if (uBLoc             >= 0) glUniform3f(uBLoc, Bang, Bfreq, Bphase);
    if (uUseSmoothLoc     >= 0) glUniform1i(uUseSmoothLoc,     useSmooth);

    glBindVertexArray(m_vao);
    glDrawArrays(GL_TRIANGLES, 0, 3);
    glBindVertexArray(0);
}

void FractalRenderer::Present() {
    // No-op: dibujas al backbuffer
}

void FractalRenderer::SaveScreenshot(const char* filenameBase, int w, int h) {
    if (w <= 0 || h <= 0) return;

    // Fecha ddmmyyyy
    std::time_t t = std::time(nullptr);
    std::tm tm{};
#ifdef _WIN32
    localtime_s(&tm, &t);
#else
    localtime_r(&t, &tm);
#endif
    char dateStr[16];
    std::strftime(dateStr, sizeof(dateStr), "%d%m%Y", &tm);

    std::string filename = std::string(filenameBase) + "_" + dateStr + ".png";

    std::vector<unsigned char> pixels((size_t)w * (size_t)h * 4);
    glPixelStorei(GL_PACK_ALIGNMENT, 1);
    glReadBuffer(GL_FRONT); // o GL_BACK si lees antes del swap
    glReadPixels(0, 0, w, h, GL_RGBA, GL_UNSIGNED_BYTE, pixels.data());

    // flip vertical
    const int row = w * 4;
    for (int y = 0; y < h/2; ++y) {
        int a = y * row, b = (h - 1 - y) * row;
        for (int i = 0; i < row; ++i) std::swap(pixels[a + i], pixels[b + i]);
    }
    stbi_write_png(filename.c_str(), w, h, 4, pixels.data(), row);
}

void FractalRenderer::resize(int width, int height) {
    if (width <= 0 || height <= 0) return;
    m_width = width; m_height = height;
    glViewport(0, 0, m_width, m_height);
}

// ======================= GL helpers =======================
GLuint FractalRenderer::compile(GLenum type, const char* src) {
    GLuint s = glCreateShader(type);
    glShaderSource(s, 1, &src, nullptr);
    glCompileShader(s);
    GLint ok = 0; glGetShaderiv(s, GL_COMPILE_STATUS, &ok);
    if (!ok) {
        char log[2048]; GLsizei n=0; glGetShaderInfoLog(s, 2048, &n, log);
        std::fprintf(stderr, "Shader compile error:\n%.*s\n", (int)n, log);
        glDeleteShader(s); return 0;
    }
    return s;
}

bool FractalRenderer::createShader() {
    GLuint vs = compile(GL_VERTEX_SHADER,   kVS);
    GLuint fs = compile(GL_FRAGMENT_SHADER, kFS);
    if (!vs || !fs) return false;

    m_prog = glCreateProgram();
    glAttachShader(m_prog, vs);
    glAttachShader(m_prog, fs);
    glLinkProgram(m_prog);
    glDeleteShader(vs);
    glDeleteShader(fs);

    GLint ok = 0; glGetProgramiv(m_prog, GL_LINK_STATUS, &ok);
    if (!ok) {
        char log[2048]; GLsizei n=0; glGetProgramInfoLog(m_prog, 2048, &n, log);
        std::fprintf(stderr, "Program link error:\n%.*s\n", (int)n, log);
        glDeleteProgram(m_prog); m_prog = 0;
        return false;
    }
    return true;
}

bool FractalRenderer::createFullscreenTri() {
    glGenVertexArrays(1, &m_vao);
    glBindVertexArray(m_vao);

    glGenBuffers(1, &m_vbo);
    glBindBuffer(GL_ARRAY_BUFFER, m_vbo);
    // Sin datos: generamos tri con gl_VertexID
    glBindBuffer(GL_ARRAY_BUFFER, 0);

    glBindVertexArray(0);
    return true;
}

void FractalRenderer::destroyGLObjects() {
    if (m_prog) { glDeleteProgram(m_prog); m_prog = 0; }
    if (m_vbo)  { glDeleteBuffers(1, &m_vbo); m_vbo = 0; }
    if (m_vao)  { glDeleteVertexArrays(1, &m_vao); m_vao = 0; }
}
