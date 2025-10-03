# motor_inferencia/razonador.py
from typing import List, Optional, Tuple
from base_conocimiento.modelos import BaseDeCasos, Caso
from motor_inferencia.similitud import similitud_jaccard
from motor_inferencia.representacion import normalizar_lista

def recuperar_caso(base: BaseDeCasos, sintomas_usuario: List[str], top_k: int = 1) -> List[Tuple[Caso, float]]:
    """
    Recupera los casos más similares según los síntomas del usuario.
    Devuelve una lista de tuplas (caso, score) ordenada de mayor a menor similitud.
    """
    similitudes = []
    for caso in base.listar_casos():
        score = similitud_jaccard(sintomas_usuario, caso.sintomas)
        similitudes.append((caso, score))

    similitudes.sort(key=lambda x: x[1], reverse=True)
    return similitudes[:top_k]

def razonar(base: BaseDeCasos, sintomas_usuario: List[str]) -> Optional[Tuple[Caso, float]]:
    """
    Recupera el mejor caso y devuelve una tupla (Caso, confianza).
    Devuelve None si no hay casos en la base.
    """
    # ✅ Normalizamos la entrada del usuario antes de buscar
    sintomas_usuario = normalizar_lista(sintomas_usuario)

    candidatos = recuperar_caso(base, sintomas_usuario, top_k=1)
    if not candidatos:
        return None

    mejor_caso, score = candidatos[0]
    return mejor_caso, score
