import json
import os
import unicodedata
import re
from difflib import get_close_matches, SequenceMatcher

# === CONFIGURACIÓN ===
_RUTA_CASOS = os.path.join("base_conocimiento", "casos.json")
_RUTA_SINONIMOS = os.path.join("base_conocimiento", "sinonimos_ontologia_enriquecido.json")
_RUTA_SINONIMOS_BACKUP = os.path.join("base_conocimiento", "sinonimos_ontologia.json")
_DEFAULT_THRESHOLD = 0.65  # similitud mínima aceptada


# === FUNCIÓN DE CARGA DE SINÓNIMOS ===
def cargar_sinonimos():
    """
    Carga los sinónimos desde los archivos enriquecido y respaldo.
    Si ambos existen, los fusiona (el enriquecido tiene prioridad).
    """
    archivos = [_RUTA_SINONIMOS_BACKUP, _RUTA_SINONIMOS]
    sinonimos_final = {}
    cargados = []

    for ruta in archivos:
        if os.path.exists(ruta):
            try:
                with open(ruta, "r", encoding="utf-8") as f:
                    data = json.load(f)
                sinonimos_final.update(data)
                cargados.append(f"{ruta} ({len(data)} entradas)")
            except Exception as e:
                print(f"❌ Error al cargar {ruta}: {e}")

    if not cargados:
        print("⚠️ No se encontró ningún archivo de sinónimos.")
        return {}

    print(f"✅ Sinónimos cargados y fusionados desde:\n   " + "\n   ".join(cargados))
    print(f"📚 Total combinados: {len(sinonimos_final)} entradas únicas")
    return sinonimos_final


# === CARGAR SINÓNIMOS AL INICIO ===
SINONIMOS = cargar_sinonimos()


# === UTILIDADES ===
def preprocesar_texto(texto: str) -> str:
    """Convierte texto a minúsculas y elimina acentos."""
    texto = texto.lower()
    texto = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )
    return texto.strip()


def normalizar_sinonimos(frase: str) -> str:
    """Devuelve la versión canónica si coincide parcial o totalmente con un sinónimo."""
    frase_norm = preprocesar_texto(frase)
    for clave, canonico in SINONIMOS.items():
        palabras_clave = clave.split()
        if all(p in frase_norm for p in palabras_clave):
            return canonico
    return frase_norm


def similitud_lexica(a: str, b: str) -> float:
    """Similitud básica entre dos textos (por caracteres)."""
    return SequenceMatcher(None, a, b).ratio()


def similitud_combinada(a: str, b: str) -> float:
    """Similitud combinando palabras y letras."""
    a_norm, b_norm = preprocesar_texto(a), preprocesar_texto(b)
    palabras_a = set(a_norm.split())
    palabras_b = set(b_norm.split())

    interseccion = len(palabras_a & palabras_b)
    union = len(palabras_a | palabras_b)
    sim_palabras = interseccion / union if union > 0 else 0
    sim_caracteres = similitud_lexica(a_norm, b_norm)

    return (sim_palabras * 0.7) + (sim_caracteres * 0.3)


def buscar_sinonimo_difuso(frase: str, lista_claves: list, umbral: float) -> str:
    """Busca coincidencia difusa con sinónimos (por caracteres)."""
    match = get_close_matches(frase, lista_claves, n=1, cutoff=umbral)
    return match[0] if match else None


def es_coincidencia_valida(frase_usuario: str, sintoma: str, similitud: float) -> bool:
    """
    Evalúa si una coincidencia semántica tiene sentido lógico o emocional.
    Evita emparejamientos absurdos.
    """
    if similitud < 0.6:
        return False

    PALABRAS_EMOCION = [
        "ansiedad", "depres", "miedo", "fobia", "tristeza", "culpa",
        "enojo", "ira", "feliz", "preocup", "estres", "insomnio",
        "energ", "soledad", "aislamiento", "apatia", "autolesion",
        "sueño", "aliment", "fatiga", "animo", "sexual", "afecto",
        "placer", "vergüenza", "panico", "temor", "emocion", "angustia"
    ]

    frase_usuario = frase_usuario.lower()
    sintoma = sintoma.lower() if sintoma else ""

    if any(p in frase_usuario for p in PALABRAS_EMOCION) or any(p in sintoma for p in PALABRAS_EMOCION):
        return True

    return False


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


# === DETECCIÓN DE RELACIONES SEMÁNTICAS ===
def detectar_relacion(frase: str):
    """Detecta relaciones semánticas tipo 'X a Y', 'X con Y', etc."""
    patrones = [
        (r"(.+?)\s+a\s+(.+)", "direccion"),
        (r"(.+?)\s+con\s+(.+)", "interaccion"),
        (r"(.+?)\s+por\s+(.+)", "causa"),
        (r"(.+?)\s+hacia\s+(.+)", "actitud")
    ]

    relaciones = []
    for patron, tipo in patrones:
        m = re.search(patron, frase)
        if m:
            x, y = m.groups()
            relaciones.append((x.strip(), tipo, y.strip()))
    return relaciones


# === FUNCIÓN PRINCIPAL ===
def buscar_equivalente_semantico(frase: str, umbral: float = _DEFAULT_THRESHOLD):
    """
    Busca coincidencias entre la frase del usuario y los síntomas base.
    Devuelve lista de (frase_usuario, sintoma_detectado, similitud).
    """

    EXPRESIONES_BIENESTAR = [
        "estoy bien", "me siento bien", "todo bien", "tranquilo",
        "feliz", "contento", "todo normal", "sin problemas",
        "no me pasa nada", "me va bien", "todo en orden", "normal",
        "no tengo problemas", "no tengo ningun problema",
        "no me siento mal", "no tengo nada", "no estoy triste", "no estoy mal",
        "todo está bien", "todo esta bien", "me encuentro bien"
    ]

    frase_norm = preprocesar_texto(frase)
    if any(exp in frase_norm for exp in EXPRESIONES_BIENESTAR):
        print(f"[SEMANTIC LOG] Frase de bienestar detectada: '{frase}' → sin síntomas relevantes.")
        return []

    sintomas_base = cargar_sintomas_desde_casos()
    if not sintomas_base:
        return []

    lista_claves = list(SINONIMOS.keys())
    partes = [p.strip() for p in re.split(r"[,.]", frase) if p.strip()]
    coincidencias = []

    for parte in partes:
        parte_norm = preprocesar_texto(parte)

        # Exacta/parcial
        canonico = normalizar_sinonimos(parte_norm)
        if canonico != parte_norm:
            print(f"[SEMANTIC LOG] Exacto/parcial: '{parte}' → '{canonico}'")
            coincidencias.append((parte, canonico, 1.0))
            continue

        # Relacional
        relaciones = detectar_relacion(parte_norm)
        if relaciones:
            for x, tipo, y in relaciones:
                x_norm = normalizar_sinonimos(x)
                y_norm = normalizar_sinonimos(y)
                print(f"[SEMANTIC LOG] Relacional: '{x}' ({tipo}) '{y}'")
                coincidencias.append((parte, f"{x_norm} [{tipo}] {y_norm}", 0.9))
            continue

        # Difusa
        difuso = buscar_sinonimo_difuso(parte_norm, lista_claves, umbral)
        if difuso:
            canonico = SINONIMOS[difuso]
            sim = similitud_combinada(parte_norm, canonico)
            if es_coincidencia_valida(parte_norm, canonico, sim):
                print(f"[SEMANTIC LOG] Difuso válido: '{parte}' ≈ '{canonico}' ({sim:.2f})")
                coincidencias.append((parte, canonico, sim))
            else:
                print(f"[SEMANTIC LOG] ❌ Difuso descartado: '{parte}' ≠ '{canonico}' ({sim:.2f})")
            continue

        # Semántica general
        mejor_sintoma, mejor_sim = None, 0.0
        for sintoma in sintomas_base:
            sim = similitud_combinada(parte_norm, sintoma)
            if sim > mejor_sim:
                mejor_sintoma, mejor_sim = sintoma, sim

        if es_coincidencia_valida(parte_norm, mejor_sintoma, mejor_sim):
            print(f"[SEMANTIC LOG] Coincidencia semántica: '{parte}' → '{mejor_sintoma}' ({mejor_sim:.2f})")
            coincidencias.append((parte, mejor_sintoma, mejor_sim))
        else:
            print(f"[SEMANTIC LOG] ❌ Coincidencia descartada: '{parte}' ≠ '{mejor_sintoma}' ({mejor_sim:.2f})")

    # --- Limpieza final ---
    coincidencias = [c for c in coincidencias if c[1] is not None]
    if not coincidencias:
        print("[SEMANTIC LOG] ⚠️ No se detectaron coincidencias válidas.")

    return coincidencias
