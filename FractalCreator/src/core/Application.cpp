// src/core/Application.cpp
#include "core/Application.h"
#include "rendering/FractalRenderer.h"
#include "fractals/DeformableFractal.h"

#include "stb/stb_image_write.h" // solo declaraciones; la implementación está en otro .cpp

#include <iostream>
#include <algorithm>
#include <cmath>
#include <vector>
#include <string>
#include <filesystem>
#include <ctime>    // std::time, std::localtime/localtime_s, std::strftime
#include <cstdio>   // std::snprintf

// glad SIEMPRE antes que glfw
#include <glad/glad.h>
#include <GLFW/glfw3.h>

// ImGui
#include "imgui.h"
#include "imgui_impl_glfw.h"
#include "imgui_impl_opengl3.h"

static const char* kGlVersion = "#version 330";

// --- helpers fecha/hora y capturas ---
static const char* kBaseToday = R"(C:\Users\Dani_\Desktop\all\work\UNION\Raven\data\today)";

static std::string TodayDateDDMMYYYY() {
    std::time_t t = std::time(nullptr);
    std::tm tm{};
#ifdef _WIN32
    localtime_s(&tm, &t);
#else
    tm = *std::localtime(&t);
#endif
    char buf[16];
    std::strftime(buf, sizeof(buf), "%d%m%Y", &tm);
    return std::string(buf);
}

static std::string NowHHMMSS() {
    std::time_t t = std::time(nullptr);
    std::tm tm{};
#ifdef _WIN32
    localtime_s(&tm, &t);
#else
    tm = *std::localtime(&t);
#endif
    char buf[16];
    std::snprintf(buf, sizeof(buf), "%02d%02d%02d", tm.tm_hour, tm.tm_min, tm.tm_sec);
    return std::string(buf);
}

static std::string MakeCapturePathToday() {
    std::filesystem::path dir = std::filesystem::path(kBaseToday) / TodayDateDDMMYYYY();
    std::error_code ec;
    std::filesystem::create_directories(dir, ec); // ok si ya existe
    std::filesystem::path file = dir / ("capture_" + NowHHMMSS() + ".png");
    return file.string();
}

static bool SaveBackbufferPNG(int width, int height, const char* path) {
    if (width <= 0 || height <= 0 || !path) return false;
    std::vector<unsigned char> pixels((size_t)width * (size_t)height * 4);
    glPixelStorei(GL_PACK_ALIGNMENT, 1);
    glReadBuffer(GL_FRONT); // o GL_BACK si lees antes del swap
    glReadPixels(0, 0, width, height, GL_RGBA, GL_UNSIGNED_BYTE, pixels.data());

    // flip vertical
    const int row = width * 4;
    for (int y = 0; y < height / 2; ++y) {
        int a = y * row, b = (height - 1 - y) * row;
        for (int i = 0; i < row; ++i) std::swap(pixels[a + i], pixels[b + i]);
    }
    return stbi_write_png(path, width, height, 4, pixels.data(), row) != 0;
}

// ====================== Application ======================

Application::Application() {}
Application::~Application() { Shutdown(); }

bool Application::Initialize() {
    if (!glfwInit()) { std::cerr << "GLFW init failed\n"; return false; }

    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);
#if __APPLE__
    glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE);
#endif

    m_window = glfwCreateWindow(1280, 720, "FractalCreator", nullptr, nullptr);
    if (!m_window) { std::cerr << "Window creation failed\n"; glfwTerminate(); return false; }
    glfwMakeContextCurrent(m_window);
    glfwSwapInterval(1);

    if (!gladLoadGLLoader((GLADloadproc)glfwGetProcAddress)) { std::cerr << "GLAD load failed\n"; return false; }

    // viewport inicial + callback de resize
    int fbw = 0, fbh = 0;
    glfwGetFramebufferSize(m_window, &fbw, &fbh);
    glViewport(0, 0, fbw, fbh);

    glfwSetWindowUserPointer(m_window, this);
    glfwSetFramebufferSizeCallback(m_window, [](GLFWwindow* w, int width, int height){
        glViewport(0, 0, width, height);
        if (auto* app = static_cast<Application*>(glfwGetWindowUserPointer(w))) {
            if (app->m_renderer) app->m_renderer->Resize(width, height);
        }
    });

    // Renderer
    m_renderer = std::make_unique<FractalRenderer>();
    if (!m_renderer->Initialize(fbw, fbh)) { std::cerr << "Renderer init failed\n"; return false; }

    // Fractal por defecto
    m_currentFractal = std::make_unique<DeformableFractal>();
    m_currentFractal->SetParameter("zoom", 1.0);
    m_currentFractal->SetParameter("offset_x", 0.0);
    m_currentFractal->SetParameter("offset_y", 0.0);
    m_currentFractal->SetParameter("max_iterations", 300.0);
    m_currentFractal->SetParameter("function_blend", 0.5);
    m_currentFractal->SetParameter("deform_mix", 0.5);
    m_currentFractal->SetParameter("shift", 0.0);

    // Input callbacks
    glfwSetScrollCallback(m_window, [](GLFWwindow* w, double /*xoff*/, double yoff) {
        if (auto* app = static_cast<Application*>(glfwGetWindowUserPointer(w))) {
            app->m_scrollDelta -= yoff; // invertir dirección si prefieres
        }
    });

    glfwSetMouseButtonCallback(m_window, [](GLFWwindow* w, int button, int action, int /*mods*/) {
        auto* app = static_cast<Application*>(glfwGetWindowUserPointer(w));
        if (!app) return;
        if (button == GLFW_MOUSE_BUTTON_LEFT) {
            if (action == GLFW_PRESS) {
                app->m_dragging = true;
                glfwGetCursorPos(w, &app->m_lastMouseX, &app->m_lastMouseY);
            } else if (action == GLFW_RELEASE) {
                app->m_dragging = false;
            }
        }
    });

    // ---------- ImGui ----------
    IMGUI_CHECKVERSION();
    ImGui::CreateContext();
    ImGuiIO& io = ImGui::GetIO();
    io.ConfigFlags |= ImGuiConfigFlags_NavEnableKeyboard;
    io.ConfigFlags |= ImGuiConfigFlags_DockingEnable;
    io.ConfigFlags |= ImGuiConfigFlags_ViewportsEnable;

    ImGui::StyleColorsDark();
    ImGuiStyle& style = ImGui::GetStyle();
    if (io.ConfigFlags & ImGuiConfigFlags_ViewportsEnable) {
        style.WindowRounding = 4.0f;
        style.Colors[ImGuiCol_WindowBg].w = 1.0f;
    }

    ImGui_ImplGlfw_InitForOpenGL(m_window, true);
    ImGui_ImplOpenGL3_Init(kGlVersion);

    m_lastTime = glfwGetTime();
    return true;
}

void Application::Run() {
    static bool showHUD = true;
    static int paletteIndex = 1; // FractalRenderer::Cosine por defecto

    bool f1Latch = false;
    double lastShot = 0.0;

    while (!glfwWindowShouldClose(m_window) && m_running) {
        const double now = glfwGetTime();
        const float dt = static_cast<float>(now - m_lastTime);
        m_lastTime = now;

        glfwPollEvents();
        HandleInput(dt);

        // Toggle HUD con F1 (latch)
        if (glfwGetKey(m_window, GLFW_KEY_F1) == GLFW_PRESS) {
            if (!f1Latch) { showHUD = !showHUD; f1Latch = true; }
        } else {
            f1Latch = false;
        }

        // Export PNG (P) con antispam
        if (glfwGetKey(m_window, GLFW_KEY_P) == GLFW_PRESS) {
            if (now - lastShot > 0.3) {
                int w=0, h=0; glfwGetFramebufferSize(m_window, &w, &h);
                std::string path = MakeCapturePathToday();
                const bool ok = SaveBackbufferPNG(w, h, path.c_str());
                std::cout << (ok ? "Saved: " : "Failed: ") << path << "\n";
                lastShot = now;
            }
        }

        // --- ImGui frame ---
        ImGui_ImplOpenGL3_NewFrame();
        ImGui_ImplGlfw_NewFrame();
        ImGui::NewFrame();

        if (showHUD) {
            if (ImGui::Begin("Fractal HUD", &showHUD, ImGuiWindowFlags_AlwaysAutoResize)) {
                double zoom  = m_currentFractal->GetParameter("zoom");
                double offx  = m_currentFractal->GetParameter("offset_x");
                double offy  = m_currentFractal->GetParameter("offset_y");
                int    iters = (int)m_currentFractal->GetParameter("max_iterations");
                float  blend = (float)m_currentFractal->GetParameter("function_blend");
                float  mix   = (float)m_currentFractal->GetParameter("deform_mix");
                float  shift = (float)m_currentFractal->GetParameter("shift");

                ImGui::Text("FPS: %.1f", ImGui::GetIO().Framerate);
                ImGui::Separator();

                ImGui::Text("Zoom: %.6f", zoom);
                if (ImGui::SliderInt("Iteraciones", &iters, 10, 5000)) {
                    m_currentFractal->SetParameter("max_iterations", (double)iters);
                }
                ImGui::Text("Offset X: %.5f", offx);
                ImGui::Text("Offset Y: %.5f", offy);

                ImGui::Separator();
                if (ImGui::SliderFloat("Function Blend", &blend, 0.0f, 1.0f)) {
                    m_currentFractal->SetFunctionBlend(blend);
                    m_currentFractal->SetParameter("function_blend", blend);
                }
                if (ImGui::SliderFloat("Deform Mix", &mix, 0.0f, 1.0f)) {
                    m_currentFractal->SetDeformMix(mix);
                    m_currentFractal->SetParameter("deform_mix", mix);
                }
                if (ImGui::SliderFloat("Shift", &shift, -3.14f, 3.14f)) {
                    m_currentFractal->SetShift(shift);
                    m_currentFractal->SetParameter("shift", shift);
                }

                ImGui::Separator();
                const char* palettes[] = { "Grayscale", "Cosine", "SinRGB", "Heat" };
                if (ImGui::Combo("Palette", &paletteIndex, palettes, IM_ARRAYSIZE(palettes))) {
                    m_renderer->SetPalette(paletteIndex);
                }
                if (ImGui::Button("Export PNG (P)")) {
                    int w=0, h=0; glfwGetFramebufferSize(m_window, &w, &h);
                    std::string path = MakeCapturePathToday();
                    const bool ok = SaveBackbufferPNG(w, h, path.c_str());
                    std::cout << (ok ? "Saved: " : "Failed: ") << path << "\n";
                }

                // Deform A/B
                auto stateA = m_currentFractal->GetDeformStateA();
                auto stateB = m_currentFractal->GetDeformStateB();
                const char* funcs[] = { "SIN","COS","ABS","ATAN","SINH","COSH","SQRT_ABS","ASIN","TAN","SIN_ABS","COS_SQUARE" };
                int fa = (int)stateA.function;
                int fb = (int)stateB.function;
                if (ImGui::Combo("Funcion A", &fa, funcs, IM_ARRAYSIZE(funcs))) { stateA.function = (DeformFunction)fa; m_currentFractal->SetDeformStateA(stateA); }
                if (ImGui::Combo("Funcion B", &fb, funcs, IM_ARRAYSIZE(funcs))) { stateB.function = (DeformFunction)fb; m_currentFractal->SetDeformStateB(stateB); }

                ImGui::SliderFloat("A: Angle", &stateA.angle, -3.14f, 3.14f);
                ImGui::SliderFloat("A: Freq",  &stateA.freq,   0.1f,  4.0f);
                ImGui::SliderFloat("A: Phase", &stateA.phase, -3.14f, 3.14f);
                if (ImGui::Button("Aplicar A")) m_currentFractal->SetDeformStateA(stateA);

                ImGui::SliderFloat("B: Angle", &stateB.angle, -3.14f, 3.14f);
                ImGui::SliderFloat("B: Freq",  &stateB.freq,   0.1f,  4.0f);
                ImGui::SliderFloat("B: Phase", &stateB.phase, -3.14f, 3.14f);
                if (ImGui::Button("Aplicar B")) m_currentFractal->SetDeformStateB(stateB);

                ImGui::Separator();
                if (ImGui::Button("Randomize")) { m_currentFractal->Randomize((uint32_t)(glfwGetTime() * 1000)); }
                ImGui::SameLine();
                if (ImGui::Button("Reset vista")) {
                    m_currentFractal->SetParameter("zoom", 1.0);
                    m_currentFractal->SetParameter("offset_x", 0.0);
                    m_currentFractal->SetParameter("offset_y", 0.0);
                }
                ImGui::TextDisabled("Atajos: WASD/QE, +/- iter, [ ] blend, , . mix, 1/2 func A/B, R random, 0 reset, P export PNG.");
            }
            ImGui::End();
        }

        // Render
        m_renderer->Clear();
        m_renderer->RenderFractal(m_currentFractal.get());

        // UI
        ImGui::Render();
        ImGui_ImplOpenGL3_RenderDrawData(ImGui::GetDrawData());

        // Viewports extra
        ImGuiIO& io = ImGui::GetIO();
        if (io.ConfigFlags & ImGuiConfigFlags_ViewportsEnable) {
            GLFWwindow* backup_ctx = glfwGetCurrentContext();
            ImGui::UpdatePlatformWindows();
            ImGui::RenderPlatformWindowsDefault();
            glfwMakeContextCurrent(backup_ctx);
        }

        glfwSwapBuffers(m_window);
    }
}

void Application::Shutdown() {
    // Destruir ImGui primero (usa el contexto de la ventana)
    ImGui_ImplOpenGL3_Shutdown();
    ImGui_ImplGlfw_Shutdown();
    ImGui::DestroyContext();

    if (m_renderer) { m_renderer->Shutdown(); m_renderer.reset(); }
    if (m_window)   { glfwDestroyWindow(m_window); m_window = nullptr; }
    glfwTerminate();
}

void Application::HandleInput(float dt) {
    if (!m_window || !m_currentFractal) return;

    ImGuiIO& io = ImGui::GetIO();
    const bool kbFree = !io.WantCaptureKeyboard;
    const bool msFree = !io.WantCaptureMouse;

    // ESC para salir
    if (kbFree && glfwGetKey(m_window, GLFW_KEY_ESCAPE) == GLFW_PRESS) {
        m_running = false;
        return;
    }

    // Zoom con Q/E o rueda
    double zoom = m_currentFractal->GetParameter("zoom");
    if (kbFree) {
        if (glfwGetKey(m_window, GLFW_KEY_Q) == GLFW_PRESS) m_scrollDelta += +1.0;
        if (glfwGetKey(m_window, GLFW_KEY_E) == GLFW_PRESS) m_scrollDelta += -1.0;
    }
    if (msFree && m_scrollDelta != 0.0) {
        const double factor = std::pow(1.1, m_scrollDelta);
        zoom = std::clamp(zoom * factor, 1e-9, 1e9);
        m_currentFractal->SetParameter("zoom", zoom);
        m_scrollDelta = 0.0;
    } else if (!msFree) {
        m_scrollDelta = 0.0;
    }

    // Pan con WASD/Flechas + drag
    double offsetX = m_currentFractal->GetParameter("offset_x");
    double offsetY = m_currentFractal->GetParameter("offset_y");

    if (kbFree) {
        const double panSpeed = 0.8 * zoom * dt;
        if (glfwGetKey(m_window, GLFW_KEY_A) == GLFW_PRESS || glfwGetKey(m_window, GLFW_KEY_LEFT)  == GLFW_PRESS) offsetX -= panSpeed;
        if (glfwGetKey(m_window, GLFW_KEY_D) == GLFW_PRESS || glfwGetKey(m_window, GLFW_KEY_RIGHT) == GLFW_PRESS) offsetX += panSpeed;
        if (glfwGetKey(m_window, GLFW_KEY_W) == GLFW_PRESS || glfwGetKey(m_window, GLFW_KEY_UP)    == GLFW_PRESS) offsetY += panSpeed;
        if (glfwGetKey(m_window, GLFW_KEY_S) == GLFW_PRESS || glfwGetKey(m_window, GLFW_KEY_DOWN)  == GLFW_PRESS) offsetY -= panSpeed;
    }

    if (msFree && m_dragging) {
        double x=0.0, y=0.0; glfwGetCursorPos(m_window, &x, &y);
        const double dx = x - m_lastMouseX;
        const double dy = y - m_lastMouseY;
        m_lastMouseX = x; m_lastMouseY = y;
        const double dragFactor = 0.002 * zoom;
        offsetX -= dx * dragFactor;
        offsetY += dy * dragFactor;
    }
    m_currentFractal->SetParameter("offset_x", offsetX);
    m_currentFractal->SetParameter("offset_y", offsetY);

    // Iteraciones +/- (teclado)
    if (kbFree && (glfwGetKey(m_window, GLFW_KEY_KP_ADD) == GLFW_PRESS || glfwGetKey(m_window, GLFW_KEY_EQUAL) == GLFW_PRESS)) {
        int it = (int)m_currentFractal->GetParameter("max_iterations");
        m_currentFractal->SetParameter("max_iterations", (double)std::min(it + 10, 5000));
    }
    if (kbFree && (glfwGetKey(m_window, GLFW_KEY_KP_SUBTRACT) == GLFW_PRESS || glfwGetKey(m_window, GLFW_KEY_MINUS) == GLFW_PRESS)) {
        int it = (int)m_currentFractal->GetParameter("max_iterations");
        m_currentFractal->SetParameter("max_iterations", (double)std::max(it - 10, 10));
    }

    // Mezclas rápidas
    if (kbFree && glfwGetKey(m_window, GLFW_KEY_LEFT_BRACKET)  == GLFW_PRESS) {
        float b = (float)m_currentFractal->GetParameter("function_blend");
        b = std::max(0.0f, b - float(0.5f * dt));
        m_currentFractal->SetFunctionBlend(b);
        m_currentFractal->SetParameter("function_blend", b);
    }
    if (kbFree && glfwGetKey(m_window, GLFW_KEY_RIGHT_BRACKET) == GLFW_PRESS) {
        float b = (float)m_currentFractal->GetParameter("function_blend");
        b = std::min(1.0f, b + float(0.5f * dt));
        m_currentFractal->SetFunctionBlend(b);
        m_currentFractal->SetParameter("function_blend", b);
    }
    if (kbFree && glfwGetKey(m_window, GLFW_KEY_COMMA) == GLFW_PRESS) {
        float m = (float)m_currentFractal->GetParameter("deform_mix");
        m = std::max(0.0f, m - float(0.5f * dt));
        m_currentFractal->SetDeformMix(m);
        m_currentFractal->SetParameter("deform_mix", m);
    }
    if (kbFree && glfwGetKey(m_window, GLFW_KEY_PERIOD) == GLFW_PRESS) {
        float m = (float)m_currentFractal->GetParameter("deform_mix");
        m = std::min(1.0f, m + float(0.5f * dt));
        m_currentFractal->SetDeformMix(m);
        m_currentFractal->SetParameter("deform_mix", m);
    }

    // Cambiar función A/B con 1 / 2
    if (kbFree) {
        auto bumpFunc = [](DeformState& s) {
            int i = (int)s.function;
            i = (i + 1) % (int)DeformFunction::COUNT;
            s.function = (DeformFunction)i;
        };
        if (glfwGetKey(m_window, GLFW_KEY_1) == GLFW_PRESS) {
            DeformState s = m_currentFractal->GetDeformStateA(); bumpFunc(s); m_currentFractal->SetDeformStateA(s);
        }
        if (glfwGetKey(m_window, GLFW_KEY_2) == GLFW_PRESS) {
            DeformState s = m_currentFractal->GetDeformStateB(); bumpFunc(s); m_currentFractal->SetDeformStateB(s);
        }
    }

    // Randomize con R (antirepetición)
    if (kbFree && glfwGetKey(m_window, GLFW_KEY_R) == GLFW_PRESS) {
        const double t = glfwGetTime();
        if (t - m_uiLastRandomTime > 0.2) {
            m_currentFractal->Randomize((uint32_t)(t * 1000));
            m_uiLastRandomTime = t;
        }
    }

    // Reset vista con 0
    if (kbFree && glfwGetKey(m_window, GLFW_KEY_0) == GLFW_PRESS) {
        m_currentFractal->SetParameter("zoom", 1.0);
        m_currentFractal->SetParameter("offset_x", 0.0);
        m_currentFractal->SetParameter("offset_y", 0.0);
    }
}
