from __future__ import annotations
import math, random
import pygame
import numpy as np
from config import GRID_SIZE, ISO_W, ISO_H, HEIGHT_SCALE, MAP_CENTER_X, MAP_TOP, FOG_RADIUS, COLD, ICE, PURPLE, MAGENTA, HOT, LAVA, GOOD, BAD
from algoritmorecocido import FUNCIONES, DOMINIOS

def mix(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(a[i] + (b[i]-a[i])*t) for i in range(3))
def bright(c, n): return tuple(min(255, v+n) for v in c)
def dark(c, n): return tuple(max(0, v-n) for v in c)

def energy_color(v):
    if v < .16: return mix((12,22,58), (27,91,148), v/.16)
    if v < .32: return mix((27,91,148), COLD, (v-.16)/.16)
    if v < .50: return mix(COLD, PURPLE, (v-.32)/.18)
    if v < .68: return mix(PURPLE, MAGENTA, (v-.50)/.18)
    if v < .86: return mix(MAGENTA, HOT, (v-.68)/.18)
    return mix(HOT, LAVA, (v-.86)/.14)

class World:
    def __init__(self, funcion_nombre: str):
        self.funcion_nombre = funcion_nombre
        self.funcion = FUNCIONES[funcion_nombre]
        self.dominio = DOMINIOS[funcion_nombre]
        self.values = self._build_values()
        self.min_value = float(np.min(self.values))
        self.max_value = float(np.max(self.values))
        self.visited = set()
        self.details = self._details()

    def _build_values(self):
        arr = np.zeros((GRID_SIZE, GRID_SIZE), dtype=float)
        for fila in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                x, y = self.cell_to_xy(col, fila)
                arr[fila, col] = self.funcion(x, y)
        return arr

    def _details(self):
        rng = random.Random(12345)
        d = {}
        for fila in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                d[(col, fila)] = {
                    'crack': rng.random() < .20,
                    'pebble': rng.random() < .28,
                    'crystal': rng.random() < .12,
                    'pillar': rng.random() < .06,
                    'moss': rng.random() < .10,
                    'seed': rng.randint(0, 999999),
                }
        return d

    def cell_to_xy(self, col, fila):
        (x_min, x_max), (y_min, y_max) = self.dominio
        x = x_min + (col/(GRID_SIZE-1))*(x_max-x_min)
        y = y_max - (fila/(GRID_SIZE-1))*(y_max-y_min)
        return x, y

    def norm(self, v):
        if abs(self.max_value-self.min_value) < 1e-12: return 0.0
        return (v-self.min_value)/(self.max_value-self.min_value)

    def height(self, col, fila):
        return 8 + int((self.norm(self.values[fila, col]) ** .72) * HEIGHT_SCALE)

    def iso_base(self, col, fila):
        return int(MAP_CENTER_X + (col-fila)*ISO_W/2), int(MAP_TOP + (col+fila)*ISO_H/2)

    def iso_top(self, col, fila):
        x, y = self.iso_base(col, fila)
        return x, y-self.height(col, fila)

    def register_visit(self, col, fila): self.visited.add((int(col), int(fila)))

    def visible_known(self, col, fila, pc, pf):
        dist = abs(col-pc) + abs(fila-pf)
        return dist <= FOG_RADIUS, (col, fila) in self.visited

    def draw_void(self, surface, tick):
        for i in range(20):
            y = 430 + i*14
            color = (120+i*4, 38+i*2, 28)
            pygame.draw.line(surface, color, (0, y), (930, y+int(math.sin(tick*.03+i)*10)), 3)
        for i in range(26):
            x = (i*91 + int(tick*(1+i%3))) % 940
            y = 515 + int(math.sin(tick*.04+i)*34)
            pygame.draw.circle(surface, (255, 122, 52), (x, y), 2+i%3)

    def crystal(self, surface, x, y, color, scale=1):
        pts=[(x,y-16*scale),(x+7*scale,y-4*scale),(x+4*scale,y+9*scale),(x-5*scale,y+10*scale),(x-8*scale,y-4*scale)]
        pygame.draw.polygon(surface, color, pts)
        pygame.draw.polygon(surface, bright(color,45), [(x,y-14*scale),(x+3*scale,y-2*scale),(x,y+6*scale),(x-4*scale,y-3*scale)])
        pygame.draw.lines(surface, (220,255,255), True, pts, 1)

    def pillar(self, surface, x, y):
        pygame.draw.rect(surface, (49,43,65), (x-5, y-28, 10, 28))
        pygame.draw.rect(surface, (87,74,111), (x-7, y-31, 14, 5))
        pygame.draw.rect(surface, (28,24,39), (x-7, y-3, 14, 5))

    def block(self, surface, col, fila, pc, pf, tick):
        val = self.values[fila, col]; n = self.norm(val); base = energy_color(n)
        visible, known = self.visible_known(col, fila, pc, pf)
        if not visible and not known: base = (8,9,18)
        elif not visible and known: base = mix(base, (8,9,18), .70)
        h = self.height(col, fila); x, y = self.iso_base(col, fila)
        top=(x,y-h); right=(x+ISO_W//2,y+ISO_H//2-h); bottom=(x,y+ISO_H-h); left=(x-ISO_W//2,y+ISO_H//2-h)
        br=(x+ISO_W//2,y+ISO_H//2); bb=(x,y+ISO_H); bl=(x-ISO_W//2,y+ISO_H//2)
        shadow = pygame.Surface((ISO_W+18, ISO_H+18), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0,0,0,65), (2,8,ISO_W+12,ISO_H+8))
        surface.blit(shadow, (x-ISO_W//2-8, y-6))
        pygame.draw.polygon(surface, dark(base,70), [left,bottom,bb,bl])
        pygame.draw.polygon(surface, dark(base,42), [right,bottom,bb,br])
        pygame.draw.polygon(surface, bright(base,16), [top,right,bottom,left])
        pygame.draw.lines(surface, dark(base,95), True, [top,right,bottom,left], 1)
        if visible or known: pygame.draw.line(surface, bright(base,60), top, right, 1)
        d=self.details[(col,fila)]; rng=random.Random(d['seed'])
        if visible or known:
            for _ in range(2):
                ox=rng.randint(-12,12); oy=rng.randint(-2,10)
                pygame.draw.line(surface, dark(base,38), (x+ox-6,y+oy-h+8), (x+ox+7,y+oy-h+5), 1)
            if d['crack'] and n>.45: pygame.draw.line(surface, (70,22,32), (x-10,y-h+7), (x+9,y-h+16), 2)
            if d['pebble']: pygame.draw.circle(surface, dark(base,55), (x+rng.randint(-10,10), y-h+rng.randint(4,19)), 2)
            if d['moss'] and n<.35:
                pygame.draw.circle(surface, (72,175,142), (x-9,y-h+15), 2)
                pygame.draw.circle(surface, (55,143,122), (x-5,y-h+17), 1)
            if n<.12: self.crystal(surface, x+9, y-h+8, ICE, 1)
            elif d['crystal'] and n<.35: self.crystal(surface, x+8, y-h+10, COLD, 1)
            if n>.82:
                r=3+int(abs(math.sin(tick*.08+col))*2)
                pygame.draw.circle(surface, LAVA, (x-6,y-h+13), r)
                pygame.draw.circle(surface, HOT, (x-6,y-h+13), max(1,r-2))
            if d['pillar'] and .25<n<.70: self.pillar(surface, x-11, y-h+12)
        if visible:
            glow=pygame.Surface((ISO_W+8, ISO_H+8), pygame.SRCALPHA)
            pygame.draw.ellipse(glow, (255,230,170,18), (0,0,ISO_W+8,ISO_H+8))
            surface.blit(glow, (x-ISO_W//2-4, y-h-2))

    def draw(self, surface, pc, pf, tick):
        self.draw_void(surface, tick)
        for s in range((GRID_SIZE-1)*2+1):
            for col in range(GRID_SIZE):
                fila = s-col
                if 0 <= fila < GRID_SIZE:
                    self.block(surface, col, fila, pc, pf, tick)

    def draw_markers(self, surface, alg, last, tick):
        mx,my = self.iso_top(alg.mejor_col, alg.mejor_fila); my += ISO_H//2
        pulse=10+int(abs(math.sin(tick*.08))*5)
        pygame.draw.circle(surface, GOOD, (mx,my), pulse, 2)
        pygame.draw.circle(surface, (220,255,235), (mx,my), 3)
        if last:
            cc,cf=last.candidato; cx,cy=self.iso_top(cc,cf); cy+=ISO_H//2
            pc,pf=last.previo; px,py=self.iso_top(pc,pf); py+=ISO_H//2
            color=GOOD if last.aceptado else BAD
            pygame.draw.line(surface, color, (px,py), (cx,cy), 3)
            pygame.draw.circle(surface, color, (cx,cy), 9, 2)
# IRONEDIT:1783045374:c35188b0f238a79ef381b0b9ba591c79f5da8e8253e9937e141543cb2130b0aa
