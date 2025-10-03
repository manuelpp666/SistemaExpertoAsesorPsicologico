import json
from base_conocimiento.almacenamiento import cargar_base, guardar_base
from base_conocimiento.modelos import Caso
from motor_inferencia.razonador import razonar
from modulo_explicacion.explicacion import ModuloExplicacion
from modulo_adquisicion.adquisicion import ModuloAdquisicion

# Ruta del archivo de sinónimos
RUTA_SINONIMOS = "base_conocimiento/sinonimos_ontologia.json"

def cargar_sinonimos(ruta=RUTA_SINONIMOS):
    """Carga el archivo de sinónimos (ontología)."""
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("⚠️ No se encontró el archivo de sinónimos.")
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

def mostrar_casos(base):
    print("\n=== 📚 Casos en la base ===")
    for caso in base.listar_casos():
        print(f"\nID: {caso.id_caso}")
        print(f"  Síntomas: {', '.join(caso.sintomas)}")
        print(f"  Diagnóstico: {caso.diagnostico}")
        print(f"  Estrategias: {', '.join(caso.estrategias)}")
        print(f"  Resultado: {caso.resultado}")
    print("\n============================\n")

def agregar_caso(base):
    print("\n=== ➕ Agregar nuevo caso ===")
    sintomas = input("Ingrese los síntomas separados por coma: ").split(",")
    sintomas = normalizar_sintomas(sintomas)

    diagnostico = input("Ingrese el diagnóstico: ")
    estrategias = input("Ingrese las estrategias (separadas por coma): ").split(",")
    estrategias = [e.strip() for e in estrategias]

    resultado = input("Ingrese el resultado observado (opcional): ")

    nuevo_caso = Caso(
        id_caso=len(base.listar_casos()) + 1,
        sintomas=sintomas,
        diagnostico=diagnostico,
        estrategias=estrategias,
        resultado=resultado if resultado else None
    )

    base.agregar_caso(nuevo_caso)
    guardar_base(base)
    print("✅ Caso agregado y guardado con éxito.\n")

def consultar_sintomas(base):
    print("\n=== 🔍 Consulta de síntomas ===")
    sintomas_usuario = input("Ingrese los síntomas separados por coma: ").split(",")
    sintomas_usuario = normalizar_sintomas(sintomas_usuario)

    recomendacion = razonar(base, sintomas_usuario)

    if recomendacion:
        print("\n=== 🧠 Recomendación del Sistema ===")
        print(f"Diagnóstico sugerido: {recomendacion['diagnostico']}")
        print(f"Estrategias recomendadas: {', '.join(recomendacion['estrategias'])}")
        print(f"Nivel de confianza (similitud): {recomendacion['confianza']:.2f}\n")

        # Explicación
        exp = ModuloExplicacion(recomendacion, recomendacion["confianza"])
        print("📖 Explicación:")
        print(exp.generar_explicacion(sintomas_usuario))
        print("")

        # Feedback (módulo de adquisición)
        opcion = input("¿Quieres guardar este caso con tu feedback? (s/n): ")
        if opcion.lower() == "s":
            diagnostico = input("Diagnóstico confirmado/modificado: ")
            estrategias = input("Estrategias confirmadas/modificadas (coma): ").split(",")
            estrategias = [e.strip() for e in estrategias]
            resultado = input("Resultado esperado/observado: ")

            adquisicion = ModuloAdquisicion(base.listar_casos(), "base_conocimiento/casos.json")
            nuevo_caso = adquisicion.incorporar_feedback(
                sintomas_usuario, diagnostico, estrategias, resultado
            )
            print(f"✅ Nuevo caso agregado con ID {nuevo_caso['id']}.\n")

    else:
        print("⚠️ No se encontró un caso similar.\n")

def main():
    base = cargar_base()

    while True:
        print("=== 🧠 Sistema Experto de Asesoría Psicológica ===")
        print("1. Ver todos los casos")
        print("2. Agregar un nuevo caso")
        print("3. Consultar con síntomas")
        print("4. Salir")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            mostrar_casos(base)
        elif opcion == "2":
            agregar_caso(base)
        elif opcion == "3":
            consultar_sintomas(base)
        elif opcion == "4":
            print("👋 Saliendo del sistema. ¡Hasta pronto!")
            break
        else:
            print("⚠️ Opción inválida. Intente de nuevo.\n")

if __name__ == "__main__":
    main()
