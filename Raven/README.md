# Raven

**Raven** es una inteligencia artificial escalable desarrollada en Python, diseñada para interpretar patrones fractales complejos y clasificarlos con base en sus propiedades visuales. Su objetivo no es generar nuevos fractales, sino **analizarlos, detectar patrones, categorizarlos** y vincularlos con conocimiento humano relevante, usando técnicas de visión computacional y machine learning.

##  Objetivo

- Analizar imágenes fractales (contornos, histogramas, momentos de Hu)
- Clasificarlas en grupos visuales similares mediante clustering (KMeans)
- Asociar cada grupo a descripciones interpretativas humanas
- Aprender progresivamente a diferenciar estilos y estructuras fractales

---

## Estructura del proyecto
raven_ai/
├── main.py
├── core/
│ ├── fractal_interpreter.py
│ ├── pattern_classifier.py
│ ├── knowledge_base.py
│ └── utils.py (opcional)
├── data/
│ ├── raw/ ← imágenes fractales
│ └── features/ ← descriptores extraídos (futuro)
├── models/ ← clasificadores entrenados (futuro)
├── notebooks/ ← análisis exploratorios
└── README.md

---

##  Requisitos

```bash
pip install numpy opencv-python scikit-learn matplotlib


