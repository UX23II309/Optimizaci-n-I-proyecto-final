from __future__ import annotations

import math
import random
import pygame
import numpy as np

from config import (
    GRID_SIZE, ISO_W, ISO_H, HEIGHT_SCALE, MAP_CENTER_X, MAP_TOP,
    COLD, ICE, PURPLE, MAGENTA, HOT, LAVA, GOOD, BAD, YELLOW
)
from objetivos import FUNCIONES, DOMINIOS


def mix(a, b, t):
    """Mezcla dos colores."""
    t = max(0.0, min(1.0, t))
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def brighten(c, amount):
    """Aclara un color."""
    return tuple(min(255, v + amount) for v in c)


def darken(c, amount):
    """Oscurece un color."""
    return tuple(max(0, v - amount) for v in c)


def energy_color(v):
    """Convierte un valor normalizado de f(x,y) en color."""
    v = max(0.0, min(1.0, v))

    if v < 0.16:
        return mix((10, 20, 54), (27, 91, 148), v / 0.16)
    if v < 0.32:
        return mix((27, 91, 148), COLD, (v - 0.16) / 0.16)
    if v < 0.50:
        return mix(COLD, PURPLE, (v - 0.32) / 0.18)
    if v < 0.68:
        return mix(PURPLE, MAGENTA, (v - 0.50) / 0.18)
    if v < 0.86:
        return mix(MAGENTA, HOT, (v - 0.68) / 0.18)

    return mix(HOT, LAVA, (v - 0.86) / 0.14)


class World:
    """Mundo visual generado a partir de la función objetivo."""

    def __init__(self, funcion_nombre: str):
        self.funcion_nombre = funcion_nombre
        self.funcion = FUNCIONES[funcion_nombre]
        self.dominio = DOMINIOS[funcion_nombre]

        # Malla de valores para pintar el terreno.
        self.values = self._build_values()
        self.min_value = float(np.min(self.values))
        self.max_value = float(np.max(self.values))

        # Detalles decorativos fijos.
        self.details = self._details()

    def _build_values(self):
        """Evalúa la función en una cuadrícula."""
        arr = np.zeros((GRID_SIZE, GRID_SIZE), dtype=float)

        for fila in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                x, y = self.cell_to_xy(col, fila)
                arr[fila, col] = self.funcion(x, y)

        return arr

    def _details(self):
        """Crea detalles decorativos estables por bloque."""
        rng = random.Random(2036)
        details = {}

        for fila in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                details[(col, fila)] = {
                    "crack": rng.random() < 0.20,
                    "pebble": rng.random() < 0.28,
                    "crystal": rng.random() < 0.12,
                    "pillar": rng.random() < 0.06,
                    "seed": rng.randint(0, 999999),
                }

        return details

    def cell_to_xy(self, col: int, fila: int):
        """Convierte celda del mapa a coordenada matemática."""
        (x_min, x_max), (y_min, y_max) = self.dominio

        x = x_min + (col / (GRID_SIZE - 1)) * (x_max - x_min)
        y = y_max - (fila / (GRID_SIZE - 1)) * (y_max - y_min)

        return x, y

    def normalize(self, value):
        """Normaliza un valor de f(x,y) al rango [0,1]."""
        if abs(self.max_value - self.min_value) < 1e-12:
            return 0.0

        norm = (value - self.min_value) / (self.max_value - self.min_value)
        return max(0.0, min(1.0, norm))

    def height_from_value(self, value):
        """Altura visual del bloque según f(x,y)."""
        norm = self.normalize(value)
        return 8 + int((norm ** 0.72) * HEIGHT_SCALE)

    def height(self, col, fila):
        """Altura del bloque en una celda."""
        value = self.values[fila, col]
        return self.height_from_value(value)

    def iso_base(self, col: float, fila: float):
        """Convierte celda a coordenada isométrica de pantalla."""
        x = MAP_CENTER_X + (col - fila) * ISO_W / 2
        y = MAP_TOP + (col + fila) * ISO_H / 2
        return int(x), int(y)

    def xy_to_cell_float(self, x: float, y: float):
        """Convierte coordenada matemática a celda con decimales."""
        (x_min, x_max), (y_min, y_max) = self.dominio

        col = ((x - x_min) / (x_max - x_min)) * (GRID_SIZE - 1)
        fila = ((y_max - y) / (y_max - y_min)) * (GRID_SIZE - 1)

        return col, fila

    def point_to_screen(self, point):
        """Convierte un punto matemático (x,y) a pantalla."""
        x, y = point
        col, fila = self.xy_to_cell_float(x, y)

        sx, sy = self.iso_base(col, fila)
        value = self.funcion(x, y)
        return sx, sy - self.height_from_value(value) + ISO_H // 2

    def draw_void(self, surface, tick):
        """Dibuja lava y partículas del fondo."""
        for i in range(18):
            y = 440 + i * 13
            color = (115 + i * 5, 38 + i * 2, 28)
            pygame.draw.line(
                surface,
                color,
                (0, y),
                (900, y + int(math.sin(tick * 0.03 + i) * 8)),
                3,
            )

        for i in range(28):
            x = (i * 93 + int(tick * (1 + i % 3))) % 910
            y = 520 + int(math.sin(tick * 0.04 + i) * 34)
            pygame.draw.circle(surface, (255, 126, 52), (x, y), 2 + i % 3)

    def _draw_crystal(self, surface, x, y, color, scale=1):
        """Dibuja un cristal decorativo."""
        pts = [
            (x, y - 15 * scale),
            (x + 7 * scale, y - 4 * scale),
            (x + 4 * scale, y + 9 * scale),
            (x - 5 * scale, y + 10 * scale),
            (x - 8 * scale, y - 4 * scale),
        ]

        pygame.draw.polygon(surface, color, pts)
        pygame.draw.polygon(
            surface,
            brighten(color, 45),
            [
                (x, y - 13 * scale),
                (x + 3 * scale, y - 2 * scale),
                (x, y + 6 * scale),
                (x - 4 * scale, y - 3 * scale),
            ],
        )
        pygame.draw.lines(surface, (220, 255, 255), True, pts, 1)

    def _draw_pillar(self, surface, x, y):
        """Dibuja un pilar pequeño."""
        pygame.draw.rect(surface, (49, 43, 65), (x - 5, y - 28, 10, 28))
        pygame.draw.rect(surface, (87, 74, 111), (x - 7, y - 31, 14, 5))
        pygame.draw.rect(surface, (28, 24, 39), (x - 7, y - 3, 14, 5))

    def _draw_block(self, surface, col, fila, tick):
        """Dibuja un bloque isométrico del terreno."""
        value = self.values[fila, col]
        norm = self.normalize(value)
        base = energy_color(norm)

        h = self.height(col, fila)
        x, y = self.iso_base(col, fila)

        top = (x, y - h)
        right = (x + ISO_W // 2, y + ISO_H // 2 - h)
        bottom = (x, y + ISO_H - h)
        left = (x - ISO_W // 2, y + ISO_H // 2 - h)

        base_right = (x + ISO_W // 2, y + ISO_H // 2)
        base_bottom = (x, y + ISO_H)
        base_left = (x - ISO_W // 2, y + ISO_H // 2)

        # Sombra bajo el bloque.
        shadow = pygame.Surface((ISO_W + 18, ISO_H + 18), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 62), (2, 8, ISO_W + 12, ISO_H + 8))
        surface.blit(shadow, (x - ISO_W // 2 - 8, y - 6))

        # Caras del bloque.
        pygame.draw.polygon(surface, darken(base, 70), [left, bottom, base_bottom, base_left])
        pygame.draw.polygon(surface, darken(base, 42), [right, bottom, base_bottom, base_right])
        pygame.draw.polygon(surface, brighten(base, 16), [top, right, bottom, left])
        pygame.draw.lines(surface, darken(base, 96), True, [top, right, bottom, left], 1)
        pygame.draw.line(surface, brighten(base, 60), top, right, 1)

        # Detalles para que no se vea plano.
        d = self.details[(col, fila)]
        rng = random.Random(d["seed"])
        for _ in range(2):
            ox = rng.randint(-12, 12)
            oy = rng.randint(-2, 10)
            pygame.draw.line(
                surface,
                darken(base, 38),
                (x + ox - 6, y + oy - h + 8),
                (x + ox + 7, y + oy - h + 5),
                1,
            )

        if d["crack"] and norm > 0.42:
            pygame.draw.line(surface, (70, 22, 32), (x - 10, y - h + 7), (x + 9, y - h + 16), 2)

        if d["pebble"]:
            pygame.draw.circle(
                surface,
                darken(base, 55),
                (x + rng.randint(-10, 10), y - h + rng.randint(4, 19)),
                2,
            )

        if norm < 0.10:
            self._draw_crystal(surface, x + 9, y - h + 8, ICE, 1)
        elif d["crystal"] and norm < 0.35:
            self._draw_crystal(surface, x + 9, y - h + 8, COLD, 1)

        if norm > 0.82:
            r = 3 + int(abs(math.sin(tick * 0.08 + col)) * 2)
            pygame.draw.circle(surface, LAVA, (x - 6, y - h + 13), r)
            pygame.draw.circle(surface, HOT, (x - 6, y - h + 13), max(1, r - 2))

        if d["pillar"] and 0.25 < norm < 0.70:
            self._draw_pillar(surface, x - 10, y - h + 12)

    def draw(self, surface, tick):
        """Dibuja todo el mundo."""
        self.draw_void(surface, tick)

        # Orden por profundidad isométrica.
        for suma in range((GRID_SIZE - 1) * 2 + 1):
            for col in range(GRID_SIZE):
                fila = suma - col
                if 0 <= fila < GRID_SIZE:
                    self._draw_block(surface, col, fila, tick)

    def draw_simplex(self, surface, vertices, record, tick):
        """Dibuja el simplex y los puntos importantes del último paso."""
        pts = [self.point_to_screen(v) for v in vertices]

        # Relleno del triángulo.
        layer = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        pygame.draw.polygon(layer, (130, 220, 255, 42), pts)
        pygame.draw.lines(layer, (170, 240, 255, 210), True, pts, 3)
        surface.blit(layer, (0, 0))

        # Datos del último paso.
        if record:
            cx, cy = self.point_to_screen(record.centroide)

            # Centroide.
            pygame.draw.circle(surface, (255, 255, 255), (cx, cy), 8, 2)
            pygame.draw.line(surface, (255, 255, 255), (cx - 10, cy), (cx + 10, cy), 1)
            pygame.draw.line(surface, (255, 255, 255), (cx, cy - 10), (cx, cy + 10), 1)

            # Punto aceptado real.
            aceptado = None
            color_aceptado = YELLOW
            etiqueta = "A"

            if record.operacion == "reflexión":
                aceptado = record.reflejado
                color_aceptado = YELLOW
                etiqueta = "R"
            elif record.operacion == "expansión":
                aceptado = record.expandido
                color_aceptado = GOOD
                etiqueta = "E"
            elif "contracción" in record.operacion:
                aceptado = record.contraido
                color_aceptado = PURPLE
                etiqueta = "K"

            # Reflejado discreto, porque no siempre es el aceptado.
            if record.reflejado:
                rx, ry = self.point_to_screen(record.reflejado)
                pygame.draw.circle(surface, YELLOW, (rx, ry), 5, 1)

            # Aceptado fuerte, para evitar confusión.
            if aceptado:
                ax, ay = self.point_to_screen(aceptado)

                glow = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
                pygame.draw.circle(glow, (*color_aceptado, 70), (ax, ay), 20)
                surface.blit(glow, (0, 0))

                pygame.draw.circle(surface, color_aceptado, (ax, ay), 10, 3)
                pygame.draw.line(surface, color_aceptado, (cx, cy), (ax, ay), 2)

                font = pygame.font.SysFont("consolas", 13, bold=True)
                img = font.render(etiqueta, True, (255, 255, 255))
                surface.blit(img, (ax - img.get_width() // 2, ay - img.get_height() // 2))

            # Si fue reducción, se marca el mejor punto.
            if record.operacion == "reducción":
                bx, by = self.point_to_screen(record.mejor)
                pygame.draw.circle(surface, BAD, (bx, by), 16, 2)

        # Vértices del simplex: mejor, medio y peor.
        vertex_colors = [(94, 234, 255), (255, 215, 105), (255, 105, 155)]

        for i, (x, y) in enumerate(pts):
            pulse = 10 + int(3 * abs(math.sin(tick * 0.09 + i)))
            color = vertex_colors[i]

            pygame.draw.circle(surface, (0, 0, 0), (x + 2, y + 4), pulse + 2)
            pygame.draw.circle(surface, color, (x, y), pulse)
            pygame.draw.circle(surface, (255, 255, 255), (x - 3, y - 3), 3)
# IRONEDIT:1783473883:85e995fa3fe9bc6a81a34033e5e6bc8eb90cfd3951632ca0a43a9f5039e18de4
