# base_conocimiento/modelos.py
from typing import List, Dict

class Caso:
    def __init__(self, id_caso: int, sintomas: List[str], diagnostico: str, estrategias: List[str], resultado: str = None):
        """
        Representa un caso psicológico en la base de conocimiento.

        Args:
            id_caso (int): Identificador único del caso
            sintomas (List[str]): Lista de síntomas reportados por el paciente
            diagnostico (str): Diagnóstico asociado (ej. "ansiedad", "depresión leve")
            estrategias (List[str]): Técnicas o intervenciones aplicadas
            resultado (str, opcional): Resultado observado tras la intervención
        """
        self.id_caso = id_caso
        self.sintomas = sintomas
        self.diagnostico = diagnostico
        self.estrategias = estrategias
        self.resultado = resultado

    def to_dict(self) -> Dict:
        return {
            "id_caso": self.id_caso,
            "sintomas": self.sintomas,
            "diagnostico": self.diagnostico,
            "estrategias": self.estrategias,
            "resultado": self.resultado
        }

    @staticmethod
    def from_dict(data: Dict):
        return Caso(
            id_caso=data["id_caso"],
            sintomas=data["sintomas"],
            diagnostico=data["diagnostico"],
            estrategias=data["estrategias"],
            resultado=data.get("resultado")
        )


class BaseDeCasos:
    def __init__(self):
        self.casos: List[Caso] = []

    def agregar_caso(self, caso: Caso):
        self.casos.append(caso)

    def buscar_por_id(self, id_caso: int) -> Caso:
        for c in self.casos:
            if c.id_caso == id_caso:
                return c
        return None

    def listar_casos(self) -> List[Caso]:
        return self.casos
