#pragma once
#include <glad/glad.h>
#include <stb/stb_image_write.h>

class BaseFractal;

class FractalRenderer {
public:
    FractalRenderer();
    ~FractalRenderer();

    bool Initialize(int width, int height);
    void Shutdown();

    void Clear();
    void RenderFractal(BaseFractal* fractal);
    void Present();

    void SaveScreenshot(const char* filename, int w, int h);

    // Resize real
    void resize(int width, int height);

    // Alias para compatibilidad
    inline void Resize(int width, int height) { resize(width, height); }

    // ========= PUBLIC API =========
    enum class VisualMode : int {
        Grayscale = 0,
        Cosine    = 1,
        SinRGB    = 2,
        Heat      = 3
    };

    inline VisualMode GetVisualMode() const { return static_cast<VisualMode>(m_mode); }
    inline void SetVisualMode(VisualMode vm) { m_mode = static_cast<int>(vm); }

    // Alias antiguo para compatibilidad
    inline void SetPalette(int mode) { SetVisualMode(static_cast<VisualMode>(mode)); }

    inline int  GetPaletteMode() const { return m_mode; }

private:
    // --- GL objects
    GLuint m_prog = 0;
    GLuint m_vao  = 0;
    GLuint m_vbo  = 0;

    // --- Uniform locations
    GLint uResolution  = -1;
    GLint uZoom        = -1;
    GLint uOffset      = -1;
    GLint uJulia       = -1;
    GLint uProc        = -1;
    GLint uMode        = -1;
    GLint uMaxIter     = -1;
    GLint uEscape      = -1;
    GLint uFractalMode = -1;

    // --- estado
    int   m_width  = 0;
    int   m_height = 0;
    int   m_mode   = 1; // default: Cosine

private:
    bool   createFullscreenTri();
    bool   createShader();
    GLuint compile(GLenum type, const char* src);
    void   destroyGLObjects();

    // helpers para extraer parámetros del fractal
    bool  TryGetF(BaseFractal* f, const char* name, float& out);
    float GetF(BaseFractal* f, const char* name, float def);
    void  GetJulia(BaseFractal* f, float& jr, float& ji);
};
