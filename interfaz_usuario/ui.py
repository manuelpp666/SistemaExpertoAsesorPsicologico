import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import re
from base_conocimiento.almacenamiento import cargar_base, guardar_base
from base_conocimiento.modelos import Caso
from motor_inferencia.razonador import razonar
from modulo_explicacion.explicacion import ModuloExplicacion
from modulo_adquisicion.adquisicion import ModuloAdquisicion

# ===== Configuración =====
RUTA_SINONIMOS = "base_conocimiento/sinonimos_ontologia.json"
STOPWORDS = {"tengo", "me", "siento", "y", "a veces", "muy", "con", "el", "la", "los", "las"}

def cargar_sinonimos(ruta=RUTA_SINONIMOS):
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def normalizar_sintomas(sintomas):
    sinonimos = cargar_sinonimos()
    normalizados = []
    for s in sintomas:
        s = s.strip().lower()
        if s in sinonimos:
            normalizados.append(sinonimos[s])
        else:
            normalizados.append(s)
    return normalizados

def procesar_sintomas_semi_libre(texto):
    """Procesa texto semi-libre en síntomas normalizados."""
    frases = re.split(r"[.,;]", texto.lower())
    sintomas = []
    sinonimos = cargar_sinonimos()
    for frase in frases:
        palabras = frase.strip().split()
        palabras = [p for p in palabras if p not in STOPWORDS]
        for p in palabras:
            if p in sinonimos:
                sintomas.append(sinonimos[p])
            else:
                sintomas.append(p)
    return list(set(sintomas))

# ===== Interfaz Gráfica =====
class SistemaExpertoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🧠 Sistema Experto de Asesoría Psicológica")
        self.geometry("750x550")
        self.configure(bg="#f0f4f7")
        self.base = cargar_base()

        # Estilo ttk
        style = ttk.Style(self)
        style.configure("TButton", font=("Segoe UI", 12), padding=6)
        style.configure("TLabel", font=("Segoe UI", 12), background="#f0f4f7")
        style.configure("TEntry", font=("Segoe UI", 12))
        style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"))

        self.iniciar_interfaz()

    def iniciar_interfaz(self):
        self.limpiar_frame()
        self.frame_rol = tk.Frame(self, bg="#f0f4f7")
        self.frame_rol.pack(pady=60)

        ttk.Label(self.frame_rol, text="¿Quién eres?", style="Header.TLabel").pack(pady=10)
        ttk.Button(self.frame_rol, text="Paciente", width=25, command=self.rol_paciente).pack(pady=5)
        ttk.Button(self.frame_rol, text="Psicólogo", width=25, command=self.rol_psicologo).pack(pady=5)

    def limpiar_frame(self):
        for widget in self.winfo_children():
            widget.destroy()

    # ===== Paciente =====
    def rol_paciente(self):
        self.limpiar_frame()
        ttk.Label(self, text="Describa sus síntomas (frases cortas, puede usar puntos o punto y coma):",
                  font=("Segoe UI", 14)).pack(pady=10)
        self.entry_sintomas = ttk.Entry(self, width=90)
        self.entry_sintomas.pack(pady=5)

        ttk.Button(self, text="Examinar", command=self.consultar_sintomas).pack(pady=10)
        self.text_resultado = scrolledtext.ScrolledText(self, width=90, height=18, font=("Segoe UI", 11))
        self.text_resultado.pack(pady=10)

        ttk.Button(self, text="Volver", command=self.iniciar_interfaz).pack(pady=5)

    def consultar_sintomas(self):
        texto_usuario = self.entry_sintomas.get()
        sintomas_usuario = procesar_sintomas_semi_libre(texto_usuario)
        recomendacion = razonar(self.base, sintomas_usuario)
        self.text_resultado.delete(1.0, tk.END)

        if recomendacion:
            sim = recomendacion.get("confianza", 0)  # usar 'confianza' en vez de 'similitud'

            # Nivel de confianza descriptivo
            if sim >= 0.7:
                nivel_confianza = "alta"
            elif sim >= 0.4:
                nivel_confianza = "moderada"
            else:
                nivel_confianza = "muy baja"

            # Si la similitud es 0, no hay diagnóstico confiable
            if sim == 0:
                exp = ModuloExplicacion(recomendacion, sim)
                texto = exp.generar_explicacion(sintomas_usuario)
            else:
                texto = f"Diagnóstico sugerido: {recomendacion['diagnostico']}\n"
                texto += f"Estrategias recomendadas: {', '.join(recomendacion['estrategias'])}\n"
                texto += f"Nivel de confianza: {nivel_confianza}\n\n"
                exp = ModuloExplicacion(recomendacion, sim)
                texto += "📖 Explicación:\n" + exp.generar_explicacion(sintomas_usuario)

            self.text_resultado.insert(tk.END, texto)
        else:
            self.text_resultado.insert(tk.END, "⚠️ No se encontró un caso similar.")

    # ===== Psicólogo =====
    def rol_psicologo(self):
        self.limpiar_frame()
        ttk.Label(self, text="Agregar nuevo caso", style="Header.TLabel").pack(pady=10)

        ttk.Label(self, text="Síntomas (coma separados)").pack(pady=3)
        self.entry_sintomas_ps = ttk.Entry(self, width=90)
        self.entry_sintomas_ps.pack(pady=5)

        ttk.Label(self, text="Diagnóstico").pack(pady=3)
        self.entry_diag = ttk.Entry(self, width=90)
        self.entry_diag.pack(pady=5)

        ttk.Label(self, text="Estrategias (coma separadas)").pack(pady=3)
        self.entry_estrategias = ttk.Entry(self, width=90)
        self.entry_estrategias.pack(pady=5)

        ttk.Label(self, text="Resultado (opcional)").pack(pady=3)
        self.entry_resultado = ttk.Entry(self, width=90)
        self.entry_resultado.pack(pady=5)

        ttk.Button(self, text="Agregar caso", command=self.agregar_caso).pack(pady=10)
        ttk.Button(self, text="Volver", command=self.iniciar_interfaz).pack(pady=5)

    def agregar_caso(self):
        sintomas = normalizar_sintomas(self.entry_sintomas_ps.get().split(","))
        diag = self.entry_diag.get()
        est = [e.strip() for e in self.entry_estrategias.get().split(",")]
        res = self.entry_resultado.get() or None

        nuevo_caso = Caso(
            id_caso=len(self.base.listar_casos()) + 1,
            sintomas=sintomas,
            diagnostico=diag,
            estrategias=est,
            resultado=res
        )
        self.base.agregar_caso(nuevo_caso)
        guardar_base(self.base)
        messagebox.showinfo("Éxito", "✅ Caso agregado con éxito.")

# ===== Ventana simple de input =====
def simple_input(prompt):
    win = tk.Toplevel()
    win.title(prompt)
    win.configure(bg="#f0f4f7")
    ttk.Label(win, text=prompt, font=("Segoe UI", 12)).pack(pady=5)
    entry = ttk.Entry(win, width=50)
    entry.pack(pady=5)
    result = []

    def ok():
        result.append(entry.get())
        win.destroy()

    ttk.Button(win, text="Aceptar", command=ok).pack(pady=5)
    win.wait_window()
    return result[0] if result else ""

# ===== Main =====
if __name__ == "__main__":
    app = SistemaExpertoApp()
    app.mainloop()
