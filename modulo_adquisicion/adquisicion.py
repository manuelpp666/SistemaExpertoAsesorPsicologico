from typing import List, Optional
from base_conocimiento.modelos import Caso, BaseDeCasos


class ModuloAdquisicion:
    """
    Módulo encargado de incorporar nuevos casos psicológicos a la base de conocimiento.
    Permite registrar experiencias observadas, retroalimentación del usuario o nuevos patrones clínicos.
    """

    def __init__(self, base_casos: BaseDeCasos, ruta_archivo: str):
        """
        :param base_casos: Instancia de BaseDeCasos.
        :param ruta_archivo: Ruta al archivo JSON donde se almacenan los casos.
        """
        self.base = base_casos
        self.ruta = ruta_archivo

    # ======================================================
    # Método principal: incorporar un nuevo caso
    # ======================================================
    def incorporar_feedback(
        self,
        sintomas: List[str],
        posible_causa: str,
        estrategias: List[str],
        resultado: Optional[str] = None,
        autoevaluaciones_sugeridas: Optional[List[str]] = None,
        riesgo: Optional[str] = "bajo",
        derivar_a: Optional[List[str]] = None,
        recomendacion_general: Optional[str] = None
    ) -> Caso:
        """
        Incorpora un nuevo caso al sistema experto psicológico.

        :param sintomas: Lista de síntomas observados.
        :param posible_causa: Hipótesis o causa probable del cuadro observado.
        :param estrategias: Estrategias o intervenciones aplicadas.
        :param resultado: Resultado o efecto observado tras aplicar las estrategias.
        :param autoevaluaciones_sugeridas: Pruebas o cuestionarios recomendados (ej. GAD-7).
        :param riesgo: Nivel de riesgo estimado ('bajo', 'moderado', 'alto').
        :param derivar_a: Lista de especialistas o servicios sugeridos para derivación.
        :param recomendacion_general: Consejos o pautas generales complementarias.
        :return: Objeto Caso recién agregado.
        """

        # Generar un nuevo ID secuencial basado en los casos existentes
        nuevo_id = max((c.id_caso for c in self.base.listar_casos()), default=0) + 1

        # Crear el nuevo objeto Caso con todos los datos
        nuevo_caso = Caso(
            id_caso=nuevo_id,
            sintomas=sintomas,
            posible_causa=posible_causa,
            estrategias=estrategias,
            resultado=resultado or "No especificado",
            autoevaluaciones_sugeridas=autoevaluaciones_sugeridas or [],
            riesgo=riesgo or "desconocido",
            derivar_a=derivar_a or [],
            recomendacion_general=recomendacion_general or "Sin recomendación adicional."
        )

        # Agregar el caso a la base y guardar los cambios en el archivo JSON
        self.base.agregar_caso(nuevo_caso)
        self.base.guardar_a_json(self.ruta)

        return nuevo_caso
