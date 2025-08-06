"""
FractalExplorer - Módulo principal del explorador de fractales
"""
module FractalExplorer

# Re-exportar los submódulos
include("communication.jl")
include("fractal_analysis.jl")

using .Communication
using .FractalAnalysis

# Re-exportar funciones principales
export Communication, FractalAnalysis
export read_fractal_params, write_explorer_status, write_fractal_analysis
export analyze_fractal_region, compute_interest_metrics
export mandelbrot_point, julia_point, burning_ship_point

end # module FractalExplorer