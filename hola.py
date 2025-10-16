import json
import os
import unicodedata
import re
from itertools import product

# === RUTAS ===
RUTA_CASOS = os.path.join("base_conocimiento", "casos.json")
RUTA_SALIDA = os.path.join("base_conocimiento", "sinonimos_ontologia.json")

# === MAPAS DE SINÓNIMOS ===
MAPEO_SEMANTICO = {
    "miedo": ["temor", "fobia", "pánico", "ansiedad", "angustia"],
    "tristeza": ["desánimo", "melancolía", "depresión", "pena"],
    "preocupación": ["inquietud", "ansiedad", "angustia", "estrés"],
    "culpa": ["vergüenza", "remordimiento", "autorreproche"],
    "ira": ["enojo", "molestia", "rabia", "frustración"],
    "cansancio": ["fatiga", "agotamiento", "falta de energía"],
    "ansiedad": ["nerviosismo", "inquietud", "tensión", "estrés"],
    "fobia": ["temor intenso", "aversión", "miedo irracional"],
}

# === PATRONES RELACIONALES (a, con, por, hacia, de) ===
PREPOSICIONES = ["a", "con", "por", "hacia", "de", "ante"]

# === FUNCIONES DE UTILIDAD ===
def preprocesar_texto(texto: str) -> str:
    texto = texto.lower()
    texto = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )
    texto = re.sub(r"[^a-zñáéíóúü\s]", "", texto)
    return texto.strip()

def generar_variaciones_basicas(base: str) -> set:
    """Genera variaciones naturales de un síntoma sin cambiar su significado."""
    variaciones = {
        base,
        f"tengo {base}",
        f"me da {base}",
        f"siento {base}",
        f"padezco {base}",
        f"experimento {base}",
        f"presento {base}",
        f"he tenido {base}",
        f"estoy con {base}"
    }
    return variaciones

def generar_sinonimos_emocionales(sintoma: str) -> set:
    """Reemplaza palabras clave por sinónimos emocionales según MAPEO_SEMANTICO."""
    variaciones = set()
    for clave, sinonimos in MAPEO_SEMANTICO.items():
        if clave in sintoma:
            for s in sinonimos:
                variaciones.add(sintoma.replace(clave, s))
    return variaciones

def generar_relacionales(sintoma: str) -> set:
    """
    Si el síntoma contiene una estructura 'X a Y' o 'X por Y',
    genera variaciones relacionales naturales (miedo ↔ fobia, tristeza ↔ desánimo, etc.)
    """
    variaciones = set()
    for prep in PREPOSICIONES:
        patron = rf"(.+?)\s+{prep}\s+(.+)"
        m = re.match(patron, sintoma)
        if m:
            x, y = m.groups()
            x, y = x.strip(), y.strip()
            variaciones.update({
                f"{x} {prep} {y}",
                f"{x} hacia {y}",
                f"{x} por {y}",
                f"{x} con {y}",
                f"{x} ante {y}",
                f"{x} al {y}",
            })
            # combinar con sinónimos emocionales de la parte X
            for clave, sinonimos in MAPEO_SEMANTICO.items():
                if clave in x:
                    for s in sinonimos:
                        variaciones.add(f"{s} {prep} {y}")
    return variaciones

def generar_contextuales(sintoma: str) -> set:
    """Agrega expresiones tipo 'síntomas de X' o 'problemas con X'."""
    base = sintoma.strip()
    variaciones = {
        f"problemas con {base}",
        f"dificultad por {base}",
        f"síntomas de {base}",
        f"molestia relacionada con {base}",
        f"trastorno asociado a {base}",
        f"tendencia a {base}",
    }
    return variaciones

# === FUNCIÓN PRINCIPAL ===
def main():
    if not os.path.exists(RUTA_CASOS):
        print("⚠️ No se encontró base_conocimiento/casos.json")
        return

    with open(RUTA_CASOS, "r", encoding="utf-8") as f:
        casos = json.load(f)

    sinonimos = {}

    for caso in casos:
        for sintoma in caso.get("sintomas", []):
            base = preprocesar_texto(sintoma)

            # Generar todas las variantes
            variaciones = set()
            variaciones |= generar_variaciones_basicas(base)
            variaciones |= generar_sinonimos_emocionales(base)
            variaciones |= generar_relacionales(base)
            variaciones |= generar_contextuales(base)

            # Añadir al diccionario
            for v in variaciones:
                v_norm = preprocesar_texto(v)
                sinonimos[v_norm] = base

    # Guardar resultado
    with open(RUTA_SALIDA, "w", encoding="utf-8") as f:
        json.dump(sinonimos, f, ensure_ascii=False, indent=2)

    print(f"✅ Archivo de sinónimos enriquecido generado: {RUTA_SALIDA}")
    print(f"Total de entradas: {len(sinonimos)}")

if __name__ == "__main__":
    main()
