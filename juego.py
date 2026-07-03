from __future__ import annotations
import random, pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, GRID_SIZE, T_INICIAL, T_MIN, ALPHA, EPSILON, PACIENCIA_SIN_MEJORA, MAX_ITER, INPUT_COOLDOWN, AUTO_DELAY
from algoritmorecocido import RecocidoGrid
from mundo import World
from personaje import Player, ParticleSystem
from ui import gradient_bg, stars, hud, title_screen, help_screen, final_screen

class GameState:
    def __init__(self, funcion='rastrigin'):
        self.funcion=funcion; start=GRID_SIZE//2
        self.algoritmo=RecocidoGrid(funcion,GRID_SIZE,start,start,T_INICIAL,T_MIN,ALPHA,EPSILON,PACIENCIA_SIN_MEJORA,MAX_ITER)
        self.world=World(funcion); self.world.register_visit(self.algoritmo.col,self.algoritmo.fila)
        self.player=Player(); px,py=self.player_screen_position(); self.player.place(px,py)
        self.particles=ParticleSystem(); self.ultima_decision=None
        self.started=False; self.help=False; self.auto=False; self.auto_timer=0; self.input_timer=0
        self.dialogo='Explora el santuario. Muévete para proponer una solución vecina U.'
    def player_screen_position(self):
        x,y=self.world.iso_top(self.algoritmo.col,self.algoritmo.fila); return x,y+18
    def reset(self,funcion=None):
        if funcion is None: funcion=self.funcion
        help_on=self.help; self.__init__(funcion); self.started=True; self.help=help_on
    def move(self,dc,df):
        if not self.started or self.algoritmo.convergido or self.input_timer>0: return
        decision=self.algoritmo.intentar_movimiento(dc,df)
        if decision is None: return
        self.input_timer=INPUT_COOLDOWN; self.ultima_decision=decision; self.world.register_visit(self.algoritmo.col,self.algoritmo.fila)
        px,py=self.player_screen_position()
        if decision.aceptado: self.player.move_to(px,py)
        else: self.player.reject()
        self.particles.decision_burst(px,py,decision.aceptado)
        if 'mejora' in decision.razon: self.dialogo='Mejora aceptada: ΔE ≤ 0. El algoritmo siempre acepta una solución mejor.'
        elif 'metropolis' in decision.razon: self.dialogo='Riesgo aceptado: aunque subió la energía, la probabilidad exp(-ΔE/T) permitió avanzar.'
        elif 'rechazo' in decision.razon: self.dialogo='Movimiento rechazado: era peor y el azar no superó la probabilidad.'
        if decision.convergido: self.dialogo='Convergencia: terminó el enfriamiento o hubo demasiados turnos sin mejora.'
    def auto_step(self):
        dirs=[(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,-1),(1,-1),(-1,1)]; random.shuffle(dirs); best=None; bestv=None
        for dc,df in dirs:
            nc=self.algoritmo.col+dc; nf=self.algoritmo.fila+df
            if 0<=nc<GRID_SIZE and 0<=nf<GRID_SIZE:
                v=self.algoritmo.evaluar_celda(nc,nf)
                if best is None or v<bestv or random.random()<.25: best=(dc,df); bestv=v
        if best: self.move(*best)
    def update(self,dt):
        if self.input_timer>0: self.input_timer-=dt
        self.player.update(); px,py=self.player_screen_position(); tr=self.algoritmo.temperatura/self.algoritmo.t_inicial
        self.particles.ambient(px+24,py-28,tr); self.particles.update()
        if self.auto and self.started and not self.algoritmo.convergido:
            self.auto_timer+=dt
            if self.auto_timer>=AUTO_DELAY: self.auto_timer=0; self.auto_step()

def make_fonts():
    return (pygame.font.SysFont('consolas',34,bold=True),pygame.font.SysFont('consolas',20,bold=True),pygame.font.SysFont('consolas',15),pygame.font.SysFont('consolas',13))

def run():
    pygame.init(); pygame.display.set_caption('Thermal Quest Showcase - Recocido Simulado')
    screen=pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT)); clock=pygame.time.Clock(); fonts=make_fonts(); state=GameState('rastrigin')
    running=True; tick=0
    while running:
        dt=clock.tick(FPS)/1000; tick+=1
        for event in pygame.event.get():
            if event.type==pygame.QUIT: running=False
            if event.type==pygame.KEYDOWN:
                k=event.key
                if k==pygame.K_ESCAPE: running=False
                elif k==pygame.K_RETURN: state.started=True
                elif k==pygame.K_h: state.help=not state.help
                elif k==pygame.K_m: state.auto=not state.auto
                elif k==pygame.K_r: state.reset()
                elif k==pygame.K_1: state.reset('rastrigin')
                elif k==pygame.K_2: state.reset('himmelblau')
                elif k==pygame.K_3: state.reset('sphere')
                elif k in (pygame.K_w,pygame.K_UP): state.move(0,-1)
                elif k in (pygame.K_s,pygame.K_DOWN): state.move(0,1)
                elif k in (pygame.K_a,pygame.K_LEFT): state.move(-1,0)
                elif k in (pygame.K_d,pygame.K_RIGHT): state.move(1,0)
                elif k==pygame.K_q: state.move(-1,-1)
                elif k==pygame.K_e: state.move(1,-1)
                elif k==pygame.K_z: state.move(-1,1)
                elif k==pygame.K_c: state.move(1,1)
        state.update(dt)
        gradient_bg(screen); stars(screen,tick)
        state.world.draw(screen,state.algoritmo.col,state.algoritmo.fila,tick); state.world.draw_markers(screen,state.algoritmo,state.ultima_decision,tick)
        state.player.draw(screen,tick,state.algoritmo.temperatura/state.algoritmo.t_inicial); state.particles.draw(screen)
        hud(screen,state,fonts)
        if not state.started: title_screen(screen,fonts,tick)
        if state.help: help_screen(screen,fonts)
        if state.algoritmo.convergido and state.started: final_screen(screen,state,fonts)
        pygame.display.flip()
    pygame.quit()
# IRONEDIT:1783042072:2a9f7540ae702b93c34c0532f4104679753c8163846befaeacf0b804e8e2e529
