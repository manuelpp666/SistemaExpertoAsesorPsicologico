# modulo_explicacion/explicacion.py
from motor_inferencia.representacion import normalizar_lista

class ModuloExplicacion:
    def __init__(self, caso, similitud):
        self.caso = caso              # objeto Caso
        self.similitud = similitud    # valor entre 0 y 1

    def generar_explicacion(self, sintomas_usuario):
        sintomas_caso = set(normalizar_lista(self.caso.sintomas))
        sintomas_usuario = set(normalizar_lista(sintomas_usuario))

        coincidencias = sintomas_usuario.intersection(sintomas_caso)

        explicacion = "Hemos analizado los síntomas que proporcionaste y los comparamos con casos similares.\n"

        if coincidencias:
            explicacion += f"✔ Los síntomas coinciden en: {', '.join(coincidencias)}.\n"
        else:
            explicacion += "⚠ No se encontró ningún síntoma que coincida con casos anteriores.\n"

        # Añadir info de riesgo y derivación
        if getattr(self.caso, "riesgo", None) and self.caso.riesgo != "desconocido":
            explicacion += f"\n⚠ Nivel de riesgo identificado: {self.caso.riesgo.upper()}.\n"
        if getattr(self.caso, "derivar_a", []):
            explicacion += f"👉 Se recomienda derivar a: {', '.join(self.caso.derivar_a)}.\n"
        if getattr(self.caso, "evaluaciones", []):
            explicacion += f"📋 Evaluaciones sugeridas: {', '.join(self.caso.evaluaciones)}.\n"

        explicacion += "\nTen en cuenta que esto es una guía y no sustituye la evaluación directa de un profesional."
        return explicacion