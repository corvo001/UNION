use anyhow::Result;
use async_trait::async_trait;
use chrono::{DateTime, Duration, Utc};
use rand::Rng;
use tracing::{debug, info};

use crate::ecosystem::*;

/// Acción que puede tomar una estrategia
#[derive(Debug, Clone)]
pub enum StrategyAction {
    SendCommand {
        target: String,
        command: Command,
    },
    ModifyStrategy {
        strategy_name: String,
        modification: StrategyModification,
    },
    RequestAnalysis {
        region: AnalysisRegion,
        parameters: AnalysisParameters,
    },
    Wait {
        duration: std::time::Duration,
    },
}

/// Modificaciones que se pueden aplicar a estrategias
#[derive(Debug, Clone)]
pub enum StrategyModification {
    ChangeFrequency(Duration),
    Enable,
    Disable,
    AdjustParameters(String, f64),
}

/// Trait para estrategias de mutación
#[async_trait]
pub trait MutationStrategy: Send + Sync {
    fn name(&self) -> &str;
    fn description(&self) -> &str;
    fn is_enabled(&self) -> bool;
    fn should_execute(&self, ecosystem_state: &EcosystemState) -> Result<bool>;
    async fn execute(&mut self, ecosystem_state: &EcosystemState) -> Result<StrategyAction>;
    fn mark_executed(&mut self);
    fn apply_modification(&mut self, modification: StrategyModification) -> Result<()>;
}

/// Estrategia de pulsos aleatorios
pub struct RandomPulseStrategy {
    enabled: bool,
    frequency: Duration,
    last_execution: Option<DateTime<Utc>>,
    mutation_intensity: f64,
}

impl RandomPulseStrategy {
    pub fn new() -> Self {
        Self {
            enabled: true,
            frequency: Duration::seconds(rand::thread_rng().gen_range(15..45)),
            last_execution: None,
            mutation_intensity: 1.0,
        }
    }
    
    fn calculate_next_frequency(&mut self) {
        // Variar frecuencia para comportamiento más orgánico
        let base_seconds = 25;
        let variation = rand::thread_rng().gen_range(-10..15);
        self.frequency = Duration::seconds(base_seconds + variation);
    }
}

#[async_trait]
impl MutationStrategy for RandomPulseStrategy {
    fn name(&self) -> &str {
        "RandomPulse"
    }
    
    fn description(&self) -> &str {
        "Mutaciones aleatorias para mantener evolución constante"
    }
    
    fn is_enabled(&self) -> bool {
        self.enabled
    }
    
    fn should_execute(&self, _ecosystem_state: &EcosystemState) -> Result<bool> {
        if !self.enabled {
            return Ok(false);
        }
        
        let now = Utc::now();
        
        match self.last_execution {
            None => Ok(true), // Primera ejecución
            Some(last) => {
                let elapsed = now.signed_duration_since(last);
                let should_execute = elapsed >= self.frequency;
                
                if should_execute {
                    debug!("RandomPulse: {} segundos desde última ejecución", elapsed.num_seconds());
                }
                
                Ok(should_execute)
            }
        }
    }
    
    async fn execute(&mut self, ecosystem_state: &EcosystemState) -> Result<StrategyAction> {
        // Ajustar intensidad basada en actividad del ecosistema
        let intensity_multiplier = match ecosystem_state.activity_level {
            ActivityLevel::Low => 1.5,      // Más agresivo si hay poca actividad
            ActivityLevel::Moderate => 1.0,
            ActivityLevel::High => 0.7,     // Más suave si hay mucha actividad
            ActivityLevel::Critical => 0.3, // Muy suave si actividad crítica
        };
        
        self.calculate_next_frequency();
        
        info!("🎲 RandomPulse: Aplicando mutación (intensidad: {:.2})", 
              self.mutation_intensity * intensity_multiplier);
        
        Ok(StrategyAction::SendCommand {
            target: "FractalMutator".to_string(),
            command: Command::Mutate,
        })
    }
    
    fn mark_executed(&mut self) {
        self.last_execution = Some(Utc::now());
    }
    
    fn apply_modification(&mut self, modification: StrategyModification) -> Result<()> {
        match modification {
            StrategyModification::ChangeFrequency(freq) => {
                self.frequency = freq;
                info!("RandomPulse: Frecuencia cambiada a {} segundos", freq.num_seconds());
            }
            StrategyModification::Enable => self.enabled = true,
            StrategyModification::Disable => self.enabled = false,
            StrategyModification::AdjustParameters(param, value) => {
                if param == "intensity" {
                    self.mutation_intensity = value.clamp(0.1, 3.0);
                    info!("RandomPulse: Intensidad ajustada a {:.2}", self.mutation_intensity);
                }
            }
        }
        Ok(())
    }
}

/// Estrategia de rotación de colores
pub struct ColorCyclerStrategy {
    enabled: bool,
    frequency: Duration,
    last_execution: Option<DateTime<Utc>>,
    current_scheme: i32,
}

impl ColorCyclerStrategy {
    pub fn new() -> Self {
        Self {
            enabled: true,
            frequency: Duration::seconds(60),
            last_execution: None,
            current_scheme: 0,
        }
    }
}

#[async_trait]
impl MutationStrategy for ColorCyclerStrategy {
    fn name(&self) -> &str {
        "ColorCycler"
    }
    
    fn description(&self) -> &str {
        "Rotación periódica de esquemas de color"
    }
    
    fn is_enabled(&self) -> bool {
        self.enabled
    }
    
    fn should_execute(&self, _ecosystem_state: &EcosystemState) -> Result<bool> {
        if !self.enabled {
            return Ok(false);
        }
        
        match self.last_execution {
            None => Ok(true),
            Some(last) => {
                let elapsed = Utc::now().signed_duration_since(last);
                Ok(elapsed >= self.frequency)
            }
        }
    }
    
    async fn execute(&mut self, _ecosystem_state: &EcosystemState) -> Result<StrategyAction> {
        // Ciclar entre esquemas de color (0-5)
        self.current_scheme = (self.current_scheme + 1) % 6;
        
        info!("🎨 ColorCycler: Cambiando a esquema de color {}", self.current_scheme);
        
        Ok(StrategyAction::SendCommand {
            target: "FractalMutator".to_string(),
            command: Command::ChangeColorScheme(self.current_scheme),
        })
    }
    
    fn mark_executed(&mut self) {
        self.last_execution = Some(Utc::now());
    }
    
    fn apply_modification(&mut self, modification: StrategyModification) -> Result<()> {
        match modification {
            StrategyModification::ChangeFrequency(freq) => self.frequency = freq,
            StrategyModification::Enable => self.enabled = true,
            StrategyModification::Disable => self.enabled = false,
            _ => {}
        }
        Ok(())
    }
}

/// Estrategia de rotación de fractales
pub struct FractalRotationStrategy {
    enabled: bool,
    frequency: Duration,
    last_execution: Option<DateTime<Utc>>,
    current_type: i32,
}

impl FractalRotationStrategy {
    pub fn new() -> Self {
        Self {
            enabled: true,
            frequency: Duration::minutes(3),
            last_execution: None,
            current_type: 0,
        }
    }
}

#[async_trait]
impl MutationStrategy for FractalRotationStrategy {
    fn name(&self) -> &str {
        "FractalRotation"
    }
    
    fn description(&self) -> &str {
        "Rotación entre diferentes tipos de fractales"
    }
    
    fn is_enabled(&self) -> bool {
        self.enabled
    }
    
    fn should_execute(&self, _ecosystem_state: &EcosystemState) -> Result<bool> {
        if !self.enabled {
            return Ok(false);
        }
        
        match self.last_execution {
            None => Ok(true),
            Some(last) => {
                let elapsed = Utc::now().signed_duration_since(last);
                Ok(elapsed >= self.frequency)
            }
        }
    }
    
    async fn execute(&mut self, ecosystem_state: &EcosystemState) -> Result<StrategyAction> {
        // Obtener tipo actual del mutador si está disponible
        if let Some(mutator) = ecosystem_state.components.get("FractalMutator") {
            if let Some(ComponentData::Fractal(fractal_state)) = &mutator.data {
                self.current_type = fractal_state.fractal_type;
            }
        }
        
        // Rotar al siguiente tipo (0: Mandelbrot, 1: Julia, 2: Burning Ship)
        let next_type = (self.current_type + 1) % 3;
        
        info!("🔄 FractalRotation: Cambiando de tipo {} a {}", self.current_type, next_type);
        
        Ok(StrategyAction::SendCommand {
            target: "FractalMutator".to_string(),
            command: Command::ChangeFractalType(next_type),
        })
    }
    
    fn mark_executed(&mut self) {
        self.last_execution = Some(Utc::now());
    }
    
    fn apply_modification(&mut self, modification: StrategyModification) -> Result<()> {
        match modification {
            StrategyModification::ChangeFrequency(freq) => self.frequency = freq,
            StrategyModification::Enable => self.enabled = true,
            StrategyModification::Disable => self.enabled = false,
            _ => {}
        }
        Ok(())
    }
}

/// Estrategia de mutación dinámica
pub struct DynamicMutationStrategy {
    enabled: bool,
    frequency: Duration,
    last_execution: Option<DateTime<Utc>>,
    last_mutation_strength: f64,
}

impl DynamicMutationStrategy {
    pub fn new() -> Self {
        Self {
            enabled: true,
            frequency: Duration::seconds(90),
            last_execution: None,
            last_mutation_strength: 0.1,
        }
    }
    
    fn calculate_optimal_strength(&self, ecosystem_state: &EcosystemState) -> f64 {
        let mut base_strength: f64 = 0.15;
        
        // Ajustar basado en el nivel de actividad
        match ecosystem_state.activity_level {
            ActivityLevel::Low => base_strength *= 1.8,      // Aumentar para estimular
            ActivityLevel::Moderate => base_strength *= 1.0, // Mantener
            ActivityLevel::High => base_strength *= 0.6,     // Reducir para estabilizar
            ActivityLevel::Critical => base_strength *= 0.2, // Reducir drásticamente
        }
        
        // Añadir variación aleatoria pequeña
        let variation = rand::thread_rng().gen_range(-0.03..0.03);
        base_strength += variation;
        
        // Asegurar que esté en rango válido
        base_strength.clamp(0.05, 0.5)
    }
}

#[async_trait]
impl MutationStrategy for DynamicMutationStrategy {
    fn name(&self) -> &str {
        "DynamicMutation"
    }
    
    fn description(&self) -> &str {
        "Ajuste dinámico de la fuerza de mutación según el estado del ecosistema"
    }
    
    fn is_enabled(&self) -> bool {
        self.enabled
    }
    
    fn should_execute(&self, _ecosystem_state: &EcosystemState) -> Result<bool> {
        if !self.enabled {
            return Ok(false);
        }
        
        match self.last_execution {
            None => Ok(true),
            Some(last) => {
                let elapsed = Utc::now().signed_duration_since(last);
                Ok(elapsed >= self.frequency)
            }
        }
    }
    
    async fn execute(&mut self, ecosystem_state: &EcosystemState) -> Result<StrategyAction> {
        let optimal_strength = self.calculate_optimal_strength(ecosystem_state);
        
        // Solo ajustar si hay un cambio significativo
        if (optimal_strength - self.last_mutation_strength).abs() > 0.02 {
            self.last_mutation_strength = optimal_strength;
            
            info!("⚙️ DynamicMutation: Ajustando fuerza a {:.3} (actividad: {:?})", 
                  optimal_strength, ecosystem_state.activity_level);
            
            Ok(StrategyAction::SendCommand {
                target: "FractalMutator".to_string(),
                command: Command::SetMutationStrength(optimal_strength),
            })
        } else {
            debug!("DynamicMutation: Fuerza actual óptima, no hay cambios");
            Ok(StrategyAction::Wait {
                duration: std::time::Duration::from_secs(30),
            })
        }
    }
    
    fn mark_executed(&mut self) {
        self.last_execution = Some(Utc::now());
    }
    
    fn apply_modification(&mut self, modification: StrategyModification) -> Result<()> {
        match modification {
            StrategyModification::ChangeFrequency(freq) => self.frequency = freq,
            StrategyModification::Enable => self.enabled = true,
            StrategyModification::Disable => self.enabled = false,
            _ => {}
        }
        Ok(())
    }
}

/// Estrategia de análisis inteligente
pub struct IntelligentAnalysisStrategy {
    enabled: bool,
    frequency: Duration,
    last_execution: Option<DateTime<Utc>>,
    analysis_threshold: f64,
}

impl IntelligentAnalysisStrategy {
    pub fn new() -> Self {
        Self {
            enabled: true,
            frequency: Duration::minutes(5),
            last_execution: None,
            analysis_threshold: 0.7,
        }
    }
    
    fn should_request_analysis(&self, ecosystem_state: &EcosystemState) -> bool {
        // Verificar si hay datos de análisis recientes
        if let Some(explorer) = ecosystem_state.components.get("FractalExplorer") {
            if let Some(ComponentData::Analysis(analysis)) = &explorer.data {
                // Si el score de interés es bajo, solicitar nuevo análisis
                if let Some(score) = analysis.metrics.get("interesting_score") {
                    return *score < self.analysis_threshold;
                }
            }
        }
        
        // Si no hay datos del explorador, solicitar análisis
        true
    }
}

#[async_trait]
impl MutationStrategy for IntelligentAnalysisStrategy {
    fn name(&self) -> &str {
        "IntelligentAnalysis"
    }
    
    fn description(&self) -> &str {
        "Solicita análisis inteligente basado en el estado del ecosistema"
    }
    
    fn is_enabled(&self) -> bool {
        self.enabled
    }
    
    fn should_execute(&self, ecosystem_state: &EcosystemState) -> Result<bool> {
        if !self.enabled {
            return Ok(false);
        }
        
        // Verificar si FractalExplorer está disponible
        if !ecosystem_state.components.contains_key("FractalExplorer") {
            return Ok(false);
        }
        
        match self.last_execution {
            None => Ok(true),
            Some(last) => {
                let elapsed = Utc::now().signed_duration_since(last);
                let time_condition = elapsed >= self.frequency;
                let analysis_condition = self.should_request_analysis(ecosystem_state);
                
                Ok(time_condition && analysis_condition)
            }
        }
    }
    
    async fn execute(&mut self, ecosystem_state: &EcosystemState) -> Result<StrategyAction> {
        info!("🔬 IntelligentAnalysis: Solicitando análisis de región actual");
        
        // Obtener región actual del mutador si está disponible
        let region = if let Some(mutator) = ecosystem_state.components.get("FractalMutator") {
            if let Some(ComponentData::Fractal(fractal_state)) = &mutator.data {
                AnalysisRegion {
                    center_real: fractal_state.parameters.center_x,
                    center_imag: fractal_state.parameters.center_y,
                    width: 2.0,
                    height: 2.0,
                    zoom: fractal_state.parameters.zoom,
                }
            } else {
                AnalysisRegion::default()
            }
        } else {
            AnalysisRegion::default()
        };
        
        let parameters = AnalysisParameters {
            resolution: 128,
            max_iterations: 200,
            deep_scan: ecosystem_state.activity_level == ActivityLevel::Low,
        };
        
        Ok(StrategyAction::RequestAnalysis { region, parameters })
    }
    
    fn mark_executed(&mut self) {
        self.last_execution = Some(Utc::now());
    }
    
    fn apply_modification(&mut self, modification: StrategyModification) -> Result<()> {
        match modification {
            StrategyModification::ChangeFrequency(freq) => self.frequency = freq,
            StrategyModification::Enable => self.enabled = true,
            StrategyModification::Disable => self.enabled = false,
            StrategyModification::AdjustParameters(param, value) => {
                if param == "threshold" {
                    self.analysis_threshold = value.clamp(0.1, 1.0);
                    info!("IntelligentAnalysis: Threshold ajustado a {:.2}", self.analysis_threshold);
                }
            }
        }
        Ok(())
    }
}