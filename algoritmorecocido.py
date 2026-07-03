from __future__ import annotations
import math, random
from dataclasses import dataclass
from typing import Callable

def himmelblau(x: float, y: float) -> float:
    return (x**2 + y - 11)**2 + (x + y**2 - 7)**2

def rastrigin(x: float, y: float) -> float:
    A = 10
    return 2*A + (x**2 - A*math.cos(2*math.pi*x)) + (y**2 - A*math.cos(2*math.pi*y))

def sphere(x: float, y: float) -> float:
    return x**2 + y**2
FUNCIONES = {'rastrigin': rastrigin, 'himmelblau': himmelblau, 'sphere': sphere}
DOMINIOS = {
    'rastrigin': ((-5.12, 5.12), (-5.12, 5.12)),
    'himmelblau': ((-5.5, 5.5), (-5.5, 5.5)),
    'sphere': ((-5.5, 5.5), (-5.5, 5.5)),
}

@dataclass
class Decision:
    iteracion: int
    previo: tuple[int, int]
    candidato: tuple[int, int]
    actual: tuple[int, int]
    mejor: tuple[int, int]
    x_actual: float
    y_actual: float
    f_actual: float
    f_candidato: float
    f_mejor: float
    delta_e: float
    temperatura_antes: float
    temperatura_despues: float
    probabilidad: float
    aleatorio: float
    aceptado: bool
    razon: str
    convergido: bool
    sin_mejora: int

class RecocidoGrid:
    def __init__(self, funcion_nombre: str, grid_size: int, col_inicial: int, fila_inicial: int,
                 t_inicial: float, t_min: float, alpha: float, epsilon: float,
                 paciencia_sin_mejora: int, max_iter: int):
        if funcion_nombre not in FUNCIONES:
            raise ValueError(f'Función no registrada: {funcion_nombre}')
        self.funcion_nombre = funcion_nombre
        self.funcion: Callable[[float, float], float] = FUNCIONES[funcion_nombre]
        self.dominio = DOMINIOS[funcion_nombre]
        self.grid_size = grid_size
        self.col, self.fila = col_inicial, fila_inicial
        self.f_actual = self.evaluar_celda(self.col, self.fila)
        self.mejor_col, self.mejor_fila = self.col, self.fila
        self.f_mejor = self.f_actual
        self.t_inicial, self.t_min = t_inicial, t_min
        self.temperatura, self.alpha = t_inicial, alpha
        self.epsilon = epsilon
        self.paciencia_sin_mejora = paciencia_sin_mejora
        self.max_iter = max_iter
        self.iteracion = 0
        self.sin_mejora = 0
        self.convergido = False
        self.historial: list[Decision] = []

    def celda_a_xy(self, col: int, fila: int) -> tuple[float, float]:
        (x_min, x_max), (y_min, y_max) = self.dominio
        x = x_min + (col/(self.grid_size-1))*(x_max-x_min)
        y = y_max - (fila/(self.grid_size-1))*(y_max-y_min)
        return x, y

    def evaluar_celda(self, col: int, fila: int) -> float:
        x, y = self.celda_a_xy(col, fila)
        return self.funcion(x, y)

    def probabilidad_aceptacion(self, delta_e: float) -> float:
        if delta_e <= 0:
            return 1.0
        if self.temperatura <= 1e-12:
            return 0.0
        return math.exp(-delta_e/self.temperatura)

    def intentar_movimiento(self, d_col: int, d_fila: int) -> Decision | None:
        if self.convergido:
            return self.historial[-1] if self.historial else None
        candidato_col = max(0, min(self.grid_size-1, self.col+d_col))
        candidato_fila = max(0, min(self.grid_size-1, self.fila+d_fila))
        if candidato_col == self.col and candidato_fila == self.fila:
            return None
        self.iteracion += 1
        previo = (self.col, self.fila)
        temp_antes = self.temperatura
        f_candidato = self.evaluar_celda(candidato_col, candidato_fila)
        delta_e = f_candidato - self.f_actual
        if delta_e <= 0:
            prob, aleatorio, aceptado, razon = 1.0, 0.0, True, 'mejora'
        else:
            prob = self.probabilidad_aceptacion(delta_e)
            aleatorio = random.random()
            aceptado = aleatorio < prob
            razon = 'metropolis' if aceptado else 'rechazo'
        if aceptado:
            self.col, self.fila = candidato_col, candidato_fila
            self.f_actual = f_candidato
        if self.f_actual < self.f_mejor - self.epsilon:
            self.mejor_col, self.mejor_fila = self.col, self.fila
            self.f_mejor = self.f_actual
            self.sin_mejora = 0
        else:
            self.sin_mejora += 1
        self.temperatura *= self.alpha
        if self.temperatura <= self.t_min or self.sin_mejora >= self.paciencia_sin_mejora or self.iteracion >= self.max_iter:
            self.convergido = True
            razon += ' | CONVERGENCIA'
        x, y = self.celda_a_xy(self.col, self.fila)
        d = Decision(self.iteracion, previo, (candidato_col, candidato_fila), (self.col, self.fila),
                     (self.mejor_col, self.mejor_fila), x, y, self.f_actual, f_candidato,
                     self.f_mejor, delta_e, temp_antes, self.temperatura, prob, aleatorio,
                     aceptado, razon, self.convergido, self.sin_mejora)
        self.historial.append(d)
        return d

    def resumen(self) -> dict:
        x, y = self.celda_a_xy(self.mejor_col, self.mejor_fila)
        return {
            'x': x, 'y': y, 'f': self.f_mejor, 'iteraciones': self.iteracion,
            'temperatura': self.temperatura,
            'metropolis': sum(1 for d in self.historial if 'metropolis' in d.razon),
            'rechazos': sum(1 for d in self.historial if 'rechazo' in d.razon),
            'funcion': self.funcion_nombre,
        }
# IRONEDIT:1783043349:805ebb5c885604ec563dd2521f4505a7ecf462ff3c4f8f5b5b8a4a8f4d4e03b0
