# motor_inferencia/razonador.py
from typing import List, Optional, Tuple
from base_conocimiento.modelos import BaseDeCasos, Caso
from motor_inferencia.representacion import normalizar_lista

def similitud_jaccard(sintomas1: List[str], sintomas2: List[str]) -> float:
    """
    Calcula la similitud de Jaccard entre dos listas de síntomas.
    """
    set1, set2 = set(sintomas1), set(sintomas2)
    if not set1 and not set2:
        return 0.0
    interseccion = set1 & set2
    union = set1 | set2
    return len(interseccion) / len(union) if union else 0.0

def recuperar_caso(base: BaseDeCasos, sintomas_usuario: List[str], top_k: int = 1) -> List[Tuple[Caso, float]]:
    sintomas_usuario = normalizar_lista(sintomas_usuario)
    

    similitudes = []

    for caso in base.listar_casos():
        sintomas_caso = normalizar_lista(caso.sintomas)
        score = similitud_jaccard(sintomas_usuario, sintomas_caso)

        # DEBUG
        print(f"[Caso {caso.id_caso}] sintomas={sintomas_caso} | score={score}")

        similitudes.append((caso, score))

    similitudes.sort(key=lambda x: x[1], reverse=True)
    return similitudes[:top_k]


def razonar(base: BaseDeCasos, sintomas_usuario: List[str], umbral: float = 0.6) -> Optional[Tuple[Caso, float]]:
    """
    Recupera el mejor caso y devuelve una tupla (Caso, confianza).
    - Similitud == 1.0 → coincidencia exacta
    - Similitud >= umbral → coincidencia parcial
    - Si ninguna cumple → None
    """
    candidatos = recuperar_caso(base, sintomas_usuario, top_k=1)
    if not candidatos:
        return None

    mejor_caso, score = candidatos[0]
    if score >= umbral:
        return mejor_caso, score

    return None