import random
import pygame
 
#animacion particulas del simplex
 
from config import GOOD, BAD, HOT, LAVA, COLD, PURPLE
 
 
class Particle:
    """Partícula individual con posición, velocidad, color y tiempo de vida limitado."""
 
    def __init__(self, x, y, color, burst=False):
        self.x = x
        self.y = y
        self.color = color
        self.vx = random.uniform(-2.6, 2.6) if burst else random.uniform(-0.35, 0.35)
        self.vy = random.uniform(-2.2, 1.0) if burst else random.uniform(-1.0, -0.12)
        self.life = random.randint(22, 48) if burst else random.randint(35, 78)
        self.max_life = self.life
        self.size = random.randint(2, 4)
 
    def update(self):
        """Actualiza posición aplicando velocidad y gravedad ligera, y reduce el tiempo de vida."""
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.035
        self.life -= 1
 
    def draw(self, surface):
        """Dibuja la partícula con alpha decreciente según su vida restante."""
        if self.life <= 0:
            return
        alpha = int(255 * self.life / self.max_life)
        s = pygame.Surface((self.size*4, self.size*4), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, alpha), (self.size*2, self.size*2), self.size)
        surface.blit(s, (self.x-self.size*2, self.y-self.size*2))
 
class ParticleSystem:
    """Administra el conjunto de partículas ambientales y de ráfaga (burst) del juego."""
 
    def __init__(self):
        self.items = []
 
    def ambient(self):
        """Genera partículas decorativas de fondo de forma continua, con límite máximo."""
        if len(self.items) < 130 and random.random() < 0.35:
            x = random.uniform(0, 900)
            y = random.uniform(440, 630)
            color = random.choice([(255, 155, 75), (255, 215, 112), (150, 120, 255), (95, 225, 255)])
            self.items.append(Particle(x, y, color, False))
 
    def burst(self, x, y, operation):
        """Lanza una ráfaga de partículas coloreadas según la operación de Nelder-Mead ejecutada."""
        color = {
            'reflexión': COLD,
            'expansión': GOOD,
            'contracción externa': PURPLE,
            'contracción interna': PURPLE,
            'reducción': BAD,
        }.get(operation, HOT)
        for _ in range(38):
            self.items.append(Particle(x, y, color, True))
 
    def update(self):
        """Actualiza todas las partículas y elimina las que ya expiraron."""
        for p in self.items:
            p.update()
        self.items = [p for p in self.items if p.life > 0]
 
    def draw(self, surface):
        """Dibuja todas las partículas activas."""
        for p in self.items:
            p.draw(surface)
# IRONEDIT:1783476037:efd8b8502974481f3d1f8df312168625a710fa634885f0826fe3b2569a514a4e
