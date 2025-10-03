# motor_inferencia/representacion.py
from typing import List

def normalizar_texto(texto: str) -> str:
    """
    Normaliza un síntoma para comparación:
    - minúsculas
    - quita espacios extra
    """
    return texto.strip().lower()

def normalizar_lista(sintomas: List[str]) -> List[str]:
    return [normalizar_texto(s) for s in sintomas]
