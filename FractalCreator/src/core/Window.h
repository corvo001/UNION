#pragma once
#include <string>

struct GLFWwindow;

class Window {
public:
    Window(int width, int height, const std::string& title);
    ~Window();
    
    bool Create();
    void Destroy();
    
    bool ShouldClose() const;
    void SwapBuffers();
    
    bool IsKeyPressed(int key) const;
    
    int GetWidth() const { return m_width; }
    int GetHeight() const { return m_height; }
    GLFWwindow* GetHandle() const { return m_window; }
    
private:
    GLFWwindow* m_window;
    int m_width, m_height;
    std::string m_title;
    
    static void ErrorCallback(int error, const char* description);
    static void FramebufferSizeCallback(GLFWwindow* window, int width, int height);
};
