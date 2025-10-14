import json
import os
import itertools

# === RUTAS ===
RUTA_CASOS = "base_conocimiento/casos.json"
RUTA_SINONIMOS = "base_conocimiento/sinonimos_ontologia.json"
RUTA_SALIDA = "base_conocimiento/sinonimos_ontologia_enriquecido.json"

# === PLANTILLAS DE VARIANTES ===
PLANTILLAS = [
    "me cuesta {s}",
    "no puedo {s}",
    "tengo problemas para {s}",
    "dificultad para {s}",
    "me resulta difícil {s}",
    "siento que no puedo {s}",
    "no logro {s}",
    "me cuesta mucho {s}",
    "problemas para {s}",
    "me es difícil {s}"
]

# === FUNCIONES ===

def cargar_json(ruta):
    if os.path.exists(ruta):
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def guardar_json(data, ruta):
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def extraer_sintomas(ruta_casos):
    casos = cargar_json(ruta_casos)
    sintomas = set()
    for caso in casos:
        for s in caso.get("sintomas", []):
            sintomas.add(s.strip().lower())
    return sorted(list(sintomas))

def generar_variantes(sintoma):
    """Genera frases naturales a partir de un síntoma."""
    variantes = set()
    texto = sintoma.lower()

    # Si el síntoma ya contiene verbo, evita duplicarlo
    if "dormir" in texto:
        variantes.update([
            "no puedo dormir bien",
            "me cuesta dormir por las noches",
            "duermo mal",
            "duermo muy poco",
            "no descanso bien"
        ])
    elif "energ" in texto:
        variantes.update([
            "no tengo energía",
            "me siento sin fuerzas",
            "sin ganas de hacer nada",
            "me falta energía",
            "me siento agotado"
        ])
    else:
        # Aplicar plantillas genéricas
        for p in PLANTILLAS:
            variantes.add(p.format(s=texto))

    return variantes

def enriquecer_sinonimos():
    print("🔍 Enriqueciendo base de sinónimos...")
    sinonimos_original = cargar_json(RUTA_SINONIMOS)
    sintomas = extraer_sintomas(RUTA_CASOS)

    enriquecido = dict(sinonimos_original)  # copia base
    contador_nuevos = 0

    for sintoma in sintomas:
        variantes = generar_variantes(sintoma)
        for v in variantes:
            if v not in enriquecido:
                enriquecido[v] = sintoma
                contador_nuevos += 1

    guardar_json(enriquecido, RUTA_SALIDA)
    print(f"✅ Enriquecimiento completado. Se agregaron {contador_nuevos} nuevas frases.")
    print(f"📄 Archivo generado: {RUTA_SALIDA}")

# === EJECUCIÓN PRINCIPAL ===
if __name__ == "__main__":
    enriquecer_sinonimos()
