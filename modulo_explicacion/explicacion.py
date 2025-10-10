# modulo_explicacion/explicacion.py
from motor_inferencia.representacion import normalizar_lista

class ModuloExplicacion:
    def __init__(self, caso, similitud):
        self.caso = caso              # Objeto Caso
        self.similitud = similitud    # valor entre 0 y 1

    def generar_explicacion(self, sintomas_usuario):
        """
        Genera una explicación textual detallada basada en el caso más similar.
        """
        # Convertimos listas a conjuntos normalizados
        sintomas_caso = set(normalizar_lista(self.caso.sintomas))
        sintomas_usuario = set(normalizar_lista(sintomas_usuario))
        coincidencias = sintomas_usuario.intersection(sintomas_caso)

        # Encabezado
        explicacion = (
            "🔍 Hemos analizado los síntomas que proporcionaste y los comparamos con casos registrados en nuestra base de conocimiento.\n\n"
        )

        # Coincidencias
        if coincidencias:
            explicacion += f"✔ Coincidencias encontradas en los síntomas: {', '.join(coincidencias)}.\n"
        else:
            explicacion += "⚠ No se encontraron coincidencias exactas con casos anteriores.\n"

        # Posible causa
        if hasattr(self.caso, "causa") and self.caso.causa:
            explicacion += f"\n🧠 Posible causa identificada: {self.caso.causa}.\n"

        # Nivel de riesgo
        if hasattr(self.caso, "riesgo") and self.caso.riesgo and self.caso.riesgo.lower() != "desconocido":
            explicacion += f"⚠ Nivel de riesgo estimado: **{self.caso.riesgo.upper()}**.\n"

        # Estrategias sugeridas
        if hasattr(self.caso, "estrategias") and self.caso.estrategias:
            explicacion += "\n💡 Estrategias recomendadas:\n"
            for i, estrategia in enumerate(self.caso.estrategias, start=1):
                explicacion += f"   {i}. {estrategia}\n"

        # Recomendación general
        if hasattr(self.caso, "recomendacion_general") and self.caso.recomendacion_general:
            explicacion += f"\n📋 Recomendación general: {self.caso.recomendacion_general}.\n"

        # Autoevaluaciones sugeridas
        if hasattr(self.caso, "autoevaluaciones_sugeridas") and self.caso.autoevaluaciones_sugeridas:
            explicacion += "\n🧾 Autoevaluaciones sugeridas:\n"
            for test in self.caso.autoevaluaciones_sugeridas:
                explicacion += f"   - {test}\n"

        # Derivaciones (si las hubiera)
        if hasattr(self.caso, "derivar_a") and self.caso.derivar_a:
            explicacion += f"\n👉 Se recomienda derivar a: {', '.join(self.caso.derivar_a)}.\n"

        # Resultado observado
        if hasattr(self.caso, "resultado") and self.caso.resultado:
            explicacion += f"\n📈 Resultado observado en casos similares: {self.caso.resultado}.\n"

        # Nivel de similitud
        explicacion += f"\n🔢 Nivel de similitud con el caso más cercano: {self.similitud*100:.1f}%.\n"

        # Cierre
        explicacion += "\n🧩 Recuerda que esta información es orientativa y NO REEMPLAZA LA EVALUACIÓN PROFESIONAL 🩺."

        return explicacion
