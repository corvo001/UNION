#include "glad/glad.h"
#include <GLFW/glfw3.h>
#include <iostream>
#include "Rendering/FractalRenderer.h"
#include "core/Application.h"

// (Opcional) callback placeholder
static void framebuffer_size_callback(GLFWwindow* window, int width, int height) {
    (void)window; (void)width; (void)height;
}

int main(int /*argc*/, char** /*argv*/) {
    Application app;
    if (!app.Initialize()) return -1;
    app.Run();
    app.Shutdown();
    return 0;
}

#ifdef _WIN32
// Shim para app GUI sin consola. OJO: sin extern "C".
#include <windows.h>
int main(int, char**);  // misma signatura que arriba (C++ linkage)
int WINAPI WinMain(HINSTANCE, HINSTANCE, LPSTR, int) {
    return main(__argc, __argv);
}
#endif
