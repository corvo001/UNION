use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use uuid::Uuid;

/// Tipos de componentes en el ecosistema
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ComponentType {
    Mutator,    // FractalMutator
    Analyzer,   // FractalExplorer
    Visualizer, // Componentes de visualización futuros
    Storage,    // Componentes de almacenamiento
}

/// Estado de un componente
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ComponentStatus {
    Running,
    Idle,
    Error,
    Offline,
}

/// Información de un componente del ecosistema
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ComponentInfo {
    pub name: String,
    pub component_type: ComponentType,
    pub status: ComponentStatus,
    pub last_seen: DateTime<Utc>,
    pub data: Option<ComponentData>,
    pub metrics: HashMap<String, f64>,
}

/// Datos específicos de cada tipo de componente
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ComponentData {
    Fractal(FractalState),
    Analysis(AnalysisData),
}

/// Estado actual del generador de fractales
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FractalState {
    pub timestamp: String,
    pub fractal_type: i32,
    pub parameters: FractalParameters,
}

/// Parámetros del fractal
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FractalParameters {
    pub zoom: f64,
    #[serde(rename = "centerX")]
    pub center_x: f64,
    #[serde(rename = "centerY")]
    pub center_y: f64,
    #[serde(rename = "maxIterations")]
    pub max_iterations: i32,
    #[serde(rename = "juliaC_real")]
    pub julia_c_real: f64,
    #[serde(rename = "juliaC_imag")]
    pub julia_c_imag: f64,
    #[serde(rename = "escapeRadius")]
    pub escape_radius: f64,
    pub power: f64,
    #[serde(rename = "colorScheme")]
    pub color_scheme: i32,
    #[serde(rename = "colorSpeed")]
    pub color_speed: f64,
    #[serde(rename = "colorOffset")]
    pub color_offset: f64,
    pub brightness: f64,
    pub contrast: f64,
    #[serde(rename = "smoothColoring")]
    pub smooth_coloring: bool,
    #[serde(rename = "mutationStrength")]
    pub mutation_strength: f64,
    #[serde(rename = "autoMutate")]
    pub auto_mutate: bool,
    #[serde(rename = "autoMutateSpeed")]
    pub auto_mutate_speed: f64,
}

/// Datos de análisis del explorador
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AnalysisData {
    pub timestamp: String,
    pub region: AnalysisRegion,
    pub fractal_type: i32,
    pub max_iterations: i32,
    pub metrics: HashMap<String, f64>,
    pub recommendation: String,
    pub component: String,
}

/// Región de análisis
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AnalysisRegion {
    pub center_real: f64,
    pub center_imag: f64,
    pub width: f64,
    pub height: f64,
    pub zoom: f64,
}

/// Parámetros para análisis
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AnalysisParameters {
    pub resolution: i32,
    pub max_iterations: i32,
    pub deep_scan: bool,
}

/// Estado completo del ecosistema
#[derive(Debug, Clone)]
pub struct EcosystemState {
    pub timestamp: DateTime<Utc>,
    pub components: HashMap<String, ComponentInfo>,
    pub health_score: f64,
    pub activity_level: ActivityLevel,
    pub recommendations: Vec<String>,
}

/// Nivel de actividad del ecosistema
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub enum ActivityLevel {
    Low,      // Poca actividad, necesita estímulo
    Moderate, // Actividad normal
    High,     // Alta actividad, puede necesitar regulación
    Critical, // Actividad extrema, necesita intervención
}

/// Recomendación del explorador
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExplorerRecommendation {
    pub timestamp: String,
    pub from_component: String,
    pub target_component: String,
    pub analysis_score: f64,
    pub recommendation: String,
}

/// Reporte completo del ecosistema
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EcosystemReport {
    pub session_id: Uuid,
    pub timestamp: DateTime<Utc>,
    pub uptime_seconds: i64,
    pub total_commands: u64,
    pub active_components: usize,
    pub components: HashMap<String, ComponentInfo>,
}

/// Comandos que se pueden enviar a componentes
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum Command {
    // Comandos para el mutador
    Mutate,
    Reset,
    SetAutoMutation(bool),
    ChangeFractalType(i32),
    ChangeColorScheme(i32),
    SetMutationStrength(f64),
    ZoomIn(f64),
    ZoomOut(f64),
    SetParameters(FractalParameters),
    
    // Comandos para el explorador
    AnalyzeCurrent,
    DeepScan,
    SetResolution(i32),
    AnalyzeRegion(AnalysisRegion),
    
    // Comandos generales
    Shutdown,
    Status,
    GetMetrics,
}

impl ExplorerRecommendation {
    /// Parsear recomendación como comando
    pub fn parse_as_command(&self) -> anyhow::Result<Option<Command>> {
        let parts: Vec<&str> = self.recommendation.split(':').collect();
        if parts.len() != 2 {
            return Ok(None);
        }
        
        let (action, value) = (parts[0], parts[1]);
        
        let command = match action {
            "INCREASE_MUTATION_STRENGTH" => {
                let strength: f64 = value.parse()?;
                Command::SetMutationStrength(strength)
            }
            "ENABLE_AUTO_MUTATION" => {
                let enable: bool = value.parse()?;
                Command::SetAutoMutation(enable)
            }
            "CHANGE_FRACTAL_TYPE" => {
                let fractal_type: i32 = value.parse()?;
                Command::ChangeFractalType(fractal_type)
            }
            "CHANGE_COLOR_SCHEME" => {
                let color_scheme: i32 = value.parse()?;
                Command::ChangeColorScheme(color_scheme)
            }
            "ZOOM_IN" => {
                let factor: f64 = value.parse()?;
                Command::ZoomIn(factor)
            }
            "ZOOM_OUT" => {
                let factor: f64 = value.parse()?;
                Command::ZoomOut(factor)
            }
            "RESET_POSITION" => {
                if value == "true" {
                    Command::Reset
                } else {
                    return Ok(None);
                }
            }
            _ => return Ok(None),
        };
        
        Ok(Some(command))
    }
}

impl Command {
    /// Convertir comando a formato de string para el mutador
    pub fn to_mutator_string(&self) -> String {
        match self {
            Command::Mutate => "mutate:true".to_string(),
            Command::Reset => "reset:true".to_string(),
            Command::SetAutoMutation(enabled) => format!("auto_mutate:{}", enabled),
            Command::ChangeFractalType(fractal_type) => format!("fractal_type:{}", fractal_type),
            Command::ChangeColorScheme(scheme) => format!("color_scheme:{}", scheme),
            Command::SetMutationStrength(strength) => format!("mutation_strength:{:.3}", strength),
            Command::ZoomIn(factor) => format!("zoom:in:{:.3}", factor),
            Command::ZoomOut(factor) => format!("zoom:out:{:.3}", factor),
            Command::Shutdown => "shutdown:true".to_string(),
            Command::Status => "status:request".to_string(),
            _ => "unknown:command".to_string(),
        }
    }
    
    /// Convertir comando a formato de string para el explorador
    pub fn to_explorer_string(&self) -> String {
        match self {
            Command::AnalyzeCurrent => "analyze_current:true".to_string(),
            Command::DeepScan => "deep_scan:true".to_string(),
            Command::SetResolution(res) => format!("set_resolution:{}", res),
            Command::Shutdown => "shutdown:true".to_string(),
            Command::Status => "status:request".to_string(),
            _ => "unknown:command".to_string(),
        }
    }
}

impl Default for FractalParameters {
    fn default() -> Self {
        Self {
            zoom: 1.0,
            center_x: 0.0,
            center_y: 0.0,
            max_iterations: 100,
            julia_c_real: -0.7,
            julia_c_imag: 0.27015,
            escape_radius: 2.0,
            power: 2.0,
            color_scheme: 0,
            color_speed: 1.0,
            color_offset: 0.0,
            brightness: 1.0,
            contrast: 1.0,
            smooth_coloring: true,
            mutation_strength: 0.1,
            auto_mutate: false,
            auto_mutate_speed: 0.01,
        }
    }
}

impl Default for AnalysisRegion {
    fn default() -> Self {
        Self {
            center_real: 0.0,
            center_imag: 0.0,
            width: 2.0,
            height: 2.0,
            zoom: 1.0,
        }
    }
}

impl Default for AnalysisParameters {
    fn default() -> Self {
        Self {
            resolution: 128,
            max_iterations: 200,
            deep_scan: false,
        }
    }
}