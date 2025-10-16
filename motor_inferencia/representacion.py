# motor_inferencia/representacion.py
from typing import List
import re
import unicodedata

def normalizar_texto(texto: str) -> str:
    """
    Normaliza un síntoma para comparación:
    - convierte a minúsculas
    - elimina tildes/acentos
    - quita espacios extra
    - mantiene la frase completa
    """
    # Quitar tildes/acentos
    texto = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )
    # Pasar a minúsculas
    texto = texto.lower()
    # Eliminar espacios al inicio/fin y dobles espacios
    texto = texto.strip()
    texto = re.sub(r'\s+', ' ', texto)
    return texto

def normalizar_lista(sintomas: List[str]) -> List[str]:
    """
    Normaliza una lista de síntomas manteniendo frases.
    Evita errores si hay valores None o vacíos.
    """
    lista_normalizada = []
    for s in sintomas:
        if isinstance(s, str) and s.strip():  # Solo procesar si es string y no está vacío
            lista_normalizada.append(normalizar_texto(s))
        elif s is None:
            print("[WARNING] Valor None detectado en lista de síntomas.")
    return lista_normalizada
