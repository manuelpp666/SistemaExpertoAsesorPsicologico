# base_conocimiento/modelos.py
from typing import List, Dict

class Caso:
    def __init__(self, id_caso: int, sintomas: List[str], diagnostico: str, estrategias: List[str],
                 resultado: str = None, evaluaciones: List[str] = None,
                 riesgo: str = None, derivar_a: List[str] = None):
        self.id_caso = id_caso
        self.sintomas = sintomas
        self.diagnostico = diagnostico
        self.estrategias = estrategias
        self.resultado = resultado
        self.evaluaciones = evaluaciones or []
        self.riesgo = riesgo or "desconocido"
        self.derivar_a = derivar_a or []

    def to_dict(self) -> Dict:
        return {
            "id_caso": self.id_caso,
            "sintomas": self.sintomas,
            "diagnostico": self.diagnostico,
            "estrategias": self.estrategias,
            "resultado": self.resultado,
            "evaluaciones": self.evaluaciones,
            "riesgo": self.riesgo,
            "derivar_a": self.derivar_a
        }

    @staticmethod
    def from_dict(data: Dict):
        return Caso(
            id_caso=data["id_caso"],
            sintomas=data["sintomas"],
            diagnostico=data["diagnostico"],
            estrategias=data["estrategias"],
            resultado=data.get("resultado"),
            evaluaciones=data.get("evaluaciones", []),
            riesgo=data.get("riesgo", "desconocido"),
            derivar_a=data.get("derivar_a", [])
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
