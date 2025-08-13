#include "ShaderProgram.h"
#include <vector>
#include <iostream>
#include <fstream>
#include <sstream>

ShaderProgram::ShaderProgram() : m_program(0) {}

ShaderProgram::~ShaderProgram() {
    if (m_program) {
        glDeleteProgram(m_program);
    }
}

bool ShaderProgram::LoadFromFiles(const std::string& vertexPath, const std::string& fragmentPath) {
    // Read vertex shader
    std::ifstream vertexFile(vertexPath);
    if (!vertexFile.is_open()) {
        std::cerr << "Could not open vertex shader: " << vertexPath << std::endl;
        return false;
    }
    
    std::stringstream vertexStream;
    vertexStream << vertexFile.rdbuf();
    vertexFile.close();
    
    // Read fragment shader
    std::ifstream fragmentFile(fragmentPath);
    if (!fragmentFile.is_open()) {
        std::cerr << "Could not open fragment shader: " << fragmentPath << std::endl;
        return false;
    }
    
    std::stringstream fragmentStream;
    fragmentStream << fragmentFile.rdbuf();
    fragmentFile.close();
    
    return LoadFromStrings(vertexStream.str(), fragmentStream.str());
}

bool ShaderProgram::LoadFromStrings(const std::string& vertexSource, const std::string& fragmentSource) {
    // Compile shaders
    GLuint vertexShader = CompileShader(vertexSource, GL_VERTEX_SHADER);
    if (vertexShader == 0) return false;
    
    GLuint fragmentShader = CompileShader(fragmentSource, GL_FRAGMENT_SHADER);
    if (fragmentShader == 0) {
        glDeleteShader(vertexShader);
        return false;
    }
    
    // Create program
    m_program = glCreateProgram();
    glAttachShader(m_program, vertexShader);
    glAttachShader(m_program, fragmentShader);
    glLinkProgram(m_program);
    
    // Check linking
    GLint success;
    glGetProgramiv(m_program, GL_LINK_STATUS, &success);
    if (!success) {
        char infoLog[512];
        glGetProgramInfoLog(m_program, 512, NULL, infoLog);
        std::cerr << "Shader program linking failed: " << infoLog << std::endl;
        
        glDeleteShader(vertexShader);
        glDeleteShader(fragmentShader);
        glDeleteProgram(m_program);
        m_program = 0;
        return false;
    }
    
    // Cleanup
    glDeleteShader(vertexShader);
    glDeleteShader(fragmentShader);
    
    return true;
}

GLuint ShaderProgram::CompileShader(const std::string& source, GLenum type) {
    GLuint shader = glCreateShader(type);
    const char* sourceCStr = source.c_str();
    glShaderSource(shader, 1, &sourceCStr, NULL);
    glCompileShader(shader);
    
    // Check compilation
    GLint success;
    glGetShaderiv(shader, GL_COMPILE_STATUS, &success);
    if (!success) {
        char infoLog[512];
        glGetShaderInfoLog(shader, 512, NULL, infoLog);
        std::cerr << "Shader compilation failed (" << 
            (type == GL_VERTEX_SHADER ? "vertex" : "fragment") << 
            "): " << infoLog << std::endl;
        glDeleteShader(shader);
        return 0;
    }
    
    return shader;
}

void ShaderProgram::Use() {
    if (m_program) glUseProgram(m_program);
}

void ShaderProgram::Unuse() {
    glUseProgram(0);
}

GLint ShaderProgram::GetUniformLocation(const std::string& name) {
    return glGetUniformLocation(m_program, name.c_str());
}

void ShaderProgram::SetUniform(const std::string& name, int value) {
    glUniform1i(GetUniformLocation(name), value);
}

void ShaderProgram::SetUniform(const std::string& name, float value) {
    glUniform1f(GetUniformLocation(name), value);
}

void ShaderProgram::SetUniform(const std::string& name, float x, float y) {
    glUniform2f(GetUniformLocation(name), x, y);
}

void ShaderProgram::SetUniform(const std::string& name, float x, float y, float z) {
    glUniform3f(GetUniformLocation(name), x, y, z);
}

void ShaderProgram::SetUniform(const std::string& name, float x, float y, float z, float w) {
    glUniform4f(GetUniformLocation(name), x, y, z, w);
}