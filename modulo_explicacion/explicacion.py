class ModuloExplicacion:
    def __init__(self, caso, similitud):
        self.caso = caso
        self.similitud = similitud  # valor entre 0 y 1, no lo mostramos aquí

    def generar_explicacion(self, sintomas_usuario):
        sintomas_caso = set(self.caso["sintomas"])
        sintomas_usuario = set(sintomas_usuario)

        coincidencias = sintomas_usuario.intersection(sintomas_caso)

        explicacion = "Hemos analizado los síntomas que proporcionaste y los comparamos con casos similares.\n"

        if coincidencias:
            explicacion += "✔ Los síntomas coinciden con casos anteriores.\n"
        else:
            explicacion += "⚠ No se encontró ningún síntoma que coincida con casos anteriores. No se puede generar un diagnóstico confiable.\n"

        explicacion += "Ten en cuenta que esto es una guía basada en casos previos y no sustituye la evaluación directa de un profesional de salud mental."

        return explicacion
