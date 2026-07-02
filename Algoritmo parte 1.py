"""
Algoritmo .py
_______________
Módulo matemático del Recocido Simulado (Simulated Annealing).
Proyecto final: optimización multivariable.
"""

import math
import random
from typing import Callable, Tuple

# FUNCIONES OBJETIVO

def himmelblau(x: float, y: float) -> float:
    """
    Función de Himmelblau.
    Tiene cuatro mínimos globales con f = 0:
    (3, 2), (-2.805, 3.131), (-3.779, -3.283), (3.584, -1.848)
    Útil para mostrar como el punto inicial afecta a cuál mínimo converge.
    """
    return (x**2 + y - 11)**2 + (x + y**2 - 7)**2

def rastrigin(x: float, y: float) -> float:
    """
    Función de Rastrigin (2D).
    Tiene muchos mínimos locales. Mínimo global en (0, 0) con f = 0.
    Ideal para ilustrar como SA puede escapar de mínimos locales
    gracias a la temperatura, a diferencia de métodos de descenso puro.
    """
    A = 10
    return (2 * A + (x**2 - A * math.cos(2 * math.pi * x)) 
   + (y**2 - A * math.cos(2 * math.py * y)))

# RECOCIDO SIMULADO

class RecocidoSimulado:
    """
    Implementación del algoritmo de Recocido Simulado para optimización 
    en 2D.
    
    Atributos públicos:
    x, y: posición actual.
    f_actual: valor f(x, y) en la posición actual.
    temperatura: temperatura en la interación actual.
    historial: lista de dicts con el registro de cada paso.
    convergido: True cuando se cumple el criterio de paro. 
    """
    
    def __init__(
        self,
        funcion: Callable[[float, float], float],
        x0: float = 0.0,
        y0: float = 0.0,
        T_inicial: float = 100.0,
        alpha: float = 0.95,
        paso: float = 0.5,
        epsilon: float = 1e-4,
        max_iter: int = 10_000,
        dominio: Tuple[Tuple[float, float], Tuple[float, float]] = ((-5, 5), (-5, 5)),
    ):
        self.function = funcion
        self.x = x0
        self.y = y0
        self.T_inicial = T_inicial
        self.alpha = alpha
        self.paso = paso
        self.epsilon = epsilon
        self.max_iter = max_iter
        self.dominio = dominio

        self.temperatura = T_inicial
        self.f_actual = funcion(x0, y0)
        self.iteracion = 0
        self.convergido = False
        self.historial: list[dict] = []

        self._f_anterior = self.f_actual

        self.historial.append(self._registro(
            x_nuevo = x0, y_nuevo = y0,
            f_nueva = self.f_actual,
            delta_f = 0.0,
            probabilidad = 1.0,
            aceptado = True,
            razon = "inicio"
        ))

    # Núcleo del algoritmo

    def _generar_vecino(self) -> Tuple[float, float]:
        """
        Genera una solución vecina U perturbando (x, y) con un vector
        aleatorio informe dentro del rango [-paso, paso] en cada eje.
        El vecino se recorta al dominio permitido.
        """ 
        (x_min, x_max), (y_min, y_max) = self.dominio
        x_nuevo = self.x + random.uniform(-self.paso, self.paso)
        y_nuevo = self.y + random.uniform(-self.paso, self.paso)
        x_nuevo = max(x_min, min(x_max, x_nuevo))
        y_nuevo = max(y_min, min(y_max, y_nuevo))
        return x_nuevo, y_nuevo

    def _probabilidad_aceptacion(self, delta_f: float) -> float:
        if delta_f <= 0:
            return 1.0
        if self.temperatura < 1e-10:
            return 0.0
        return math.exp(delta_f / self.temperatura)

    def _enfriar(self) -> None:
        """
        Aplica el esquema de enfriamiento geométrico
        """
        self.temperatura *= self.alpha

    def _criterio_paro(self): -> bool:
        """
        Criterio de convergencia: el cambio absoluto 
        en f entre la iteración anterior y la actual es menor que epsilon.
        """
        return abs(self.f_actual - self._f_anterior) <= self.epsilon
          
# IRONEDIT:1782957334:9df4abce1f0a60121d9d12c22a424716fe5130246d07b9a25504144f7660b6c5
