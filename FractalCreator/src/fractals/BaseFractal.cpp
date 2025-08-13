#include "BaseFractal.h"

void BaseFractal::SetParameter(const std::string& name, double value) {
    m_parameters[name] = value;
}

double BaseFractal::GetParameter(const std::string& name) const {
    auto it = m_parameters.find(name);
    return (it != m_parameters.end()) ? it->second : 0.0;
}

bool BaseFractal::HasParameter(const std::string& name) const {
    return m_parameters.find(name) != m_parameters.end();
}
