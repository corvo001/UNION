#include <iostream>
#include <complex>
#include <vector>
#include <cmath>
#include <fstream>
#include <string>
#include <chrono>
#include <algorithm>

class FractalCreator {
private:
    // Parámetros básicos del fractal
    float zoom = 1.0f;
    float offsetX = 0.0f;
    float offsetY = 0.0f;
    int iterations = 200;
    
    // Parámetros de Julia
    std::complex<float> juliaConstant{0.355f, 0.355f};
    float escapeThreshold = 4.0f;
    
    // Parámetros de deformación A
    float angle = 0.0f;
    float freq = 1.0f;
    float phase = 0.0f;
    int funcID = 0;
    float edgeGlow = 1.0f;
    float edgeHueShift = 1.0f;
    
    // Parámetros de deformación B
    float angleTarget = 0.0f;
    float freqTarget = 1.0f;
    float phaseTarget = 0.0f;
    int funcID2 = 1;
    float edgeGlowTarget = 1.0f;
    float edgeHueShiftTarget = 1.0f;
    
    // Parámetros de control
    float shift = 0.0f;
    float funcBlend = 0.0f;
    float deformMix = 0.0f;
    int visualMode = 0; // 0 = B/N, 1 = Color
    float edgeSaturation = 1.0f;
    
    // Dimensiones de salida
    int width = 1024;
    int height = 1024;
    
    // Tiempo para animaciones
    float currentTime = 0.0f;

public:
    // Constructor
    FractalCreator(int w = 1024, int h = 1024) : width(w), height(h) {}
    
    // Estructura para RGB
    struct RGB {
        float r, g, b;
        RGB(float r = 0, float g = 0, float b = 0) : r(r), g(g), b(b) {}
    };
    
    // Funciones matemáticas complejas
    std::complex<float> complexSq(const std::complex<float>& z) {
        float real = z.real() * z.real() - z.imag() * z.imag();
        float imag = 2.0f * z.real() * z.imag();
        return std::complex<float>(real, imag);
    }
    
    std::complex<float> rotate(const std::complex<float>& z, float angle) {
        float c = std::cos(angle);
        float s = std::sin(angle);
        float real = c * z.real() - s * z.imag();
        float imag = s * z.real() + c * z.imag();
        return std::complex<float>(real, imag);
    }
    
    std::complex<float> applyFunc(const std::complex<float>& z, int id) {
        switch(id) {
            case 0: return std::sin(z);
            case 1: return std::cos(z);
            case 2: return std::complex<float>(std::abs(z.real()), std::abs(z.imag()));
            case 3: return std::sinh(z);
            case 4: return std::cosh(z);
            case 5: return std::atan(z);
            case 6: {
                float magnitude = std::abs(z);
                return std::complex<float>(std::sqrt(magnitude), 0);
            }
            case 7: return std::asin(z);
            case 8: return std::tan(z);
            case 9: {
                float absReal = std::abs(z.real());
                float absImag = std::abs(z.imag());
                return std::sin(std::complex<float>(absReal, absImag));
            }
            case 10: return std::cos(z * z);
            default: return z;
        }
    }
    
    std::complex<float> applyFuncBlend(const std::complex<float>& z, int id1, int id2, float blend) {
        auto f1 = applyFunc(z, id1);
        auto f2 = applyFunc(z, id2);
        return f1 * (1.0f - blend) + f2 * blend;
    }
    
    std::complex<float> deform(const std::complex<float>& z) {
        float angleBlend = std::sin(z.real() + angle);
        float freqBlend = std::cos(z.imag() + freq);
        float phaseBlend = std::sin(z.real() * z.imag() + phase);
        
        auto rotZ = rotate(z, angleBlend);
        auto wave = 0.5f * applyFuncBlend(
            freqBlend * z + std::complex<float>(shift, 0) + std::complex<float>(phaseBlend, 0),
            funcID, funcID2, funcBlend
        );
        
        return rotZ + wave;
    }
    
    std::complex<float> deformRecursive(const std::complex<float>& z) {
        auto first = deform(z);
        auto second = deform(first);
        return first * 0.5f + second * 0.5f;
    }
    
    // Ciclo suave respiratorio
    float getDeformMix(float time) {
        float breathDuration = 6.0f;
        float phase = std::fmod(time / breathDuration, 1.0f);
        return 0.5f - 0.5f * std::cos(phase * 2.0f * M_PI);
    }
    
    // Función principal del fractal
    float calculateFractal(std::complex<float> uv) {
        std::complex<float> z = uv;
        std::complex<float> c = juliaConstant;
        float escape = escapeThreshold;
        int iter = 0;
        
        float deformMixValue = getDeformMix(currentTime);
        
        for (int i = 0; i < iterations; i++) {
            auto tA = deformRecursive(z);
            auto tB = deform(z);
            auto t = tA * (1.0f - deformMixValue) + tB * deformMixValue;
            
            z = complexSq(t) + c;
            
            // Verificar si es finito
            if (!std::isfinite(z.real()) || !std::isfinite(z.imag())) break;
            if (std::norm(z) > escape) break;
            
            iter++;
        }
        
        return static_cast<float>(iter) / iterations;
    }
    
    // Conversión HSV a RGB
    RGB hsv2rgb(float h, float s, float v) {
        float c = v * s;
        float x = c * (1.0f - std::abs(std::fmod(h * 6.0f, 2.0f) - 1.0f));
        float m = v - c;
        
        float r1, g1, b1;
        
        if (h < 1.0f/6.0f) { r1 = c; g1 = x; b1 = 0; }
        else if (h < 2.0f/6.0f) { r1 = x; g1 = c; b1 = 0; }
        else if (h < 3.0f/6.0f) { r1 = 0; g1 = c; b1 = x; }
        else if (h < 4.0f/6.0f) { r1 = 0; g1 = x; b1 = c; }
        else if (h < 5.0f/6.0f) { r1 = x; g1 = 0; b1 = c; }
        else { r1 = c; g1 = 0; b1 = x; }
        
        return RGB(r1 + m, g1 + m, b1 + m);
    }
    
    // Generar fractal completo
    std::vector<std::vector<RGB>> generateFractal() {
        std::vector<std::vector<RGB>> image(height, std::vector<RGB>(width));
        
        float aspect = static_cast<float>(width) / height;
        
        for (int y = 0; y < height; y++) {
            for (int x = 0; x < width; x++) {
                // Mapear coordenadas UV
                float u = (static_cast<float>(x) / width - 0.5f) * zoom + offsetX;
                float v = (static_cast<float>(y) / height - 0.5f) * zoom / aspect + offsetY;
                
                std::complex<float> uv(u, v);
                float val = calculateFractal(uv);
                val = std::clamp(val, 0.0f, 1.0f);
                
                if (visualMode == 0) {
                    // Modo blanco y negro
                    image[y][x] = RGB(val, val, val);
                } else {
                    // Modo color
                    float edge = std::clamp((val - 0.9f) / (0.995f - 0.9f), 0.0f, 1.0f);
                    
                    float glowBlend = (edgeGlow * (1.0f - funcBlend) + edgeGlowTarget * funcBlend) * 0.5f;
                    float hueBlend = (edgeHueShift * (1.0f - funcBlend) + edgeHueShiftTarget * funcBlend) * 0.5f;
                    
                    float glow = edge * glowBlend;
                    float hue = std::fmod(currentTime * hueBlend + val, 1.0f);
                    
                    image[y][x] = hsv2rgb(hue, edgeSaturation, glow);
                }
            }
        }
        
        return image;
    }
    
    // Setters para configuración
    void setZoom(float z) { zoom = z; }
    void setOffset(float x, float y) { offsetX = x; offsetY = y; }
    void setIterations(int iter) { iterations = iter; }
    void setJuliaConstant(float real, float imag) { juliaConstant = std::complex<float>(real, imag); }
    void setEscapeThreshold(float threshold) { escapeThreshold = threshold; }
    void setTime(float time) { currentTime = time; }
    void setVisualMode(int mode) { visualMode = mode; }
    
    // Setters para parámetros de deformación A
    void setDeformA(float ang, float fr, float ph, int fid, float glow, float hue) {
        angle = ang; freq = fr; phase = ph; funcID = fid; 
        edgeGlow = glow; edgeHueShift = hue;
    }
    
    // Setters para parámetros de deformación B
    void setDeformB(float ang, float fr, float ph, int fid, float glow, float hue) {
        angleTarget = ang; freqTarget = fr; phaseTarget = ph; funcID2 = fid;
        edgeGlowTarget = glow; edgeHueShiftTarget = hue;
    }
    
    void setBlending(float blend, float mix, float sh, float sat) {
        funcBlend = blend; deformMix = mix; shift = sh; edgeSaturation = sat;
    }
    
    // Exportar como PPM (formato simple)
    void exportPPM(const std::string& filename) {
        auto image = generateFractal();
        
        std::ofstream file(filename);
        file << "P3\n" << width << " " << height << "\n255\n";
        
        for (const auto& row : image) {
            for (const auto& pixel : row) {
                int r = static_cast<int>(pixel.r * 255);
                int g = static_cast<int>(pixel.g * 255);
                int b = static_cast<int>(pixel.b * 255);
                file << r << " " << g << " " << b << " ";
            }
            file << "\n";
        }
    }
    
    // Exportar configuración como JSON
    void exportConfig(const std::string& filename) {
        std::ofstream file(filename);
        file << "{\n";
        file << "  \"zoom\": " << zoom << ",\n";
        file << "  \"offsetX\": " << offsetX << ",\n";
        file << "  \"offsetY\": " << offsetY << ",\n";
        file << "  \"iterations\": " << iterations << ",\n";
        file << "  \"juliaConstant\": [" << juliaConstant.real() << ", " << juliaConstant.imag() << "],\n";
        file << "  \"escapeThreshold\": " << escapeThreshold << ",\n";
        file << "  \"angle\": " << angle << ",\n";
        file << "  \"freq\": " << freq << ",\n";
        file << "  \"phase\": " << phase << ",\n";
        file << "  \"funcID\": " << funcID << ",\n";
        file << "  \"angleTarget\": " << angleTarget << ",\n";
        file << "  \"freqTarget\": " << freqTarget << ",\n";
        file << "  \"phaseTarget\": " << phaseTarget << ",\n";
        file << "  \"funcID2\": " << funcID2 << ",\n";
        file << "  \"funcBlend\": " << funcBlend << ",\n";
        file << "  \"visualMode\": " << visualMode << ",\n";
        file << "  \"time\": " << currentTime << "\n";
        file << "}\n";
    }
};

// Función principal de ejemplo
int main() {
    std::cout << "FractalCreator - Iniciando generación" << std::endl;
    
    FractalCreator creator(512, 512);
    
    // Configuración de ejemplo
    creator.setZoom(1.5f);
    creator.setOffset(-0.2f, 0.1f);
    creator.setIterations(150);
    creator.setJuliaConstant(-0.4f, 0.6f);
    creator.setTime(2.5f);
    creator.setVisualMode(1); // Modo color
    
    // Generar y exportar
    creator.exportPPM("fractal_output.ppm");
    creator.exportConfig("fractal_config.json");
    
    std::cout << "Fractal generado: fractal_output.ppm" << std::endl;
    std::cout << "Configuración guardada: fractal_config.json" << std::endl;
    
    return 0;
}