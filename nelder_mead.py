#cálulo de movimiento de simplex
#Idea principal: En 2 variables, el simplex es un triángulo con 3 puntos.
# Se ordenan los puntos según f(x,y).
#El peor punto se reemplaza usando reflexión, expansión, contracción o reducción.
from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Callable

from objetivos import FUNCIONES, DOMINIOS


# Un punto es una coordenada (x, y)
Point = tuple[float, float]


@dataclass
class NMRecord:
    """
    Registro de una iteración.
    El juego usa esto para mostrar qué pasó en pantalla.
    """
    iteracion: int
    vertices_antes: list[Point]
    vertices_despues: list[Point]
    f_antes: list[float]
    f_despues: list[float]
    mejor: Point
    bueno: Point
    peor: Point
    centroide: Point
    reflejado: Point | None
    expandido: Point | None
    contraido: Point | None
    operacion: str
    explicacion: str
    simplex_size: float
    f_std: float
    convergido: bool


class NelderMead2D:
    """
    Implementación sencilla de Nelder-Mead para funciones f(x,y).

    Coeficientes usados:
    alpha = 1.0  reflexión
    gamma = 2.0  expansión
    rho   = 0.5  contracción
    sigma = 0.5  reducción
    """

    def __init__(
        self,
        funcion_nombre: str,
        alpha: float = 1.0,
        gamma: float = 2.0,
        rho: float = 0.5,
        sigma: float = 0.5,
        simplex_eps: float = 0.05,
        f_eps: float = 1e-4,
        max_iter: int = 250,
        seed: int | None = None,
    ):
        # Validamos que exista la función elegida.
        if funcion_nombre not in FUNCIONES:
            raise ValueError(f"Función no registrada: {funcion_nombre}")

        # Guardamos la función objetivo y su dominio.
        self.funcion_nombre = funcion_nombre
        self.funcion: Callable[[float, float], float] = FUNCIONES[funcion_nombre]
        self.dominio = DOMINIOS[funcion_nombre]

        # Parámetros clásicos de Nelder-Mead.
        self.alpha = alpha
        self.gamma = gamma
        self.rho = rho
        self.sigma = sigma

        # Criterios de paro.
        self.simplex_eps = simplex_eps
        self.f_eps = f_eps
        self.max_iter = max_iter

        # Estado del algoritmo.
        self.rng = random.Random(seed)
        self.iteracion = 0
        self.convergido = False
        self.historial: list[NMRecord] = []

        # Creamos el triángulo inicial y lo ordenamos.
        self.vertices = self._crear_simplex_inicial()
        self._ordenar()

    # ------------------------------------------------------------
    # Funciones auxiliares pequeñas
    # ------------------------------------------------------------

    def _crear_simplex_inicial(self) -> list[Point]:
        """Crea un triángulo inicial dentro del dominio de la función."""
        (x_min, x_max), (y_min, y_max) = self.dominio

        # Punto central aleatorio.
        cx = self.rng.uniform(x_min * 0.45, x_max * 0.45)
        cy = self.rng.uniform(y_min * 0.45, y_max * 0.45)

        # Tamaño del triángulo según el dominio.
        escala_x = (x_max - x_min) * 0.16
        escala_y = (y_max - y_min) * 0.16

        # Tres puntos = triángulo simplex.
        return [
            self._clip((cx, cy)),
            self._clip((cx + escala_x, cy + escala_y * 0.12)),
            self._clip((cx + escala_x * 0.28, cy + escala_y)),
        ]

    def _clip(self, p: Point) -> Point:
        """Evita que un punto salga del dominio permitido."""
        (x_min, x_max), (y_min, y_max) = self.dominio
        x, y = p
        x = max(x_min, min(x_max, x))
        y = max(y_min, min(y_max, y))
        return x, y

    def f(self, p: Point) -> float:
        """Evalúa la función objetivo en un punto."""
        return self.funcion(p[0], p[1])

    def _ordenar(self) -> None:
        """Ordena los vértices de menor a mayor valor de f."""
        self.vertices.sort(key=self.f)

    @staticmethod
    def _sumar(a: Point, b: Point) -> Point:
        return a[0] + b[0], a[1] + b[1]

    @staticmethod
    def _restar(a: Point, b: Point) -> Point:
        return a[0] - b[0], a[1] - b[1]
    @staticmethod
    def _multiplicar(k: float, p: Point) -> Point:
        return k * p[0], k * p[1]

    @staticmethod
    def _distancia(a: Point, b: Point) -> float:
        return math.hypot(a[0] - b[0], a[1] - b[1])

    def _centroide(self) -> Point:
        """Centroide usando los dos mejores puntos, sin usar el peor."""
        mejor, bueno, _peor = self.vertices
        return ((mejor[0] + bueno[0]) / 2, (mejor[1] + bueno[1]) / 2)

    def simplex_size(self) -> float:
        """Tamaño del triángulo: distancia máxima entre sus vértices."""
        a, b, c = self.vertices
        return max(
            self._distancia(a, b),
            self._distancia(a, c),
            self._distancia(b, c),
        )

    def f_std(self) -> float:
        """Mide qué tan diferentes son los valores de f en los vértices."""
        valores = [self.f(v) for v in self.vertices]
        media = sum(valores) / len(valores)
        return math.sqrt(sum((v - media) ** 2 for v in valores) / len(valores))

    def _reducir(self, mejor: Point) -> None:
        """Mueve todos los puntos hacia el mejor punto."""
        nuevos_vertices = [mejor]

        for v in self.vertices[1:]:
            # nuevo = mejor + sigma * (v - mejor)
            direccion = self._restar(v, mejor)
            nuevo = self._sumar(mejor, self._multiplicar(self.sigma, direccion))
            nuevos_vertices.append(self._clip(nuevo))

        self.vertices = nuevos_vertices

#paso de nelder mead
    def step(self) -> NMRecord:
        """Ejecuta una iteración completa del algoritmo."""
        if self.convergido and self.historial:
            return self.historial[-1]

        # 1 Ordenar los vértices por su valor de f.
        self._ordenar()
        vertices_antes = list(self.vertices)
        f_antes = [self.f(v) for v in vertices_antes]

        mejor, bueno, peor = self.vertices
        f_mejor = self.f(mejor)
        f_bueno = self.f(bueno)
        f_peor = self.f(peor)

        # 2 Calcular centroide sin el peor punto.
        centroide = self._centroide()

        # Variables para guardar puntos candidatos.
        reflejado = None
        expandido = None
        contraido = None

        # 3 Reflexión: mover el peor al otro lado del centroide.
        direccion = self._restar(centroide, peor)
        reflejado = self._clip(
            self._sumar(centroide, self._multiplicar(self.alpha, direccion))
        )
        f_reflejado = self.f(reflejado)

        # 4  Decidir qué operación se acepta.
        if f_mejor <= f_reflejado < f_bueno:
            # Caso normal: la reflexión mejora al peor.
            self.vertices[-1] = reflejado
            operacion = "reflexión"
            explicacion = "El reflejado mejora al peor, entonces reemplaza al peor punto."

        elif f_reflejado < f_mejor:
            # Si la reflexión es muy buena, probamos expansión.
            direccion_exp = self._restar(reflejado, centroide)
            expandido = self._clip(
                self._sumar(centroide, self._multiplicar(self.gamma, direccion_exp))
            )

            if self.f(expandido) < f_reflejado:
                self.vertices[-1] = expandido
                operacion = "expansión"
                explicacion = "La reflexión fue muy buena, se expandió y mejoró todavía más."
            else:
                self.vertices[-1] = reflejado
                operacion = "reflexión"
                explicacion = "La expansión no mejoró, por eso se acepta solo la reflexión."

        else:
            # Si la reflexión no conviene, intentamos contracción.
            if f_reflejado < f_peor:
                # Contracción externa: entre centroide y reflejado.
                direccion_con = self._restar(reflejado, centroide)
                contraido = self._clip(
                    self._sumar(centroide, self._multiplicar(self.rho, direccion_con))
                )

                if self.f(contraido) <= f_reflejado:
                    self.vertices[-1] = contraido
                    operacion = "contracción externa"
                    explicacion = "La reflexión no bastó; se aceptó una contracción externa."
                else:
                    self._reducir(mejor)
                    operacion = "reducción"
                    explicacion = "La contracción externa no mejoró; se reduce todo hacia el mejor."
            else:
                # Contracción interna: entre centroide y peor.
                direccion_con = self._restar(peor, centroide)
                contraido = self._clip(
                    self._sumar(centroide, self._multiplicar(self.rho, direccion_con))
                )

                if self.f(contraido) < f_peor:
                    self.vertices[-1] = contraido
                    operacion = "contracción interna"
                    explicacion = "La reflexión fue mala; se contrajo hacia dentro y mejoró al peor."
                else:
                    self._reducir(mejor)
                    operacion = "reducción"
                    explicacion = "Nada mejoró; el simplex se encoge hacia el mejor punto."

        # 5. Actualizar datos después del movimiento.
        self.iteracion += 1
        self._ordenar()

        f_despues = [self.f(v) for v in self.vertices]
        size = self.simplex_size()
        fstd = self.f_std()

        # 6. Criterio de paro matemático.
        if size <= self.simplex_eps or fstd <= self.f_eps or self.iteracion >= self.max_iter:
            self.convergido = True

        # 7. Guardar registro para que el juego lo muestre.
        record = NMRecord(
            iteracion=self.iteracion,
            vertices_antes=vertices_antes,
            vertices_despues=list(self.vertices),
            f_antes=f_antes,
            f_despues=f_despues,
            mejor=self.vertices[0],
            bueno=self.vertices[1],
            peor=self.vertices[2],
            centroide=centroide,
            reflejado=reflejado,
            expandido=expandido,
            contraido=contraido,
            operacion=operacion,
            explicacion=explicacion,
            simplex_size=size,
            f_std=fstd,
            convergido=self.convergido,
        )

        self.historial.append(record)
        return record


    def predecir_operacion(self) -> str:
        """
        Predice qué operación haría Nelder-Mead en el siguiente paso.

        Se usa en el modo reto:
        - el jugador elige una operación;
        - el juego calcula cuál era la correcta;
        - luego ejecuta el paso real.

        Para no modificar el algoritmo original, se crea una copia sencilla
        del estado actual y se ejecuta step() solo en esa copia.
        """
        copia = NelderMead2D(
            funcion_nombre=self.funcion_nombre,
            alpha=self.alpha,
            gamma=self.gamma,
            rho=self.rho,
            sigma=self.sigma,
            simplex_eps=self.simplex_eps,
            f_eps=self.f_eps,
            max_iter=self.max_iter,
            seed=0,
        )

        # Copiamos el estado actual.
        copia.vertices = list(self.vertices)
        copia.iteracion = self.iteracion
        copia.convergido = self.convergido
        copia.historial = []

        # El step de la copia nos dice qué operación tocaría.
        registro = copia.step()
        return registro.operacion

    def resumen(self) -> dict:
        """Devuelve el resultado final para la pantalla de cierre."""
        self._ordenar()
        mejor = self.vertices[0]

        return {
            "funcion": self.funcion_nombre,
            "x": mejor[0],
            "y": mejor[1],
            "f": self.f(mejor),
            "iteraciones": self.iteracion,
            "simplex_size": self.simplex_size(),
            "f_std": self.f_std(),
            "convergido": self.convergido,
            "reflexiones": sum(1 for h in self.historial if h.operacion == "reflexión"),
            "expansiones": sum(1 for h in self.historial if h.operacion == "expansión"),
            "contracciones": sum(1 for h in self.historial if "contracción" in h.operacion),
            "reducciones": sum(1 for h in self.historial if h.operacion == "reducción"),
        }
# IRONEDIT:1783469747:ec8df7b2c06a9d10f01a13ab1d0a8172ce831ccc5d39e69cdf0f2b4a8d745e12
