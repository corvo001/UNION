"""
Motor de análisis matemático para fractales
"""
module FractalAnalysis

using LinearAlgebra
using Statistics
using Printf

export analyze_fractal_region, compute_interest_metrics, 
       mandelbrot_point, julia_point, burning_ship_point

function mandelbrot_point(c::Complex{Float64}, max_iterations::Int)
    z = 0.0 + 0.0im
    for i in 1:max_iterations
        if abs2(z) > 4.0
            smooth_i = i + 1 - log(log(abs(z)))/log(2.0)
            return (i, smooth_i)
        end
        z = z^2 + c
    end
    return (max_iterations, Float64(max_iterations))
end

function julia_point(z::Complex{Float64}, c::Complex{Float64}, max_iterations::Int)
    for i in 1:max_iterations
        if abs2(z) > 4.0
            smooth_i = i + 1 - log(log(abs(z)))/log(2.0)
            return (i, smooth_i)
        end
        z = z^2 + c
    end
    return (max_iterations, Float64(max_iterations))
end

function burning_ship_point(c::Complex{Float64}, max_iterations::Int)
    z = 0.0 + 0.0im
    for i in 1:max_iterations
        if abs2(z) > 4.0
            smooth_i = i + 1 - log(log(abs(z)))/log(2.0)
            return (i, smooth_i)
        end
        z = complex(abs(real(z)), abs(imag(z)))^2 + c
    end
    return (max_iterations, Float64(max_iterations))
end

function compute_interest_metrics(iterations::Matrix{Int}, escape_times::Matrix{Float64}, max_iterations::Int)
    resolution = size(iterations, 1)
    
    # Fracción en el conjunto
    in_set = sum(iterations .== max_iterations)
    set_fraction = in_set / (resolution^2)
    
    # Entropía básica
    unique_vals = unique(vec(iterations))
    entropy = 0.0
    for val in unique_vals
        count = sum(iterations .== val)
        if count > 0
            p = count / (resolution^2)
            entropy -= p * log2(p)
        end
    end
    entropy_normalized = length(unique_vals) > 1 ? entropy / log2(length(unique_vals)) : 0.0
    
    # Complejidad como varianza
    complexity_measure = var(Float64.(vec(iterations))) / (max_iterations^2)
    
    # Gradiente para detectar bordes - VERSIÓN CORREGIDA
    if resolution > 1
        grad_x = diff(Float64.(iterations), dims=1)  # (resolution-1, resolution)
        grad_y = diff(Float64.(iterations), dims=2)  # (resolution, resolution-1)
        
        # Tomar solo la región común válida
        min_rows = min(size(grad_x, 1), size(grad_y, 1))
        min_cols = min(size(grad_x, 2), size(grad_y, 2))
        
        if min_rows > 0 && min_cols > 0
            grad_x_common = grad_x[1:min_rows, 1:min_cols]
            grad_y_common = grad_y[1:min_rows, 1:min_cols]
            avg_gradient = mean(abs.(grad_x_common) .+ abs.(grad_y_common))
        else
            avg_gradient = 0.0
        end
    else
        avg_gradient = 0.0
    end
    
    gradient_normalized = min(avg_gradient / max_iterations, 1.0)
    
    # Score de interés
    interest_score = (set_fraction * 0.25 + entropy_normalized * 0.35 + 
                     complexity_measure * 0.25 + gradient_normalized * 0.15)
    
    return Dict{String, Float64}(
        "set_fraction" => set_fraction,
        "entropy" => entropy_normalized,
        "complexity_measure" => complexity_measure,
        "average_gradient" => gradient_normalized,
        "interesting_score" => min(interest_score, 1.0),
        "escape_variance" => var(vec(escape_times)),
        "escape_mean" => mean(escape_times),
        "boundary_length" => gradient_normalized,
        "resolution" => Float64(resolution)
    )
end

end # module FractalAnalysis