import math, random
import pygame
from config import GOOD, BAD, HOT, LAVA, COLD, ICE

class Player:
    def __init__(self):
        self.x=self.y=self.tx=self.ty=0.0; self.face=1; self.shake=0; self.flash=0
    def place(self,x,y): self.x=self.tx=float(x); self.y=self.ty=float(y)
    def move_to(self,x,y):
        if x>self.tx: self.face=1
        elif x<self.tx: self.face=-1
        self.tx=float(x); self.ty=float(y)
    def reject(self): self.shake=18; self.flash=14
    def update(self):
        self.x+=(self.tx-self.x)*.22; self.y+=(self.ty-self.y)*.22
        self.shake=max(0,self.shake-1); self.flash=max(0,self.flash-1)
    def draw(self,surface,tick,temp_ratio):
        x=int(self.x); y=int(self.y)
        if self.shake>0: x+=int(math.sin(self.shake*2.4)*5)
        bob=int(math.sin(tick*.16)*3)
        glow=pygame.Surface((126,126),pygame.SRCALPHA)
        alpha=int(45+105*max(0,min(1,temp_ratio)))
        pygame.draw.circle(glow,(255,143,69,alpha),(63,63),42)
        pygame.draw.circle(glow,(255,227,135,alpha//3),(63,63),60)
        surface.blit(glow,(x-63,y-68))
        pygame.draw.ellipse(surface,(0,0,0,120),(x-23,y+19,46,13))
        yy=y+bob
        pygame.draw.polygon(surface,(20,17,30),[(x-14,yy-5),(x,yy-16),(x+14,yy-5),(x,yy+8)])
        pygame.draw.polygon(surface,(33,25,47),[(x-14,yy-5),(x,yy+8),(x,yy+30),(x-14,yy+14)])
        pygame.draw.polygon(surface,(51,40,72),[(x+14,yy-5),(x,yy+8),(x,yy+30),(x+14,yy+14)])
        pygame.draw.polygon(surface,(86,49,76),[(x-14,yy+14),(x,yy+30),(x+14,yy+14),(x,yy+8)])
        scarf=ICE if temp_ratio>.45 else HOT
        pygame.draw.line(surface,scarf,(x-10,yy),(x+13,yy+4),3)
        pygame.draw.rect(surface,(239,194,138),(x-9,yy-30,18,15))
        pygame.draw.rect(surface,(83,52,34),(x-10,yy-34,20,6))
        pygame.draw.rect(surface,(245,248,255),(x-5,yy-25,2,2)); pygame.draw.rect(surface,(245,248,255),(x+4,yy-25,2,2))
        step=int(abs(math.sin(tick*.23))*4)
        pygame.draw.rect(surface,(13,13,22),(x-8,yy+25,6,14+step)); pygame.draw.rect(surface,(13,13,22),(x+2,yy+25,6,14-step))
        fx=x+26*self.face; fy=yy-25
        pygame.draw.line(surface,(95,56,32),(x+9*self.face,yy-3),(fx,fy),4)
        pygame.draw.circle(surface,HOT,(fx,fy),9); pygame.draw.circle(surface,LAVA,(fx-1,fy-2),6); pygame.draw.circle(surface,(255,245,170),(fx-3,fy-4),3)
        if self.flash>0: pygame.draw.circle(surface,BAD,(x,yy+2),24,2)

class Particle:
    def __init__(self,x,y,color,mode='ember'):
        self.x=x; self.y=y; self.color=color; self.mode=mode
        if mode=='burst': self.vx=random.uniform(-2.8,2.8); self.vy=random.uniform(-2.6,1.0); self.life=random.randint(22,48)
        elif mode=='snow': self.vx=random.uniform(-.25,.25); self.vy=random.uniform(-.7,-.05); self.life=random.randint(40,88)
        else: self.vx=random.uniform(-.45,.45); self.vy=random.uniform(-1,-.12); self.life=random.randint(35,78)
        self.max_life=self.life; self.size=random.randint(2,4)
    def update(self):
        self.x+=self.vx; self.y+=self.vy; self.vy += .045 if self.mode=='burst' else .012; self.life-=1
    def draw(self,surface):
        if self.life<=0: return
        alpha=int(255*self.life/self.max_life)
        s=pygame.Surface((self.size*4,self.size*4),pygame.SRCALPHA)
        pygame.draw.circle(s,(*self.color,alpha),(self.size*2,self.size*2),self.size)
        surface.blit(s,(self.x-self.size*2,self.y-self.size*2))

class ParticleSystem:
    def __init__(self): self.items=[]
    def ambient(self,x,y,temp_ratio):
        if len(self.items)<140 and random.random()<.46:
            color=random.choice([(255,155,75),(255,215,112),(150,120,255),(95,225,255)])
            mode='ember' if temp_ratio>.25 else 'snow'
            self.items.append(Particle(x+random.uniform(-24,24),y+random.uniform(-28,8),color,mode))
    def decision_burst(self,x,y,accepted):
        color=GOOD if accepted else BAD
        for _ in range(32): self.items.append(Particle(x,y,color,'burst'))
    def update(self):
        for p in self.items: p.update()
        self.items=[p for p in self.items if p.life>0]
    def draw(self,surface):
        for p in self.items: p.draw(surface)
# IRONEDIT:1783041811:79df10693815740253537a733bf653b7b48169ad9cc8ff935b21dca664419b88
