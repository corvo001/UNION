#include <iostream>
#include <fstream>
#include <cmath>

class Complex {
public:
    double real, imag;
    
    Complex(double r = 0.0, double i = 0.0) : real(r), imag(i) {}
    
    Complex operator+(const Complex& other) const {
        return Complex(real + other.real, imag + other.imag);
    }
    
    Complex operator*(const Complex& other) const {
        return Complex(
            real * other.real - imag * other.imag,
            real * other.imag + imag * other.real
        );
    }
    
    double MagnitudeSquared() const {
        return real * real + imag * imag;
    }
};

int mandelbrotIterations(const Complex& c, int maxIter) {
    Complex z(0.0, 0.0);
    for (int i = 0; i < maxIter; ++i) {
        if (z.MagnitudeSquared() > 4.0) {
            return i;
        }
        z = z * z + c;
    }
    return maxIter;
}

int main() {
    std::cout << "Generando fractal..." << std::endl;
    
    const int width = 400;
    const int height = 400;
    const int maxIter = 50;
    
    std::ofstream file("fractal.ppm");
    file << "P3\n" << width << " " << height << "\n255\n";
    
    for (int y = 0; y < height; ++y) {
        for (int x = 0; x < width; ++x) {
            double real = (x - width/2.0) * 3.0 / width - 0.5;
            double imag = (y - height/2.0) * 3.0 / width;
            
            Complex c(real, imag);
            int iter = mandelbrotIterations(c, maxIter);
            
            int color = (iter * 255) / maxIter;
            file << color << " " << (255-color) << " 128 ";
        }
        file << "\n";
    }
    
    file.close();
    std::cout << "Fractal creado: fractal.ppm" << std::endl;
    return 0;
}