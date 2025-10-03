cbr_psicologia/
├─ base_conocimiento/                      # Base de Conocimiento
│  ├─ casos.json                           # Casos iniciales
│  ├─ sinonimos_ontologia.json             # Ontología y sinónimos
│  ├─ modelos.py                           # Definición de Caso y BaseDeCasos
│  └─ almacenamiento.py                    # Guardado y carga
│
├─ motor_inferencia/                       # Motor de Inferencia (Razonamiento CBR)
│  ├─ representacion.py                    # Normalización y vectorización de síntomas
│  ├─ similitud.py                         # Métricas de similitud (Jaccard, Coseno, etc.)
│  └─ razonador.py                         # Implementación de las 4R (Recuperar, Reutilizar, Revisar, Retener)
│
├─ modulo_explicacion/                     # Módulo de Explicación
│  └─ explicacion.py                       # Justificación de las recomendaciones
│
├─ modulo_adquisicion/                     # Módulo de Adquisición del Conocimiento
│  └─ adquisicion.py                       # Incorporación de nuevos casos (feedback)
│
├─ interfaz_usuario/                       # Interfaz de Usuario
│  └─ ui.py                     # Interfaz en Streamlit
│
├─ pruebas/                                # Pruebas unitarias
│  ├─ test_similitud.py
│  ├─ test_razonador.py
│  └─ test_explicacion.py
│
├─ utils/                                  # Utilidades generales
│  └─ helpers.py                           # Validaciones, logs, funciones de apoyo
│
├─ requirements.txt                        # Dependencias
└─ README.md                               # Documentación del proyecto