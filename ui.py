#paneles y explicaciones
import pygame

from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, RIGHT_PANEL_X, RIGHT_PANEL_Y, RIGHT_PANEL_W, RIGHT_PANEL_H,
    BOTTOM_PANEL_X, BOTTOM_PANEL_Y, BOTTOM_PANEL_W, BOTTOM_PANEL_H,
    TEXT, MUTED, TITLE, PANEL_BG, PANEL_CARD, PANEL_LINE, PANEL_DARK,
    COLD, ICE, PURPLE, MAGENTA, HOT, LAVA, GOOD, BAD, BG_TOP, BG_MID, BG_BOTTOM
)
from objetivos import DESCRIPCIONES


def text(surface, msg, x, y, font, color=TEXT, max_width=None, gap=4):
    """Dibuja texto en pantalla; si se da max_width, hace wrap automático por palabras."""
    msg = str(msg)
    if max_width is None:
        img = font.render(msg, True, color)
        surface.blit(img, (x, y))
        return y + img.get_height()
    words = msg.split()
    line = ''
    yy = y
    for word in words:
        trial = line + word + ' '
        if font.size(trial)[0] <= max_width:
            line = trial
        else:
            img = font.render(line, True, color)
            surface.blit(img, (x, yy))
            yy += img.get_height() + gap
            line = word + ' '
    if line:
        img = font.render(line, True, color)
        surface.blit(img, (x, yy))
        yy += img.get_height() + gap
    return yy


def gradient_bg(surface):
    """Pinta el fondo con degradado vertical (top -> mid -> bottom) usando los colores de config."""
    for y in range(SCREEN_HEIGHT):
        t = y / SCREEN_HEIGHT
        if t < 0.55:
            k = t / 0.55
            c = tuple(int(BG_TOP[i] + (BG_MID[i]-BG_TOP[i])*k) for i in range(3))
        else:
            k = (t-0.55)/0.45
            c = tuple(int(BG_MID[i] + (BG_BOTTOM[i]-BG_MID[i])*k) for i in range(3))
        pygame.draw.line(surface, c, (0,y), (SCREEN_WIDTH,y))


def stars(surface, tick):
    """Dibuja un campo de estrellas parpadeantes en el fondo, animadas con el contador tick."""

    for i in range(115):
        x = (i * 173) % SCREEN_WIDTH
        y = (i * 97 + int(tick * (0.05 + (i % 5)*0.025))) % SCREEN_HEIGHT
        col = (75 + i % 80, 70 + i % 65, 125 + i % 105)
        surface.set_at((x, y), col)


def panel(surface, rect, radius=18):
    """Dibuja un panel rectangular con borde redondeado, usado como contenedor base de la UI."""
    pygame.draw.rect(surface, PANEL_BG, rect, border_radius=radius)
    pygame.draw.rect(surface, PANEL_LINE, rect, 2, border_radius=radius)


def card(surface, x, y, w, h, title, font):
    """Dibuja una tarjeta con encabezado de título, usada dentro de los paneles del HUD."""

    pygame.draw.rect(surface, PANEL_CARD, (x,y,w,h), border_radius=16)
    pygame.draw.rect(surface, PANEL_LINE, (x,y,w,h), 2, border_radius=16)
    pygame.draw.rect(surface, (45,38,70), (x+10,y+9,w-20,30), border_radius=10)
    text(surface, title, x+18, y+13, font, TITLE)


def bar(surface, x, y, w, h, ratio, color, bg=(54,49,70)):
    """Dibuja una barra de progreso (0 a 1) usada para mostrar el cierre del simplex."""
    ratio = max(0, min(1, ratio))
    pygame.draw.rect(surface, bg, (x,y,w,h), border_radius=8)
    pygame.draw.rect(surface, color, (x,y,int(w*ratio),h), border_radius=8)
    pygame.draw.rect(surface, (230,230,240), (x,y,w,h), 2, border_radius=8)


def hud(surface, state, fonts):
    """
    Dibuja el panel derecho y el panel inferior.
    """
    big, med, small, tiny = fonts
    nm = state.nm
    record = state.record

    # Panel derecho principal
    panel(surface, pygame.Rect(RIGHT_PANEL_X, RIGHT_PANEL_Y, RIGHT_PANEL_W, RIGHT_PANEL_H), 20)

    x = RIGHT_PANEL_X + 24
    y = RIGHT_PANEL_Y + 20
    ancho = RIGHT_PANEL_W - 48

    
    # Función pequeña para separar secciones
    def separador(y_pos):
        pygame.draw.line(surface, PANEL_LINE, (x, y_pos), (x + ancho, y_pos), 1)
        return y_pos + 14

    # Título

    text(surface, 'NELDER', x, y, big, TITLE)
    text(surface, 'QUEST', x + 155, y, big, COLD)
    y += 42

    text(surface, 'Método Nelder-Mead / Simplex', x, y, tiny, MUTED)
    y += 28

    y = separador(y)

    # Información general
   
    modo = 'RETO' if state.challenge else 'APRENDIZAJE'

    text(surface, f'Función: {nm.funcion_nombre}', x, y, small, TITLE)
    y += 22

    text(surface, f'Modo: {modo}', x, y, small, COLD)
    y += 22

    # Barra de energía de aprendizaje
    color_energy = GOOD if state.energy > 40 else BAD
    text(surface, 'Energía de aprendizaje', x, y, tiny, MUTED)
    y += 18
    bar(surface, x, y, ancho, 12, state.energy / 100.0, color_energy)
    y += 18
    text(surface, f'Energía: {int(state.energy)}%', x, y, tiny, TEXT)
    y += 20

    # Aciertos, si existen en esta versión
    if hasattr(state, 'intentos') and state.intentos > 0:
        porcentaje = (state.aciertos / state.intentos) * 100
        text(surface, f'Aciertos: {state.aciertos}/{state.intentos} ({porcentaje:.0f}%)', x, y, tiny, GOOD)
    else:
        text(surface, 'Reto: TAB para evaluar aprendizaje', x, y, tiny, MUTED)
    y += 22

    text(surface, f'Iteración: {nm.iteracion}', x, y, small, TEXT)
    y += 26

    y = separador(y)

    # Simplex actual
    text(surface, 'SIMPLEX ACTUAL', x, y, med, TITLE)
    y += 30

    vals = [nm.f(v) for v in nm.vertices]

    text(surface, f'Mejor:  f = {vals[0]:.5f}', x, y, small, GOOD)
    y += 23

    text(surface, f'Medio:  f = {vals[1]:.5f}', x, y, small, COLD)
    y += 23

    text(surface, f'Peor:   f = {vals[2]:.5f}', x, y, small, BAD)
    y += 26

    text(surface, f'Tamaño simplex: {nm.simplex_size():.4f}', x, y, tiny, MUTED)
    y += 20

    text(surface, f'Desv. f: {nm.f_std():.6f}', x, y, tiny, MUTED)
    y += 25

    y = separador(y)

    # Operación actual
    text(surface, 'PASO ACTUAL', x, y, med, TITLE)
    y += 30

    if record is None:
        text(surface, 'ESPACIO: paso guiado. TAB: modo reto para elegir operación.', x, y, small, TEXT, ancho)
        y += 56
    else:
        op_color = {
            'reflexión': COLD,
            'expansión': GOOD,
            'contracción externa': PURPLE,
            'contracción interna': PURPLE,
            'reducción': BAD,
        }.get(record.operacion, TITLE)

        text(surface, f'Acción: {record.operacion}', x, y, small, op_color)
        y += 25

        text(surface, 'C = centroide', x, y, tiny, MUTED)
        y += 19

        text(surface, 'R/E/K = punto evaluado o aceptado', x, y, tiny, MUTED)
        y += 24

        ratio = max(0, min(1, 1 - nm.simplex_size() / 2.8))
        bar(surface, x, y, ancho, 14, ratio, GOOD)
        y += 22

        text(surface, 'Cierre del triángulo', x, y, tiny, MUTED)
        y += 24

    y = separador(y)

    # Explicación
    text(surface, 'FUNCIÓN OBJETIVO', x, y, med, TITLE)
    y += 30
    
    descripcion = DESCRIPCIONES[nm.funcion_nombre]
    y = text(surface, f'{nm.funcion_nombre}: {descripcion}', x, y, small, TEXT, ancho)
    y += 12

    # Frase corta para que el jugador entienda por qué se eligió esa función
    if nm.funcion_nombre == 'himmelblau':
        extra = 'Útil para ver varios valles posibles.'
    elif nm.funcion_nombre == 'rosenbrock':
        extra = 'Útil para ver un valle curvo y estrecho.'
    elif nm.funcion_nombre == 'rastrigin':
        extra = 'Útil para ver muchos mínimos locales.'
    else:
        extra = 'Caso suave para probar convergencia.'

    panel(surface, pygame.Rect(BOTTOM_PANEL_X, BOTTOM_PANEL_Y - 48, BOTTOM_PANEL_W, BOTTOM_PANEL_H + 48), 18)

    # Explicación del paso actual
    text(surface, 'Explicación del paso', BOTTOM_PANEL_X + 20, BOTTOM_PANEL_Y - 34, med, TITLE)

    if record is None:
        msg = 'Observa el triángulo: el azul es mejor, el amarillo es medio y el rosa es peor. Presiona ESPACIO para iniciar.'
    else:
        msg = state.feedback

    text(surface, msg, BOTTOM_PANEL_X + 20, BOTTOM_PANEL_Y - 5, small, TEXT, BOTTOM_PANEL_W - 40)

    # Controles: se dejan igual, solo bajan dentro del mismo panel
    text(surface, 'Controles', BOTTOM_PANEL_X + 20, BOTTOM_PANEL_Y + 40, med, TITLE)

    line1 = 'ESPACIO: paso   |   TAB: modo reto   |   F reflexión   E expansión   C contracción   D reducción'
    line2 = 'M: automático   |   1 Himmelblau   2 Rosenbrock   3 Rastrigin   4 Sphere   |   R reiniciar   H ayuda'

    text(surface, line1, BOTTOM_PANEL_X + 20, BOTTOM_PANEL_Y + 70, tiny, TEXT)
    text(surface, line2, BOTTOM_PANEL_X + 20, BOTTOM_PANEL_Y + 92, tiny, TEXT)

    mode = 'AUTOMÁTICO' if state.auto else 'MANUAL'
    reto = 'RETO' if state.challenge else 'APRENDIZAJE'
  
    text(
        surface,
        f'Modo: {mode} / {reto}. Cada paso representa una decisión real de Nelder-Mead.',
        BOTTOM_PANEL_X + 20,
        BOTTOM_PANEL_Y + 118,
        tiny,
        MUTED
    )


def title_screen(surface, fonts, tick):
    """Pantalla de bienvenida: explica la metáfora del juego y las teclas para iniciar."""
    big, med, small, tiny = fonts
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0,0,0,178))
    surface.blit(overlay, (0,0))

    box = pygame.Rect(135, 70, 1010, 565)
    pygame.draw.rect(surface, (17,15,30), box, border_radius=24)
    pygame.draw.rect(surface, TITLE, box, 3, border_radius=24)

    text(surface, 'NELDER QUEST', box.x+46, box.y+38, big, TITLE)
    text(surface, 'El triángulo que busca el valle frío', box.x+50, box.y+86, med, COLD)

    lines = [
        'Juego pseudo-3D isométrico para aprender Nelder-Mead.',
        'El simplex es un triángulo de 3 puntos sobre una función f(x,y).',
        'Cada turno ordena los puntos: mejor, medio y peor.',
        'El peor punto se mueve usando reflexión, expansión, contracción o reducción.',
        'TAB activa el modo reto para elegir tú la operación.',
        'El mapa muestra la función: azul/frío es bajo; lava/alto es grande.'
    ]

    y = box.y + 150
    for line in lines:
        y = text(surface, '• ' + line, box.x+52, y, small, TEXT, box.w-104)
        y += 9

    text(surface, 'Funciones: 1 Himmelblau   2 Rosenbrock   3 Rastrigin   4 Sphere', box.x+52, y+18, med, TITLE)
    
    if (tick // 30) % 2 == 0:
        text(surface, 'Presiona ENTER para iniciar', box.x+52, box.bottom-82, med, GOOD)

    text(surface, 'Presiona H para ver ayuda', box.x+52, box.bottom-45, small, MUTED)


def help_screen(surface, fonts):
    """Pantalla de ayuda: explica paso a paso qué representa cada operación de Nelder-Mead."""
    big, med, small, tiny = fonts
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0,0,0,190))
    surface.blit(overlay, (0,0))

    box = pygame.Rect(125, 58, 1030, 605)
    pygame.draw.rect(surface, (17,15,30), box, border_radius=24)
    pygame.draw.rect(surface, COLD, box, 3, border_radius=24)

    text(surface, '¿Qué aprende quien juega?', box.x+42, box.y+34, big, TITLE)

    y = box.y + 96
    lines = [
        '1. El triángulo es el simplex de Nelder-Mead en 2D.',
        '2. Los tres vértices se ordenan por valor de f(x,y): mejor, medio y peor.',
        '3. El centroide se calcula usando los dos mejores puntos, ignorando el peor.',
        '4. Reflexión: el peor se empuja al otro lado del centroide.',
        '5. Expansión: si la reflexión es excelente, se intenta ir más lejos.',
        '6. Contracción: si la reflexión no ayuda, el punto se acerca al centroide.',
        '7. Reducción: si nada funciona, todo el triángulo se encoge hacia el mejor.',
        '8. Victoria/convergencia: el triángulo se vuelve pequeño o los valores de f son casi iguales.',
        '',
        'Modo reto: presiona F, E, C o D para intentar elegir la operación correcta.'
    ]

    for line in lines:
        y = text(surface, line, box.x+48, y, small, TEXT, box.w-96)
        y += 8

    text(surface, 'Presiona H para cerrar.', box.x+48, box.bottom-55, med, COLD)


def final_screen(surface, state, fonts):
    """Pantalla de cierre al converger: muestra el resumen numérico devuelto por nm.resumen()."""
    big, med, small, tiny = fonts
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0,0,0,175))
    surface.blit(overlay, (0,0))

    box = pygame.Rect(190, 108, 900, 510)
    pygame.draw.rect(surface, (17,15,30), box, border_radius=24)
    pygame.draw.rect(surface, GOOD, box, 3, border_radius=24)

    res = state.nm.resumen()
    text(surface, 'Convergencia alcanzada', box.x+46, box.y+40, big, TITLE)
    text(surface, 'El triángulo simplex ya es suficientemente pequeño o sus valores de f son casi iguales.',
         box.x+48, box.y+88, small, MUTED, box.w-96)

    y = box.y + 145
    lines = [
        f"Función: {res['funcion']}",
        f"Mejor punto aproximado: x = {res['x']:.5f}, y = {res['y']:.5f}",
        f"Mejor valor encontrado: f(x,y) = {res['f']:.8f}",
        f"Iteraciones: {res['iteraciones']}",
        f"Tamaño final del simplex: {res['simplex_size']:.6f}",
        f"Desviación final de f: {res['f_std']:.8f}",
        f"Reflexiones: {res['reflexiones']} | Expansiones: {res['expansiones']} | Contracciones: {res['contracciones']} | Reducciones: {res['reducciones']}",
        '',
        'Interpretación: el algoritmo movió el peor vértice hasta encerrar una zona mínima.'
    ]

    for line in lines:
        y = text(surface, line, box.x+50, y, small, TEXT, box.w-100)
        y += 7

    text(surface, 'R = reiniciar   |   1/2/3/4 = cambiar función   |   ESC = salir', box.x+50, box.bottom-55, med, GOOD)
    
# IRONEDIT:1783496901:e165c95e3e0183ad7af43bdb9103146fccc2757d6c837490b1baf7c3c05cedff
