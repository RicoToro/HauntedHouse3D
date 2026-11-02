from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import sys
import random
import math

# VARIÁVEIS GLOBAIS
# Declarando tudo global pra conseguir acessar de dentro das callbacks do GLUT.

global angle, fAspect, view_w, view_h, texto
global anguloX, anguloY, camX, camY, camZ
global vidas, pontos, qtdcolisao, estado_jogo, qtd_fantasmas, modo_luz
global player_x, player_z, player_step_x, player_step_z, passos_fluidos, player_dir
global chave_x, chave_z, angulo_chave, fantasmas

# Setup inicial da câmera 3D
angle = 45.0          # Zoom
fAspect = 1.0         # Proporção da tela
view_w, view_h = 800, 600
anguloX, anguloY = 0.0, 20.0  # Rotação da cena (setinhas do teclado)
camX, camY, camZ = 0.0, 16.0, 24.0 # Posição da câmera (X, Y, Z)
texto = "(0,0)"       # Pra mostrar o (x,y) do mouse na tela

# Variáveis do jogo
vidas = 3
qtdcolisao = 3        # Cópia das vidas pra mostrar no texto, igual ao exemplo da aula
pontos = 0
estado_jogo = 1       # 1 = Jogando, 2 = Pausado, 3 = Game Over, 0 = Sair
qtd_fantasmas = 3     # Dificuldade média por padrão
modo_luz = 1          # Luz normal de início (1 a 5)

# Variáveis do nosso boneco
player_x = 0.0
player_z = 7.0
player_step_x = 0.0   # Velocidade em X
player_step_z = 0.0   # Velocidade em Z
passos_fluidos = 0    # Contador pra dar aquele efeito de deslizar/inércia
player_dir = 180.0    # Pra onde o boneco tá olhando
player_raio = 0.55    # Hitbox do jogador

# Variáveis da chave (coletável)
chave_x = 4.0
chave_z = -2.0
angulo_chave = 0.0    # Pra chave ficar girando na tela

# Limites do mapa (chão)
LIMITE_X_MIN, LIMITE_X_MAX = -11.0, 11.0
LIMITE_Z_MIN, LIMITE_Z_MAX = -8.8, 9.0

# Hitboxes dos móveis pra ninguém atravessar parede (AABB)
OBSTACULOS = [
    {"xmin": -3.1, "xmax": 3.1,  "zmin": -7.2, "zmax": -4.8}, # Sofá
    {"xmin": -2.1, "xmax": 2.1,  "zmin": -0.8, "zmax":  1.8}, # Mesa
    {"xmin": -11.5,"xmax": -9.9, "zmin": -1.6, "zmax":  3.6}, # Estante
    {"xmin":  5.8, "xmax": 7.2,  "zmin": -6.7, "zmax": -5.3}, # Abajur
    {"xmin": -8.4, "xmax": -5.6, "zmin": -9.6, "zmax": -8.8}  # Porta
]

# Pontos de patrulha pros fantasmas ficarem andando pela sala
WAYPOINTS = [
    (-8.5, -6.5), (0.0, -8.2), (8.5, -6.5), (8.5, 0.5),
    (8.5, 6.8),   (0.0, 7.2),  (-8.5, 6.8), (-6.0, -2.5), (5.5, -2.5)
]

# Config dos fantasmas. Cada um tem um comportamento e uma cor diferente.
fantasmas = [
    {"x": -8.0, "z": -6.0, "vel": 0.18, "cor": (1.0, 0.15, 0.15), "padrao": "waypoints", "estado": "ronda", "timer": 80,  "cd": 40, "wp": 0, "fase": 0.0, "theta": 0.0, "ang": 0.0},
    {"x":  8.0, "z": -6.0, "vel": 0.17, "cor": (0.75, 0.2, 1.0),  "padrao": "orbita",    "estado": "ronda", "timer": 110, "cd": 50, "wp": 1, "fase": 1.5, "theta": 0.0, "ang": 0.0},
    {"x": -8.0, "z":  4.0, "vel": 0.18, "cor": (0.2, 0.95, 0.5),  "padrao": "curvo",     "estado": "ronda", "timer": 95,  "cd": 45, "wp": 2, "fase": 3.0, "theta": 1.0, "ang": 45.0},
    {"x":  8.0, "z":  4.0, "vel": 0.19, "cor": (1.0, 0.55, 0.1),  "padrao": "espiral",   "estado": "ronda", "timer": 130, "cd": 60, "wp": 3, "fase": 4.5, "theta": 3.1, "ang": 0.0}
]
FANTASMA_RAIO = 0.60

# LÓGICA DE JOGO E COLISÕES

def VerificaColisaoMoveis(x, z, raio):
    """Checa se a posição (x, z) tá batendo em algum móvel da lista de obstáculos."""
    for obs in OBSTACULOS:
        if (obs["xmin"] - raio) < x < (obs["xmax"] + raio) and \
           (obs["zmin"] - raio) < z < (obs["zmax"] + raio):
            return True # Bateu!
    return False

def SorteiaChave():
    """Gera um respawn pra chave num lugar livre (fora dos móveis e longe de mim)."""
    while True:
        cx = random.uniform(LIMITE_X_MIN + 1.5, LIMITE_X_MAX - 1.5)
        cz = random.uniform(LIMITE_Z_MIN + 1.5, LIMITE_Z_MAX - 1.5)
        if not VerificaColisaoMoveis(cx, cz, 0.8) and math.hypot(cx - player_x, cz - player_z) > 4.0:
            return cx, cz

def PosicionaPersonagens():
    """Dá um reset geral nas posições (bom pra quando o jogo começa ou quando tomo dano)."""
    global player_x, player_z, player_step_x, player_step_z, passos_fluidos, fantasmas
    
    player_x, player_z = 0.0, 7.0
    player_step_x, player_step_z = 0.0, 0.0
    passos_fluidos = 0
    
    # Joga os fantasmas pros cantos da sala pra não me matarem na hora
    cantos = [(-8.5, -6.5), (8.5, -6.5), (-8.5, 3.5), (8.5, 3.5)]
    for i in range(4):
        fantasmas[i]["x"], fantasmas[i]["z"] = cantos[i]
        fantasmas[i]["estado"] = "ronda"
        fantasmas[i]["timer"] = random.randint(70, 140)
        fantasmas[i]["cd"] = random.randint(40, 80)

# HUD E TEXTOS NA TELA (2D)

def DesenhaTexto(string):
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
    """Escreve os status na tela por cima do 3D (HUD)."""
    global qtdcolisao, pontos, qtd_fantasmas, modo_luz, texto, estado_jogo
    
    # Desativa luz e profundidade rapidinho só pra escrever na tela
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)
    
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0.0, 800.0, 0.0, 600.0) # Modo 2D
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # Barra superior (Vidas, Pontos, etc) - igual ao formato pedido nas aulas
    glColor3f(1.0, 1.0, 1.0)
    glRasterPos2f(20.0, 570.0)
    barras = "|" * qtdcolisao
    p = "{0:s} - Numero de Vidas ({1:d})   |   Pontos: {2:d}   |   Fantasmas: {3:d}".format(barras, qtdcolisao, pontos, qtd_fantasmas)
    DesenhaTexto(p)

    # Legenda dos controles na parte de baixo
    glColor3f(0.8, 0.9, 1.0)
    glRasterPos2f(20.0, 545.0)
    DesenhaTextoPequeno("WASD: Mover | Setas: Girar Sala | Clique Esq ou Z/X: Zoom | 1-5: Luz | Botao Direito: MENU | Mouse: " + texto)

    # Avisos grandes no meio da tela
    if estado_jogo == 2:
        glColor3f(1.0, 1.0, 0.0)
        glRasterPos2f(310.0, 310.0)
        DesenhaTexto("JOGO PAUSADO")
    elif estado_jogo == 3:
        glColor3f(1.0, 0.2, 0.2)
        glRasterPos2f(260.0, 310.0)
        DesenhaTexto("FIM DE JOGO! Use o Menu para Reiniciar")

    # Devolve tudo pro 3D
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)

# CONFIGS DE LUZ E MATERIAL (Baseado nos slides da disciplina)

def iluminacao():
    """Gerencia a iluminação e as cores dependendo da tecla que apertar (1 a 5)."""
    global modo_luz
    
    if modo_luz == 1:   # Normal
        luzAmbiente = [0.35, 0.35, 0.35, 1.0]
        luzDifusa   = [0.75, 0.75, 0.75, 1.0]
    elif modo_luz == 2: # Fraca (Clima de terror)
        luzAmbiente = [0.08, 0.08, 0.12, 1.0]
        luzDifusa   = [0.22, 0.22, 0.32, 1.0]
    elif modo_luz == 3: # Vermelho
        luzAmbiente = [0.3, 0.0, 0.0, 1.0]
        luzDifusa   = [1.0, 0.0, 0.0, 1.0]
    elif modo_luz == 4: # Verde
        luzAmbiente = [0.0, 0.3, 0.0, 1.0]
        luzDifusa   = [0.0, 1.0, 0.0, 1.0]
    elif modo_luz == 5: # Azul
        luzAmbiente = [0.0, 0.0, 0.35, 1.0]
        luzDifusa   = [0.1, 0.3, 1.0, 1.0]

    luzEspecular   = [0.5, 0.5, 0.5, 1.0]
    posicaoLuz     = [6.5, 4.5, -6.0, 1.0] # Posição na lâmpada do abajur
    
    especularidade = [0.4, 0.4, 0.4, 0.4]
    especMaterial  = 50

    glClearColor(0.05, 0.05, 0.08, 1.0) # Cor do fundo da tela
    glShadeModel(GL_SMOOTH)
    
    # Refletância do material
    glMaterialfv(GL_FRONT, GL_SPECULAR, especularidade)
    glMateriali(GL_FRONT, GL_SHININESS, especMaterial)
    
    # Ativa as luzes
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, luzAmbiente)
    glLightfv(GL_LIGHT0, GL_AMBIENT, luzAmbiente)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, luzDifusa)
    glLightfv(GL_LIGHT0, GL_SPECULAR, luzEspecular)
    glLightfv(GL_LIGHT0, GL_POSITION, posicaoLuz)

    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_DEPTH_TEST) 
    glEnable(GL_NORMALIZE)

# MODELAGEM 3D (Cenário, Personagens e Itens)

def chao():
    # Base do piso
    glColor3f(0.28, 0.18, 0.10)
    glPushMatrix()
    glTranslatef(0.0, -0.3, 0.0)
    glScalef(24.0, 0.6, 20.0)
    glutSolidCube(1.0)
    glPopMatrix()

    # Desenha um quadriculado no chão pra dar noção de movimento
    glColor3f(0.22, 0.14, 0.08)
    glBegin(GL_QUADS)
    for ix in range(-12, 12, 2):
        for iz in range(-10, 10, 2):
            if (ix + iz) % 4 == 0:
                glVertex3f(float(ix), 0.02, float(iz))
                glVertex3f(float(ix + 2), 0.02, float(iz))
                glVertex3f(float(ix + 2), 0.02, float(iz + 2))
                glVertex3f(float(ix), 0.02, float(iz + 2))
    glEnd()

def paredes():
    # Parede do fundo
    glColor3f(0.40, 0.33, 0.44)
    glPushMatrix(); glTranslatef(0.0, 3.5, -9.75); glScalef(24.0, 7.0, 0.5); glutSolidCube(1.0); glPopMatrix()
    # Parede da esquerda
    glColor3f(0.36, 0.29, 0.40)
    glPushMatrix(); glTranslatef(-11.75, 3.5, 0.0); glScalef(0.5, 7.0, 20.0); glutSolidCube(1.0); glPopMatrix()

def porta():
    glPushMatrix()
    glTranslatef(-7.0, 2.5, -9.3)
    glColor3f(0.2, 0.1, 0.05)
    glPushMatrix(); glScalef(2.6, 5.0, 0.3); glutSolidCube(1.0); glPopMatrix() # Batente
    glColor3f(0.45, 0.22, 0.08)
    glPushMatrix(); glTranslatef(0.0, 0.0, 0.1); glScalef(2.2, 4.7, 0.25); glutSolidCube(1.0); glPopMatrix() # Porta
    glColor3f(0.9, 0.8, 0.1)
    glPushMatrix(); glTranslatef(0.8, -0.1, 0.25); glutSolidSphere(0.14, 12, 12); glPopMatrix() # Maçaneta
    glPopMatrix()

def sofa():
    glPushMatrix()
    glTranslatef(0.0, 0.45, -6.0)
    glColor3f(0.55, 0.12, 0.15)
    glPushMatrix(); glScalef(6.0, 0.9, 2.2); glutSolidCube(1.0); glPopMatrix() # Assento
    glPushMatrix(); glTranslatef(0.0, 1.1, -0.85); glScalef(6.0, 1.5, 0.5); glutSolidCube(1.0); glPopMatrix() # Encosto
    glPushMatrix(); glTranslatef(-2.75, 0.6, 0.0); glScalef(0.5, 1.1, 2.2); glutSolidCube(1.0); glPopMatrix() # Braço esq
    glPushMatrix(); glTranslatef(2.75, 0.6, 0.0);  glScalef(0.5, 1.1, 2.2); glutSolidCube(1.0); glPopMatrix() # Braço dir
    glPopMatrix()

def mesa():
    glPushMatrix()
    glTranslatef(0.0, 0.0, 0.5)
    glColor3f(0.32, 0.18, 0.08)
    glPushMatrix(); glTranslatef(0.0, 1.3, 0.0); glScalef(4.0, 0.22, 2.4); glutSolidCube(1.0); glPopMatrix() # Tampo
    # Pernas da mesa (loopzinho pra facilitar)
    for px in [-1.7, 1.7]:
        for pz in [-0.9, 0.9]:
            glPushMatrix(); glTranslatef(px, 0.65, pz); glScalef(0.22, 1.3, 0.22); glutSolidCube(1.0); glPopMatrix()
    glPopMatrix()

def estante():
    glPushMatrix()
    glTranslatef(-10.7, 0.0, 1.0)
    glRotatef(90.0, 0.0, 1.0, 0.0) # Vira de lado pra colar na parede
    glColor3f(0.28, 0.15, 0.05)
    glPushMatrix(); glTranslatef(0.0, 2.6, -0.5); glScalef(4.8, 5.2, 0.15); glutSolidCube(1.0); glPopMatrix()
    for lx in [-2.3, 2.3]:
        glPushMatrix(); glTranslatef(lx, 2.6, 0.0); glScalef(0.2, 5.2, 1.2); glutSolidCube(1.0); glPopMatrix()
    for py in [0.3, 1.8, 3.3, 5.0]:
        glPushMatrix(); glTranslatef(0.0, py, 0.0); glScalef(4.8, 0.2, 1.2); glutSolidCube(1.0); glPopMatrix()
    
    # Colocando uns livros só pra não ficar vazia
    cores = [(0.8,0.1,0.1), (0.1,0.6,0.2), (0.1,0.2,0.8), (0.8,0.7,0.1), (0.6,0.1,0.6)]
    for i, c in enumerate(cores):
        glColor3f(c[0], c[1], c[2])
        glPushMatrix(); glTranslatef(-1.4 + i * 0.7, 3.85, 0.0); glScalef(0.45, 0.9, 0.8); glutSolidCube(1.0); glPopMatrix()
    glPopMatrix()

def abajur():
    glPushMatrix()
    glTranslatef(6.5, 0.0, -6.0)
    glColor3f(0.2, 0.2, 0.2)
    glPushMatrix(); glTranslatef(0.0, 0.15, 0.0); glScalef(1.2, 0.3, 1.2); glutSolidCube(1.0); glPopMatrix()
    glPushMatrix(); glTranslatef(0.0, 2.2, 0.0);  glScalef(0.16, 4.2, 0.16); glutSolidCube(1.0); glPopMatrix()
    
    # Cúpula amarela (tem que girar o cone pq o GLUT faz ele apontando no eixo Z)
    glColor3f(1.0, 0.9, 0.4)
    glPushMatrix()
    glTranslatef(0.0, 4.4, 0.0)
    glRotatef(-90.0, 1.0, 0.0, 0.0)
    glutSolidCone(0.9, 1.2, 16, 8)
    glPopMatrix()
    glPopMatrix()

def desenhaJogador():
    """Monta o nosso bonequinho e gira ele pro lado que tá andando."""
    global player_x, player_z, player_dir
    glPushMatrix()
    glTranslatef(player_x, 0.0, player_z)
    glRotatef(player_dir, 0.0, 1.0, 0.0)

    # Pernas e Corpo (só uns cubinhos esticados mesmo)
    glColor3f(0.15, 0.2, 0.45)
    glPushMatrix(); glTranslatef(-0.18, 0.35, 0.0); glScalef(0.22, 0.7, 0.25); glutSolidCube(1.0); glPopMatrix()
    glPushMatrix(); glTranslatef( 0.18, 0.35, 0.0); glScalef(0.22, 0.7, 0.25); glutSolidCube(1.0); glPopMatrix()
    glColor3f(0.1, 0.55, 1.0)
    glPushMatrix(); glTranslatef(0.0, 1.0, 0.0); glScalef(0.7, 0.9, 0.45); glutSolidCube(1.0); glPopMatrix()

    # Cabeça e Olhos
    glColor3f(1.0, 0.85, 0.7)
    glPushMatrix(); glTranslatef(0.0, 1.75, 0.0); glutSolidSphere(0.35, 16, 16)
    glColor3f(0.0, 0.0, 0.0)
    glPushMatrix(); glTranslatef(-0.12, 0.05, 0.32); glutSolidSphere(0.06, 8, 8); glPopMatrix()
    glPushMatrix(); glTranslatef( 0.12, 0.05, 0.32); glutSolidSphere(0.06, 8, 8); glPopMatrix()
    glPopMatrix()
    glPopMatrix()

def desenhaChave():
    """A chave do jogo, feita com um Torus (argola) e um cubo pro dente, girando no eixo."""
    global chave_x, chave_z, angulo_chave
    glPushMatrix()
    glTranslatef(chave_x, 0.8, chave_z)
    glRotatef(angulo_chave, 0.0, 1.0, 0.0)
    glColor3f(1.0, 0.85, 0.0)
    glutSolidTorus(0.09, 0.24, 12, 16)
    glPushMatrix(); glTranslatef(0.38, 0.0, 0.0); glScalef(0.45, 0.1, 0.1); glutSolidCube(1.0); glPopMatrix()
    glPopMatrix()

def desenhaFantasmas():
    """Desenha os inimigos na tela com aquele efeito de flutuar."""
    global fantasmas, qtd_fantasmas
    for i in range(qtd_fantasmas):
        f = fantasmas[i]
        glPushMatrix()
        
        # Faz eles ficarem subindo e descendo de levinho
        flutuacao = math.sin(f["fase"] * 1.5) * 0.15
        glTranslatef(f["x"], 0.85 + flutuacao, f["z"])
        glRotatef(f["ang"], 0.0, 1.0, 0.0)

        glColor3f(f["cor"][0], f["cor"][1], f["cor"][2])
        glPushMatrix(); glTranslatef(0.0, 0.35, 0.0); glutSolidSphere(0.55, 16, 16); glPopMatrix()
        glPushMatrix(); glTranslatef(0.0, 0.4, 0.0); glRotatef(90.0, 1.0, 0.0, 0.0); glutSolidCone(0.56, 1.1, 16, 8); glPopMatrix()

        # Os olhos ficam amarelos se a IA decidir dar um bote na gente
        for ox in [-0.2, 0.2]:
            if f["estado"] == "ataque":
                glColor3f(1.0, 1.0, 0.0)
            else:
                glColor3f(1.0, 1.0, 1.0)
            glPushMatrix()
            glTranslatef(ox, 0.4, 0.48)
            glutSolidSphere(0.12, 10, 10)
            glColor3f(0.0, 0.0, 0.0)
            glTranslatef(0.0, 0.0, 0.08)
            glutSolidSphere(0.06, 8, 8)
            glPopMatrix()
        glPopMatrix()

# RENDER E CÂMERA

def EspecificaParametrosVisualizacao():
    """Setup da câmera usando perspective e lookAt."""
    global angle, fAspect, camX, camY, camZ
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(angle, fAspect, 0.1, 500.0)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(camX, camY, camZ, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0)

def Desenha():
    """Callback de display. Aqui é onde a mágica toda é desenhada frame a frame."""
    global anguloX, anguloY, estado_jogo
    
    if estado_jogo == 0:
        sys.exit(0) # Trata a opção de sair do menu

    EspecificaParametrosVisualizacao()
    iluminacao()
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Pra gente poder rodar a sala toda usando as setinhas do teclado
    glPushMatrix()
    glRotated(anguloX, 0.0, 1.0, 0.0)
    glRotated(anguloY, 1.0, 0.0, 0.0)

    chao()
    paredes()
    porta()
    sofa()
    mesa()
    estante()
    abajur()

    desenhaChave()
    desenhaJogador()
    desenhaFantasmas()
    glPopMatrix()

    Comentarios() # Escreve o HUD por cima
    glutSwapBuffers()

# LÓGICA DE ATUALIZAÇÃO (RODA A CADA 33ms)

def Timer(value):
    """
    Motor do jogo. Bota o jogador pra andar suavemente, roda a IA dos fantasmas
    e checa as colisões de tudo.
    """
    global player_x, player_z, player_step_x, player_step_z, passos_fluidos, player_dir
    global chave_x, chave_z, angulo_chave, fantasmas, qtd_fantasmas, pontos, vidas, qtdcolisao, estado_jogo

    if estado_jogo == 1:
        angulo_chave = (angulo_chave + 6.0) % 360.0

        # Movimento fluido do jogador (desliza de leve em vez de parar seco)
        if passos_fluidos > 0:
            passos_fluidos -= 1
            nx = player_x + player_step_x
            nz = player_z + player_step_z

            if LIMITE_X_MIN <= nx <= LIMITE_X_MAX and not VerificaColisaoMoveis(nx, player_z, player_raio):
                player_x = nx
            if LIMITE_Z_MIN <= nz <= LIMITE_Z_MAX and not VerificaColisaoMoveis(player_x, nz, player_raio):
                player_z = nz

            # "Atrito" pra ir parando suave
            player_step_x *= 0.85
            player_step_z *= 0.85

        # IA dos Fantasmas (Eles decidem se patrulham ou se tentam te pegar)
        atacando_agora = sum(1 for i in range(qtd_fantasmas) if fantasmas[i]["estado"] == "ataque")

        for i in range(qtd_fantasmas):
            f = fantasmas[i]
            f["fase"] += 0.12
            if f["cd"] > 0:
                f["cd"] -= 1

            dist_p = math.hypot(player_x - f["x"], player_z - f["z"])
            f["timer"] -= 1

            # Máquina de estados basicona
            if f["estado"] == "ronda":
                # Acorda e ataca se chegar muito perto ou aleatoriamente pelo timer
                if ((dist_p < 6.0 and f["cd"] == 0) or (f["timer"] <= 0 and f["cd"] == 0 and random.random() < 0.4)) and atacando_agora < 2:
                    f["estado"] = "ataque"
                    f["timer"] = random.randint(75, 115) 
                    atacando_agora += 1
                elif f["timer"] <= 0:
                    f["timer"] = random.randint(80, 140)
            elif f["estado"] == "ataque":
                if f["timer"] <= 0:
                    f["estado"] = "ronda"
                    f["cd"] = random.randint(90, 150) # Tempo de recarga pra não spammar ataque
                    f["timer"] = random.randint(90, 150)
                    atacando_agora -= 1

            # Movimentação deles
            vel = f["vel"] * 1.25 if f["estado"] == "ataque" else f["vel"]

            if f["estado"] == "ataque":
                alvo_x = player_x + math.sin(f["fase"] * 2.0) * 0.8
                alvo_z = player_z + math.cos(f["fase"] * 2.0) * 0.8
            else:
                if f["padrao"] == "waypoints":
                    wx, wz = WAYPOINTS[f["wp"]]
                    if math.hypot(wx - f["x"], wz - f["z"]) < 1.6:
                        f["wp"] = random.randint(0, len(WAYPOINTS) - 1)
                        wx, wz = WAYPOINTS[f["wp"]]
                    alvo_x = wx + math.sin(f["fase"]) * 2.0
                    alvo_z = wz + math.cos(f["fase"]) * 2.0
                elif f["padrao"] == "orbita":
                    f["theta"] += 0.04
                    alvo_x = math.cos(f["theta"]) * 6.8
                    alvo_z = -2.0 + math.sin(f["theta"]) * 5.5
                elif f["padrao"] == "curvo":
                    f["theta"] += random.uniform(-0.15, 0.15)
                    alvo_x = f["x"] + math.sin(f["theta"]) * 4.0
                    alvo_z = f["z"] + math.cos(f["theta"]) * 4.0
                else:
                    f["theta"] += 0.05
                    alvo_x = chave_x + math.cos(f["theta"]) * 3.8
                    alvo_z = chave_z + math.sin(f["theta"]) * 3.8

            dx = alvo_x - f["x"]
            dz = alvo_z - f["z"]
            norma = math.hypot(dx, dz)
            if norma > 0.001:
                dx = (dx / norma) * vel
                dz = (dz / norma) * vel

            f["ang"] = math.degrees(math.atan2(dx, dz))
            fx_novo = f["x"] + dx
            fz_novo = f["z"] + dz

            livre_x = (LIMITE_X_MIN <= fx_novo <= LIMITE_X_MAX) and not VerificaColisaoMoveis(fx_novo, f["z"], FANTASMA_RAIO)
            livre_z = (LIMITE_Z_MIN <= fz_novo <= LIMITE_Z_MAX) and not VerificaColisaoMoveis(f["x"], fz_novo, FANTASMA_RAIO)

            # Os fantasmas também desviam dos móveis (não atravessam)
            if livre_x and livre_z:
                f["x"], f["z"] = fx_novo, fz_novo
            elif livre_x:
                f["x"] += (1.0 if dx >= 0 else -1.0) * vel
            elif livre_z:
                f["z"] += (1.0 if dz >= 0 else -1.0) * vel
            else:
                f["theta"] += 1.5
                f["wp"] = (f["wp"] + 1) % len(WAYPOINTS)

        # Checa se encostou na chave
        if math.hypot(player_x - chave_x, player_z - chave_z) < 1.1:
            pontos += 10
            chave_x, chave_z = SorteiaChave()

        # Checa se algum fantasma pegou o player
        for i in range(qtd_fantasmas):
            f = fantasmas[i]
            if math.hypot(player_x - f["x"], player_z - f["z"]) < (player_raio + FANTASMA_RAIO):
                vidas -= 1
                qtdcolisao = vidas
                PosicionaPersonagens()
                if vidas <= 0:
                    estado_jogo = 3
                break

    glutPostRedisplay()
    glutTimerFunc(33, Timer, 1)

# INPUTS (Teclado, Mouse e Menus)

def GerenciaTeclado(key, x, y):
    """Callback pro teclado normal (WASD, números, P, Z, X, C)."""
    global player_step_x, player_step_z, passos_fluidos, player_dir
    global modo_luz, angle, camX, camY, camZ, estado_jogo

    vel_impulso = 0.36
    # Em vez de pular direto pra posição, dá um "impulso" pro timer resolver suave
    if key == b'w' or key == b'W':
        player_step_z = -vel_impulso
        passos_fluidos = 10
        player_dir = math.degrees(math.atan2(player_step_x, player_step_z))
    elif key == b's' or key == b'S':
        player_step_z = vel_impulso
        passos_fluidos = 10
        player_dir = math.degrees(math.atan2(player_step_x, player_step_z))
    elif key == b'a' or key == b'A':
        player_step_x = -vel_impulso
        passos_fluidos = 10
        player_dir = math.degrees(math.atan2(player_step_x, player_step_z))
    elif key == b'd' or key == b'D':
        player_step_x = vel_impulso
        passos_fluidos = 10
        player_dir = math.degrees(math.atan2(player_step_x, player_step_z))
    
    elif key in [b'1', b'2', b'3', b'4', b'5']:
        modo_luz = int(key.decode())
    
    elif (key == b'z' or key == b'Z') and angle >= 15.0:
        angle -= 5.0
    elif (key == b'x' or key == b'X') and angle <= 120.0:
        angle += 5.0
    
    elif key == b'c' or key == b'C':
        if camZ == 24.0: camX, camY, camZ = 0.0, 28.0, 4.0
        elif camY == 28.0: camX, camY, camZ = 18.0, 14.0, 18.0
        else: camX, camY, camZ = 0.0, 16.0, 24.0
        
    elif key == b'p' or key == b'P':
        estado_jogo = 2 if estado_jogo == 1 else 1

    glutPostRedisplay()

def TeclasEspeciais(key, x, y):
    """Callback para setas (rotaciona a visão do mapa)."""
    global anguloX, anguloY
    if key == GLUT_KEY_UP:
        anguloY -= 3.0
    elif key == GLUT_KEY_DOWN:
        anguloY += 3.0
    elif key == GLUT_KEY_LEFT:
        anguloX -= 3.0
    elif key == GLUT_KEY_RIGHT:
        anguloX += 3.0
    EspecificaParametrosVisualizacao()
    glutPostRedisplay()

def MoveMouseBotaoPressionado(x, y):
    """Atualiza o (x,y) no HUD."""
    global texto
    texto = "Botao pressionado ({0:d}, {1:d})".format(x, y)
    glutPostRedisplay()

def MoveMouse(x, y):
    """Atualiza o (x,y) no HUD sem clicar."""
    global texto
    texto = "(" + str(x) + ", " + str(y) + ")"
    glutPostRedisplay()

def GerenciaMouse(button, state, x, y):
    """Zoom e ativação do Menu no clique direito."""
    global angle
    if button == GLUT_LEFT_BUTTON:
        if state == GLUT_DOWN:
            if angle >= 15.0: angle -= 5.0
    if button == GLUT_MIDDLE_BUTTON:
        if state == GLUT_DOWN:
            if angle <= 120.0: angle += 5.0
    if button == GLUT_RIGHT_BUTTON:
        if state == GLUT_DOWN:
            CriaMenu() # Mostra o popup
    EspecificaParametrosVisualizacao()
    glutPostRedisplay()

def MenuDificuldade(op):
    """Gerencia o submenu de quantidade de inimigos."""
    global qtd_fantasmas, vidas, qtdcolisao, pontos, estado_jogo, chave_x, chave_z
    if op == 0:   qtd_fantasmas = 2
    elif op == 1: qtd_fantasmas = 3
    elif op == 2: qtd_fantasmas = 4
    vidas, qtdcolisao, pontos, estado_jogo = 3, 3, 0, 1
    PosicionaPersonagens()
    chave_x, chave_z = SorteiaChave()
    glutPostRedisplay()
    return 0

def MenuIluminacao(op):
    """Gerencia o submenu das cores."""
    global modo_luz
    if op == 0:   modo_luz = 1
    elif op == 1: modo_luz = 2
    elif op == 2: modo_luz = 3
    elif op == 3: modo_luz = 4
    elif op == 4: modo_luz = 5
    glutPostRedisplay()
    return 0

def MenuPrincipal(op):
    """Ações diretas do menu principal."""
    global vidas, qtdcolisao, pontos, estado_jogo, chave_x, chave_z, angle
    if op == 0: 
        vidas, qtdcolisao, pontos, estado_jogo = 3, 3, 0, 1
        PosicionaPersonagens()
        chave_x, chave_z = SorteiaChave()
    elif op == 1:
        estado_jogo = 2 if estado_jogo == 1 else 1
    elif op == 2:
        if angle <= 120.0: angle += 10.0
    elif op == 3:
        estado_jogo = 0 
    glutPostRedisplay()
    return 0

def CriaMenu():
    """Monta a interface de menu padrão do GLUT."""
    submenu1 = glutCreateMenu(MenuDificuldade)
    glutAddMenuEntry(b"Facil (2 Fantasmas)", 0)
    glutAddMenuEntry(b"Medio (3 Fantasmas)", 1)
    glutAddMenuEntry(b"Dificil (4 Fantasmas)", 2)

    submenu2 = glutCreateMenu(MenuIluminacao)
    glutAddMenuEntry(b"Normal", 0)
    glutAddMenuEntry(b"Fraca (Penumbra)", 1)
    glutAddMenuEntry(b"Colorida (Vermelha)", 2)
    glutAddMenuEntry(b"Colorida (Verde)", 3)
    glutAddMenuEntry(b"Colorida (Azul)", 4)

    menu = glutCreateMenu(MenuPrincipal)
    glutAddSubMenu(b"Dificuldade (N. de Fantasmas)", submenu1)
    glutAddSubMenu(b"Iluminacao da Casa", submenu2)
    glutAddMenuEntry(b"Iniciar / Reiniciar", 0)
    glutAddMenuEntry(b"Pausar / Continuar", 1)
    glutAddMenuEntry(b"Zoom Out (Afastar)", 2)
    glutAddMenuEntry(b"Desligar", 3)
    glutAttachMenu(GLUT_RIGHT_BUTTON)
    return 0

# INICIALIZAÇÃO

def AlteraTamanhoJanela(w, h):
    """Garante que a tela não quebre se redimensionar."""
    global view_w, view_h, fAspect
    if h == 0: h = 1
    glViewport(0, 0, w, h)
    view_w, view_h = w, h
    fAspect = w / h
    EspecificaParametrosVisualizacao()

def Inicializa():
    """Valores de arranque antes de entrar no loop do GLUT."""
    global angle, vidas, qtdcolisao, pontos, estado_jogo, chave_x, chave_z
    glClearColor(0.05, 0.05, 0.08, 1.0)
    angle = 45.0
    vidas, qtdcolisao, pontos, estado_jogo = 3, 3, 0, 1
    PosicionaPersonagens()
    chave_x, chave_z = SorteiaChave()
    iluminacao()
    CriaMenu()

def main():
    """Setup obrigatório e amarração dos callbacks no GLUT."""
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(800, 600)
    glutInitWindowPosition(10, 10)
    glutCreateWindow(b"Projeto CG - Jogo 4: Haunted House")
    
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
