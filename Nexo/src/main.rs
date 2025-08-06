use anyhow::{Context, Result};
use chrono::{DateTime, Utc};
use clap::Parser;
use std::collections::HashMap;
use std::path::PathBuf;
use std::time::Duration;
use tokio::time::interval;
use tracing::{error, info, debug, warn};
use uuid::Uuid;

mod ecosystem;
mod strategies;
mod communication;
mod analysis;

use ecosystem::*;
use strategies::*;
use communication::*;
use analysis::*;

/// Nexo - Coordinador inteligente del ecosistema fractal sin iconos
#[derive(Parser, Debug)]
#[command(name = "nexo")]
#[command(about = "Coordinador del ecosistema fractal")]
struct Args {
    /// Ruta del directorio compartido
    #[arg(short, long, default_value = "./shared")]
    shared_path: PathBuf,
    
    /// Intervalo de coordinación en segundos
    #[arg(short, long, default_value = "2")]
    interval: u64,
    
    /// Habilitar modo debug
    #[arg(short, long)]
    debug: bool,
    
    /// Archivo de configuración
    #[arg(short, long)]
    config: Option<PathBuf>,
}

#[tokio::main]
async fn main() -> Result<()> {
    let args = Args::parse();
    
    // Configurar logging
    let subscriber = tracing_subscriber::fmt()
        .with_max_level(if args.debug { 
            tracing::Level::DEBUG 
        } else { 
            tracing::Level::INFO 
        })
        .finish();
    
    tracing::subscriber::set_global_default(subscriber)
        .context("Failed to set tracing subscriber")?;

    info!("🔗 NEXO - Coordinador del Ecosistema Fractal sin iconos");
    info!("========================================================");
    
    // Crear coordinador
    let mut coordinator = EcosystemCoordinator::new(args.shared_path.clone())?;
    
    info!("📁 Directorio compartido: {}", args.shared_path.display());
    info!("⏱️  Intervalo de coordinación: {}s", args.interval);
    
    // Ejecutar coordinador
    coordinator.run(Duration::from_secs(args.interval)).await?;
    
    Ok(())
}

/// Coordinador principal del ecosistema
pub struct EcosystemCoordinator {
    shared_path: PathBuf,
    components: HashMap<String, ComponentInfo>,
    strategies: Vec<Box<dyn MutationStrategy>>,
    communication: CommunicationManager,
    analyzer: EcosystemAnalyzer,
    session_id: Uuid,
    start_time: DateTime<Utc>,
    total_commands: u64,
    last_mutation: Option<DateTime<Utc>>,
}

impl EcosystemCoordinator {
    pub fn new(shared_path: PathBuf) -> Result<Self> {
        // Crear directorio compartido si no existe
        std::fs::create_dir_all(&shared_path)
            .context("Failed to create shared directory")?;
        
        let session_id = Uuid::new_v4();
        let communication = CommunicationManager::new(shared_path.clone())?;
        let analyzer = EcosystemAnalyzer::new();
        
        // Inicializar estrategias de mutación
        let strategies: Vec<Box<dyn MutationStrategy>> = vec![
            Box::new(RandomPulseStrategy::new()),
            Box::new(ColorCyclerStrategy::new()),
            Box::new(FractalRotationStrategy::new()),
            Box::new(DynamicMutationStrategy::new()),
            Box::new(IntelligentAnalysisStrategy::new()),
        ];
        
        info!("🧠 Estrategias inicializadas: {}", strategies.len());
        for strategy in &strategies {
            if strategy.is_enabled() {
                info!("  ✓ {}: {}", strategy.name(), strategy.description());
            }
        }
        
        Ok(Self {
            shared_path,
            components: HashMap::new(),
            strategies,
            communication,
            analyzer,
            session_id,
            start_time: Utc::now(),
            total_commands: 0,
            last_mutation: None,
        })
    }
    
    /// Loop principal del coordinador
    pub async fn run(&mut self, interval_duration: Duration) -> Result<()> {
        info!("🚀 Iniciando coordinación del ecosistema...");
        
        let mut coordination_interval = interval(interval_duration);
        let mut report_interval = interval(Duration::from_secs(300)); // 5 minutos
        
        // Crear archivo de log de sesión
        self.communication.log_session_start(self.session_id, &self.start_time)?;
        
        loop {
            tokio::select! {
                _ = coordination_interval.tick() => {
                    if let Err(e) = self.coordination_cycle().await {
                        error!("Error en ciclo de coordinación: {}", e);
                    }
                }
                _ = report_interval.tick() => {
                    if let Err(e) = self.generate_comprehensive_report().await {
                        error!("Error generando reporte: {}", e);
                    }
                }
                _ = tokio::signal::ctrl_c() => {
                    info!("🛑 Señal de interrupción recibida, cerrando...");
                    break;
                }
            }
        }
        
        self.shutdown().await?;
        Ok(())
    }
    
    /// Ciclo principal de coordinación
    async fn coordination_cycle(&mut self) -> Result<()> {
        debug!("🔄 Ejecutando ciclo de coordinación");
        
        // 1. Leer estado de todos los componentes
        self.discover_and_update_components().await?;
        
        // 2. Analizar el ecosistema
        let ecosystem_state = self.analyzer.analyze_ecosystem(&self.components)?;
        
        // 3. Ejecutar estrategias
        self.execute_strategies(&ecosystem_state).await?;
        
        // 4. Procesar recomendaciones de componentes
        self.process_component_recommendations().await?;
        
        // 5. Actualizar métricas
        self.update_metrics();
        
        Ok(())
    }
    
    /// Descubrir y actualizar información de componentes
    async fn discover_and_update_components(&mut self) -> Result<()> {
        // Leer estado del mutador
        if let Ok(mutator_state) = self.communication.read_fractal_state().await {
            self.components.insert(
                "FractalMutator".to_string(),
                ComponentInfo {
                    name: "FractalMutator".to_string(),
                    component_type: ComponentType::Mutator,
                    status: ComponentStatus::Running,
                    last_seen: Utc::now(),
                    data: Some(ComponentData::Fractal(mutator_state)),
                    metrics: HashMap::new(),
                }
            );
        }
        
        // Leer estado del explorador
        if let Ok(explorer_state) = self.communication.read_explorer_status().await {
            self.components.insert(
                "FractalExplorer".to_string(),
                ComponentInfo {
                    name: "FractalExplorer".to_string(),
                    component_type: ComponentType::Analyzer,
                    status: ComponentStatus::Running,
                    last_seen: Utc::now(),
                    data: Some(ComponentData::Analysis(explorer_state)),
                    metrics: HashMap::new(),
                }
            );
        }
        
        // Leer análisis del explorador
        if let Ok(analysis) = self.communication.read_fractal_analysis().await {
            if let Some(component) = self.components.get_mut("FractalExplorer") {
                component.data = Some(ComponentData::Analysis(analysis));
            }
        }
        
        Ok(())
    }
    
    /// Ejecutar estrategias de mutación
    async fn execute_strategies(&mut self, ecosystem_state: &EcosystemState) -> Result<()> {
        // Collect actions first to avoid borrowing issues
        let mut actions = Vec::new();
        
        for strategy in &mut self.strategies {
            if strategy.should_execute(ecosystem_state)? {
                debug!("🎯 Ejecutando estrategia: {}", strategy.name());
                
                let action = strategy.execute(ecosystem_state).await?;
                actions.push(action);
                strategy.mark_executed();
            }
        }
        
        // Execute actions after borrowing is complete
        for action in actions {
            match action {
                StrategyAction::SendCommand { target, command } => {
                    self.send_command_to_component(&target, &command).await?;
                }
                StrategyAction::ModifyStrategy { strategy_name, modification } => {
                    self.modify_strategy(&strategy_name, modification)?;
                }
                StrategyAction::RequestAnalysis { region, parameters } => {
                    self.request_analysis(region, parameters).await?;
                }
                StrategyAction::Wait { duration } => {
                    debug!("⏳ Estrategia solicitó espera de {:?}", duration);
                    tokio::time::sleep(duration).await;
                }
            }
        }
        
        Ok(())
    }
    
    /// Enviar comando a un componente específico
    async fn send_command_to_component(&mut self, target: &str, command: &Command) -> Result<()> {
        match target {
            "FractalMutator" => {
                self.communication.send_mutator_command(command).await?;
            }
            "FractalExplorer" => {
                self.communication.send_explorer_command(command).await?;
            }
            _ => {
                warn!("Componente desconocido: {}", target);
                return Ok(());
            }
        }
        
        self.total_commands += 1;
        if matches!(command, Command::Mutate) {
            self.last_mutation = Some(Utc::now());
        }
        
        info!("📤 Comando enviado a {}: {:?}", target, command);
        Ok(())
    }
    
    /// Procesar recomendaciones de componentes
    async fn process_component_recommendations(&mut self) -> Result<()> {
        // Leer recomendaciones del explorador
        if let Ok(recommendations) = self.communication.read_explorer_recommendations().await {
            info!("💡 Procesando {} recomendaciones del explorador", recommendations.len());
            
            for recommendation in recommendations {
                match recommendation.parse_as_command()? {
                    Some(command) => {
                        self.send_command_to_component("FractalMutator", &command).await?;
                    }
                    None => {
                        debug!("Recomendación no reconocida: {}", recommendation.recommendation);
                    }
                }
            }
        }
        
        Ok(())
    }
    
    /// Solicitar análisis específico
    async fn request_analysis(&self, _region: AnalysisRegion, _parameters: AnalysisParameters) -> Result<()> {
        let command = Command::AnalyzeCurrent;
        self.communication.send_explorer_command(&command).await?;
        info!("🔬 Análisis solicitado al explorador");
        Ok(())
    }
    
    /// Modificar estrategia dinámicamente
    fn modify_strategy(&mut self, strategy_name: &str, modification: StrategyModification) -> Result<()> {
        for strategy in &mut self.strategies {
            if strategy.name() == strategy_name {
                strategy.apply_modification(modification)?;
                info!("🔧 Estrategia {} modificada", strategy_name);
                return Ok(());
            }
        }
        
        warn!("Estrategia no encontrada: {}", strategy_name);
        Ok(())
    }
    
    /// Actualizar métricas del coordinador
    fn update_metrics(&mut self) {
        // Actualizar métricas de componentes
        for (_name, component) in &mut self.components {
            let uptime = Utc::now().signed_duration_since(self.start_time);
            component.metrics.insert("uptime_seconds".to_string(), uptime.num_seconds() as f64);
            
            if let Some(ComponentData::Fractal(fractal_data)) = &component.data {
                component.metrics.insert("zoom".to_string(), fractal_data.parameters.zoom);
                component.metrics.insert("iterations".to_string(), fractal_data.parameters.max_iterations as f64);
            }
        }
    }
    
    /// Generar reporte comprensivo
    async fn generate_comprehensive_report(&self) -> Result<()> {
        let uptime = Utc::now().signed_duration_since(self.start_time);
        let active_components = self.components.values()
            .filter(|c| matches!(c.status, ComponentStatus::Running))
            .count();
        
        info!("📊 REPORTE DEL ECOSISTEMA");
        info!("========================");
        info!("⏰ Tiempo activo: {} minutos", uptime.num_minutes());
        info!("📤 Comandos enviados: {}", self.total_commands);
        info!("🔧 Componentes activos: {}", active_components);
        
        if let Some(last_mutation) = self.last_mutation {
            let since_mutation = Utc::now().signed_duration_since(last_mutation);
            info!("🧬 Última mutación: hace {} segundos", since_mutation.num_seconds());
        }
        
        // Reporte de componentes
        for (name, component) in &self.components {
            info!("  📦 {}: {:?}", name, component.status);
            if let Some(data) = &component.data {
                match data {
                    ComponentData::Fractal(fractal) => {
                        info!("    🎯 Zoom: {:.2}, Tipo: {}", 
                            fractal.parameters.zoom, fractal.fractal_type);
                    }
                    ComponentData::Analysis(analysis) => {
                        info!("    🔍 Análisis: score {:.3}", 
                            analysis.metrics.get("interesting_score").unwrap_or(&0.0));
                    }
                }
            }
        }
        
        // Reporte de estrategias
        info!("🎯 ESTRATEGIAS:");
        for strategy in &self.strategies {
            let status = if strategy.is_enabled() { "ACTIVA" } else { "INACTIVA" };
            info!("  {} {}: {}", 
                if strategy.is_enabled() { "✓" } else { "⏸" },
                strategy.name(), 
                status
            );
        }
        
        // Guardar reporte en archivo
        self.communication.save_ecosystem_report(&EcosystemReport {
            session_id: self.session_id,
            timestamp: Utc::now(),
            uptime_seconds: uptime.num_seconds(),
            total_commands: self.total_commands,
            active_components,
            components: self.components.clone(),
        }).await?;
        
        Ok(())
    }
    
    /// Cerrar coordinador limpiamente
    async fn shutdown(&mut self) -> Result<()> {
        info!("🏁 Cerrando Nexo...");
        
        // Generar reporte final
        self.generate_comprehensive_report().await?;
        
        // Notificar cierre a componentes
        let shutdown_command = Command::Shutdown;
        let _ = self.communication.send_mutator_command(&shutdown_command).await;
        let _ = self.communication.send_explorer_command(&shutdown_command).await;
        
        info!("✅ Nexo cerrado correctamente");
        Ok(())
    }
}