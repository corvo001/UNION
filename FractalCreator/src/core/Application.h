#pragma once
#include <memory>

class Window;
class Renderer;
class FractalGenerator;

class Application {
public:
    Application();
    ~Application();
    
    bool Initialize();
    void Run();
    void Shutdown();
    
private:
    std::unique_ptr<Window> m_window;
    std::unique_ptr<Renderer> m_renderer;
    std::unique_ptr<FractalGenerator> m_generator;
    
    bool m_running;
    double m_lastTime;
    
    void Update(float deltaTime);
    void Render();
    void HandleInput();
};