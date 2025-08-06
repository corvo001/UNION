#!/usr/bin/env julia

"""
FractalExplorer - Explorador Inteligente de Fractales
Componente Julia del ecosistema UNION
Versión avanzada con todas las funcionalidades
"""

using GLMakie
using JSON3
using Dates
using Statistics
using LinearAlgebra
using Printf

# Variables globales del explorador
const EXPLORER_VERSION = "1.0.0"
const SHARED_PATH = "shared"  # Directorio local para exportación
const RESOLUTION = 512  # Mayor resolución para análisis
const MAX_ITER = 200    # Más iteraciones para mejor precisión

# Definir estructuras de datos localmente
struct RavenAnalysis
    timestamp::String
    fractal_type::Int
    analysis_results::Dict{String, Float64}
    ai_recommendations::Vector{String}
    complexity_score::Float64
    interest_regions::Vector{Dict{String, Float64}}
end

# Estado del explorador mejorado
mutable struct ExplorerState
    running::Bool
    auto_scan::Bool
    last_analysis::DateTime
    scan_count::Int
    export_count::Int
    centro_x::Float64
    centro_y::Float64
    zoom::Float64
    fractal_type::Int
    julia_c::Complex{Float64}
    analysis_mode::Symbol  # :manual, :auto, :intelligent
    current_analysis::Union{RavenAnalysis, Nothing}
end

# Estado global
const state = ExplorerState(
    false, true, now(), 0, 0,
    0.0, 0.0, 1.0, 0, -0.7 + 0.27015im, :auto, nothing
)

# Colores para diferentes métricas
const COLOR_SCHEMES = [:hot, :plasma, :viridis, :turbo, :inferno, :cool, :winter, :spring, :summer]
const METRIC_COLORS = [:hot, :plasma, :viridis, :coolwarm]

"""
Funciones de cálculo de fractales
"""
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

"""
Calcular fractal optimizado con análisis en tiempo real
"""
function calcular_fractal_con_analisis(h, w, cx, cy, zoom, fractal_type, julia_c, max_iter)
    img = zeros(Float64, h, w)
    iterations_matrix = zeros(Int, h, w)
    escape_times = zeros(Float64, h, w)
    
    rango = 4.0 / zoom
    
    # Cálculo paralelo del fractal
    Threads.@threads for i in 1:h
        for j in 1:w
            # Mapear a coordenadas complejas
            real_c = cx + (j - w/2) * rango / w
            imag_c = cy + (i - h/2) * rango / h
            c = complex(real_c, imag_c)
            
            # Calcular según el tipo de fractal
            iter, escape_time = if fractal_type == 0  # Mandelbrot
                mandelbrot_point(c, max_iter)
            elseif fractal_type == 1  # Julia
                julia_point(c, julia_c, max_iter)
            elseif fractal_type == 2  # Burning Ship
                burning_ship_point(c, max_iter)
            else
                mandelbrot_point(c, max_iter)
            end
            
            iterations_matrix[i, j] = iter
            escape_times[i, j] = escape_time
            img[i, j] = escape_time / max_iter
        end
    end
    
    return img, iterations_matrix, escape_times
end

"""
Computar métricas de interés avanzadas
"""
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
    
    # Gradiente para detectar bordes
    if resolution > 1
        grad_x = diff(Float64.(iterations), dims=1)
        grad_y = diff(Float64.(iterations), dims=2)
        
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

"""
Inicializar sistema de comunicación
"""
function initialize_communication(shared_path::String = "shared")
    # Crear directorio compartido si no existe
    if !isdir(shared_path)
        mkpath(shared_path)
        println("📁 Directorio compartido creado: $shared_path")
    end
    
    println("📡 Sistema de comunicación inicializado")
    println("   Ruta compartida: $shared_path")
    println("   Rol: Visualización y exportación de resultados")
    return true
end

"""
Leer análisis de Raven
"""
function read_raven_analysis()::Union{RavenAnalysis, Nothing}
    file_path = joinpath(SHARED_PATH, "raven_analysis.json")
    
    if !isfile(file_path)
        return nothing
    end
    
    try
        content = read(file_path, String)
        data = JSON3.read(content)
        
        analysis = RavenAnalysis(
            get(data, "timestamp", string(now())),
            get(data, "fractal_type", 0),
            get(data, "analysis_results", Dict{String, Float64}()),
            get(data, "ai_recommendations", String[]),
            get(data, "complexity_score", 0.0),
            get(data, "interest_regions", Dict{String, Float64}[])
        )
        
        println("🐍 Análisis de Raven leído: complejidad $(analysis.complexity_score)")
        
        # Marcar como procesado
        processed_path = joinpath(SHARED_PATH, "processed_raven_$(replace(string(now()), ":" => "-")).json")
        mv(file_path, processed_path)
        
        return analysis
        
    catch e
        @error "Error leyendo análisis de Raven" exception=e
        return nothing
    end
end

"""
Escribir resultados de visualización
"""
function write_visualization_results(
    fractal_data::Matrix{Float64}, 
    fractal_params::Dict{String, Any},
    visualization_metrics::Dict{String, Float64}
)
    timestamp = string(now())
    
    # Crear resultado de visualización
    result = Dict(
        "timestamp" => timestamp,
        "fractal_type" => get(fractal_params, "fractal_type", 0),
        "center_x" => get(fractal_params, "center_x", 0.0),
        "center_y" => get(fractal_params, "center_y", 0.0),
        "zoom" => get(fractal_params, "zoom", 1.0),
        "resolution" => get(fractal_params, "resolution", 512),
        "metrics" => visualization_metrics,
        "visualization_settings" => Dict(
            "color_scheme" => get(fractal_params, "color_scheme", "hot"),
            "max_iterations" => get(fractal_params, "max_iterations", 200),
            "export_format" => "JSON",
            "quality" => "high"
        ),
        "component" => "FractalExplorer"
    )
    
    # Escribir resultado principal
    result_path = joinpath(SHARED_PATH, "visualization_result.json")
    
    try
        json_data = JSON3.write(result)
        write(result_path, json_data)
        
        # También crear historial
        history_path = joinpath(SHARED_PATH, "export_history_$(replace(timestamp, ":" => "-")).json")
        write(history_path, json_data)
        
        state.export_count += 1
        
        println("📤 Resultado de visualización exportado:")
        println("   📊 Métricas: $(length(visualization_metrics)) calculadas")
        println("   📁 Total exportaciones: $(state.export_count)")
        
    catch e
        @error "Error escribiendo resultado de visualización" exception=e
    end
end

"""
Función principal del explorador
"""
function main()
    println("FRACTAL EXPLORER v$EXPLORER_VERSION")
    println("=====================================")
    println("Explorador inteligente de fractales en Julia")
    println("Parte del ecosistema UNION")
    println()
    
    # Inicializar comunicación con Nexo
    if !initialize_communication(SHARED_PATH)
        @warn "Sistema de comunicación no disponible - modo standalone"
    else
        println("Conectado al ecosistema UNION")
    end
    
    # Configurar estado inicial
    state.running = true
    state.last_analysis = now()
    
    # Crear interfaz con GLMakie
    fig, timer = crear_interfaz_explorer()
    
    println("FractalExplorer iniciado con éxito!")
    return fig, timer
end

"""
Crear interfaz principal del explorador
"""
function crear_interfaz_explorer()
    # Crear figura principal con múltiples paneles
    fig = Figure(size=(1200, 900), fontsize=12)
    
    # Panel principal del fractal
    ax_main = Axis(fig[1:2, 1:2], 
                   title="FractalExplorer - Análisis Inteligente",
                   aspect=DataAspect())
    
    # Panel de métricas en tiempo real
    ax_metrics = Axis(fig[1, 3], 
                      title="Métricas de Interés",
                      xlabel="Tiempo", ylabel="Score")
    
    # Panel de análisis detallado
    ax_analysis = Axis(fig[2, 3],
                       title="Análisis Detallado",
                       aspect=DataAspect())
    
    # Generar fractal inicial
    println("Generando fractal inicial...")
    datos_fractal = Observable{Matrix{Float64}}(zeros(RESOLUTION, RESOLUTION))
    iterations_data = Observable{Matrix{Int}}(zeros(Int, RESOLUTION, RESOLUTION))  
    metrics_data = Observable{Dict{String, Float64}}(Dict{String, Float64}())
    
    # Actualizar fractal inicial
    actualizar_fractal_completo!(datos_fractal, iterations_data, metrics_data)
    
    # Visualización principal del fractal
    hm_main = heatmap!(ax_main, datos_fractal, colormap=:hot)
    
    # Visualización de métricas (placeholder inicial)
    metrics_history = Observable(Float64[])
    time_history = Observable(Float64[])
    lines!(ax_metrics, time_history, metrics_history, color=:cyan, linewidth=2)
    
    # Análisis detallado (heatmap de complejidad)
    analysis_viz = heatmap!(ax_analysis, datos_fractal, colormap=:viridis)
    
    # Panel de información en tiempo real
    info_panel = GridLayout(fig[3, 1:3])
    
    # Información básica
    info_text = Observable("Centro: (0.0, 0.0) | Zoom: 1.0x | Tipo: Mandelbrot")
    Label(info_panel[1, 1:2], info_text, tellwidth=false, fontsize=14)
    
    # Métricas actuales
    metrics_text = Observable("Score: 0.0 | Complejidad: 0.0 | Entropía: 0.0")
    Label(info_panel[2, 1:2], metrics_text, tellwidth=false, fontsize=12, color=:orange)
    
    # Recomendaciones del análisis
    recommendations_text = Observable("Iniciando análisis...")
    Label(info_panel[3, 1:2], recommendations_text, tellwidth=false, fontsize=11, color=:lightblue)
    
    # Panel de controles
    controls_panel = GridLayout(fig[4, 1:3])
    
    # Controles principales
    btn_analyze = Button(controls_panel[1, 1], label="ANALIZAR REGIÓN")
    btn_auto_scan = Button(controls_panel[1, 2], label="AUTO-SCAN: ON")
    btn_colors = Button(controls_panel[1, 3], label="CAMBIAR COLORES")
    btn_fractal_type = Button(controls_panel[1, 4], label="TIPO: MANDELBROT")
    
    # Controles de zoom
    btn_zoom_in = Button(controls_panel[2, 1], label="ZOOM IN (2x)")
    btn_zoom_out = Button(controls_panel[2, 2], label="ZOOM OUT (0.5x)")
    btn_reset = Button(controls_panel[2, 3], label="RESET VISTA")
    btn_deep_scan = Button(controls_panel[2, 4], label="ANÁLISIS PROFUNDO")
    
    # Variables de control
    color_actual = Ref(1)
    auto_scan_active = Ref(true)
    
    # === EVENTOS INTERACTIVOS ===
    
    # Navegación con clic (paneo inteligente)
    on(events(ax_main).mousebutton) do evento
        if evento.button == Mouse.left && evento.action == Mouse.press
            try
                pos = mouseposition(ax_main.scene)
                if pos !== nothing
                    # Convertir a coordenadas del fractal
                    rango = 4.0 / state.zoom
                    nuevo_centro_x = state.centro_x + (pos[1] - RESOLUTION/2) * rango / RESOLUTION
                    nuevo_centro_y = state.centro_y + (pos[2] - RESOLUTION/2) * rango / RESOLUTION
                    
                    state.centro_x = nuevo_centro_x
                    state.centro_y = nuevo_centro_y
                    
                    println("Navegando a: ($(round(state.centro_x, digits=4)), $(round(state.centro_y, digits=4)))")
                    actualizar_fractal_completo!(datos_fractal, iterations_data, metrics_data)
                    actualizar_interfaz!(info_text, metrics_text, recommendations_text, metrics_data[])
                    
                    # Enviar análisis a Nexo si está conectado
                    enviar_analisis_a_nexo(metrics_data[])
                end
            catch e
                @warn "Error en navegación" exception=e
            end
        end
    end
    
    # Análisis manual
    on(btn_analyze.clicks) do n
        println("Iniciando análisis manual...")
        realizar_analisis_completo!(datos_fractal, iterations_data, metrics_data, analysis_viz)
        actualizar_interfaz!(info_text, metrics_text, recommendations_text, metrics_data[])
        enviar_analisis_a_nexo(metrics_data[])
    end
    
    # Toggle auto-scan
    on(btn_auto_scan.clicks) do n
        auto_scan_active[] = !auto_scan_active[]
        state.auto_scan = auto_scan_active[]
        btn_auto_scan.label = state.auto_scan ? "AUTO-SCAN: ON" : "AUTO-SCAN: OFF"
        println("Auto-scan: $(state.auto_scan ? "activado" : "desactivado")")
    end
    
    # Cambiar colores
    on(btn_colors.clicks) do n
        color_actual[] = (color_actual[] % length(COLOR_SCHEMES)) + 1
        hm_main.colormap = COLOR_SCHEMES[color_actual[]]
        println("Esquema de color: $(COLOR_SCHEMES[color_actual[]])")
    end
    
    # Cambiar tipo de fractal
    on(btn_fractal_type.clicks) do n
        state.fractal_type = (state.fractal_type + 1) % 3
        fractal_names = ["MANDELBROT", "JULIA", "BURNING SHIP"]
        btn_fractal_type.label = "TIPO: $(fractal_names[state.fractal_type + 1])"
        println("Cambiado a: $(fractal_names[state.fractal_type + 1])")
        actualizar_fractal_completo!(datos_fractal, iterations_data, metrics_data)
        actualizar_interfaz!(info_text, metrics_text, recommendations_text, metrics_data[])
    end
    
    # Controles de zoom
    on(btn_zoom_in.clicks) do n
        state.zoom *= 2.0
        println("Zoom aumentado a: $(state.zoom)x")
        actualizar_fractal_completo!(datos_fractal, iterations_data, metrics_data)
        actualizar_interfaz!(info_text, metrics_text, recommendations_text, metrics_data[])
    end
    
    on(btn_zoom_out.clicks) do n
        state.zoom = max(state.zoom / 2.0, 0.1)
        println("Zoom reducido a: $(state.zoom)x")
        actualizar_fractal_completo!(datos_fractal, iterations_data, metrics_data)
        actualizar_interfaz!(info_text, metrics_text, recommendations_text, metrics_data[])
    end
    
    # Reset vista
    on(btn_reset.clicks) do n
        state.centro_x = 0.0
        state.centro_y = 0.0
        state.zoom = 1.0
        state.fractal_type = 0
        println("Vista reseteada")
        actualizar_fractal_completo!(datos_fractal, iterations_data, metrics_data)
        actualizar_interfaz!(info_text, metrics_text, recommendations_text, metrics_data[])
    end
    
    # Análisis profundo
    on(btn_deep_scan.clicks) do n
        println("Iniciando análisis profundo...")
        realizar_analisis_profundo!(datos_fractal, iterations_data, metrics_data, analysis_viz)
        actualizar_interfaz!(info_text, metrics_text, recommendations_text, metrics_data[])
        generar_recomendaciones_inteligentes(metrics_data[])
    end
    
    # === LOOP PRINCIPAL DE AUTO-ANÁLISIS ===
    
    # Timer para auto-scan y comunicación con Nexo
    timer = Timer(0.0, interval=5.0) do timer
        if state.auto_scan && auto_scan_active[]
            # Leer comandos de Nexo
            procesar_comandos_nexo!(datos_fractal, iterations_data, metrics_data)
            
            # Auto-análisis periódico
            if now() - state.last_analysis > Millisecond(30000)  # Cada 30 segundos
                realizar_analisis_completo!(datos_fractal, iterations_data, metrics_data, analysis_viz)
                actualizar_interfaz!(info_text, metrics_text, recommendations_text, metrics_data[])
                enviar_analisis_a_nexo(metrics_data[])
                state.last_analysis = now()
            end
        end
    end
    
    # Mostrar interfaz
    display(fig)
    
    println("✅ Interfaz del explorador lista!")
    println()
    println("CONTROLES:")
    println("   CLIC IZQUIERDO: Navegar a región")
    println("   ANALIZAR REGIÓN: Análisis matemático detallado")
    println("   AUTO-SCAN: Análisis automático continuo")
    println("   CAMBIAR COLORES: Rotar esquemas de visualización")
    println("   ZOOM: Acercar/alejar vista")
    println("   ANÁLISIS PROFUNDO: Análisis con IA y recomendaciones")
    println()
    println("Estado: Conectado al ecosistema UNION")
    println("Comunicación con Nexo: Activa")
    println()
    println("⚠️  MANTÉN LA CONSOLA ABIERTA - No la cierres")
    
    return fig, timer
end

"""
Actualizar fractal completo con análisis
"""
function actualizar_fractal_completo!(datos_fractal, iterations_data, metrics_data)
    img, iterations, escape_times = calcular_fractal_con_analisis(
        RESOLUTION, RESOLUTION, state.centro_x, state.centro_y, 
        state.zoom, state.fractal_type, state.julia_c, MAX_ITER
    )
    
    # Actualizar observables
    datos_fractal[] = img
    iterations_data[] = iterations
    
    # Calcular métricas de interés
    metrics = compute_interest_metrics(iterations, escape_times, MAX_ITER)
    metrics_data[] = metrics
    
    state.scan_count += 1
end

"""
Realizar análisis completo con visualización de métricas
"""
function realizar_analisis_completo!(datos_fractal, iterations_data, metrics_data, analysis_viz)
    actualizar_fractal_completo!(datos_fractal, iterations_data, metrics_data)
    
    # Crear visualización de análisis (mapa de complejidad)
    metrics = metrics_data[]
    complexity_map = create_complexity_visualization(iterations_data[])
    if analysis_viz !== nothing
        analysis_viz.input_args[1][] = complexity_map
    end
    
    println("📊 Análisis completo - Score: $(round(metrics["interesting_score"], digits=3))")
end

"""
Análisis profundo con IA
"""
function realizar_analisis_profundo!(datos_fractal, iterations_data, metrics_data, analysis_viz)
    println("Ejecutando análisis profundo con IA...")
    
    realizar_analisis_completo!(datos_fractal, iterations_data, metrics_data, analysis_viz)
    
    # Análisis adicional con IA
    metrics = metrics_data[]
    
    # Análisis de patrones avanzado
    patterns = analyze_advanced_patterns(iterations_data[])
    merge!(metrics, patterns)
    
    # Predicción de regiones interesantes
    interesting_regions = predict_interesting_regions(iterations_data[], metrics)
    
    # Actualizar métricas con análisis profundo
    metrics_data[] = metrics
    
    println("Análisis profundo completado")
    println("   Patrones detectados: $(length(patterns))")
    println("   Regiones de interés: $(length(interesting_regions))")
end

"""
Crear visualización de complejidad
"""
function create_complexity_visualization(iterations::Matrix{Int})
    h, w = size(iterations)
    complexity_map = zeros(Float64, h, w)
    
    # Calcular gradiente local como medida de complejidad
    for i in 2:h-1
        for j in 2:w-1
            grad_x = Float64(iterations[i+1, j] - iterations[i-1, j])
            grad_y = Float64(iterations[i, j+1] - iterations[i, j-1])
            complexity_map[i, j] = sqrt(grad_x^2 + grad_y^2)
        end
    end
    
    return complexity_map
end

"""
Actualizar interfaz con métricas actuales
"""
function actualizar_interfaz!(info_text, metrics_text, recommendations_text, metrics)
    fractal_names = ["Mandelbrot", "Julia", "Burning Ship"]
    current_fractal = fractal_names[state.fractal_type + 1]
    
    info_text[] = @sprintf("Centro: (%.4f, %.4f) | Zoom: %.2fx | Tipo: %s", 
                          state.centro_x, state.centro_y, state.zoom, current_fractal)
    
    interest_score = get(metrics, "interesting_score", 0.0)
    complexity = get(metrics, "complexity_measure", 0.0)
    entropy = get(metrics, "entropy", 0.0)
    
    metrics_text[] = @sprintf("Score: %.3f | Complejidad: %.3f | Entropía: %.3f | Escaneos: %d", 
                             interest_score, complexity, entropy, state.scan_count)
    
    # Generar recomendación basada en métricas
    recommendation = generate_recommendation(metrics)
    recommendations_text[] = "💡 $recommendation"
end

"""
Generar recomendación basada en métricas
"""
function generate_recommendation(metrics::Dict{String, Float64})::String
    interest_score = get(metrics, "interesting_score", 0.0)
    complexity = get(metrics, "complexity_measure", 0.0)
    boundary_length = get(metrics, "boundary_length", 0.0)
    
    if interest_score < 0.3
        return "Región poco interesante - recomendar mutación o cambio de zona"
    elseif interest_score > 0.8
        return "Región muy interesante - reducir mutación para explorar en detalle"
    elseif complexity < 0.2
        return "Baja complejidad - incrementar iteraciones o zoom"
    elseif boundary_length > 0.9
        return "Frontera compleja detectada - analizar con mayor resolución"
    else
        return "Región moderadamente interesante - continuar exploración"
    end
end

"""
Procesar comandos de Nexo
"""
function procesar_comandos_nexo!(datos_fractal, iterations_data, metrics_data)
    commands_file = joinpath(SHARED_PATH, "explorer_commands.txt")
    if isfile(commands_file)
        try
            commands = readlines(commands_file)
            rm(commands_file)
            
            for command in commands
                if command == "analyze_current"
                    realizar_analisis_completo!(datos_fractal, iterations_data, metrics_data, nothing)
                elseif command == "deep_scan"
                    realizar_analisis_profundo!(datos_fractal, iterations_data, metrics_data, nothing)
                end
            end
        catch e
            @warn "Error procesando comandos" exception=e
        end
    end
end

"""
Enviar análisis a Nexo
"""
function enviar_analisis_a_nexo(metrics::Dict{String, Float64})
    try
        # Parámetros del fractal actual
        fractal_params = Dict{String, Any}(
            "fractal_type" => state.fractal_type,
            "center_x" => state.centro_x,
            "center_y" => state.centro_y,
            "zoom" => state.zoom,
            "resolution" => RESOLUTION,
            "max_iterations" => MAX_ITER
        )
        
        write_visualization_results(zeros(Float64, 2, 2), fractal_params, metrics)
        
    catch e
        @warn "Error enviando análisis a Nexo" exception=e
    end
end

"""
Generar recomendaciones inteligentes para Nexo
"""
function generar_recomendaciones_inteligentes(metrics::Dict{String, Float64})
    recommendations = String[]
    interest_score = get(metrics, "interesting_score", 0.0)
    complexity = get(metrics, "complexity_measure", 0.0)
    
    if interest_score < 0.3
        push!(recommendations, "INCREASE_MUTATION_STRENGTH:0.3")
        push!(recommendations, "ENABLE_AUTO_MUTATION:true")
    elseif interest_score > 0.8
        push!(recommendations, "ZOOM_IN:2.0")
        push!(recommendations, "CHANGE_COLOR_SCHEME:$(rand(0:5))")
    end
    
    if complexity > 0.7
        push!(recommendations, "ZOOM_IN:1.5")
    elseif complexity < 0.2
        push!(recommendations, "CHANGE_FRACTAL_TYPE:$(rand(0:2))")
    end
    
    if !isempty(recommendations)
        # Escribir recomendaciones
        rec_file = joinpath(SHARED_PATH, "explorer_recommendations.json")
        try
            rec_data = Dict(
                "timestamp" => string(now()),
                "from_component" => "FractalExplorer",
                "target_component" => "FractalMutator",
                "analysis_score" => interest_score,
                "recommendations" => recommendations
            )
            
            json_data = JSON3.write(rec_data)
            write(rec_file, json_data)
            println("💡 $(length(recommendations)) recomendaciones enviadas a Nexo")
        catch e
            @warn "Error escribiendo recomendaciones" exception=e
        end
    end
end

"""
Análisis de patrones avanzado con IA
"""
function analyze_advanced_patterns(iterations::Matrix{Int})
    patterns = Dict{String, Float64}()
    
    # Detección de simetría
    patterns["symmetry_score"] = detect_symmetry(iterations)
    
    # Detección de auto-similitud
    patterns["self_similarity"] = detect_self_similarity(iterations)
    
    # Análisis espectral
    patterns["spectral_complexity"] = analyze_frequency_content(iterations)
    
    return patterns
end

"""
Detectar simetría en la imagen
"""
function detect_symmetry(iterations::Matrix{Int})
    h, w = size(iterations)
    center_h, center_w = h÷2, w÷2
    
    # Simetría horizontal
    h_symmetry = 0.0
    for i in 1:center_h
        for j in 1:w
            if iterations[i, j] == iterations[h-i+1, j]
                h_symmetry += 1
            end
        end
    end
    h_symmetry /= (center_h * w)
    
    # Simetría vertical  
    v_symmetry = 0.0
    for i in 1:h
        for j in 1:center_w
            if iterations[i, j] == iterations[i, w-j+1]
                v_symmetry += 1
            end
        end
    end
    v_symmetry /= (h * center_w)
    
    return (h_symmetry + v_symmetry) / 2
end

"""
Detectar auto-similitud usando correlación a diferentes escalas
"""
function detect_self_similarity(iterations::Matrix{Int})
    h, w = size(iterations)
    
    # Tomar región central
    center_region = iterations[h÷4:3*h÷4, w÷4:3*w÷4]
    
    # Reducir a diferentes escalas y comparar
    scales = [2, 4]
    similarities = Float64[]
    
    for scale in scales
        # Submuestrear
        small_region = center_region[1:scale:end, 1:scale:end]
        if size(small_region, 1) > 10 && size(small_region, 2) > 10
            try
                # Correlación con la región original redimensionada
                correlation = cor(vec(Float64.(center_region[1:size(small_region,1)*scale, 1:size(small_region,2)*scale])), 
                                repeat(vec(Float64.(small_region)), scale^2))
                push!(similarities, abs(correlation))
            catch
                # Si hay error en correlación, usar medida alternativa
                push!(similarities, 0.5)
            end
        end
    end
    
    return isempty(similarities) ? 0.0 : mean(similarities)
end

"""
Análisis de contenido frecuencial
"""
function analyze_frequency_content(iterations::Matrix{Int})
    try
        # Convertir a float y centrar
        data = Float64.(iterations) .- mean(iterations)
        
        # Simplificación: usar solo estadísticas de los gradientes
        grad_x = diff(data, dims=1)
        grad_y = diff(data, dims=2)
        
        # Varianza de gradientes como proxy de complejidad espectral
        spectral_measure = var(grad_x) + var(grad_y)
        return min(spectral_measure / 10000, 1.0)  # Normalizar
    catch
        return 0.5  # Valor por defecto si falla
    end
end

"""
Predecir regiones interesantes usando análisis local
"""
function predict_interesting_regions(iterations::Matrix{Int}, metrics::Dict{String, Float64})
    h, w = size(iterations)
    interesting_regions = Tuple{Int, Int, Float64}[]  # (x, y, score)
    
    # Dividir en regiones y analizar cada una
    region_size = 32
    for i in 1:region_size:h-region_size
        for j in 1:region_size:w-region_size
            region = iterations[i:i+region_size-1, j:j+region_size-1]
            
            # Calcular score local
            local_variance = var(Float64.(region))
            local_entropy = calculate_local_entropy(region)
            local_score = (local_variance / 1000 + local_entropy) / 2
            
            if local_score > 0.6  # Umbral de interés
                push!(interesting_regions, (i+region_size÷2, j+region_size÷2, local_score))
            end
        end
    end
    
    return interesting_regions
end

"""
Calcular entropía local de una región
"""
function calculate_local_entropy(region::Matrix{Int})
    # Histograma de valores
    hist = Dict{Int, Int}()
    for val in region
        hist[val] = get(hist, val, 0) + 1
    end
    
    # Calcular entropía
    total_pixels = length(region)
    entropy = 0.0
    for count in values(hist)
        if count > 0
            p = count / total_pixels
            entropy -= p * log2(p)
        end
    end
    
    return entropy / 8  # Normalizar aproximadamente
end

"""
Generar resumen de exportación
"""
function generate_export_summary()
    uptime = Int(round((now() - state.last_analysis).value / 1000))
    
    summary = Dict(
        "timestamp" => string(now()),
        "component" => "FractalExplorer",
        "role" => "Visualización y Exportación",
        "uptime_seconds" => uptime,
        "total_scans" => state.scan_count,
        "total_exports" => state.export_count,
        "shared_directory" => SHARED_PATH,
        "status" => "active"
    )
    
    # Escribir resumen
    summary_path = joinpath(SHARED_PATH, "export_summary.json")
    
    try
        json_data = JSON3.write(summary)
        write(summary_path, json_data)
        println("📋 Resumen de exportación generado")
    catch e
        @error "Error generando resumen de exportación" exception=e
    end
    
    return summary
end

# Ejecutar si es llamado directamente
if abspath(PROGRAM_FILE) == @__FILE__
    try
        fig, timer = main()
        
        # Mantener la ventana abierta - método robusto
        println("🎮 Presiona Ctrl+C para salir")
        println("📱 O cierra la ventana para terminar")
        println("⚠️  LA VENTANA ESTÁ ABIERTA - Mira en tu pantalla!")
        
        # Loop principal - método simple y robusto
        try
            while true
                sleep(1.0)  # Dormir 1 segundo
                # Simplemente mantener el programa vivo
                # El usuario puede cerrar con Ctrl+C o cerrando la ventana
            end
        catch InterruptException
            println("\n🛑 Programa interrumpido por el usuario")
        end
        
        # Cleanup
        close(timer)
        
        # Generar resumen final
        generate_export_summary()
        
        println("✅ FractalExplorer terminado correctamente")
        
    catch e
        @error "Error en FractalExplorer" exception=e
        println("❌ El programa terminó con errores")
        rethrow(e)
    end
end