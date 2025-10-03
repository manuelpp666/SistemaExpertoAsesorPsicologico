from base_conocimiento.almacenamiento import guardar_json

class ModuloAdquisicion:
    def __init__(self, base, ruta_archivo):
        self.base = base
        self.ruta = ruta_archivo

    def incorporar_feedback(self, sintomas, diagnostico, estrategias, resultado):
        nuevo_caso = {
            "id": len(self.base) + 1,
            "sintomas": sintomas,
            "diagnostico": diagnostico,
            "estrategias": estrategias,
            "resultado": resultado
        }
        self.base.append(nuevo_caso)
        guardar_json(self.ruta, self.base)
        return nuevo_caso
