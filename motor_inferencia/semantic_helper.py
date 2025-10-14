# motor_inferencia/semantic_helper.py
import os
import numpy as np
from sentence_transformers import SentenceTransformer, util

# === CONFIGURACIÓN ===
# Modelo español liviano entrenado para similitud de oraciones
# (descarga automática la primera vez)
_MODEL_NAME = "hiiamsid/sentence_similarity_spanish_es"
_SIM_THRESHOLD = 0.75  # similitud mínima aceptada

# === CARGA PERSISTENTE ===
_model = None

def cargar_modelo():
    """Carga el modelo semántico solo una vez."""
    global _model
    if _model is None:
        print("🧠 Cargando modelo semántico español...")
        _model = SentenceTransformer(_MODEL_NAME)
    return _model


def similitud_semantica(texto1: str, texto2: str) -> float:
    """Devuelve la similitud semántica entre dos frases (0 a 1)."""
    model = cargar_modelo()
    emb1 = model.encode(texto1, convert_to_tensor=True)
    emb2 = model.encode(texto2, convert_to_tensor=True)
    sim = util.cos_sim(emb1, emb2).item()
    return float(sim)


def buscar_equivalente_semantico(frase: str, lista_sintomas: list, umbral: float = _SIM_THRESHOLD):
    """
    Busca el síntoma más semánticamente parecido a una frase.
    Devuelve (síntoma_encontrado, similitud) o (None, 0) si no hay coincidencia.
    """
    model = cargar_modelo()
    frase_emb = model.encode(frase, convert_to_tensor=True)
    sintomas_emb = model.encode(lista_sintomas, convert_to_tensor=True)
    similitudes = util.cos_sim(frase_emb, sintomas_emb)[0].cpu().numpy()

    idx_max = np.argmax(similitudes)
    sim_max = similitudes[idx_max]
    if sim_max >= umbral:
        return lista_sintomas[idx_max], float(sim_max)
    else:
        return None, float(sim_max)
