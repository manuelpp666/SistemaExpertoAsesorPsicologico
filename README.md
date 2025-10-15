SISTEMAEXPERTO/
├─ base_conocimiento/                      # Base de Conocimiento
│  ├─ casos.json                           # Casos iniciales
│  ├─ sinonimos_ontologia.json             # Ontología y sinónimos
│  ├─ sinonimos_ontologia_enriquecido.json # Los sinónimos extendidos que derivan de los sinonimos_ontologia
│  ├─ modelos.py                           # Definición de Caso y BaseDeCasos
│  └─ almacenamiento.py                    # Guardado y carga
│
├─ motor_inferencia/                       # Motor de Inferencia (Razonamiento CBR)
│  ├─ representacion.py                    # Normalización y vectorización de síntomas
│  └─ razonador.py                         # Permite analizar y recuperar los casos con mayor similitud(razonar)
│  └─ semantic_helper.py                   # Mejora de la interpretación de los síntomas que el paciente ingresa
│
├─ modulo_explicacion/                     # Módulo de Explicación
│  └─ explicacion.py                       # Justificación de las recomendaciones con su respectiva explicación
│
│
├─ interfaz_usuario/                       # Interfaz de Usuario
│  └─ ui.py                                # Interfaz en Tkinter
│
│
│
└─ README.md                               # Documentación del proyecto

