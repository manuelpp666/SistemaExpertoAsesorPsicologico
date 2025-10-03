# motor_inferencia/similitud.py
from typing import List
from motor_inferencia.representacion import normalizar_lista

def similitud_jaccard(lista1: List[str], lista2: List[str]) -> float:
    """
    Calcula similitud de Jaccard entre dos listas de síntomas.
    """
    set1, set2 = set(normalizar_lista(lista1)), set(normalizar_lista(lista2))
    if not set1 and not set2:
        return 0.0
    return len(set1 & set2) / len(set1 | set2)
