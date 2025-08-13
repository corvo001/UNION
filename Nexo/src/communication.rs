use anyhow::{Context, Result};
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::path::{Path, PathBuf};
use tokio::fs;
use tracing::{debug, error, info, warn};
use uuid::Uuid;

use crate::ecosystem::*;

/// Gestor de comunicación con el sistema de archivos compartidos
pub struct CommunicationManager {
    shared_path: PathBuf,
}

impl CommunicationManager {
    pub fn new(shared_path: PathBuf) -> Result<Self> {
        std::fs::create_dir_all(&shared_path)
            .context("Failed to create shared directory")?;
        
        info!("📡 CommunicationManager inicializado en: {}", shared_path.display());
        
        Ok(Self { shared_path })
    }
    
    /// Leer estado actual del mutador de fractales
    pub async fn read_fractal_state(&self) -> Result<FractalState> {
        let file_path = self.shared_path.join("fractal_params.json");
        
        if !file_path.exists() {
            return Err(anyhow::anyhow!("Archivo de parámetros del mutador no encontrado"));
        }
        
        let content = fs::read_to_string(&file_path).await
            .context("Failed to read fractal parameters")?;
        
        let fractal_state: FractalState = serde_json::from_str(&content)
            .context("Failed to parse fractal parameters")?;
        
        debug!("📖 Estado del mutador leído: tipo {}, zoom {:.2}", 
               fractal_state.fractal_type, fractal_state.parameters.zoom);
        
        Ok(fractal_state)
    }
    
    /// Leer estado del explorador de fractales
    pub async fn read_explorer_status(&self) -> Result<AnalysisData> {
        let file_path = self.shared_path.join("explorer_status.json");
        
        if !file_path.exists() {
            return Err(anyhow::anyhow!("Estado del explorador no encontrado"));
        }
        
        let content = fs::read_to_string(&file_path).await
            .context("Failed to read explorer status")?;
        
        #[derive(Deserialize)]
        struct ExplorerStatus {
            timestamp: String,
            component: String,
            status: String,
            #[serde(rename = "isRunning")]
            is_running: bool,
            uptime_seconds: i64,
            total_scans: i32,
            regions_discovered: i32,
            average_interest_score: f64,
            current_resolution: i32,
            language: String,
        }
        
        let status: ExplorerStatus = serde_json::from_str(&content)
            .context("Failed to parse explorer status")?;
        
        // Convertir a AnalysisData
        let mut metrics = std::collections::HashMap::new();
        metrics.insert("total_scans".to_string(), status.total_scans as f64);
        metrics.insert("regions_discovered".to_string(), status.regions_discovered as f64);
        metrics.insert("average_interest_score".to_string(), status.average_interest_score);
        metrics.insert("uptime_seconds".to_string(), status.uptime_seconds as f64);
        metrics.insert("current_resolution".to_string(), status.current_resolution as f64);
        
        let analysis_data = AnalysisData {
            timestamp: status.timestamp,
            region: AnalysisRegion::default(),
            fractal_type: 0,
            max_iterations: 0,
            metrics,
            recommendation: format!("Explorer {} - {} escaneos completados", 
                                   status.status, status.total_scans),
            component: status.component,
        };
        
        debug!("📖 Estado del explorador leído: {} escaneos, score promedio {:.3}", 
               status.total_scans, status.average_interest_score);
        
        Ok(analysis_data)
    }
    
    /// Leer análisis detallado del explorador
    pub async fn read_fractal_analysis(&self) -> Result<AnalysisData> {
        let file_path = self.shared_path.join("fractal_analysis.json");
        
        if !file_path.exists() {
            return Err(anyhow::anyhow!("Análisis del explorador no encontrado"));
        }
        
        let content = fs::read_to_string(&file_path).await
            .context("Failed to read fractal analysis")?;
        
        let analysis: AnalysisData = serde_json::from_str(&content)
            .context("Failed to parse fractal analysis")?;
        
        debug!("📖 Análisis detallado leído: score {:.3}", 
               analysis.metrics.get("interesting_score").unwrap_or(&0.0));
        
        Ok(analysis)
    }
    
    /// Leer recomendaciones del explorador
    pub async fn read_explorer_recommendations(&self) -> Result<Vec<ExplorerRecommendation>> {
        let file_path = self.shared_path.join("explorer_recommendations.json");
        
        if !file_path.exists() {
            return Ok(Vec::new()); // No hay recomendaciones
        }
        
        let content = fs::read_to_string(&file_path).await
            .context("Failed to read explorer recommendations")?;
        
        #[derive(Deserialize)]
        struct RecommendationsFile {
            timestamp: String,
            from_component: String,
            target_component: String,
            analysis_score: f64,
            recommendations: Vec<String>,
        }
        
        let rec_file: RecommendationsFile = serde_json::from_str(&content)
            .context("Failed to parse explorer recommendations")?;
        
        // Convertir a lista de ExplorerRecommendation
        let mut recommendations = Vec::new();
        for rec in rec_file.recommendations {
            recommendations.push(ExplorerRecommendation {
                timestamp: rec_file.timestamp.clone(),
                from_component: rec_file.from_component.clone(),
                target_component: rec_file.target_component.clone(),
                analysis_score: rec_file.analysis_score,
                recommendation: rec,
            });
        }
        
        if !recommendations.is_empty() {
            info!("📖 {} recomendaciones del explorador leídas", recommendations.len());
            
            // Eliminar archivo después de leer para evitar procesamiento duplicado
            if let Err(e) = fs::remove_file(&file_path).await {
                warn!("No se pudo eliminar archivo de recomendaciones: {}", e);
            }
        }
        
        Ok(recommendations)
    }
    
    /// Enviar comando al mutador de fractales
    pub async fn send_mutator_command(&self, command: &Command) -> Result<()> {
        let file_path = self.shared_path.join("commands.json");
        let command_str = command.to_mutator_string();
        
        fs::write(&file_path, &command_str).await
            .context("Failed to write mutator command")?;
        
        info!("📤 Comando enviado al mutador: {}", command_str);
        Ok(())
    }
    
    /// Enviar comando al explorador de fractales
    pub async fn send_explorer_command(&self, command: &Command) -> Result<()> {
        let file_path = self.shared_path.join("explorer_commands.json");
        let command_str = command.to_explorer_string();
        
        fs::write(&file_path, &command_str).await
            .context("Failed to write explorer command")?;
        
        info!("📤 Comando enviado al explorador: {}", command_str);
        Ok(())
    }
    
    /// Guardar reporte del ecosistema
    pub async fn save_ecosystem_report(&self, report: &EcosystemReport) -> Result<()> {
        let file_path = self.shared_path.join("ecosystem_report.json");
        
        let json = serde_json::to_string_pretty(report)
            .context("Failed to serialize ecosystem report")?;
        
        fs::write(&file_path, json).await
            .context("Failed to write ecosystem report")?;
        
        debug!("📄 Reporte del ecosistema guardado");
        Ok(())
    }
    
    /// Registrar inicio de sesión
    pub fn log_session_start(&self, session_id: Uuid, start_time: &DateTime<Utc>) -> Result<()> {
        let file_path = self.shared_path.join("nexo_session.log");
        
        let log_entry = format!(
            "[{}] SESSION_START: {} - Nexo coordinador iniciado\n",
            start_time.format("%Y-%m-%d %H:%M:%S UTC"),
            session_id
        );
        
        std::fs::write(&file_path, log_entry)
            .context("Failed to write session log")?;
        
        info!("📝 Sesión registrada: {}", session_id);
        Ok(())
    }
    
    /// Verificar salud de los componentes
    pub async fn check_component_health(&self) -> Result<ComponentHealthReport> {
        let mut report = ComponentHealthReport {
            timestamp: Utc::now(),
            components: std::collections::HashMap::new(),
        };
        
        // Verificar mutador
        let mutator_health = self.check_file_freshness("fractal_params.json", 30).await?;
        report.components.insert("FractalMutator".to_string(), mutator_health);
        
        // Verificar explorador
        let explorer_health = self.check_file_freshness("explorer_status.json", 60).await?;
        report.components.insert("FractalExplorer".to_string(), explorer_health);
        
        Ok(report)
    }
    
    /// Verificar frescura de un archivo (últimos N segundos)
    async fn check_file_freshness(&self, filename: &str, max_age_seconds: i64) -> Result<ComponentHealth> {
        let file_path = self.shared_path.join(filename);
        
        if !file_path.exists() {
            return Ok(ComponentHealth {
                status: HealthStatus::Missing,
                last_update: None,
                age_seconds: None,
                message: format!("Archivo {} no encontrado", filename),
            });
        }
        
        let metadata = fs::metadata(&file_path).await
            .context("Failed to read file metadata")?;
        
        let modified = metadata.modified()
            .context("Failed to get file modification time")?;
        
        let age = std::time::SystemTime::now()
            .duration_since(modified)
            .unwrap_or_default()
            .as_secs() as i64;
        
        let status = if age <= max_age_seconds {
            HealthStatus::Healthy
        } else if age <= max_age_seconds * 2 {
            HealthStatus::Stale
        } else {
            HealthStatus::Unhealthy
        };
        
        Ok(ComponentHealth {
            status,
            last_update: Some(DateTime::from_timestamp(
                modified.duration_since(std::time::UNIX_EPOCH)
                    .unwrap_or_default()
                    .as_secs() as i64,
                0
            ).unwrap_or_else(|| Utc::now())),
            age_seconds: Some(age),
            message: format!("Archivo {} actualizado hace {} segundos", filename, age),
        })
    }
    
    /// Limpiar archivos temporales antiguos
    pub async fn cleanup_old_files(&self, max_age_hours: i64) -> Result<usize> {
        let mut cleaned_files = 0;
        let cutoff_time = Utc::now() - chrono::Duration::hours(max_age_hours);
        
        let temp_patterns = vec![
            "temp_*.json",
            "*.tmp",
            "backup_*.json",
        ];
        
        for _pattern in temp_patterns {
            // En un sistema real, usaríamos glob o similar
            // Por simplicidad, solo limpiamos archivos conocidos
            let temp_files = vec![
                "temp_analysis.json",
                "temp_commands.json",
                "backup_params.json",
            ];
            
            for temp_file in temp_files {
                let file_path = self.shared_path.join(temp_file);
                if file_path.exists() {
                    if let Ok(metadata) = fs::metadata(&file_path).await {
                        if let Ok(modified) = metadata.modified() {
                            let file_time = DateTime::from_timestamp(
                                modified.duration_since(std::time::UNIX_EPOCH)
                                    .unwrap_or_default()
                                    .as_secs() as i64,
                                0
                            ).unwrap_or_else(|| Utc::now());
                            
                            if file_time < cutoff_time {
                                if let Ok(()) = fs::remove_file(&file_path).await {
                                    cleaned_files += 1;
                                    debug!("🗑️ Archivo temporal eliminado: {}", temp_file);
                                }
                            }
                        }
                    }
                }
            }
        }
        
        if cleaned_files > 0 {
            info!("🧹 Limpieza completada: {} archivos eliminados", cleaned_files);
        }
        
        Ok(cleaned_files)
    }
    
    /// Crear backup de estado crítico
    pub async fn backup_critical_state(&self) -> Result<()> {
        let timestamp = Utc::now().format("%Y%m%d_%H%M%S");
        let backup_dir = self.shared_path.join("backups");
        
        fs::create_dir_all(&backup_dir).await
            .context("Failed to create backup directory")?;
        
        // Backup de parámetros del mutador
        let params_file = self.shared_path.join("fractal_params.json");
        if params_file.exists() {
            let backup_file = backup_dir.join(format!("fractal_params_{}.json", timestamp));
            fs::copy(&params_file, &backup_file).await
                .context("Failed to backup fractal parameters")?;
        }
        
        // Backup de análisis del explorador
        let analysis_file = self.shared_path.join("fractal_analysis.json");
        if analysis_file.exists() {
            let backup_file = backup_dir.join(format!("fractal_analysis_{}.json", timestamp));
            fs::copy(&analysis_file, &backup_file).await
                .context("Failed to backup fractal analysis")?;
        }
        
        info!("💾 Backup del estado crítico creado: {}", timestamp);
        Ok(())
    }
}

/// Reporte de salud de componentes
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ComponentHealthReport {
    pub timestamp: DateTime<Utc>,
    pub components: std::collections::HashMap<String, ComponentHealth>,
}

/// Salud de un componente individual
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ComponentHealth {
    pub status: HealthStatus,
    pub last_update: Option<DateTime<Utc>>,
    pub age_seconds: Option<i64>,
    pub message: String,
}

/// Estados de salud posibles
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum HealthStatus {
    Healthy,   // Funcionando correctamente
    Stale,     // Datos antiguos pero aceptables
    Unhealthy, // Datos muy antiguos o problemáticos
    Missing,   // Componente no encontrado
}