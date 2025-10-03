# base_conocimiento/almacenamiento.py
import json
from .modelos import Caso, BaseDeCasos
import os

RUTA_ARCHIVO = os.path.join(os.path.dirname(__file__), "casos.json")

def guardar_base(base: BaseDeCasos, ruta: str = RUTA_ARCHIVO):
    data = [c.to_dict() for c in base.listar_casos()]
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def cargar_base(ruta: str = RUTA_ARCHIVO) -> BaseDeCasos:
    base = BaseDeCasos()
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            data = json.load(f)
            for c in data:
                base.agregar_caso(Caso.from_dict(c))
    except FileNotFoundError:
        print("⚠️ No se encontró la base de casos, se creará una nueva.")
    return base

def guardar_json(data, ruta):
    """Guarda cualquier estructura de datos en un JSON."""
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)