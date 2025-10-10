# motor_inferencia/razonador.py
from typing import List, Optional, Tuple, Callable
from base_conocimiento.modelos import BaseDeCasos, Caso
from motor_inferencia.representacion import normalizar_lista
from difflib import SequenceMatcher


def similitud_jaccard(sintomas1: List[str], sintomas2: List[str]) -> float:
    """
    Calcula la similitud entre dos listas de síntomas usando una versión
    flexible del índice de Jaccard, donde se cuenta una coincidencia si
    las cadenas se parecen al menos un 60%.
    """
    set1, set2 = set(sintomas1), set(sintomas2)
    if not set1 or not set2:
        return 0.0

    interseccion = 0
    for s1 in set1:
        for s2 in set2:
            ratio = SequenceMatcher(None, s1, s2).ratio()
            if ratio >= 0.6:  # 60% de parecido cuenta como coincidencia
                interseccion += 1
                break

    union = len(set1 | set2)
    return interseccion / union if union else 0.0


def recuperar_caso(base: BaseDeCasos, sintomas_usuario: List[str]) -> List[Tuple[Caso, float]]:
    """
    Recupera todos los casos con su similitud, ordenados de mayor a menor.
    """
    sintomas_usuario = normalizar_lista(sintomas_usuario)
    similitudes = []

    for caso in base.listar_casos():
        sintomas_caso = normalizar_lista(caso.sintomas)
        score = similitud_jaccard(sintomas_usuario, sintomas_caso)
        print(f"[DEBUG] Caso {caso.id_caso} → similitud={score:.2f} | causa={caso.posible_causa}")
        similitudes.append((caso, score))

    similitudes.sort(key=lambda x: x[1], reverse=True)
    return similitudes


def razonar(
    base: BaseDeCasos,
    sintomas_usuario: List[str],
    umbral: float = 0.6,
    preguntar_callback: Optional[Callable[[str], str]] = None
) -> Optional[Tuple[Caso, float, Optional[str]]]:
    """
    Recupera el caso más probable según los síntomas.
    Si el usuario da un solo síntoma, pregunta síntomas adicionales (si hay ambigüedad).
    Si hay empate, añade explicación sobre la ambigüedad.
    Si todas las similitudes son 0.0, devuelve None.
    """
    sintomas_usuario = normalizar_lista(sintomas_usuario)
    coincidencias = recuperar_caso(base, sintomas_usuario)

    if not coincidencias:
        return None

    # Si todos los puntajes son 0.0 → no hay ningún caso relevante
    if all(score == 0 for _, score in coincidencias):
        return None

    # --- Caso A: un solo síntoma ---
    if len(sintomas_usuario) == 1:
        sintoma = sintomas_usuario[0]
        # Solo considerar casos con similitud > 0
        candidatos = [c for c, s in coincidencias if sintoma in normalizar_lista(c.sintomas) and s > 0]

        # Si no hay ningún candidato con similitud positiva
        if not candidatos and coincidencias[0][1] == 0:
            return None

        # Si hay varios casos con ese síntoma
        if len(candidatos) > 1 and preguntar_callback:
            for candidato in candidatos:
                for sint in normalizar_lista(candidato.sintomas):
                    if sint != sintoma:
                        respuesta = preguntar_callback(
                            f"Me has dado poca información.\n¿Tienes {sint}?"
                        )
                        if respuesta.lower().startswith("s"):
                            return candidato, 1.0, None  # Seleccionado directamente
            # Si no confirmó ninguno
            return candidatos[0], 0.5, None

        # Si solo hay uno o no se requiere preguntar
        mejor_caso, score = coincidencias[0]
        if score == 0:
            return None
        return mejor_caso, score, None

    # --- Caso B: varios síntomas ---
    mejor_score = coincidencias[0][1]
    empatados = [c for c, s in coincidencias if s == mejor_score]

    # Si el mejor caso no supera el umbral → no se considera válido
    if mejor_score < umbral:
        return None

    if len(empatados) > 1:
        explicacion = (
            f"Se eligió el caso '{empatados[0].posible_causa}', "
            f"pero también podría coincidir con '{empatados[1].posible_causa}'."
        )
        return empatados[0], mejor_score, explicacion

    return coincidencias[0][0], mejor_score, None
