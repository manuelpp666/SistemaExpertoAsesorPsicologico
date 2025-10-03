# modulo_explicacion/explicacion.py
from motor_inferencia.representacion import normalizar_lista

class ModuloExplicacion:
    def __init__(self, caso, similitud):
        self.caso = caso              # objeto Caso
        self.similitud = similitud    # valor entre 0 y 1

    def generar_explicacion(self, sintomas_usuario):
        # ✅ normalizar ambos lados antes de comparar
        sintomas_caso = set(normalizar_lista(self.caso.sintomas))
        sintomas_usuario = set(normalizar_lista(sintomas_usuario))

        coincidencias = sintomas_usuario.intersection(sintomas_caso)

        explicacion = "Hemos analizado los síntomas que proporcionaste y los comparamos con casos similares.\n"

        if coincidencias:
            explicacion += f"✔ Los síntomas coinciden en: {', '.join(coincidencias)}.\n"
        else:
            explicacion += "⚠ No se encontró ningún síntoma que coincida con casos anteriores. No se puede generar un diagnóstico confiable.\n"

        explicacion += "Ten en cuenta que esto es una guía basada en casos previos y no sustituye la evaluación directa de un profesional de salud mental."

        return explicacion
