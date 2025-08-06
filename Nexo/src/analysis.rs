use anyhow::Result;
use chrono::{DateTime, Duration, Utc};
use std::collections::HashMap;
use tracing::debug;

use crate::ecosystem::*;

/// Analizador del estado del ecosistema
pub struct EcosystemAnalyzer {
    analysis_history: Vec<EcosystemSnapshot>,
    max_history_size: usize,
}

/// Snapshot del ecosistema en un momento específico
#[derive(Debug, Clone)]
struct EcosystemSnapshot {
    timestamp: DateTime<Utc>,
    health_score: f64,
    activity_level: ActivityLevel,
    component_count: usize,
    mutation_rate: f64,
    analysis_quality: f64,
}

impl EcosystemAnalyzer {
    pub fn new() -> Self {
        Self {
            analysis_history: Vec::new(),
            max_history_size: 100, // Mantener últimos 100 snapshots
        }
    }
    
    /// Analizar el estado completo del ecosistema
    pub fn analyze_ecosystem(&mut self, components: &HashMap<String, ComponentInfo>) -> Result<EcosystemState> {
        let timestamp = Utc::now();
        
        // Calcular métricas básicas
        let health_score = self.calculate_health_score(components)?;
        let activity_level = self.determine_activity_level(components)?;
        let recommendations = self.generate_recommendations(components, &activity_level)?;
        
        // Crear snapshot para el historial
        let snapshot = EcosystemSnapshot {
            timestamp,
            health_score,
            activity_level: activity_level.clone(),
            component_count: components.len(),
            mutation_rate: self.calculate_mutation_rate(components),
            analysis_quality: self.calculate_analysis_quality(components),
        };
        
        // Añadir al historial
        self.add_to_history(snapshot);
        
        debug!("🔍 Análisis del ecosistema: salud {:.2}, actividad {:?}", 
               health_score, activity_level);
        
        Ok(EcosystemState {
            timestamp,
            components: components.clone(),
            health_score,
            activity_level,
            recommendations,
        })
    }
    
    /// Calcular puntuación de salud del ecosistema
    fn calculate_health_score(&self, components: &HashMap<String, ComponentInfo>) -> Result<f64> {
        if components.is_empty() {
            return Ok(0.0);
        }
        
        let mut total_score = 0.0;
        let mut component_count = 0;
        
        for (name, component) in components {
            let component_score = match &component.status {
                ComponentStatus::Running => {
                    // Puntuación basada en la frescura de los datos
                    let age = Utc::now().signed_duration_since(component.last_seen);
                    let age_score = if age <= Duration::seconds(30) {
                        1.0
                    } else if age <= Duration::minutes(2) {
                        0.8
                    } else if age <= Duration::minutes(5) {
                        0.6
                    } else {
                        0.3
                    };
                    
                    // Ajustar según datos específicos del componente
                    match &component.data {
                        Some(ComponentData::Fractal(fractal)) => {
                            // Penalizar valores extremos que pueden indicar problemas
                            let zoom_score = if fractal.parameters.zoom > 1000.0 || fractal.parameters.zoom < 0.01 {
                                0.7
                            } else {
                                1.0
                            };
                            
                            let mutation_score = if fractal.parameters.mutation_strength > 0.8 {
                                0.8
                            } else {
                                1.0
                            };
                            
                            age_score * zoom_score * mutation_score
                        }
                        Some(ComponentData::Analysis(analysis)) => {
                            // Puntuación basada en calidad del análisis
                            let quality_score = analysis.metrics.get("interesting_score")
                                .map(|score| score.clamp(0.0, 1.0))
                                .unwrap_or(0.5);
                            
                            age_score * (0.5 + quality_score * 0.5)
                        }
                        None => age_score * 0.8, // Penalizar falta de datos
                    }
                }
                ComponentStatus::Idle => 0.6,
                ComponentStatus::Error => 0.2,
                ComponentStatus::Offline => 0.0,
            };
            
            total_score += component_score;
            component_count += 1;
            
            debug!("Salud de {}: {:.2}", name, component_score);
        }
        
        let average_score = total_score / component_count as f64;
        
        // Bonificación por tener múltiples componentes funcionando
        let diversity_bonus = match component_count {
            0 => 0.0,
            1 => 0.9,
            2 => 1.0,
            3 => 1.1,
            _ => 1.2,
        };
        
        Ok((average_score * diversity_bonus).min(1.0))
    }
    
    /// Determinar nivel de actividad del ecosistema
    fn determine_activity_level(&self, components: &HashMap<String, ComponentInfo>) -> Result<ActivityLevel> {
        let mut activity_indicators = Vec::new();
        
        // Analizar actividad del mutador
        if let Some(mutator) = components.get("FractalMutator") {
            if let Some(ComponentData::Fractal(fractal)) = &mutator.data {
                // Auto-mutación indica alta actividad
                if fractal.parameters.auto_mutate {
                    activity_indicators.push(3.0);
                }
                
                // Fuerza de mutación alta indica actividad
                if fractal.parameters.mutation_strength > 0.3 {
                    activity_indicators.push(2.0);
                } else if fractal.parameters.mutation_strength > 0.1 {
                    activity_indicators.push(1.0);
                } else {
                    activity_indicators.push(0.5);
                }
                
                // Zoom extremo puede indicar actividad excesiva
                if fractal.parameters.zoom > 500.0 {
                    activity_indicators.push(3.0);
                }
            }
        }
        
        // Analizar actividad del explorador
        if let Some(explorer) = components.get("FractalExplorer") {
            if let Some(ComponentData::Analysis(analysis)) = &explorer.data {
                // Análisis recientes indican actividad
                let age = Utc::now().signed_duration_since(
                    DateTime::parse_from_rfc3339(&analysis.timestamp)
                        .unwrap_or_else(|_| Utc::now().into())
                        .with_timezone(&Utc)
                );
                
                if age <= Duration::minutes(1) {
                    activity_indicators.push(2.0);
                } else if age <= Duration::minutes(5) {
                    activity_indicators.push(1.0);
                } else {
                    activity_indicators.push(0.3);
                }
                
                // Score de interés alto indica actividad valiosa
                if let Some(score) = analysis.metrics.get("interesting_score") {
                    if *score > 0.8 {
                        activity_indicators.push(2.0);
                    } else if *score > 0.5 {
                        activity_indicators.push(1.0);
                    }
                }
            }
        }
        
        // Analizar historial de actividad
        let historical_activity = self.calculate_historical_activity();
        activity_indicators.push(historical_activity);
        
        // Calcular actividad promedio
        let average_activity = if activity_indicators.is_empty() {
            0.5
        } else {
            activity_indicators.iter().sum::<f64>() / activity_indicators.len() as f64
        };
        
        let level = if average_activity >= 2.5 {
            ActivityLevel::Critical
        } else if average_activity >= 1.8 {
            ActivityLevel::High
        } else if average_activity >= 0.8 {
            ActivityLevel::Moderate
        } else {
            ActivityLevel::Low
        };
        
        debug!("Actividad del ecosistema: {:.2} -> {:?}", average_activity, level);
        
        Ok(level)
    }
    
    /// Calcular tasa de mutación actual
    fn calculate_mutation_rate(&self, components: &HashMap<String, ComponentInfo>) -> f64 {
        if let Some(mutator) = components.get("FractalMutator") {
            if let Some(ComponentData::Fractal(fractal)) = &mutator.data {
                let base_rate = fractal.parameters.mutation_strength;
                
                // Ajustar por auto-mutación
                if fractal.parameters.auto_mutate {
                    return base_rate * (1.0 + fractal.parameters.auto_mutate_speed * 10.0);
                }
                
                return base_rate;
            }
        }
        
        0.0
    }
    
    /// Calcular calidad del análisis actual
    fn calculate_analysis_quality(&self, components: &HashMap<String, ComponentInfo>) -> f64 {
        if let Some(explorer) = components.get("FractalExplorer") {
            if let Some(ComponentData::Analysis(analysis)) = &explorer.data {
                // Combinar múltiples métricas de calidad
                let interest_score = analysis.metrics.get("interesting_score").unwrap_or(&0.0);
                let complexity = analysis.metrics.get("complexity_measure").unwrap_or(&0.0);
                let boundary = analysis.metrics.get("boundary_length").unwrap_or(&0.0);
                
                // Promedio ponderado de métricas
                return interest_score * 0.5 + complexity * 0.3 + boundary * 0.2;
            }
        }
        
        0.5 // Valor por defecto
    }
    
    /// Calcular actividad histórica
    fn calculate_historical_activity(&self) -> f64 {
        if self.analysis_history.len() < 2 {
            return 1.0; // Valor neutral si no hay historial
        }
        
        let recent_snapshots = self.analysis_history
            .iter()
            .rev()
            .take(10) // Últimos 10 snapshots
            .collect::<Vec<_>>();
        
        if recent_snapshots.is_empty() {
            return 1.0;
        }
        
        // Calcular tendencia de actividad
        let mut activity_sum = 0.0;
        let mut trend_factor = 1.0;
        
        for (i, snapshot) in recent_snapshots.iter().enumerate() {
            let weight = 1.0 - (i as f64 * 0.1); // Dar más peso a snapshots recientes
            activity_sum += match snapshot.activity_level {
                ActivityLevel::Critical => 3.0 * weight,
                ActivityLevel::High => 2.0 * weight,
                ActivityLevel::Moderate => 1.0 * weight,
                ActivityLevel::Low => 0.5 * weight,
            };
        }
        
        // Detectar tendencias crecientes o decrecientes
        if recent_snapshots.len() >= 3 {
            let recent_avg = recent_snapshots[0..3].iter()
                .map(|s| s.health_score)
                .sum::<f64>() / 3.0;
            
            let older_avg = recent_snapshots[3..6.min(recent_snapshots.len())].iter()
                .map(|s| s.health_score)
                .sum::<f64>() / (6.min(recent_snapshots.len()) - 3) as f64;
            
            if recent_avg > older_avg + 0.1 {
                trend_factor = 1.2; // Tendencia positiva
            } else if recent_avg < older_avg - 0.1 {
                trend_factor = 0.8; // Tendencia negativa
            }
        }
        
        (activity_sum / recent_snapshots.len() as f64 * trend_factor).clamp(0.0, 3.0)
    }
    
    /// Generar recomendaciones basadas en el análisis
    fn generate_recommendations(&self, components: &HashMap<String, ComponentInfo>, activity_level: &ActivityLevel) -> Result<Vec<String>> {
        let mut recommendations = Vec::new();
        
        // Recomendaciones basadas en nivel de actividad
        match activity_level {
            ActivityLevel::Low => {
                recommendations.push("Incrementar estímulos de mutación".to_string());
                recommendations.push("Solicitar análisis profundo".to_string());
                recommendations.push("Considerar cambio de parámetros".to_string());
            }
            ActivityLevel::Critical => {
                recommendations.push("Reducir intensidad de mutación".to_string());
                recommendations.push("Implementar regulación automática".to_string());
                recommendations.push("Monitorear estabilidad del sistema".to_string());
            }
            _ => {}
        }
        
        // Recomendaciones específicas por componente
        if let Some(mutator) = components.get("FractalMutator") {
            if let Some(ComponentData::Fractal(fractal)) = &mutator.data {
                if fractal.parameters.zoom > 1000.0 {
                    recommendations.push("Zoom extremo detectado - considerar reset".to_string());
                }
                
                if fractal.parameters.mutation_strength > 0.5 {
                    recommendations.push("Fuerza de mutación muy alta - reducir gradualmente".to_string());
                }
                
                if !fractal.parameters.auto_mutate && *activity_level == ActivityLevel::Low {
                    recommendations.push("Activar auto-mutación para aumentar actividad".to_string());
                }
            }
        }
        
        // Verificar si falta el explorador
        if !components.contains_key("FractalExplorer") {
            recommendations.push("FractalExplorer offline - reiniciar componente".to_string());
        }
        
        // Recomendaciones basadas en historial
        if self.analysis_history.len() >= 5 {
            let recent_health = self.analysis_history.iter()
                .rev()
                .take(5)
                .map(|s| s.health_score)
                .collect::<Vec<_>>();
            
            let avg_health = recent_health.iter().sum::<f64>() / recent_health.len() as f64;
            
            if avg_health < 0.6 {
                recommendations.push("Salud del ecosistema baja - diagnóstico completo requerido".to_string());
            }
        }
        
        Ok(recommendations)
    }
    
    /// Añadir snapshot al historial
    fn add_to_history(&mut self, snapshot: EcosystemSnapshot) {
        self.analysis_history.push(snapshot);
        
        // Mantener tamaño del historial limitado
        if self.analysis_history.len() > self.max_history_size {
            self.analysis_history.remove(0);
        }
    }
    
    /// Obtener métricas históricas del ecosistema
    pub fn get_historical_metrics(&self) -> HistoricalMetrics {
        if self.analysis_history.is_empty() {
            return HistoricalMetrics::default();
        }
        
        let snapshots = &self.analysis_history;
        let count = snapshots.len() as f64;
        
        let avg_health = snapshots.iter().map(|s| s.health_score).sum::<f64>() / count;
        let avg_mutation_rate = snapshots.iter().map(|s| s.mutation_rate).sum::<f64>() / count;
        let avg_analysis_quality = snapshots.iter().map(|s| s.analysis_quality).sum::<f64>() / count;
        
        // Calcular distribución de niveles de actividad
        let mut activity_distribution = HashMap::new();
        for snapshot in snapshots {
            let counter = activity_distribution.entry(snapshot.activity_level.clone()).or_insert(0);
            *counter += 1;
        }
        
        // Detectar patrones o anomalías
        let health_trend = if snapshots.len() >= 5 {
            let recent = snapshots.iter().rev().take(5).map(|s| s.health_score).sum::<f64>() / 5.0;
            let older = snapshots.iter().rev().skip(5).take(5).map(|s| s.health_score).sum::<f64>() / 5.0;
            
            if recent > older + 0.1 {
                "Improving".to_string()
            } else if recent < older - 0.1 {
                "Declining".to_string()
            } else {
                "Stable".to_string()
            }
        } else {
            "Insufficient data".to_string()
        };
        
        HistoricalMetrics {
            total_snapshots: snapshots.len(),
            average_health: avg_health,
            average_mutation_rate: avg_mutation_rate,
            average_analysis_quality: avg_analysis_quality,
            activity_distribution,
            health_trend,
            time_span_minutes: if snapshots.len() >= 2 {
                snapshots.last().unwrap().timestamp
                    .signed_duration_since(snapshots.first().unwrap().timestamp)
                    .num_minutes()
            } else {
                0
            },
        }
    }
}

/// Métricas históricas del ecosistema
#[derive(Debug, Clone)]
pub struct HistoricalMetrics {
    pub total_snapshots: usize,
    pub average_health: f64,
    pub average_mutation_rate: f64,
    pub average_analysis_quality: f64,
    pub activity_distribution: HashMap<ActivityLevel, i32>,
    pub health_trend: String,
    pub time_span_minutes: i64,
}

impl Default for HistoricalMetrics {
    fn default() -> Self {
        Self {
            total_snapshots: 0,
            average_health: 0.0,
            average_mutation_rate: 0.0,
            average_analysis_quality: 0.0,
            activity_distribution: HashMap::new(),
            health_trend: "No data".to_string(),
            time_span_minutes: 0,
        }
    }
}