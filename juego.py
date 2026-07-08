#conexión de pygame y el algoritmo de nelder
from __future__ import annotations

import pygame

from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
    NM_ALPHA, NM_GAMMA, NM_RHO, NM_SIGMA,
    SIMPLEX_EPS, F_EPS, MAX_ITER,
    AUTO_DELAY, INPUT_COOLDOWN, ANIMATION_TIME
)
from nelder_mead import NelderMead2D
from mundo import World
from animacion import ParticleSystem
from ui import gradient_bg, stars, hud, title_screen, help_screen, final_screen


class GameState:
    """
    Guarda todo el estado del juego.

    Esto ayuda a no revolver:
    - la lógica matemática,
    - la lógica visual,
    - los controles,
    - y los datos que se muestran en pantalla.
    """

    def __init__(self, funcion='himmelblau'):
        self.funcion = funcion

        # Creamos el algoritmo con la función elegida.
        self.nm = NelderMead2D(
            funcion_nombre=funcion,
            alpha=NM_ALPHA,
            gamma=NM_GAMMA,
            rho=NM_RHO,
            sigma=NM_SIGMA,
            simplex_eps=SIMPLEX_EPS,
            f_eps=F_EPS,
            max_iter=MAX_ITER,
        )

        # Mundo visual generado a partir de la misma función objetivo.
        self.world = World(funcion)

        # Partículas decorativas.
        self.particles = ParticleSystem()

        # Último registro del algoritmo. Sirve para explicar qué pasó.
        self.record = None

        # Estados de pantalla.
        self.started = False
        self.help = False
        self.auto = False
        self.challenge = False

        # Temporizadores.
        self.auto_timer = 0.0
        self.input_timer = 0.0

        # Mensaje pedagógico del panel.
        self.feedback = (
            'Presiona ESPACIO para ejecutar un paso o TAB para activar el modo reto.'
        )

        # Animación del simplex.
        # Los vértices reales cambian de golpe por el algoritmo,
        # pero los vértices visuales se mueven poco a poco.
        self.visual_vertices = list(self.nm.vertices)
        self.animating = False
        self.anim_time = 0.0
        self.anim_start = list(self.nm.vertices)
        self.anim_target = list(self.nm.vertices)

    def reset(self, funcion=None):
        """Reinicia el juego, conservando si la ayuda estaba abierta."""
        if funcion is None:
            funcion = self.funcion

        keep_help = self.help
        keep_challenge = self.challenge

        self.__init__(funcion)

        self.started = True
        self.help = keep_help
        self.challenge = keep_challenge

    def _normalizar_op(self, op: str) -> str:
        """
        Agrupa las dos contracciones como una sola respuesta.

        El algoritmo puede devolver:
        - contracción externa
        - contracción interna

        Pero para el jugador basta con responder "contracción".
        """
        if 'contracción' in op:
            return 'contracción'
        return op

    def _comenzar_animacion(self, vertices_antes, vertices_despues):
        """
        Prepara la animación del simplex.

        Esto corrige el problema de que el simplex parecía no llegar al punto:
        ahora no se permite otro paso hasta que termine la animación.
        """
        self.anim_start = list(self.visual_vertices)
        self.anim_target = list(vertices_despues)
        self.anim_time = 0.0
        self.animating = True

    def step(self, guess=None):
        """
        Ejecuta un paso de Nelder-Mead.

        Si guess viene con texto, significa que el jugador está en modo reto
        e intentó adivinar la operación: reflexión, expansión, contracción
        o reducción.
        """
        if not self.started or self.nm.convergido:
            return

        # Evitamos que el usuario avance mientras el triángulo aún se anima.
        if self.input_timer > 0 or self.animating:
            return

        # Modo reto: primero vemos cuál operación sería la correcta.
        if guess is not None:
            esperada = self._normalizar_op(self.nm.predecir_operacion())
            elegida = self._normalizar_op(guess)

            if elegida == esperada:
                self.feedback = f'Correcto: la operación era {esperada}.'
            else:
                self.feedback = f'Elegiste {elegida}, pero tocaba {esperada}. Se ejecuta para aprender.'

        # Ejecutamos el paso real del algoritmo.
        self.record = self.nm.step()
        self.input_timer = INPUT_COOLDOWN

        # Animamos desde el estado visual actual hasta el nuevo simplex real.
        self._comenzar_animacion(self.record.vertices_antes, self.record.vertices_despues)

        # Partículas en el mejor punto actual.
        sx, sy = self.world.point_to_screen(self.nm.vertices[0])
        self.particles.burst(sx, sy, self.record.operacion)

        # Si no estamos en modo reto, mostramos explicación normal.
        if guess is None:
            self.feedback = self.record.explicacion

    def update(self, dt):
        """Actualiza temporizadores, animación y partículas."""
        if self.input_timer > 0:
            self.input_timer -= dt

        self.particles.ambient()
        self.particles.update()

        # Animación del triángulo con interpolación sencilla.
        if self.animating:
            self.anim_time += dt
            t = min(1.0, self.anim_time / ANIMATION_TIME)

            # Suavizado para que no se vea robótico.
            t = t * t * (3 - 2 * t)

            nuevos = []
            for inicio, fin in zip(self.anim_start, self.anim_target):
                x = inicio[0] + (fin[0] - inicio[0]) * t
                y = inicio[1] + (fin[1] - inicio[1]) * t
                nuevos.append((x, y))

            self.visual_vertices = nuevos

            if self.anim_time >= ANIMATION_TIME:
                self.visual_vertices = list(self.nm.vertices)
                self.animating = False

        # Modo automático: ejecuta pasos solo cuando no hay animación.
        if self.auto and self.started and not self.nm.convergido and not self.animating:
            self.auto_timer += dt
            if self.auto_timer >= AUTO_DELAY:
                self.auto_timer = 0
                self.step()

def make_fonts():
    """Fuentes del sistema. No requiere archivos externos."""
    big = pygame.font.SysFont('consolas', 34, bold=True)
    med = pygame.font.SysFont('consolas', 20, bold=True)
    small = pygame.font.SysFont('consolas', 15)
    tiny = pygame.font.SysFont('consolas', 13)
    return big, med, small, tiny


def run():
    """Función principal del juego."""
    pygame.init()
    pygame.display.set_caption('Nelder Quest Final - Nelder-Mead')
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    fonts = make_fonts()

    state = GameState('himmelblau')
    running = True
    tick = 0

    while running:
        dt = clock.tick(FPS) / 1000.0
        tick += 1

        # Eventos del teclado y ventana.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                k = event.key

                if k == pygame.K_ESCAPE:
                    running = False

                elif k == pygame.K_RETURN:
                    state.started = True

                elif k == pygame.K_SPACE:
                    # Modo aprendizaje: el juego ejecuta el paso correcto.
                    state.step()

                elif k == pygame.K_TAB:
                    # Modo reto: el jugador elige la operación.
                    state.challenge = not state.challenge
                    state.feedback = (
                        'Modo reto activo: elige F/E/C/D.'
                        if state.challenge else
                        'Modo aprendizaje activo: ESPACIO ejecuta el paso correcto.'
                    )

                elif k == pygame.K_m:
                    state.auto = not state.auto

                elif k == pygame.K_h:
                    state.help = not state.help

                elif k == pygame.K_r:
                    state.reset()

                elif k == pygame.K_1:
                    state.reset('himmelblau')

                elif k == pygame.K_2:
                    state.reset('rosenbrock')

                elif k == pygame.K_3:
                    state.reset('rastrigin')

                elif k == pygame.K_4:
                    state.reset('sphere')

                # Controles del modo reto.
                elif state.challenge:
                    if k == pygame.K_f:
                        state.step('reflexión')
                    elif k == pygame.K_e:
                        state.step('expansión')
                    elif k == pygame.K_c:
                        state.step('contracción')
                    elif k == pygame.K_d:
                        state.step('reducción')

        # Actualizar y dibujar.
        state.update(dt)

        gradient_bg(screen)
        stars(screen, tick)
        state.world.draw(screen, tick)
        state.world.draw_simplex(screen, state.visual_vertices, state.record, tick)
        state.particles.draw(screen)

        hud(screen, state, fonts)

        if not state.started:
            title_screen(screen, fonts, tick)

        if state.help:
            help_screen(screen, fonts)

        if state.nm.convergido and state.started:
            final_screen(screen, state, fonts)

        pygame.display.flip()

    pygame.quit()
# IRONEDIT:1783473922:89442688be10841c1dae41a8bee9fa3400a4ee7a4449db9ad086e22e79fa616a
