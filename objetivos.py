#funciones objetivo para el juego 
#cambiar función sin cambiar la lógica de nelder
from __future__ import annotations
import math


def sphere(x: float, y: float) -> float:
    """Sphere: f(x,y)=x²+y². Un mínimo suave en (0,0)."""
    return x*x + y*y


def himmelblau(x: float, y: float) -> float:
    """Himmelblau: varios mínimos globales."""
    return (x*x + y - 11)**2 + (x + y*y - 7)**2


def rastrigin(x: float, y: float) -> float:
    """Rastrigin 2D: muchos mínimos locales."""
    A = 10
    return 2*A + (x*x - A*math.cos(2*math.pi*x)) + (y*y - A*math.cos(2*math.pi*y))


def rosenbrock(x: float, y: float) -> float:
    """Rosenbrock 2D: valle curvo y estrecho."""
    return 100*(y - x*x)**2 + (1 - x)**2


FUNCIONES = {
    'himmelblau': himmelblau,
    'rosenbrock': rosenbrock,
    'rastrigin': rastrigin,
    'sphere': sphere,
}

DOMINIOS = {
    'himmelblau': ((-5.5, 5.5), (-5.5, 5.5)),
    'rosenbrock': ((-2.2, 2.2), (-1.2, 3.2)),
    'rastrigin': ((-5.12, 5.12), (-5.12, 5.12)),
    'sphere': ((-5.5, 5.5), (-5.5, 5.5)),
}

DESCRIPCIONES = {
    'himmelblau': 'Cuatro valles fríos: el punto inicial importa.',
    'rosenbrock': 'Valle curvo y estrecho: ideal para Nelder-Mead.',
    'rastrigin': 'Muchos mínimos locales: terreno engañoso.',
    'sphere': 'Un solo mínimo suave: caso fácil de prueba.',
}
# IRONEDIT:1783473187:e7c8be82d317d4456a9e167267c1e0ca55572ae2dc0fec10464145788b254352
