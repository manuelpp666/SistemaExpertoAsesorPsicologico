class ModuloExplicacion:
    def __init__(self, caso, similitud):
        self.caso = caso
        self.similitud = similitud

    def generar_explicacion(self, sintomas_usuario):
        sintomas_caso = set(self.caso["sintomas"])
        sintomas_usuario = set(sintomas_usuario)

        coincidencias = sintomas_usuario.intersection(sintomas_caso)
        faltantes = sintomas_usuario - sintomas_caso

        explicacion = f"Se seleccionó el caso ID {self.caso['id']} porque comparte síntomas clave con tu situación.\n"
        if coincidencias:
            explicacion += f"✔ Coincidencias: {', '.join(coincidencias)}.\n"
        if faltantes:
            explicacion += f"⚠ Síntomas no encontrados en este caso: {', '.join(faltantes)}.\n"

        explicacion += f"Nivel de confianza: {self.similitud:.2f}"
        return explicacion
