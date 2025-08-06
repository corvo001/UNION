"""
Sistema de comunicación con Nexo via archivos JSON compartidos
FractalExplorer EXPORTA los resultados visualizados
"""
module Communication

using JSON3
using Dates
using Printf

export read_raven_analysis, write_visualization_results, write_explorer_status, 
       read_explorer_commands, VisualizationResult, ExplorerStatus, 
       initialize_communication, generate_export_summary

# Estructuras de datos para comunicación
struct RavenAnalysis
    timestamp::String
    fractal_type::Int
    analysis_results::Dict{String, Float64}
    ai_recommendations::Vector{String}
    complexity_score::Float64
    interest_regions::Vector{Dict{String, Float64}}
end

struct VisualizationResult
    timestamp::String
    fractal_type::Int
    center_x::Float64
    center_y::Float64
    zoom::Float64
    resolution::Int
    exported_image_path::String
    metrics::Dict{String, Float64}
    visualization_settings::Dict{String, Any}
    component::String
end

struct ExplorerStatus
    timestamp::String
    component::String
    status::String
    is_running::Bool
    uptime_seconds::Int
    total_visualizations::Int
    exports_generated::Int
    current_resolution::Int
    language::String
end

# Variables globales para tracking
const SHARED_PATH = Ref{String}("shared")  # Dentro de FractalExplorer
const START_TIME = Ref{DateTime}(now())
const VISUALIZATION_COUNT = Ref{Int}(0)
const EXPORT_COUNT = Ref{Int}(0)

"""
Inicializar sistema de comunicación
"""
function initialize_communication(shared_path::String = "shared")
    SHARED_PATH[] = shared_path
    START_TIME[] = now()
    
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
Leer análisis de Raven (IA)
"""
function read_raven_analysis()::Union{RavenAnalysis, Nothing}
    file_path = joinpath(SHARED_PATH[], "raven_analysis.json")
    
    if !isfile(file_path)
        return nothing  # No hay análisis nuevo
    end
    
    try
        content = read(file_path, String)
        data = JSON3.read(content)
        
        analysis = RavenAnalysis(
            get(data, :timestamp, string(now())),
            get(data, :fractal_type, 0),
            get(data, :analysis_results, Dict{String, Float64}()),
            get(data, :ai_recommendations, String[]),
            get(data, :complexity_score, 0.0),
            get(data, :interest_regions, Dict{String, Float64}[])
        )
        
        println("🐍 Análisis de Raven leído: complejidad $(analysis.complexity_score)")
        
        # Marcar como procesado moviendo el archivo
        processed_path = joinpath(SHARED_PATH[], "processed_raven_analysis_$(now()).json")
        mv(file_path, processed_path)
        
        return analysis
        
    catch e
        @error "Error leyendo análisis de Raven" exception=e
        return nothing
    end
end

"""
Escribir resultados de visualización (EXPORTACIÓN PRINCIPAL)
"""
function write_visualization_results(
    fractal_data::Matrix{Float64}, 
    fractal_params::Dict{String, Any},
    visualization_metrics::Dict{String, Float64}
)
    timestamp = string(now())
    
    # Crear nombre único para la imagen exportada
    image_filename = "fractal_export_$(replace(timestamp, ":" => "-", "." => "_")).png"
    image_path = joinpath(SHARED_PATH[], image_filename)
    
    # TODO: Exportar imagen del fractal (esto se haría con Plots o similar)
    # save_fractal_image(fractal_data, image_path)
    
    # Crear resultado de visualización
    result = VisualizationResult(
        timestamp,
        get(fractal_params, "fractal_type", 0),
        get(fractal_params, "center_x", 0.0),
        get(fractal_params, "center_y", 0.0),
        get(fractal_params, "zoom", 1.0),
        get(fractal_params, "resolution", 512),
        image_path,
        visualization_metrics,
        Dict(
            "color_scheme" => get(fractal_params, "color_scheme", "hot"),
            "max_iterations" => get(fractal_params, "max_iterations", 200),
            "export_format" => "PNG",
            "quality" => "high"
        ),
        "FractalExplorer"
    )
    
    # Escribir resultado principal
    result_path = joinpath(SHARED_PATH[], "visualization_result.json")
    
    try
        json_data = JSON3.write(result)
        write(result_path, json_data)
        
        # También crear historial
        history_path = joinpath(SHARED_PATH[], "export_history_$(replace(timestamp, ":" => "-")).json")
        write(history_path, json_data)
        
        EXPORT_COUNT[] += 1
        
        println("📤 Resultado de visualización exportado:")
        println("   📊 Métricas: $(length(visualization_metrics)) calculadas")
        println("   🖼️  Imagen: $image_filename")
        println("   📁 Total exportaciones: $(EXPORT_COUNT[])")
        
    catch e
        @error "Error escribiendo resultado de visualización" exception=e
    end
end

"""
Escribir estado del explorador
"""
function write_explorer_status(status::String = "visualizing")
    uptime = Int(round((now() - START_TIME[]).value / 1000))
    
    explorer_status = ExplorerStatus(
        string(now()),
        "FractalExplorer",
        status,
        true,
        uptime,
        VISUALIZATION_COUNT[],
        EXPORT_COUNT[],
        512,  # Resolución actual
        "Julia"
    )
    
    file_path = joinpath(SHARED_PATH[], "explorer_status.json")
    
    try
        json_data = JSON3.write(explorer_status)
        write(file_path, json_data)
        println("📤 Estado del explorador actualizado: $(EXPORT_COUNT[]) exportaciones, uptime $(uptime)s")
    catch e
        @error "Error escribiendo estado del explorador" exception=e
    end
end

"""
Leer comandos para el explorador (enviados por Nexo)
"""
function read_explorer_commands()::Vector{String}
    file_path = joinpath(SHARED_PATH[], "explorer_commands.json")
    
    if !isfile(file_path)
        return String[]
    end
    
    try
        content = read(file_path, String)
        data = JSON3.read(content)
        
        # Eliminar archivo después de leer
        rm(file_path)
        
        commands = get(data, :commands, String[])
        
        if !isempty(commands)
            println("📨 $(length(commands)) comandos recibidos de Nexo")
        end
        
        return commands
        
    catch e
        @error "Error leyendo comandos del explorador" exception=e
        return String[]
    end
end

"""
Generar resumen de exportación
"""
function generate_export_summary()::Dict{String, Any}
    uptime = Int(round((now() - START_TIME[]).value / 1000))
    
    summary = Dict{String, Any}(
        "timestamp" => string(now()),
        "component" => "FractalExplorer",
        "role" => "Visualización y Exportación",
        "uptime_seconds" => uptime,
        "total_visualizations" => VISUALIZATION_COUNT[],
        "total_exports" => EXPORT_COUNT[],
        "average_exports_per_minute" => uptime > 0 ? (EXPORT_COUNT[] * 60.0 / uptime) : 0.0,
        "shared_directory" => SHARED_PATH[],
        "status" => "active"
    )
    
    # Escribir resumen
    summary_path = joinpath(SHARED_PATH[], "export_summary.json")
    
    try
        json_data = JSON3.write(summary)
        write(summary_path, json_data)
        println("📋 Resumen de exportación generado")
    catch e
        @error "Error generando resumen de exportación" exception=e
    end
    
    return summary
end

"""
Limpiar archivos antiguos
"""
function cleanup_old_exports(days_old::Int = 7)
    try
        cutoff_time = now() - Day(days_old)
        
        files_cleaned = 0
        for file in readdir(SHARED_PATH[])
            if startswith(file, "export_history_") || startswith(file, "processed_")
                file_path = joinpath(SHARED_PATH[], file)
                file_time = unix2datetime(stat(file_path).mtime)
                
                if file_time < cutoff_time
                    rm(file_path)
                    files_cleaned += 1
                end
            end
        end
        
        if files_cleaned > 0
            println("🧹 Limpieza completada: $files_cleaned archivos antiguos eliminados")
        end
        
    catch e
        @warn "Error en limpieza de archivos" exception=e
    end
end

end # module Communication