import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import re
from difflib import SequenceMatcher

from base_conocimiento.almacenamiento import cargar_base, guardar_base
from base_conocimiento.modelos import Caso
from motor_inferencia.razonador import razonar
from modulo_explicacion.explicacion import ModuloExplicacion
from motor_inferencia.semantic_helper import buscar_equivalente_semantico

# ===== CONFIGURACIÓN GLOBAL =====
RUTA_SINONIMOS = "base_conocimiento/sinonimos_ontologia_enriquecido.json"
STOPWORDS = {"tengo", "me", "siento", "y", "a veces", "muy", "con", "el", "la", "los", "las", "de", "en", "por"}


# ===== UTILIDADES DE PROCESAMIENTO =====
def cargar_sinonimos(ruta=RUTA_SINONIMOS):
    """Carga el archivo JSON de sinónimos."""
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def buscar_sinonimo_aproximado(frase, sinonimos, umbral=0.7):
    """
    Busca el sinónimo más parecido a la frase dada.
    Si la similitud supera el umbral, devuelve el valor del sinónimo.
    En caso contrario, devuelve la frase original.
    """
    frase = frase.lower().strip()
    mejor, sim_mejor = frase, 0
    for key, val in sinonimos.items():
        sim = SequenceMatcher(None, frase, key.lower()).ratio()
        if sim > sim_mejor and sim >= umbral:
            mejor, sim_mejor = val, sim
    return mejor


def normalizar_sintomas(sintomas):
    """Normaliza una lista de síntomas usando el diccionario de sinónimos."""
    sinonimos = cargar_sinonimos()
    return [sinonimos.get(s.strip().lower(), s.strip().lower()) for s in sintomas if s.strip()]


def procesar_sintomas_semi_libre(texto):
    frases = re.split(r"[.,;]", texto.lower())
    sinonimos = cargar_sinonimos()
    sintomas = []
    base_sintomas = list(sinonimos.values())  # para comparación semántica

    for frase in frases:
        frase = frase.strip()
        if not frase or frase in STOPWORDS:
            continue

        # 1️⃣ Exacta
        if frase in sinonimos:
            sintomas.append(sinonimos[frase])
            continue

        # 2️⃣ Difusa (ya la tienes con buscar_sinonimo_aproximado)
        aproximado = buscar_sinonimo_aproximado(frase, sinonimos, umbral=0.7)
        if aproximado != frase:
            sintomas.append(aproximado)
            continue

        # 3️⃣ Semántica
        encontrado, sim = buscar_equivalente_semantico(frase, base_sintomas)
        if encontrado:
            print(f"🔍 Coincidencia semántica: '{frase}' ≈ '{encontrado}' ({sim:.2f})")
            sintomas.append(encontrado)
        else:
            sintomas.append(frase)  # mantener texto original

    return list(set(sintomas))


# ===== INTERFAZ PRINCIPAL =====
class SistemaExpertoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🧠 Asesor Psicológico Inteligente")
        self.minsize(900, 600)
        self.configure(bg="#F9FAFB")
        self.resizable(False, False)
        self.base = cargar_base()

        # ===== Estilos Modernos =====
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure("TButton",
                        font=("Segoe UI", 12, "bold"),
                        foreground="white",
                        background="#3B82F6",
                        borderwidth=0,
                        padding=(10, 6))
        style.map("TButton", background=[("active", "#2563EB")])

        style.configure("TLabel", font=("Segoe UI", 12), background="#F9FAFB", foreground="#1F2937")
        style.configure("Header.TLabel",
                        font=("Segoe UI", 18, "bold"),
                        background="#F9FAFB",
                        foreground="#111827")

        style.configure("TEntry", font=("Segoe UI", 11), padding=6)
        style.configure("TFrame", background="#F9FAFB")

        self.iniciar_interfaz()

    def limpiar_frame(self):
        """Elimina widgets actuales de la ventana."""
        for widget in self.winfo_children():
            widget.destroy()

    # ===== PANTALLA INICIAL =====
    def iniciar_interfaz(self):
        self.limpiar_frame()

        frame = ttk.Frame(self)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        ttk.Label(frame, text="🧠 Sistema Experto de Asesoría Psicológica", style="Header.TLabel").pack(pady=(0, 20))
        ttk.Label(frame, text="Selecciona tu rol para continuar:", font=("Segoe UI", 13)).pack(pady=(0, 10))

        ttk.Button(frame, text="Soy Paciente", width=25, command=self.rol_paciente).pack(pady=5)
        ttk.Button(frame, text="Soy Psicólogo", width=25, command=self.rol_psicologo).pack(pady=5)

    # ===== PACIENTE =====
    def rol_paciente(self):
        self.limpiar_frame()

        # --- Contenedor principal ---
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True, pady=20)

        # ===== SECCIÓN SUPERIOR =====
        top_frame = ttk.Frame(container)
        top_frame.pack(pady=(10, 10))

        ttk.Label(
            top_frame,
            text="Describa sus síntomas (use comas, puntos o punto y coma):",
            style="Header.TLabel"
        ).pack(pady=(0, 10))

        self.entry_sintomas = ttk.Entry(top_frame, width=80)
        self.entry_sintomas.pack(pady=(0, 10))

        ttk.Button(top_frame, text="Analizar", command=self.consultar_sintomas).pack(pady=(0, 15))

        # ===== SECCIÓN MEDIA =====
        middle_frame = ttk.Frame(container)
        middle_frame.pack(fill="both", expand=True, padx=20)

        self.text_resultado = scrolledtext.ScrolledText(
            middle_frame,
            width=95,
            height=18,
            font=("Segoe UI", 11),
            bg="#F3F4F6",
            fg="#111827",
            wrap="word",
            relief="flat",
            borderwidth=1
        )
        self.text_resultado.pack(fill="both", expand=True, pady=(0, 10))

        # ===== SECCIÓN INFERIOR =====
        bottom_frame = ttk.Frame(container)
        bottom_frame.pack(pady=(5, 15))

        ttk.Button(
            bottom_frame,
            text="⬅ Volver",
            command=self.iniciar_interfaz
        ).pack(ipadx=12, ipady=6)

    def consultar_sintomas(self):
        """Analiza los síntomas ingresados por el paciente."""
        texto_usuario = self.entry_sintomas.get().strip()
        sintomas_usuario = procesar_sintomas_semi_libre(texto_usuario)
        self.text_resultado.delete(1.0, tk.END)

        if not sintomas_usuario:
            messagebox.showwarning("Advertencia", "Por favor, ingrese al menos un síntoma.")
            return

        if len(sintomas_usuario) == 1:
            sintoma = sintomas_usuario[0]
            casos_relacionados = [c for c in self.base.listar_casos() if sintoma in c.sintomas]

            if len(casos_relacionados) > 1:
                messagebox.showinfo(
                    "Información adicional requerida",
                    "Te haré unas preguntas para entender mejor tu situación."
                )

                for caso in casos_relacionados:
                    otros = [s for s in caso.sintomas if s != sintoma]
                    if not otros:
                        continue
                    pregunta = f"¿También presentas {otros[0]}?"
                    if messagebox.askyesno("Confirmación", pregunta):
                        return self.mostrar_resultado(caso, sintomas_usuario)
                messagebox.showinfo(
                    "Sin coincidencia clara",
                    "No se pudo determinar un caso específico con la información proporcionada."
                )
                return

        resultado = razonar(self.base, sintomas_usuario)

        if resultado is None:
            self.text_resultado.insert(tk.END, "⚠️ No se encontró un caso similar en la base de conocimiento.")
            return

        if isinstance(resultado, tuple) and len(resultado) >= 2:
            caso, sim = resultado[0], resultado[1]
            self.mostrar_resultado(caso, sintomas_usuario, sim)
        else:
            messagebox.showerror("Error", "El razonador devolvió un resultado inesperado.")

    def mostrar_resultado(self, caso, sintomas_usuario, sim=None):
        """Muestra el caso más similar y su explicación."""
        sim = sim or 1.0
        nivel_confianza = "alta" if sim >= 0.7 else "moderada" if sim >= 0.4 else "baja"

        texto = (
            f"🩺 Posible causa: {getattr(caso, 'posible_causa', 'No especificada')}\n"
            f"💡 Estrategias sugeridas: {', '.join(getattr(caso, 'estrategias', [])) or 'No especificadas'}\n"
            f"🧘 Recomendación general: {getattr(caso, 'recomendacion_general', 'Mantener rutinas saludables')}\n"
            f"🧾 Autoevaluaciones sugeridas: {', '.join(getattr(caso, 'autoevaluaciones_sugeridas', [])) or 'No especificadas'}\n"
            f"🔎 Nivel de riesgo: {getattr(caso, 'riesgo', 'no definido')}\n"
            f"📊 Nivel de confianza: {nivel_confianza}\n\n"
        )

        exp = ModuloExplicacion(caso, sim)
        texto += "📖 Explicación:\n" + exp.generar_explicacion(sintomas_usuario)

        posibles = [
            c for c in self.base.listar_casos()
            if c.id_caso != caso.id_caso and any(s in c.sintomas for s in sintomas_usuario)
        ]
        if posibles:
            texto += "\n\n⚠️ Casos relacionados:\n"
            for otro in posibles[:2]:
                texto += f"  - {getattr(otro, 'posible_causa', 'No especificada')}\n"

        self.text_resultado.delete(1.0, tk.END)
        self.text_resultado.insert(tk.END, texto)

    # ===== PSICÓLOGO =====
    def rol_psicologo(self):
        """Pantalla para que el psicólogo agregue nuevos casos."""
        self.limpiar_frame()
        frame = ttk.Frame(self)
        frame.pack(pady=20)

        ttk.Label(frame, text="🧩 Agregar nuevo caso a la base de conocimiento", style="Header.TLabel").pack(pady=10)

        campos = [
            "Síntomas (coma separados)",
            "Posible causa",
            "Estrategias (coma separadas)",
            "Resultado (opcional)",
            "Autoevaluaciones sugeridas (opcional)",
            "Riesgo (bajo/moderado/alto)",
            "Derivar a (opcional)",
            "Recomendación general"
        ]
        self.entries_ps = []

        for texto in campos:
            ttk.Label(frame, text=texto).pack(pady=(8, 2))
            entry = ttk.Entry(frame, width=80)
            entry.pack(pady=3)
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

        ttk.Button(frame, text="💾 Guardar caso", command=self.agregar_caso).pack(pady=(15, 8))
        ttk.Button(frame, text="⬅ Volver", command=self.iniciar_interfaz).pack()

    def agregar_caso(self):
        """Agrega un nuevo caso a la base de conocimiento."""
        sintomas = normalizar_sintomas(self.entry_sintomas.get().split(","))
        causa = self.entry_causa.get()
        estrategias = [e.strip() for e in self.entry_estrategias.get().split(",") if e.strip()]
        resultado = self.entry_resultado.get() or "No especificado"
        autoevals = [a.strip() for a in self.entry_autoevals.get().split(",") if a.strip()]
        riesgo = self.entry_riesgo.get() or "bajo"
        derivar_a = [d.strip() for d in self.entry_derivar.get().split(",") if d.strip()]
        recomendacion = self.entry_recomendacion.get() or "Mantener rutinas saludables"

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
        messagebox.showinfo("✅ Éxito", "Caso agregado correctamente.")
        self.iniciar_interfaz()


# ===== EJECUCIÓN =====
if __name__ == "__main__":
    app = SistemaExpertoApp()
    app.mainloop()
