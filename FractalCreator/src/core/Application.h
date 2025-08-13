#pragma once
#include <memory>

struct GLFWwindow;

class FractalRenderer;
class DeformableFractal;

class Application {
public:
    Application();
    ~Application();

    bool Initialize();
    void Run();
    void Shutdown();

private:
    void HandleInput(float dt);

    // GLFW
    GLFWwindow* m_window = nullptr;

    // Render y fractal
    std::unique_ptr<FractalRenderer> m_renderer;
    std::unique_ptr<DeformableFractal> m_currentFractal;

    // Timing
    double m_lastTime = 0.0;
    bool m_running = true;

    // Entrada
    bool   m_dragging = false;
    double m_lastMouseX = 0.0, m_lastMouseY = 0.0;
    double m_scrollDelta = 0.0; // acumulamos zoom por rueda

    // UI state opcional (para evitar autofire con teclas si quieres)
    double m_uiLastRandomTime = -10.0;
};
