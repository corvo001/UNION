#include "Renderer.h"
#include <iostream>

Renderer::Renderer() {
    std::cout << "Renderer creado (versión simple)" << std::endl;
}

Renderer::~Renderer() = default;

bool Renderer::Initialize() {
    std::cout << "Renderer inicializado" << std::endl;
    return true;
}

void Renderer::Clear() {
    // Versión simple - no hace nada
}

void Renderer::RenderFractal() {
    std::cout << "Renderizando fractal..." << std::endl;
}

void Renderer::Shutdown() {
    std::cout << "Renderer cerrado" << std::endl;
}