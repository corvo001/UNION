#include "Application.h"
#include "Window.h"
#include "../Rendering/Renderer.h"
#include "../Generation/FractalGenerator.h"
#include <iostream>
#include <GLFW/glfw3.h>

Application::Application() 
    : m_running(false), m_lastTime(0.0) {
}

Application::~Application() = default;

bool Application::Initialize() {
    // Inicializar GLFW
    if (!glfwInit()) {
        std::cerr << "Failed to initialize GLFW" << std::endl;
        return false;
    }
    
    // Crear ventana
    m_window = std::make_unique<Window>(800, 600, "Fractal Explorer");
    if (!m_window->Create()) {
        return false;
    }
    
    // Crear renderer
    m_renderer = std::make_unique<Renderer>();
    if (!m_renderer->Initialize()) {
        return false;
    }
    
    // Crear generador de fractales
    m_generator = std::make_unique<FractalGenerator>();
    
    m_running = true;
    m_lastTime = glfwGetTime();
    
    std::cout << "Application initialized successfully!" << std::endl;
    return true;
}

void Application::Run() {
    while (m_running && !m_window->ShouldClose()) {
        double currentTime = glfwGetTime();
        float deltaTime = static_cast<float>(currentTime - m_lastTime);
        m_lastTime = currentTime;
        
        HandleInput();
        Update(deltaTime);
        Render();
        
        m_window->SwapBuffers();
        glfwPollEvents();
    }
}

void Application::Update(float deltaTime) {
    // Aquí irá la lógica de actualización
    // Por ahora solo mantener el loop funcionando
    (void)deltaTime; // Evitar warning de variable no usada
}

void Application::Render() {
    m_renderer->Clear();
    m_renderer->RenderFractal();
    // El swap de buffers se hace en Run()
}

void Application::HandleInput() {
    // Input básico - cerrar con ESC
    if (m_window->IsKeyPressed(GLFW_KEY_ESCAPE)) {
        m_running = false;
    }
}

void Application::Shutdown() {
    m_generator.reset();
    m_renderer.reset();
    m_window.reset();
    glfwTerminate();
    
    std::cout << "Application shutdown complete" << std::endl;
}
