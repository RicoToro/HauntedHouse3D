from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import sys
import random
import math

# ==============================================================================
# VARIÁVEIS GLOBAIS
# Tudo declarado global aqui no topo pra seguir o padrão dos slides da aula
# ==============================================================================
global win, view_w, view_h, texto
global vidas, qtdcolisao, pontos, estado_jogo, qtd_fantasmas, brilho_nivel
global player_x, player_y, player_step_x, player_step_y, passos_fluidos
global chave_x, chave_y, fantasmas

# Tamanho do mundo 2D (vai de -150 a 150 nos eixos X e Y, igual ao exemplo do slide)
win = 150.0
view_w, view_h = 700, 700
texto = "(0,0)"

# Variáveis da partida
vidas = 3
qtdcolisao = 3        # Variável usada no exemplo de correção do professor
pontos = 0
estado_jogo = 1       # 1 = Jogando, 2 = Pausado, 3 = Game Over, 0 = Sair
qtd_fantasmas = 3     # Padrão: 3 fantasmas (muda no menu de dificuldade)
brilho_nivel = 2      # 1 = Escuro (Penumbra), 2 = Normal, 3 = Mais Brilho

# Variáveis do nosso personagem (2D usa X e Y)
player_x = 0.0
player_y = -110.0
player_step_x = 0.0
player_step_y = 0.0
passos_fluidos = 0    # Contador pra dar inércia e deixar o andar fluido
player_raio = 8.0

# Posição inicial da chave
chave_x = 0.0
chave_y = 40.0

# Limites das paredes da mansão 2D (pra não deixar sair da janela)
LIMITE_MIN_X, LIMITE_MAX_X = -140.0, 140.0
LIMITE_MIN_Y, LIMITE_MAX_Y = -135.0, 115.0

# Obstáculos internos do mapa 2D (pilares/móveis vistos de cima) pra ter onde se esconder
OBSTACULOS_2D = [
    {"xmin": -65.0, "xmax": -25.0, "ymin":  20.0, "ymax":  50.0}, # Bloco Sup Esquerdo
    {"xmin":  25.0, "xmax":  65.0, "ymin":  20.0, "ymax":  50.0}, # Bloco Sup Direito
    {"xmin": -25.0, "xmax":  25.0, "ymin": -25.0, "ymax":   5.0}, # Mesa Central
    {"xmin": -70.0, "xmax": -30.0, "ymin": -80.0, "ymax": -55.0}, # Bloco Inf Esquerdo
    {"xmin":  30.0, "xmax":  70.0, "ymin": -80.0, "ymax": -55.0}  # Bloco Inf Direito
]

# Pontos de patrulha pros fantasmas não andarem só em linha reta
WAYPOINTS_2D = [
    (-110.0,  85.0), (0.0,  90.0), (110.0,  85.0),
    (-110.0, -15.0), (110.0, -15.0),
    (-110.0, -110.0), (0.0, -60.0), (110.0, -110.0)
]

# Lista dos fantasmas (o menu de dificuldade escolhe quantos entram no loop: 2, 3 ou 4)
fantasmas = [
    {"x": -110.0, "y":  80.0, "vel": 2.3, "cor": (1.0, 0.15, 0.15), "padrao": "waypoints", "estado": "ronda", "timer": 80,  "cd": 40, "wp": 0, "fase": 0.0, "theta": 0.0},
    {"x":  110.0, "y":  80.0, "vel": 2.2, "cor": (0.75, 0.2, 1.0),  "padrao": "orbita",    "estado": "ronda", "timer": 110, "cd": 50, "wp": 2, "fase": 1.5, "theta": 0.0},
    {"x": -110.0, "y": -40.0, "vel": 2.3, "cor": (0.2, 0.95, 0.5),  "padrao": "curvo",     "estado": "ronda", "timer": 95,  "cd": 45, "wp": 3, "fase": 3.0, "theta": 1.0},
    {"x":  110.0, "y": -40.0, "vel": 2.4, "cor": (1.0, 0.55, 0.1),  "padrao": "espiral",   "estado": "ronda", "timer": 130, "cd": 60, "wp": 4, "fase": 4.5, "theta": 3.1}
]
FANTASMA_RAIO = 9.0

# ==============================================================================
# FUNÇÕES DE COLISÃO E SORTEIO
# ==============================================================================

def VerificaColisao2D(x, y, raio):
    """Checa se o personagem ou fantasma bateu em algum bloco do cenário."""
    for obs in OBSTACULOS_2D:
        if (obs["xmin"] - raio) < x < (obs["xmax"] + raio) and \
           (obs["ymin"] - raio) < y < (obs["ymax"] + raio):
            return True
    return False

def SorteiaChave():
    """Coloca a chave num ponto aleatório que não fique preso dentro dos blocos."""
    while True:
        cx = random.uniform(LIMITE_MIN_X + 15.0, LIMITE_MAX_X - 15.0)
        cy = random.uniform(LIMITE_MIN_Y + 15.0, LIMITE_MAX_Y - 15.0)
        if not VerificaColisao2D(cx, cy, 10.0) and math.hypot(cx - player_x, cy - player_y) > 50.0:
            return cx, cy

def PosicionaPersonagens():
    """Reseta o player lá embaixo e manda os fantasmas pros cantos."""
    global player_x, player_y, player_step_x, player_step_y, passos_fluidos, fantasmas
    player_x, player_y = 0.0, -110.0
    player_step_x, player_step_y = 0.0, 0.0
    passos_fluidos = 0

    cantos = [(-115.0, 85.0), (115.0, 85.0), (-115.0, -35.0), (115.0, -35.0)]
    for i in range(4):
        fantasmas[i]["x"], fantasmas[i]["y"] = cantos[i]
        fantasmas[i]["estado"] = "ronda"
        fantasmas[i]["timer"] = random.randint(70, 140)
        fantasmas[i]["cd"] = random.randint(40, 80)

# ==============================================================================
# DESENHO DE TEXTO E PRIMITIVAS 2D (glBegin / glEnd)
# ==============================================================================

def DesenhaTexto(string):
    """Função de texto igualzinha à do slide de correção."""
    glPushMatrix()
    for char in string:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
    glPopMatrix()

def DesenhaTextoPequeno(string):
    glPushMatrix()
    for char in string:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(char))
    glPopMatrix()

def Comentarios():
    """Mostra o placar, vidas e coordenadas do mouse no topo da janela."""
    global qtdcolisao, pontos, qtd_fantasmas, texto, estado_jogo
    
    glColor3f(1.0, 1.0, 1.0)
    glRasterPos2f(-142.0, 136.0)
    barras = "|" * qtdcolisao
    p = "{0:s} - Numero de Vidas ({1:d})   |   Pontos: {2:d}   |   Fantasmas: {3:d}".format(barras, qtdcolisao, pontos, qtd_fantasmas)
    DesenhaTexto(p)

    glColor3f(0.8, 0.85, 1.0)
    glRasterPos2f(-142.0, 123.0)
    DesenhaTextoPequeno("Setas ou WASD: Mover | P: Pausar | R: Reiniciar | Botao Direito: MENU | Mouse: " + texto)

    if estado_jogo == 2:
        glColor3f(1.0, 1.0, 0.0)
        glRasterPos2f(-35.0, 10.0)
        DesenhaTexto("JOGO PAUSADO")
    elif estado_jogo == 3:
        glColor3f(1.0, 0.2, 0.2)
        glRasterPos2f(-85.0, 10.0)
        DesenhaTexto("FIM DE JOGO! Use o Menu para Reiniciar")

def DesenhaMapa2D():
    """Desenha o chão, as bordas da sala e os móveis/obstáculos usando GL_QUADS."""
    global brilho_nivel
    # Fator que muda o brilho das cores conforme escolhido no menu (0.5 = escuro, 0.85 = médio, 1.25 = claro)
    fator = [0.5, 0.85, 1.25][brilho_nivel - 1]

    # Ladrilhos de fundo da Casa Assombrada
    for ix in range(-140, 140, 20):
        for iy in range(-135, 115, 25):
            if ((ix // 20) + (iy // 25)) % 2 == 0:
                glColor3f(0.12 * fator, 0.09 * fator, 0.18 * fator)
            else:
                glColor3f(0.15 * fator, 0.11 * fator, 0.22 * fator)
            glBegin(GL_QUADS)
            glVertex2f(float(ix), float(iy))
            glVertex2f(float(ix + 20), float(iy))
            glVertex2f(float(ix + 20), float(iy + 25))
            glVertex2f(float(ix), float(iy + 25))
            glEnd()

    # Moldura das paredes (Limites da arena)
    glColor3f(0.45 * fator, 0.30 * fator, 0.60 * fator)
    glLineWidth(3.0)
    glBegin(GL_LINE_LOOP)
    glVertex2f(LIMITE_MIN_X, LIMITE_MIN_Y)
    glVertex2f(LIMITE_MAX_X, LIMITE_MIN_Y)
    glVertex2f(LIMITE_MAX_X, LIMITE_MAX_Y)
    glVertex2f(LIMITE_MIN_X, LIMITE_MAX_Y)
    glEnd()

    # Desenha os móveis/pilares onde não dá pra atravessar
    for obs in OBSTACULOS_2D:
        # Preenchimento de madeira escura
        glColor3f(0.35 * fator, 0.20 * fator, 0.10 * fator)
        glBegin(GL_QUADS)
        glVertex2f(obs["xmin"], obs["ymin"])
        glVertex2f(obs["xmax"], obs["ymin"])
        glVertex2f(obs["xmax"], obs["ymax"])
        glVertex2f(obs["xmin"], obs["ymax"])
        glEnd()
        # Borda do móvel
        glColor3f(0.55 * fator, 0.35 * fator, 0.20 * fator)
        glBegin(GL_LINE_LOOP)
        glVertex2f(obs["xmin"], obs["ymin"])
        glVertex2f(obs["xmax"], obs["ymin"])
        glVertex2f(obs["xmax"], obs["ymax"])
        glVertex2f(obs["xmin"], obs["ymax"])
        glEnd()

def DesenhaJogador2D():
    """Desenha o nosso boneco usando GL_QUADS, GL_POLYGON e GL_TRIANGLES."""
    global player_x, player_y, brilho_nivel
    fator = min([0.65, 1.0, 1.2][brilho_nivel - 1], 1.0)

    glPushMatrix()
    glTranslatef(player_x, player_y, 0.0)

    # Corpo (Azul)
    glColor3f(0.1 * fator, 0.55 * fator, 1.0 * fator)
    glBegin(GL_QUADS)
    glVertex2f(-6.5, -7.5)
    glVertex2f( 6.5, -7.5)
    glVertex2f( 6.5,  2.5)
    glVertex2f(-6.5,  2.5)
    glEnd()

    # Cabeça redonda feita com GL_POLYGON
    glColor3f(1.0 * fator, 0.85 * fator, 0.7 * fator)
    glBegin(GL_POLYGON)
    for i in range(14):
        ang = 2.0 * math.pi * i / 14
        glVertex2f(math.cos(ang) * 5.0, 3.5 + math.sin(ang) * 5.0)
    glEnd()

    # Chapéu de caçador (GL_TRIANGLES)
    glColor3f(0.2 * fator, 0.3 * fator, 0.6 * fator)
    glBegin(GL_TRIANGLES)
    glVertex2f(-6.0, 6.5)
    glVertex2f( 6.0, 6.5)
    glVertex2f( 0.0, 11.5)
    glEnd()

    glPopMatrix()

def DesenhaChave2D():
    """Desenha a chave dourada no mapa."""
    global chave_x, chave_y
    glPushMatrix()
    glTranslatef(chave_x, chave_y, 0.0)
    glColor3f(1.0, 0.85, 0.0)

    # Argola da chave (Losango / Polígono)
    glBegin(GL_POLYGON)
    glVertex2f(-7.0,  0.0)
    glVertex2f(-3.5,  3.5)
    glVertex2f( 0.0,  0.0)
    glVertex2f(-3.5, -3.5)
    glEnd()

    # Haste e dentes (GL_QUADS)
    glBegin(GL_QUADS)
    glVertex2f(0.0, -1.2); glVertex2f(7.0, -1.2); glVertex2f(7.0, 1.2); glVertex2f(0.0, 1.2)
    glVertex2f(3.5, -4.0); glVertex2f(4.8, -4.0); glVertex2f(4.8, -1.2); glVertex2f(3.5, -1.2)
    glVertex2f(5.7, -4.0); glVertex2f(7.0, -4.0); glVertex2f(7.0, -1.2); glVertex2f(5.7, -1.2)
    glEnd()
    glPopMatrix()

def DesenhaFantasmas2D():
    """Desenha os fantasmas activos. Os olhos ficam amarelos quando estão dando bote."""
    global fantasmas, qtd_fantasmas, brilho_nivel
    fator = min([0.65, 1.0, 1.2][brilho_nivel - 1], 1.0)

    for i in range(qtd_fantasmas):
        f = fantasmas[i]
        glPushMatrix()
        glTranslatef(f["x"], f["y"], 0.0)

        glColor3f(f["cor"][0] * fator, f["cor"][1] * fator, f["cor"][2] * fator)
        # Corpo do fantasma
        glBegin(GL_POLYGON)
        glVertex2f(-8.0, -8.0)
        glVertex2f( 8.0, -8.0)
        glVertex2f( 8.0,  2.0)
        for j in range(9):
            ang = math.pi * j / 8
            glVertex2f(math.cos(ang) * 8.0, 2.0 + math.sin(ang) * 6.5)
        glEnd()

        # Olhos (Brancos na ronda, Amarelos no bote!)
        if f["estado"] == "ataque":
            glColor3f(1.0, 1.0, 0.0)
        else:
            glColor3f(1.0, 1.0, 1.0)
        glBegin(GL_QUADS)
        glVertex2f(-5.0, 1.0); glVertex2f(-1.5, 1.0); glVertex2f(-1.5, 4.5); glVertex2f(-5.0, 4.5)
        glVertex2f( 1.5, 1.0); glVertex2f( 5.0, 1.0); glVertex2f( 5.0, 4.5); glVertex2f( 1.5, 4.5)
        glEnd()

        # Pupilas
        glColor3f(0.0, 0.0, 0.0)
        glBegin(GL_QUADS)
        glVertex2f(-3.8, 1.8); glVertex2f(-2.0, 1.8); glVertex2f(-2.0, 3.5); glVertex2f(-3.8, 3.5)
        glVertex2f( 2.0, 1.8); glVertex2f( 3.8, 1.8); glVertex2f( 3.8, 3.5); glVertex2f( 2.0, 3.5)
        glEnd()

        glPopMatrix()

# ==============================================================================
# FUNÇÃO DESENHA PRINCIPAL (Padrão Slide 93)
# ==============================================================================

def Desenha():
    global estado_jogo, brilho_nivel
    if estado_jogo == 0:
        sys.exit(0)

    # Ajusta a cor de fundo conforme o brilho escolhido no menu
    fator_bg = [0.4, 1.0, 1.6][brilho_nivel - 1]
    glClearColor(0.06 * fator_bg, 0.05 * fator_bg, 0.10 * fator_bg, 1.0)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glClear(GL_COLOR_BUFFER_BIT)

    DesenhaMapa2D()
    DesenhaChave2D()
    DesenhaJogador2D()
    DesenhaFantasmas2D()
    Comentarios()

    glutSwapBuffers()

# ==============================================================================
# TIMER (33ms - Movimento fluido do player e IA dos fantasmas)
# ==============================================================================

def Timer(value):
    global player_x, player_y, player_step_x, player_step_y, passos_fluidos
    global chave_x, chave_y, fantasmas, qtd_fantasmas, pontos, vidas, qtdcolisao, estado_jogo

    if estado_jogo == 1:
        # 1. Movimento fluido do jogador com deslize (inércia) e colisão nos eixos X e Y separados
        if passos_fluidos > 0:
            passos_fluidos -= 1
            nx = player_x + player_step_x
            ny = player_y + player_step_y

            if (LIMITE_MIN_X + player_raio) <= nx <= (LIMITE_MAX_X - player_raio) and not VerificaColisao2D(nx, player_y, player_raio):
                player_x = nx
            if (LIMITE_MIN_Y + player_raio) <= ny <= (LIMITE_MAX_Y - player_raio) and not VerificaColisao2D(player_x, ny, player_raio):
                player_y = ny

            # Desacelera suave em vez de parar seco
            player_step_x *= 0.85
            player_step_y *= 0.85

        # 2. IA dos fantasmas (Rondas Curvas + Bote Temporário)
        atacando_agora = sum(1 for i in range(qtd_fantasmas) if fantasmas[i]["estado"] == "ataque")

        for i in range(qtd_fantasmas):
            f = fantasmas[i]
            f["fase"] += 0.12
            if f["cd"] > 0:
                f["cd"] -= 1

            dist_p = math.hypot(player_x - f["x"], player_y - f["y"])
            f["timer"] -= 1

            # Decide quando entra em ataque e quando cansa e volta pra ronda
            if f["estado"] == "ronda":
                if ((dist_p < 75.0 and f["cd"] == 0) or (f["timer"] <= 0 and f["cd"] == 0 and random.random() < 0.4)) and atacando_agora < 2:
                    f["estado"] = "ataque"
                    f["timer"] = random.randint(75, 115)
                    atacando_agora += 1
                elif f["timer"] <= 0:
                    f["timer"] = random.randint(80, 140)
            elif f["estado"] == "ataque":
                if f["timer"] <= 0:
                    f["estado"] = "ronda"
                    f["cd"] = random.randint(90, 150)
                    f["timer"] = random.randint(90, 150)
                    atacando_agora -= 1

            vel = f["vel"] * 1.25 if f["estado"] == "ataque" else f["vel"]

            if f["estado"] == "ataque":
                alvo_x = player_x + math.sin(f["fase"] * 2.0) * 12.0
                alvo_y = player_y + math.cos(f["fase"] * 2.0) * 12.0
            else:
                if f["padrao"] == "waypoints":
                    wx, wy = WAYPOINTS_2D[f["wp"]]
                    if math.hypot(wx - f["x"], wy - f["y"]) < 20.0:
                        f["wp"] = random.randint(0, len(WAYPOINTS_2D) - 1)
                        wx, wy = WAYPOINTS_2D[f["wp"]]
                    alvo_x = wx + math.sin(f["fase"]) * 25.0
                    alvo_y = wy + math.cos(f["fase"]) * 25.0
                elif f["padrao"] == "orbita":
                    f["theta"] += 0.04
                    alvo_x = math.cos(f["theta"]) * 90.0
                    alvo_y = -10.0 + math.sin(f["theta"]) * 65.0
                elif f["padrao"] == "curvo":
                    f["theta"] += random.uniform(-0.15, 0.15)
                    alvo_x = f["x"] + math.cos(f["theta"]) * 50.0
                    alvo_y = f["y"] + math.sin(f["theta"]) * 50.0
                else:
                    f["theta"] += 0.05
                    alvo_x = chave_x + math.cos(f["theta"]) * 45.0
                    alvo_y = chave_y + math.sin(f["theta"]) * 45.0

            dx = alvo_x - f["x"]
            dy = alvo_y - f["y"]
            norma = math.hypot(dx, dy)
            if norma > 0.001:
                dx = (dx / norma) * vel
                dy = (dy / norma) * vel

            fx_novo = f["x"] + dx
            fy_novo = f["y"] + dy

            livre_x = (LIMITE_MIN_X + FANTASMA_RAIO <= fx_novo <= LIMITE_MAX_X - FANTASMA_RAIO) and not VerificaColisao2D(fx_novo, f["y"], FANTASMA_RAIO)
            livre_y = (LIMITE_MIN_Y + FANTASMA_RAIO <= fy_novo <= LIMITE_MAX_Y - FANTASMA_RAIO) and not VerificaColisao2D(f["x"], fy_novo, FANTASMA_RAIO)

            # Desvia dos móveis deslizando pela borda
            if livre_x and livre_y:
                f["x"], f["y"] = fx_novo, fy_novo
            elif livre_x:
                f["x"] += (1.0 if dx >= 0 else -1.0) * vel
            elif livre_y:
                f["y"] += (1.0 if dy >= 0 else -1.0) * vel
            else:
                f["theta"] += 1.5
                f["wp"] = (f["wp"] + 1) % len(WAYPOINTS_2D)

        # 3. Colisão Jogador <-> Chave
        if math.hypot(player_x - chave_x, player_y - chave_y) < 15.0:
            pontos += 10
            chave_x, chave_y = SorteiaChave()

        # 4. Colisão Jogador <-> Fantasmas
        for i in range(qtd_fantasmas):
            f = fantasmas[i]
            if math.hypot(player_x - f["x"], player_y - f["y"]) < (player_raio + FANTASMA_RAIO):
                vidas -= 1
                qtdcolisao = vidas
                PosicionaPersonagens()
                if vidas <= 0:
                    estado_jogo = 3
                break

    glutPostRedisplay()
    glutTimerFunc(33, Timer, 1)

# ==============================================================================
# EVENTOS DE TECLADO, MOUSE E MENU (Padrão Intr_OpenGL(Parte2_Menus1).pdf)
# ==============================================================================

def GerenciaTeclado(key, x, y):
    """Controla o boneco no WASD e atalhos de pausa/reiniciar."""
    global player_step_x, player_step_y, passos_fluidos, estado_jogo
    global vidas, qtdcolisao, pontos, chave_x, chave_y

    impulso = 4.8
    if key == b'w' or key == b'W':
        player_step_y = impulso
        passos_fluidos = 10
    elif key == b's' or key == b'S':
        player_step_y = -impulso
        passos_fluidos = 10
    elif key == b'a' or key == b'A':
        player_step_x = -impulso
        passos_fluidos = 10
    elif key == b'd' or key == b'D':
        player_step_x = impulso
        passos_fluidos = 10
    elif key == b'p' or key == b'P':
        estado_jogo = 2 if estado_jogo == 1 else 1
    elif key == b'r' or key == b'R':
        vidas, qtdcolisao, pontos, estado_jogo = 3, 3, 0, 1
        PosicionaPersonagens()
        chave_x, chave_y = SorteiaChave()

    glutPostRedisplay()

def TeclasEspeciais(key, x, y):
    """Também permite andar usando as setinhas do teclado."""
    global player_step_x, player_step_y, passos_fluidos
    impulso = 4.8
    if key == GLUT_KEY_UP:
        player_step_y = impulso
        passos_fluidos = 10
    elif key == GLUT_KEY_DOWN:
        player_step_y = -impulso
        passos_fluidos = 10
    elif key == GLUT_KEY_LEFT:
        player_step_x = -impulso
        passos_fluidos = 10
    elif key == GLUT_KEY_RIGHT:
        player_step_x = impulso
        passos_fluidos = 10
    glutPostRedisplay()

def MoveMouseBotaoPressionado(x, y):
    global texto
    texto = "Botao pressionado ({0:d}, {1:d})".format(x, y)
    glutPostRedisplay()

def MoveMouse(x, y):
    global texto
    texto = "(" + str(x) + ", " + str(y) + ")"
    glutPostRedisplay()

def GerenciaMouse(button, state, x, y):
    if button == GLUT_RIGHT_BUTTON:
        if state == GLUT_DOWN:
            CriaMenu()
    glutPostRedisplay()

def MenuDificuldade(op):
    """Seleciona o número de fantasmas pelo menu."""
    global qtd_fantasmas, vidas, qtdcolisao, pontos, estado_jogo, chave_x, chave_y
    if op == 0:   qtd_fantasmas = 2
    elif op == 1: qtd_fantasmas = 3
    elif op == 2: qtd_fantasmas = 4
    vidas, qtdcolisao, pontos, estado_jogo = 3, 3, 0, 1
    PosicionaPersonagens()
    chave_x, chave_y = SorteiaChave()
    glutPostRedisplay()
    return 0

def MenuCorBrilho(op):
    """Muda para mais brilho ou menos brilho conforme pedido."""
    global brilho_nivel
    if op == 0:   brilho_nivel = 1 # Menos Brilho (Escuro)
    elif op == 1: brilho_nivel = 2 # Brilho Normal
    elif op == 2: brilho_nivel = 3 # Mais Brilho (Claro)
    glutPostRedisplay()
    return 0

def MenuPrincipal(op):
    global vidas, qtdcolisao, pontos, estado_jogo, chave_x, chave_y
    if op == 0:
        vidas, qtdcolisao, pontos, estado_jogo = 3, 3, 0, 1
        PosicionaPersonagens()
        chave_x, chave_y = SorteiaChave()
    elif op == 1:
        estado_jogo = 2 if estado_jogo == 1 else 1
    elif op == 2:
        estado_jogo = 0
    glutPostRedisplay()
    return 0

def CriaMenu():
    """Cria o menu e os submenus no mesmo formato do Slide 98."""
    submenu1 = glutCreateMenu(MenuDificuldade)
    glutAddMenuEntry(b"Facil (2 Fantasmas)", 0)
    glutAddMenuEntry(b"Medio (3 Fantasmas)", 1)
    glutAddMenuEntry(b"Dificil (4 Fantasmas)", 2)

    submenu2 = glutCreateMenu(MenuCorBrilho)
    glutAddMenuEntry(b"Menos Brilho (Escuro)", 0)
    glutAddMenuEntry(b"Brilho Normal", 1)
    glutAddMenuEntry(b"Mais Brilho (Claro)", 2)

    menu = glutCreateMenu(MenuPrincipal)
    glutAddSubMenu(b"Dificuldade (N. de Fantasmas)", submenu1)
    glutAddSubMenu(b"Cor / Brilho", submenu2)
    glutAddMenuEntry(b"Iniciar / Reiniciar", 0)
    glutAddMenuEntry(b"Pausar / Continuar", 1)
    glutAddMenuEntry(b"Desligar", 2)
    glutAttachMenu(GLUT_RIGHT_BUTTON)
    return 0

# ==============================================================================
# INICIALIZAÇÃO E CONFIGURAÇÃO DE JANELA 2D (Slide 94)
# ==============================================================================

def AlteraTamanhoJanela(w, h):
    global view_w, view_h, win
    if h == 0:
        h = 1
    glViewport(0, 0, w, h)
    view_w = w
    view_h = h
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(-win, win, -win, win)

def Inicializa():
    global win, vidas, qtdcolisao, pontos, estado_jogo, chave_x, chave_y, texto
    glClearColor(0.06, 0.05, 0.10, 1.0)
    win = 150.0
    texto = "(0,0)"
    vidas, qtdcolisao, pontos, estado_jogo = 3, 3, 0, 1
    PosicionaPersonagens()
    chave_x, chave_y = SorteiaChave()
    CriaMenu()

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(700, 700)
    glutInitWindowPosition(10, 10)
    glutCreateWindow(b"Projeto CG - Jogo 4: Haunted House (Parte 2D)")
    
    glutDisplayFunc(Desenha)
    glutReshapeFunc(AlteraTamanhoJanela)
    glutKeyboardFunc(GerenciaTeclado)
    glutSpecialFunc(TeclasEspeciais)
    glutMotionFunc(MoveMouseBotaoPressionado)
    glutPassiveMotionFunc(MoveMouse)
    glutMouseFunc(GerenciaMouse)
    glutTimerFunc(33, Timer, 1)
    
    Inicializa()
    glutMainLoop()

main()
