# motor_inferencia/similitud.py
from typing import List
from motor_inferencia.representacion import normalizar_lista

def similitud_jaccard(lista1: List[str], lista2: List[str]) -> float:
    """
    Calcula la similitud de Jaccard entre dos listas de síntomas.
    - Normaliza ambas listas (minúsculas, sin espacios extra, etc.).
    - Compara como conjuntos (el orden no importa).
    """
    # ✅ Normalizamos antes de comparar
    set1 = set(normalizar_lista(lista1))
    set2 = set(normalizar_lista(lista2))

    if not set1 and not set2:
        return 0.0

    interseccion = set1 & set2
    union = set1 | set2
    return len(interseccion) / len(union) if union else 0.0
