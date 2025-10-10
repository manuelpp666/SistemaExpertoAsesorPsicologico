import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import re
from base_conocimiento.almacenamiento import cargar_base, guardar_base
from base_conocimiento.modelos import Caso
from motor_inferencia.razonador import razonar
from modulo_explicacion.explicacion import ModuloExplicacion

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
        normalizados.append(sinonimos.get(s, s))
    return normalizados

def procesar_sintomas_semi_libre(texto):
    """Procesa texto semi-libre en síntomas normalizados."""
    frases = re.split(r"[.,;]", texto.lower())
    sintomas = []
    sinonimos = cargar_sinonimos()
    for frase in frases:
        frase = frase.strip()
        if not frase or frase in STOPWORDS:
            continue
        sintomas.append(sinonimos.get(frase, frase))
    return list(set(sintomas))

# ===== Interfaz Gráfica =====
class SistemaExpertoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🧠 Sistema Experto de Asesoría Psicológica")
        self.geometry("780x580")
        self.configure(bg="#f0f4f7")
        self.base = cargar_base()

        # Estilos
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TButton", font=("Segoe UI", 12), padding=6, background="#A5D6A7")
        style.map("TButton",
                  background=[("active", "#81C784")],
                  foreground=[("disabled", "#aaaaaa")])
        style.configure("TLabel", font=("Segoe UI", 12), background="#f0f4f7")
        style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), background="#f0f4f7", foreground="#4E342E")

        self.iniciar_interfaz()

    def limpiar_frame(self):
        for widget in self.winfo_children():
            widget.destroy()

    # ===== Pantalla inicial =====
    def iniciar_interfaz(self):
        self.limpiar_frame()
        frame = tk.Frame(self, bg="#f0f4f7")
        frame.pack(pady=60)

        ttk.Label(frame, text="¿Quién eres?", style="Header.TLabel").pack(pady=10)
        ttk.Button(frame, text="Paciente", width=25, command=self.rol_paciente).pack(pady=5)
        ttk.Button(frame, text="Psicólogo", width=25, command=self.rol_psicologo).pack(pady=5)

    # ===== PACIENTE =====
    def rol_paciente(self):
        self.limpiar_frame()
        ttk.Label(self, text="Describa sus síntomas (use comas, puntos o punto y coma):",
                  font=("Segoe UI", 14)).pack(pady=10)

        self.entry_sintomas = ttk.Entry(self, width=90)
        self.entry_sintomas.pack(pady=5)

        ttk.Button(self, text="Examinar", command=self.consultar_sintomas).pack(pady=10)
        self.text_resultado = scrolledtext.ScrolledText(self, width=90, height=20, font=("Segoe UI", 11),
                                                        bg="#FFF3E0", fg="#3E2723")
        self.text_resultado.pack(pady=10)
        ttk.Button(self, text="Volver", command=self.iniciar_interfaz).pack(pady=5)

    def consultar_sintomas(self):
        texto_usuario = self.entry_sintomas.get().strip()
        sintomas_usuario = procesar_sintomas_semi_libre(texto_usuario)
        self.text_resultado.delete(1.0, tk.END)

        if not sintomas_usuario:
            messagebox.showwarning("⚠️ Advertencia", "Por favor, ingrese al menos un síntoma.")
            return

        # Caso 1: Solo un síntoma → hacer preguntas emergentes
        if len(sintomas_usuario) == 1:
            sintoma = sintomas_usuario[0]
            casos_relacionados = [c for c in self.base.listar_casos() if sintoma in c.sintomas]

            if len(casos_relacionados) > 1:
                messagebox.showinfo(
                    "🤔 Información insuficiente",
                    "Me has dado poca información. Te preguntaré algo para darte una mejor respuesta."
                )

                for caso in casos_relacionados:
                    otros = [s for s in caso.sintomas if s != sintoma]
                    if not otros:
                        continue
                    pregunta = f"¿Tienes también {otros[0]}?"
                    respuesta = messagebox.askyesno("Confirmación", pregunta)
                    if respuesta:
                        return self.mostrar_resultado(caso, sintomas_usuario)
                messagebox.showinfo(
                    "⚠️ Sin coincidencia exacta",
                    "No se pudo determinar un caso específico con la información proporcionada."
                )
                return

        # Caso 2: Varios síntomas → usar razonador
        resultado = razonar(self.base, sintomas_usuario)

        # Manejo flexible del resultado
        if resultado is None:
            self.text_resultado.insert(tk.END, "⚠️ No se encontró un caso similar en la base de conocimiento.")
            return

        if isinstance(resultado, tuple):
            if len(resultado) == 2:
                caso, sim = resultado
            elif len(resultado) > 2:
                caso, sim = resultado[0], resultado[1]
            else:
                messagebox.showerror("❌ Error", f"Resultado inesperado del razonador: {resultado}")
                return
        else:
            messagebox.showerror("❌ Error", f"El razonador devolvió un tipo inesperado: {type(resultado)}")
            return

        self.mostrar_resultado(caso, sintomas_usuario, sim)

    def mostrar_resultado(self, caso, sintomas_usuario, sim=None):
        """Muestra en pantalla los resultados y explicación."""
        if sim is None:
            sim = 1.0  # Para casos confirmados por preguntas

        nivel_confianza = (
            "alta" if sim >= 0.7 else
            "moderada" if sim >= 0.4 else
            "baja"
        )

        posible_causa = getattr(caso, "posible_causa", "No especificada")
        estrategias = getattr(caso, "estrategias", [])
        recomendacion = getattr(caso, "recomendacion_general", "Mantener rutinas saludables")
        autoevals = getattr(caso, "autoevaluaciones_sugeridas", [])
        riesgo = getattr(caso, "riesgo", "no definido")

        texto = f"🩺 Posible causa: {posible_causa}\n"
        texto += f"💡 Estrategias sugeridas: {', '.join(estrategias) if estrategias else 'No especificadas'}\n"
        texto += f"🧘 Recomendación general: {recomendacion}\n"
        texto += f"🧾 Autoevaluaciones sugeridas: {', '.join(autoevals) if autoevals else 'No especificadas'}\n"
        texto += f"🔎 Nivel de riesgo: {riesgo}\n"
        texto += f"📊 Nivel de confianza: {nivel_confianza}\n\n"

        exp = ModuloExplicacion(caso, sim)
        texto += "📖 Explicación:\n" + exp.generar_explicacion(sintomas_usuario)

        posibles = [c for c in self.base.listar_casos() if c.id_caso != caso.id_caso and any(s in c.sintomas for s in sintomas_usuario)]
        if posibles:
            texto += "\n⚠️ También podría estar relacionado con otros casos similares:\n"
            for otro in posibles[:2]:
                texto += f"  - {getattr(otro, 'posible_causa', 'Causa no especificada')}\n"

        self.text_resultado.delete(1.0, tk.END)
        self.text_resultado.insert(tk.END, texto)

    # ===== PSICÓLOGO =====
    def rol_psicologo(self):
        self.limpiar_frame()
        ttk.Label(self, text="Agregar nuevo caso a la base de conocimiento", style="Header.TLabel").pack(pady=10)

        campos = [
            "Síntomas (coma separados)",
            "Posible causa",
            "Estrategias (coma separadas)",
            "Resultado (opcional)",
            "Autoevaluaciones sugeridas (coma separadas, opcional)",
            "Riesgo (bajo/moderado/alto, opcional)",
            "Derivar a (coma separadas, opcional)",
            "Recomendación general"
        ]
        self.entries_ps = []

        for texto in campos:
            ttk.Label(self, text=texto).pack(pady=3)
            entry = ttk.Entry(self, width=90)
            entry.pack(pady=5)
            self.entries_ps.append(entry)

        (
            self.entry_sintomas,
            self.entry_causa,
            self.entry_estrategias,
            self.entry_resultado,
            self.entry_autoevals,
            self.entry_riesgo,
            self.entry_derivar,
            self.entry_recomendacion
        ) = self.entries_ps

        ttk.Button(self, text="Guardar caso", command=self.agregar_caso).pack(pady=10)
        ttk.Button(self, text="Volver", command=self.iniciar_interfaz).pack(pady=5)

    def agregar_caso(self):
        sintomas = normalizar_sintomas(self.entry_sintomas.get().split(","))
        causa = self.entry_causa.get()
        estrategias = [e.strip() for e in self.entry_estrategias.get().split(",") if e.strip()]
        resultado = self.entry_resultado.get() or "No especificado"
        autoevals = [a.strip() for a in self.entry_autoevals.get().split(",") if a.strip()]
        riesgo = self.entry_riesgo.get() or "bajo"
        derivar_a = [d.strip() for d in self.entry_derivar.get().split(",") if d.strip()]
        recomendacion = self.entry_recomendacion.get() or "mantener rutinas saludables"

        nuevo_caso = Caso(
            id_caso=len(self.base.listar_casos()) + 1,
            sintomas=sintomas,
            posible_causa=causa,
            estrategias=estrategias,
            resultado=resultado,
            autoevaluaciones_sugeridas=autoevals,
            riesgo=riesgo,
            derivar_a=derivar_a,
            recomendacion_general=recomendacion
        )

        self.base.agregar_caso(nuevo_caso)
        guardar_base(self.base)
        messagebox.showinfo("✅ Éxito", "Caso agregado correctamente a la base de conocimiento.")
        self.iniciar_interfaz()


# ===== MAIN =====
if __name__ == "__main__":
    app = SistemaExpertoApp()
    app.mainloop()
