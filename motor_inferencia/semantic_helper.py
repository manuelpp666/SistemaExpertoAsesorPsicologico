# motor_inferencia/semantic_helper.py
import json
import os
import unicodedata
from difflib import get_close_matches, SequenceMatcher

# === CONFIGURACIÓN ===
_RUTA_CASOS = os.path.join("base_conocimiento", "casos.json")
_DEFAULT_THRESHOLD = 0.4  # similitud mínima aceptada

# === SINÓNIMOS ===
SINONIMOS = {
    "me quiero morir": "ideas suicidas",
    "me quiero matar": "ideas suicidas",
    "no quiero vivir": "ideas suicidas",
    "terminar con todo": "ideas suicidas",
    "sin ganas de vivir": "ideas suicidas",
    "no tengo hambre": "pérdida de apetito",
    "no puedo dormir": "insomnio",
    "duermo poco": "insomnio",
    "estoy cansado": "falta de energía",
    "me siento triste": "tristeza persistente",
    "no tengo energía": "falta de energía",
    "me siento solo": "aislamiento social",
    "tengo mucho sueño": "falta de energía",
    "me siento fatigado": "falta de energía",
}

# === UTILIDADES ===
def preprocesar_texto(texto: str) -> str:
    """Minúsculas y quitar acentos."""
    texto = texto.lower()
    texto = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )
    return texto.strip()

def normalizar_sinonimos(frase: str) -> str:
    """Devuelve la versión canónica si coincide con un sinónimo."""
    frase_norm = preprocesar_texto(frase)
    for clave, canonico in SINONIMOS.items():
        if clave in frase_norm:
            return canonico
    return frase_norm

def similitud_lexica(a: str, b: str) -> float:
    """Similitud básica entre dos textos."""
    return SequenceMatcher(None, a, b).ratio()

def buscar_sinonimo_difuso(frase: str, lista_claves: list, umbral: float) -> str:
    """Busca coincidencia difusa en sinónimos."""
    match = get_close_matches(frase, lista_claves, n=1, cutoff=umbral)
    return match[0] if match else None

# === CARGA DE CASOS ===
def cargar_sintomas_desde_casos():
    """Lee todos los síntomas únicos de base_conocimiento/casos.json."""
    if not os.path.exists(_RUTA_CASOS):
        print(f"⚠️ No se encontró {_RUTA_CASOS}")
        return []

    with open(_RUTA_CASOS, "r", encoding="utf-8") as f:
        casos = json.load(f)

    sintomas = set()
    for caso in casos:
        for s in caso.get("sintomas", []):
            sintomas.add(preprocesar_texto(s))
    return list(sintomas)

# === FUNCIÓN PRINCIPAL ===
def buscar_equivalente_semantico(frase: str, umbral: float = _DEFAULT_THRESHOLD):
    """
    Busca coincidencias entre la frase del usuario y todos los síntomas
    definidos en los casos de conocimiento.
    Devuelve lista de (frase_usuario, sintoma_detectado, similitud)
    """
    sintomas_base = cargar_sintomas_desde_casos()
    if not sintomas_base:
        return []

    lista_claves = list(SINONIMOS.keys())
    partes = [p.strip() for p in frase.split(",") if p.strip()]
    coincidencias = []

    for parte in partes:
        parte_norm = preprocesar_texto(parte)

        # 1️⃣ Coincidencia exacta con sinónimos
        canonico = normalizar_sinonimos(parte_norm)
        if canonico != parte_norm:
            print(f"[SEMANTIC LOG] Exacto: '{parte}' → '{canonico}'")
            coincidencias.append((parte, canonico, 1.0))
            continue

        # 2️⃣ Coincidencia difusa con sinónimos
        difuso = buscar_sinonimo_difuso(parte_norm, lista_claves, umbral)
        if difuso:
            canonico = SINONIMOS[difuso]
            print(f"[SEMANTIC LOG] Difuso: '{parte}' ≈ '{canonico}'")
            coincidencias.append((parte, canonico, umbral))
            continue

        # 3️⃣ Coincidencia léxica con síntomas de casos
        mejor_sintoma = None
        mejor_sim = 0.0
        for sintoma in sintomas_base:
            sim = similitud_lexica(parte_norm, sintoma)
            if sim > mejor_sim:
                mejor_sintoma, mejor_sim = sintoma, sim

        if mejor_sim >= umbral:
            print(f"[SEMANTIC LOG] Semántica: '{parte}' ≈ '{mejor_sintoma}' ({mejor_sim:.2f})")
            coincidencias.append((parte, mejor_sintoma, mejor_sim))
        else:
            print(f"[SEMANTIC LOG] Sin coincidencia para: '{parte}'")
            coincidencias.append((parte, None, 0.0))

    return coincidencias
