from typing import List, Dict, Optional
import json
import os


class Caso:
    """
    Representa un caso psicológico almacenado en la base de conocimiento.
    Contiene síntomas, causa probable, estrategias de intervención, nivel de riesgo y recomendaciones generales.
    """

    def __init__(
        self,
        id_caso: int,
        sintomas: List[str],
        posible_causa: str,
        estrategias: List[str],
        resultado: Optional[str] = None,
        autoevaluaciones_sugeridas: Optional[List[str]] = None,
        riesgo: Optional[str] = None,
        derivar_a: Optional[List[str]] = None,
        recomendacion_general: Optional[str] = None
    ):
        self.id_caso = id_caso
        self.sintomas = sintomas
        self.posible_causa = posible_causa
        self.estrategias = estrategias
        self.resultado = resultado or "No especificado"
        self.autoevaluaciones_sugeridas = autoevaluaciones_sugeridas or []
        self.riesgo = riesgo or "desconocido"
        self.derivar_a = derivar_a or []
        self.recomendacion_general = recomendacion_general or "Sin recomendación adicional."

    # ======================================================
    # Conversiones entre objeto y diccionario
    # ======================================================
    def to_dict(self) -> Dict:
        """Convierte el caso a un diccionario compatible con JSON."""
        return {
            "id_caso": self.id_caso,
            "sintomas": self.sintomas,
            "posible_causa": self.posible_causa,
            "estrategias": self.estrategias,
            "resultado": self.resultado,
            "autoevaluaciones_sugeridas": self.autoevaluaciones_sugeridas,
            "riesgo": self.riesgo,
            "derivar_a": self.derivar_a,
            "recomendacion_general": self.recomendacion_general
        }

    @staticmethod
    def from_dict(data: Dict) -> "Caso":
        """Crea un objeto Caso a partir de un diccionario (por ejemplo, al leer JSON)."""
        return Caso(
            id_caso=data.get("id_caso"),
            sintomas=data.get("sintomas", []),
            posible_causa=data.get("posible_causa", "No especificado"),
            estrategias=data.get("estrategias", []),
            resultado=data.get("resultado"),
            autoevaluaciones_sugeridas=data.get("autoevaluaciones_sugeridas", []),
            riesgo=data.get("riesgo", "desconocido"),
            derivar_a=data.get("derivar_a", []),
            recomendacion_general=data.get("recomendacion_general", "Sin recomendación adicional.")
        )


class BaseDeCasos:
    """
    Contiene una colección de casos psicológicos.
    Permite buscarlos, listarlos, agregarlos y persistirlos en archivos JSON.
    """

    def __init__(self):
        self.casos: List[Caso] = []

    # ------------------------------------------------------
    # Operaciones sobre la colección de casos
    # ------------------------------------------------------
    def agregar_caso(self, caso: Caso):
        """Agrega un nuevo caso a la base."""
        self.casos.append(caso)

    def buscar_por_id(self, id_caso: int) -> Optional[Caso]:
        """Busca un caso por su ID."""
        return next((c for c in self.casos if c.id_caso == id_caso), None)

    def listar_casos(self) -> List[Caso]:
        """Devuelve la lista completa de casos."""
        return self.casos

    # ------------------------------------------------------
    # Persistencia en JSON
    # ------------------------------------------------------
    def cargar_desde_json(self, ruta: str):
        """Carga todos los casos desde un archivo JSON."""
        if not os.path.exists(ruta):
            raise FileNotFoundError(f"No se encontró el archivo: {ruta}")

        with open(ruta, "r", encoding="utf-8") as f:
            datos = json.load(f)

        # El archivo puede contener una lista o un solo caso
        if isinstance(datos, dict):
            self.casos = [Caso.from_dict(datos)]
        elif isinstance(datos, list):
            self.casos = [Caso.from_dict(item) for item in datos]
        else:
            raise ValueError("Formato de archivo JSON no reconocido.")

    def guardar_a_json(self, ruta: str):
        """Guarda los casos actuales en un archivo JSON."""
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump([c.to_dict() for c in self.casos], f, ensure_ascii=False, indent=4)
