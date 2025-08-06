#pragma once
#include <memory>

class BaseFractal;

class Renderer {
public:
    Renderer();
    ~Renderer();
    
    bool Initialize();
    void Shutdown();
    void Clear();
    void RenderFractal();
    
private:
    // Versión simplificada sin OpenGL
};