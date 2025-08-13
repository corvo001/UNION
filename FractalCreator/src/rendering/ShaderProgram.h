#pragma once
#include <string>
#include "glad/glad.h"

class ShaderProgram {
public:
    ShaderProgram();
    ~ShaderProgram();
    
    bool LoadFromFiles(const std::string& vertexPath, const std::string& fragmentPath);
    bool LoadFromStrings(const std::string& vertexSource, const std::string& fragmentSource);
    
    void Use();
    void Unuse();
    
    // Uniform setters
    void SetUniform(const std::string& name, int value);
    void SetUniform(const std::string& name, float value);
    void SetUniform(const std::string& name, float x, float y);
    void SetUniform(const std::string& name, float x, float y, float z);
    void SetUniform(const std::string& name, float x, float y, float z, float w);
    
    GLuint GetProgram() const { return m_program; }
    bool IsValid() const { return m_program != 0; }
    
private:
    GLuint m_program;
    GLuint CompileShader(const std::string& source, GLenum type);
    GLint GetUniformLocation(const std::string& name);
};
