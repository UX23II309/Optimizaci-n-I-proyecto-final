import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, TEXT, MUTED, TITLE, PANEL_BG, PANEL_CARD, PANEL_LINE, COLD, PURPLE, HOT, GOOD, BAD, BG_TOP, BG_MID, BG_BOTTOM

def text(surface,msg,x,y,font,color=TEXT,max_width=None,gap=4):
    msg=str(msg)
    if max_width is None:
        img=font.render(msg,True,color); surface.blit(img,(x,y)); return y+img.get_height()
    words=msg.split(); line=''; yy=y
    for word in words:
        trial=line+word+' '
        if font.size(trial)[0] <= max_width: line=trial
        else:
            img=font.render(line,True,color); surface.blit(img,(x,yy)); yy+=img.get_height()+gap; line=word+' '
    if line:
        img=font.render(line,True,color); surface.blit(img,(x,yy)); yy+=img.get_height()+gap
    return yy

def gradient_bg(surface):
    for y in range(SCREEN_HEIGHT):
        t=y/SCREEN_HEIGHT
        if t<.55:
            k=t/.55; c=tuple(int(BG_TOP[i]+(BG_MID[i]-BG_TOP[i])*k) for i in range(3))
        else:
            k=(t-.55)/.45; c=tuple(int(BG_MID[i]+(BG_BOTTOM[i]-BG_MID[i])*k) for i in range(3))
        pygame.draw.line(surface,c,(0,y),(SCREEN_WIDTH,y))

def stars(surface,tick):
    for i in range(120):
        x=(i*173)%SCREEN_WIDTH; y=(i*97+int(tick*(.05+(i%5)*.025)))%SCREEN_HEIGHT
        surface.set_at((x,y),(75+i%80,70+i%65,125+i%105))

def panel(surface,rect,radius=18):
    pygame.draw.rect(surface,PANEL_BG,rect,border_radius=radius); pygame.draw.rect(surface,PANEL_LINE,rect,2,border_radius=radius)

def card(surface,x,y,w,h,title,font):
    pygame.draw.rect(surface,PANEL_CARD,(x,y,w,h),border_radius=16); pygame.draw.rect(surface,PANEL_LINE,(x,y,w,h),2,border_radius=16)
    pygame.draw.rect(surface,(45,38,70),(x+10,y+9,w-20,30),border_radius=10); text(surface,title,x+18,y+13,font,TITLE)

def bar(surface,x,y,w,h,ratio,color,bg=(54,49,70)):
    ratio=max(0,min(1,ratio)); pygame.draw.rect(surface,bg,(x,y,w,h),border_radius=8); pygame.draw.rect(surface,color,(x,y,int(w*ratio),h),border_radius=8); pygame.draw.rect(surface,(230,230,240),(x,y,w,h),2,border_radius=8)

def hud(surface,state,fonts):
    big,med,small,tiny=fonts; alg=state.algoritmo; px,py,pw,ph=935,24,320,672
    panel(surface,pygame.Rect(px,py,pw,ph),20)
    text(surface,'THERMAL',px+20,py+20,big,TITLE); text(surface,'QUEST',px+183,py+20,big,COLD); text(surface,'Santuario del Núcleo Frío',px+22,py+62,tiny,MUTED)
    y=py+92
    card(surface,px+16,y,pw-32,136,'Estado del algoritmo',med); yy=y+48
    for line,col in [(f'Función: {alg.funcion_nombre}',TEXT),(f'Iteración: {alg.iteracion}',TEXT),(f'Coordenada: ({alg.col}, {alg.fila})',TEXT),(f'f actual: {alg.f_actual:.5f}',TEXT),(f'mejor f: {alg.f_mejor:.5f}',GOOD)]: yy=text(surface,line,px+32,yy,small,col)+3
    y+=150
    card(surface,px+16,y,pw-32,110,'Temperatura',med); yy=y+48; ratio=alg.temperatura/alg.t_inicial
    text(surface,f'T = {alg.temperatura:.4f}',px+32,yy,small); bar(surface,px+32,yy+27,pw-64,18,ratio,HOT); text(surface,f'T = αT,  α = {alg.alpha:.3f}',px+32,yy+53,tiny,MUTED)
    y+=124
    card(surface,px+16,y,pw-32,174,'Decisión del turno',med); yy=y+48; d=state.ultima_decision
    if d is None: text(surface,'Muévete para proponer una solución vecina U.',px+32,yy,small,MUTED,pw-64)
    else:
        yy=text(surface,f'ΔE = {d.delta_e:+.5f}',px+32,yy,small)+3; yy=text(surface,f'p = exp(-ΔE/T) = {d.probabilidad:.4f}',px+32,yy,small)+9
        bar(surface,px+32,yy,pw-64,16,d.probabilidad,PURPLE); mark=px+32+int((pw-64)*max(0,min(1,d.aleatorio))); pygame.draw.line(surface,TEXT,(mark,yy-7),(mark,yy+23),2)
        yy+=28; yy=text(surface,f'r = {d.aleatorio:.3f}',px+32,yy,tiny,MUTED)+4; text(surface,('ACEPTADO' if d.aceptado else 'RECHAZADO')+': '+d.razon,px+32,yy,small,GOOD if d.aceptado else BAD,pw-64)
    y+=188
    card(surface,px+16,y,pw-32,118,'Guía',med); text(surface,state.dialogo,px+32,y+48,small,TEXT,pw-64)
    bx,by,bw,bh=26,590,875,104; panel(surface,pygame.Rect(bx,by,bw,bh),18)
    text(surface,'Controles',bx+20,by+16,med,TITLE); text(surface,'WASD/Flechas: mover | Q/E/Z/C: diagonales | M: auto | 1/2/3: función | R: reiniciar | H: ayuda',bx+20,by+48,small,TEXT)
    text(surface,f'Modo: {"AUTOMÁTICO" if state.auto else "MANUAL"}. Cada movimiento equivale a una iteración.',bx+20,by+74,tiny,MUTED)

def title_screen(surface,fonts,tick):
    big,med,small,tiny=fonts; overlay=pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT),pygame.SRCALPHA); overlay.fill((0,0,0,178)); surface.blit(overlay,(0,0))
    box=pygame.Rect(145,72,990,565); pygame.draw.rect(surface,(17,15,30),box,border_radius=24); pygame.draw.rect(surface,TITLE,box,3,border_radius=24)
    text(surface,'THERMAL QUEST',box.x+46,box.y+38,big,TITLE); text(surface,'El Santuario del Núcleo Frío',box.x+50,box.y+86,med,COLD)
    lines=['Juego pseudo-3D isométrico para aprender Recocido Simulado.','El mundo representa una función objetivo f(x,y).','Las plataformas azules son zonas de menor energía; las de lava son valores altos.','Te mueves con WASD/flechas. Cada movimiento propone una solución vecina U.','Si U mejora, avanzas. Si U empeora, se acepta con probabilidad exp(-ΔE/T).','La temperatura baja cada turno: al inicio exploras más, al final arriesgas menos.']
    y=box.y+150
    for line in lines: y=text(surface,'• '+line,box.x+52,y,small,TEXT,box.w-104)+9
    text(surface,'Funciones: 1 = Rastrigin   2 = Himmelblau   3 = Sphere',box.x+52,y+18,med,TITLE)
    text(surface,'Recomendado para demo: empieza con Rastrigin para mostrar mínimos locales.',box.x+52,y+58,small,MUTED)
    if (tick//30)%2==0: text(surface,'Presiona ENTER para iniciar',box.x+52,box.bottom-82,med,GOOD)
    text(surface,'Presiona H para ayuda',box.x+52,box.bottom-45,small,MUTED)

def help_screen(surface,fonts):
    big,med,small,tiny=fonts; overlay=pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT),pygame.SRCALPHA); overlay.fill((0,0,0,190)); surface.blit(overlay,(0,0))
    box=pygame.Rect(135,60,1010,600); pygame.draw.rect(surface,(17,15,30),box,border_radius=24); pygame.draw.rect(surface,COLD,box,3,border_radius=24)
    text(surface,'¿Qué aprende quien juega?',box.x+42,box.y+34,big,TITLE); y=box.y+96
    lines=['1. La posición del personaje es la solución actual.','2. Cada movimiento propone una solución vecina U.','3. Se evalúa f(U) y se calcula ΔE = f(U) - f(actual).','4. Si ΔE <= 0, el movimiento es mejor y se acepta siempre.','5. Si ΔE > 0, el movimiento es peor, pero puede aceptarse con p = exp(-ΔE/T).','6. La temperatura T baja después de cada turno con T = αT.','7. A temperatura alta, el juego permite más riesgos; a temperatura baja, se vuelve estricto.','8. La niebla y el relieve representan información incompleta y mínimos locales.','','Esto traduce el algoritmo a decisiones jugables: explorar, arriesgar y enfriarse.']
    for line in lines: y=text(surface,line,box.x+48,y,small,TEXT,box.w-96)+8
    text(surface,'Presiona H para cerrar.',box.x+48,box.bottom-55,med,COLD)

def final_screen(surface,state,fonts):
    big,med,small,tiny=fonts; overlay=pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT),pygame.SRCALPHA); overlay.fill((0,0,0,175)); surface.blit(overlay,(0,0))
    box=pygame.Rect(198,112,890,500); pygame.draw.rect(surface,(17,15,30),box,border_radius=24); pygame.draw.rect(surface,GOOD,box,3,border_radius=24); res=state.algoritmo.resumen()
    text(surface,'Convergencia alcanzada',box.x+46,box.y+40,big,TITLE); text(surface,'El sistema terminó por criterio matemático: temperatura baja, paciencia sin mejora o máximo de seguridad.',box.x+48,box.y+88,small,MUTED,box.w-96)
    y=box.y+145
    lines=[f'Función: {res["funcion"]}',f'Mejor punto aproximado: x = {res["x"]:.5f}, y = {res["y"]:.5f}',f'Mejor valor encontrado: f(x,y) = {res["f"]:.8f}',f'Iteraciones: {res["iteraciones"]}',f'Temperatura final: {res["temperatura"]:.6f}',f'Movimientos peores aceptados por Metropolis: {res["metropolis"]}',f'Movimientos rechazados: {res["rechazos"]}','','Interpretación: el algoritmo puede aceptar riesgo para escapar de mínimos locales.']
    for line in lines: y=text(surface,line,box.x+50,y,small,TEXT,box.w-100)+7
    text(surface,'R = reiniciar | 1/2/3 = cambiar función | ESC = salir',box.x+50,box.bottom-55,med,GOOD)
# IRONEDIT:1783045598:5cafc160af68e2fe9c2246173fd758a14ac6f574d3a8e11e9cd925e8bca4a9ad
