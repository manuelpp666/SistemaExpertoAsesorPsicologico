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
    """
    return [normalizar_texto(s) for s in sintomas if s.strip()]
