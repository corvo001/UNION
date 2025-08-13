#include "Window.h"
#include <GLFW/glfw3.h>
#include <iostream>

Window::Window(int width, int height, const std::string& title)
    : m_window(nullptr), m_width(width), m_height(height), m_title(title) {}

Window::~Window() {
    Destroy();
}

bool Window::Create() {
    m_window = glfwCreateWindow(m_width, m_height, m_title.c_str(), nullptr, nullptr);
    if (!m_window) {
        std::cerr << "Failed to create GLFW window" << std::endl;
        return false;
    }
    
    glfwMakeContextCurrent(m_window);
    glfwSetErrorCallback(ErrorCallback);
    glfwSetFramebufferSizeCallback(m_window, FramebufferSizeCallback);
    
    return true;
}

void Window::Destroy() {
    if (m_window) {
        glfwDestroyWindow(m_window);
        m_window = nullptr;
    }
}

bool Window::ShouldClose() const {
    return m_window && glfwWindowShouldClose(m_window);
}

void Window::SwapBuffers() {
    if (m_window) {
        glfwSwapBuffers(m_window);
    }
}

bool Window::IsKeyPressed(int key) const {
    return m_window && glfwGetKey(m_window, key) == GLFW_PRESS;
}

void Window::ErrorCallback(int error, const char* description) {
    std::cerr << "GLFW Error " << error << ": " << description << std::endl;
}

void Window::FramebufferSizeCallback(GLFWwindow* window, int width, int height) {
    // Handle window resize
    glViewport(0, 0, width, height);
}
