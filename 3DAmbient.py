from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import sys

# 
# VARIÁVEIS GLOBAIS
# Declaradas no escopo global pra manter o estado entre as callbacks do GLUT
# 
global angle, fAspect, view_w, view_h, texto
global anguloX, anguloY, camX, camY, camZ, cam_modo
global modo_luz, brilho_nivel

# Parâmetros da câmera e projeção perspectiva
angle = 45.0          # Campo de visão (FOV) no eixo Y -> usamos pra fazer o Zoom
fAspect = 1.0         # Proporção largura/altura da tela (evita achatar o desenho)
view_w, view_h = 800, 600

# Ângulos de rotação da cena pelas setas do teclado
# Começa em 15 graus pra dar uma visão isométrica/diagonal legal do quarto
anguloX = 15.0        
anguloY = 15.0        

# Posição inicial da câmera no gluLookAt
cam_modo = 1
camX, camY, camZ = 0.0, 6.5, 16.0
texto = "(0,0)"       # Guarda a coordenada (x, y) do mouse pra mostrar no topo

# Estados da iluminação (1 a 5) e intensidade do brilho (1 a 3)
modo_luz = 1          
brilho_nivel = 2      

# 
# TEXTO 2D NA TELA (HUD)
# Baseado na correção de exibição de caracteres do material de aula
# 

def DesenhaTexto(string):
    """Percorre a string caractere por caractere desenhando o bitmap na tela."""
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
    """
    Cria uma camada 2D temporária por cima do 3D pra escrever o menu de ajuda
    e as coordenadas do mouse sem que o texto gire junto com o quarto.
    """
    global modo_luz, brilho_nivel, cam_modo, texto

    # Desliga a iluminação e o Z-buffer pro texto não ficar escuro nem sumir atrás das paredes
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)

    # Salva a matriz de projeção 3D e joga uma ortográfica 2D (800x600) só pro texto
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0.0, 800.0, 0.0, 600.0)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    nomes_luz = {1: "Normal", 2: "Fraca (Penumbra)", 3: "Vermelha", 4: "Verde", 5: "Azul"}
    nomes_brilho = {1: "Baixo", 2: "Normal", 3: "Alto"}

    # Cabeçalho principal
    glColor3f(1.0, 1.0, 1.0)
    glRasterPos2f(20.0, 570.0)
    titulo = "Ambiente 3D: Quarto  |  Luz: {0:s}  |  Brilho: {1:s}  |  Camera: {2:d}".format(
        nomes_luz[modo_luz], nomes_brilho[brilho_nivel], cam_modo
    )
    DesenhaTexto(titulo)

    # Linha de instruções e posição atual do cursor do mouse
    glColor3f(0.8, 0.9, 1.0)
    glRasterPos2f(20.0, 545.0)
    DesenhaTextoPequeno("Setas: Girar (Com Limite) | Clique Esq ou Z/X: Zoom | 1-5: Luz | C: Mudar Camera | Botao Dir: MENU | Mouse: " + texto)

    # Desempilha as matrizes pra devolver a projeção 3D intacta
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

    # Religa o 3D
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)

# 
# ILUMINAÇÃO E MATERIAIS (Gouraud / GL_LIGHT0)
# 

def iluminacao():
    """
    Define os vetores RGBA de luz ambiente, difusa e especular.
    A posição da luz foi colocada perto da cúpula do abajur do quarto.
    """
    global modo_luz, brilho_nivel

    # Fatores que multiplicam os vetores de luz quando mudamos o brilho no menu
    mult_luz = [0.45, 1.0, 1.45][brilho_nivel - 1]
    mult_espec = [0.15, 0.5, 1.0][brilho_nivel - 1]

    # Alterna os canais RGB conforme o modo escolhido (1 a 5)
    if modo_luz == 1:   # Luz Branca / Normal
        luzAmbiente = [0.30 * mult_luz, 0.30 * mult_luz, 0.30 * mult_luz, 1.0]
        luzDifusa   = [0.75 * mult_luz, 0.75 * mult_luz, 0.70 * mult_luz, 1.0]
    elif modo_luz == 2: # Luz Fraca (Clima noturno)
        luzAmbiente = [0.06 * mult_luz, 0.06 * mult_luz, 0.10 * mult_luz, 1.0]
        luzDifusa   = [0.22 * mult_luz, 0.20 * mult_luz, 0.30 * mult_luz, 1.0]
    elif modo_luz == 3: # Luz Vermelha
        luzAmbiente = [0.30 * mult_luz, 0.0, 0.0, 1.0]
        luzDifusa   = [0.95 * mult_luz, 0.1, 0.1, 1.0]
    elif modo_luz == 4: # Luz Verde
        luzAmbiente = [0.0, 0.30 * mult_luz, 0.0, 1.0]
        luzDifusa   = [0.1, 0.95 * mult_luz, 0.1, 1.0]
    elif modo_luz == 5: # Luz Azul
        luzAmbiente = [0.0, 0.0, 0.35 * mult_luz, 1.0]
        luzDifusa   = [0.15, 0.30, 1.0 * mult_luz, 1.0]

    luzEspecular   = [mult_espec, mult_espec, mult_espec, 1.0]
    posicaoLuz     = [-2.2, 3.8, -3.5, 1.0] # Coordenada da lâmpada do abajur

    # Capacidade de brilho dos móveis (concentração do reflexo especular)
    especularidade = [mult_espec, mult_espec, mult_espec, 1.0]
    especMaterial  = [20, 50, 100][brilho_nivel - 1]

    glClearColor(0.05, 0.05, 0.08, 1.0)
    
    # Habilita o modelo de Gouraud (interpola as cores suavemente entre os vértices)
    glShadeModel(GL_SMOOTH)

    glMaterialfv(GL_FRONT, GL_SPECULAR, especularidade)
    glMateriali(GL_FRONT, GL_SHININESS, especMaterial)
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, luzAmbiente)

    # Passa os parâmetros pra fonte de luz 0
    glLightfv(GL_LIGHT0, GL_AMBIENT, luzAmbiente)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, luzDifusa)
    glLightfv(GL_LIGHT0, GL_SPECULAR, luzEspecular)
    glLightfv(GL_LIGHT0, GL_POSITION, posicaoLuz)

    # GL_COLOR_MATERIAL permite usar glColor3f direto nos objetos sem perder o efeito da luz
    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_DEPTH_TEST) # Z-Buffer pra esconder faces que estão atrás de outros móveis
    glEnable(GL_NORMALIZE)  # Recalcula as normais depois de usar glScalef nos cubos

# 
# MODELAGEM DOS OBJETOS DO QUARTO
# Todos os móveis usam glPushMatrix() e glPopMatrix() pra que a translação e 
# escala de uma peça não acumule e deforme o próximo móvel da lista.
# 

def chao_e_paredes():
    """Monta a estrutura física do quarto (piso, tapete e paredes em L)."""
    # Piso de madeira (cubo achatado em Y e esticado em X e Z)
    glColor3f(0.42, 0.26, 0.14)
    glPushMatrix()
    glTranslatef(0.0, -0.2, 0.0)
    glScalef(14.0, 0.4, 12.0)
    glutSolidCube(1.0)
    glPopMatrix()

    # Tapete azul no centro do quarto
    glColor3f(0.25, 0.32, 0.48)
    glPushMatrix()
    glTranslatef(0.5, 0.02, 0.5)
    glScalef(6.0, 0.04, 4.5)
    glutSolidCube(1.0)
    glPopMatrix()

    # Parede do fundo
    glColor3f(0.75, 0.72, 0.68)
    glPushMatrix()
    glTranslatef(0.0, 3.0, -5.8)
    glScalef(14.0, 6.0, 0.4)
    glutSolidCube(1.0)
    glPopMatrix()

    # Parede da esquerda
    glColor3f(0.70, 0.67, 0.63)
    glPushMatrix()
    glTranslatef(-6.8, 3.0, 0.0)
    glScalef(0.4, 6.0, 12.0)
    glutSolidCube(1.0)
    glPopMatrix()

    # Parede da direita
    glColor3f(0.68, 0.65, 0.60)
    glPushMatrix()
    glTranslatef(6.8, 3.0, 0.0)
    glScalef(0.4, 6.0, 12.0)
    glutSolidCube(1.0)
    glPopMatrix()

def cama():
    """Objeto 1: Cama posicionada no canto esquerdo do quarto."""
    glPushMatrix()
    glTranslatef(-4.2, 0.0, -2.5) # Move o conjunto inteiro da cama pro canto

    # Base de madeira
    glColor3f(0.32, 0.18, 0.08)
    glPushMatrix()
    glTranslatef(0.0, 0.4, 0.0)
    glScalef(3.2, 0.4, 5.2)
    glutSolidCube(1.0)
    glPopMatrix()

    # Cabeceira alta
    glPushMatrix()
    glTranslatef(0.0, 1.3, -2.5)
    glScalef(3.2, 2.2, 0.25)
    glutSolidCube(1.0)
    glPopMatrix()

    # 4 pés da cama gerados com laço for nas coordenadas das pontas
    for px in [-1.4, 1.4]:
        for pz in [-2.4, 2.4]:
            glPushMatrix()
            glTranslatef(px, 0.2, pz)
            glScalef(0.2, 0.4, 0.2)
            glutSolidCube(1.0)
            glPopMatrix()

    # Colchão branco
    glColor3f(0.92, 0.92, 0.95)
    glPushMatrix()
    glTranslatef(0.0, 0.75, 0.1)
    glScalef(2.9, 0.45, 4.8)
    glutSolidCube(1.0)
    glPopMatrix()

    # Cobertor vermelho por cima do colchão
    glColor3f(0.65, 0.15, 0.18)
    glPushMatrix()
    glTranslatef(0.0, 0.78, 0.85)
    glScalef(2.95, 0.48, 3.3)
    glutSolidCube(1.0)
    glPopMatrix()

    # Travesseiro perto da cabeceira
    glColor3f(0.98, 0.98, 1.0)
    glPushMatrix()
    glTranslatef(0.0, 1.05, -1.6)
    glScalef(1.8, 0.22, 0.8)
    glutSolidCube(1.0)
    glPopMatrix()

    glPopMatrix()

def abajur():
    """Objeto 2: Criado-mudo com o abajur (usa glutSolidCone na cúpula)."""
    glPushMatrix()
    glTranslatef(-1.8, 0.0, -4.8)

    # Mesinha de cabeceira
    glColor3f(0.32, 0.18, 0.08)
    glPushMatrix()
    glTranslatef(0.0, 0.55, 0.0)
    glScalef(1.2, 1.1, 1.2)
    glutSolidCube(1.0)
    glPopMatrix()

    # Base metálica e haste do abajur
    glColor3f(0.25, 0.25, 0.28)
    glPushMatrix()
    glTranslatef(0.0, 1.15, 0.0)
    glScalef(0.5, 0.1, 0.5)
    glutSolidCube(1.0)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(0.0, 1.65, 0.0)
    glScalef(0.1, 0.9, 0.1)
    glutSolidCube(1.0)
    glPopMatrix()

    # Cúpula do abajur: rotacionamos -90 graus em X porque o cone padrão do GLUT aponta pra Z
    glColor3f(1.0, 0.88, 0.35)
    glPushMatrix()
    glTranslatef(0.0, 1.9, 0.0)
    glRotatef(-90.0, 1.0, 0.0, 0.0)
    glutSolidCone(0.55, 0.7, 16, 8)
    glPopMatrix()

    glPopMatrix()

def mesa():
    """Objeto 3: Mesa/Bancada que serve de suporte para a Televisão."""
    glPushMatrix()
    glTranslatef(1.8, 0.0, -4.4)

    glColor3f(0.35, 0.20, 0.10)
    # Tampo superior (fica na altura Y = 1.4 com espessura 0.2 -> topo em Y = 1.5)
    glPushMatrix()
    glTranslatef(0.0, 1.4, 0.0)
    glScalef(3.8, 0.2, 1.8)
    glutSolidCube(1.0)
    glPopMatrix()

    # Prateleira de baixo da mesa
    glPushMatrix()
    glTranslatef(0.0, 0.5, 0.0)
    glScalef(3.4, 0.12, 1.5)
    glutSolidCube(1.0)
    glPopMatrix()

    # 4 pernas da mesa
    for px in [-1.7, 1.7]:
        for pz in [-0.7, 0.7]:
            glPushMatrix()
            glTranslatef(px, 0.7, pz)
            glScalef(0.2, 1.4, 0.2)
            glutSolidCube(1.0)
            glPopMatrix()

    glPopMatrix()

def televisao():
    """Objeto 4: Televisão apoiada exatamente em cima do tampo da mesa (Y = 1.5)."""
    glPushMatrix()
    glTranslatef(1.8, 1.5, -4.4)

    # Pedestal da TV
    glColor3f(0.12, 0.12, 0.15)
    glPushMatrix()
    glTranslatef(0.0, 0.05, 0.0)
    glScalef(1.0, 0.1, 0.6)
    glutSolidCube(1.0)
    glPopMatrix()

    # Pescoço do suporte
    glPushMatrix()
    glTranslatef(0.0, 0.25, -0.05)
    glScalef(0.25, 0.4, 0.15)
    glutSolidCube(1.0)
    glPopMatrix()

    # Carcaça preta da tela
    glColor3f(0.08, 0.08, 0.10)
    glPushMatrix()
    glTranslatef(0.0, 1.15, 0.0)
    glScalef(2.8, 1.6, 0.15)
    glutSolidCube(1.0)
    glPopMatrix()

    # Display azulado ligeiramente deslocado pra frente (Z = 0.09) pra não dar Z-fighting
    glColor3f(0.18, 0.45, 0.75)
    glPushMatrix()
    glTranslatef(0.0, 1.15, 0.09)
    glScalef(2.55, 1.38, 0.02)
    glutSolidCube(1.0)
    glPopMatrix()

    # Botão power (esfera vermelha no cantinho inferior direito da moldura)
    glColor3f(1.0, 0.1, 0.1)
    glPushMatrix()
    glTranslatef(1.25, 0.42, 0.09)
    glutSolidSphere(0.04, 8, 8)
    glPopMatrix()

    glPopMatrix()

def estante():
    """Objeto 5: Estante com livros na parede lateral esquerda."""
    glPushMatrix()
    glTranslatef(-6.0, 0.0, 2.5)
    glRotatef(90.0, 0.0, 1.0, 0.0) # Gira 90 graus pra encostar na parede esquerda

    glColor3f(0.30, 0.16, 0.06)
    # Painel traseiro
    glPushMatrix()
    glTranslatef(0.0, 2.2, -0.45)
    glScalef(3.6, 4.4, 0.1)
    glutSolidCube(1.0)
    glPopMatrix()

    # Tábuas laterais
    for lx in [-1.75, 1.75]:
        glPushMatrix()
        glTranslatef(lx, 2.2, 0.0)
        glScalef(0.15, 4.4, 1.0)
        glutSolidCube(1.0)
        glPopMatrix()

    # 4 Prateleiras horizontais
    for py in [0.2, 1.4, 2.7, 4.2]:
        glPushMatrix()
        glTranslatef(0.0, py, 0.0)
        glScalef(3.6, 0.15, 1.0)
        glutSolidCube(1.0)
        glPopMatrix()

    # Livros coloridos distribuídos em duas prateleiras
    cores_livros = [
        (0.85, 0.15, 0.15), (0.15, 0.65, 0.25), (0.15, 0.30, 0.85),
        (0.85, 0.75, 0.15), (0.65, 0.15, 0.65), (0.15, 0.75, 0.75)
    ]
    for i, c in enumerate(cores_livros):
        glColor3f(c[0], c[1], c[2])
        glPushMatrix()
        glTranslatef(-1.2 + i * 0.48, 3.2, 0.0)
        glScalef(0.38, 0.85, 0.7)
        glutSolidCube(1.0)
        glPopMatrix()

    for i, c in enumerate(reversed(cores_livros)):
        glColor3f(c[0], c[1], c[2])
        glPushMatrix()
        glTranslatef(-1.2 + i * 0.48, 1.9, 0.0)
        glScalef(0.38, 0.80, 0.7)
        glutSolidCube(1.0)
        glPopMatrix()

    glPopMatrix()

def armario():
    """Objeto 6: Guarda-roupa de duas portas na parede direita."""
    glPushMatrix()
    glTranslatef(5.6, 0.0, 0.5)
    glRotatef(-90.0, 0.0, 1.0, 0.0) # Gira -90 graus pra ficar de frente pro quarto

    # Caixote principal do armário
    glColor3f(0.38, 0.22, 0.10)
    glPushMatrix()
    glTranslatef(0.0, 2.4, 0.0)
    glScalef(4.2, 4.8, 1.6)
    glutSolidCube(1.0)
    glPopMatrix()

    # Portas frontais
    glColor3f(0.46, 0.28, 0.14)
    for px in [-1.0, 1.0]:
        glPushMatrix()
        glTranslatef(px, 2.4, 0.82)
        glScalef(1.9, 4.4, 0.08)
        glutSolidCube(1.0)
        glPopMatrix()

    # Maçanetas/puxadores redondos (glutSolidSphere)
    glColor3f(0.9, 0.8, 0.2)
    for px in [-0.2, 0.2]:
        glPushMatrix()
        glTranslatef(px, 2.3, 0.92)
        glutSolidSphere(0.1, 10, 10)
        glPopMatrix()

    glPopMatrix()

# 
# PROJEÇÃO PERSPECTIVA E RENDERIZAÇÃO DA CENA
# 

def EspecificaParametrosVisualizacao():
    """
    Define a lente da câmera (gluPerspective) e a posição do observador (gluLookAt).
    Seguindo os slides de correção, não colocamos glOrtho aqui junto com gluPerspective
    para que a rotação e o zoom funcionem perfeitamente.
    """
    global angle, fAspect, camX, camY, camZ
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(angle, fAspect, 0.1, 500.0)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    # Câmera em (camX, camY, camZ) olhando para o meio do quarto (0.0, 2.0, -1.0)
    gluLookAt(camX, camY, camZ, 0.0, 2.0, -1.0, 0.0, 1.0, 0.0)

def Desenha():
    """Callback principal chamada sempre que a tela precisa ser redesenhada."""
    global anguloX, anguloY

    EspecificaParametrosVisualizacao()
    iluminacao()
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glPushMatrix()
    # Aplica a rotação controlada pelo usuário nas setas do teclado (Slide 19)
    glRotated(anguloY, 1.0, 0.0, 0.0)
    glRotated(anguloX, 0.0, 1.0, 0.0)

    # Desenha a estrutura e os 6 objetos do quarto
    chao_e_paredes()
    cama()
    abajur()
    mesa()
    televisao()
    estante()
    armario()

    glPopMatrix()

    Comentarios()
    glutSwapBuffers()

# 
# INTERAÇÃO: TECLADO, MOUSE E LIMITES DE ÂNGULO (CLAMPING)
#

def AlternarCamera(modo):
    """Permite olhar o quarto de 4 ângulos diferentes pré-configurados."""
    global cam_modo, camX, camY, camZ, anguloX, anguloY
    cam_modo = modo
    if cam_modo == 1:   # Visão Frontal Padrão
        camX, camY, camZ = 0.0, 6.5, 16.0
        anguloX, anguloY = 15.0, 15.0
    elif cam_modo == 2: # Visão Superior (Planta baixa do quarto)
        camX, camY, camZ = 0.0, 18.0, 6.0
        anguloX, anguloY = 0.0, 30.0
    elif cam_modo == 3: # Visão do Canto Esquerdo (Foco na TV e Armário)
        camX, camY, camZ = -9.0, 6.5, 13.0
        anguloX, anguloY = -15.0, 12.0
    elif cam_modo == 4: # Visão do Canto Direito (Foco na Cama e Estante)
        camX, camY, camZ = 9.0, 6.5, 13.0
        anguloX, anguloY = 15.0, 12.0

def GerenciaTeclado(key, x, y):
    """Atalhos no teclado para iluminação (1-5), zoom (Z/X), câmera (C) e brilho (B)."""
    global modo_luz, brilho_nivel, angle, cam_modo

    if key in [b'1', b'2', b'3', b'4', b'5']:
        modo_luz = int(key.decode())
    elif (key == b'z' or key == b'Z') and angle >= 15.0:
        angle -= 5.0 # Zoom In
    elif (key == b'x' or key == b'X') and angle <= 90.0:
        angle += 5.0 # Zoom Out
    elif key == b'c' or key == b'C':
        AlternarCamera((cam_modo % 4) + 1)
    elif key == b'b' or key == b'B':
        brilho_nivel = (brilho_nivel % 3) + 1
    elif key == b'r' or key == b'R':
        angle = 45.0
        AlternarCamera(1)
    elif ord(key) == 27: # ESC fecha a janela
        sys.exit(0)

    EspecificaParametrosVisualizacao()
    glutPostRedisplay()

def TeclasEspeciais(key, x, y):
    """
    Rotaciona o quarto pelas setas do teclado, mas aplica travas (clamping)
    para impedir que a câmera passe para baixo do chão da casa ou vire para
    trás das paredes.
    """
    global anguloX, anguloY
    
    # Seta pra cima e pra baixo controlam a inclinação vertical (anguloY)
    # Trava mínima em -5.0 (não deixa olhar por baixo do piso) e máxima em 65.0 (visão de topo)
    if key == GLUT_KEY_UP:
        if anguloY > -5.0:
            anguloY -= 3.0
    elif key == GLUT_KEY_DOWN:
        if anguloY < 65.0:
            anguloY += 3.0
            
    # Seta esquerda e direita giram o quarto lateralmente entre -45 e +45 graus
    elif key == GLUT_KEY_LEFT:
        if anguloX > -45.0:
            anguloX -= 3.0
    elif key == GLUT_KEY_RIGHT:
        if anguloX < 45.0:
            anguloX += 3.0

    EspecificaParametrosVisualizacao()
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
    """Clique esquerdo aproxima (Zoom In), botão do meio afasta e botão direito abre o Menu."""
    global angle
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        if angle >= 15.0:
            angle -= 5.0
    if button == GLUT_MIDDLE_BUTTON and state == GLUT_DOWN:
        if angle <= 90.0:
            angle += 5.0
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        CriaMenu()
    EspecificaParametrosVisualizacao()
    glutPostRedisplay()

# 
# MENU POP-UP DO GLUT (Botão Direito)
# 

def MenuIluminacao(op):
    global modo_luz
    modo_luz = op + 1
    glutPostRedisplay()
    return 0

def MenuBrilho(op):
    global brilho_nivel
    brilho_nivel = op + 1
    glutPostRedisplay()
    return 0

def MenuCamera(op):
    AlternarCamera(op + 1)
    EspecificaParametrosVisualizacao()
    glutPostRedisplay()
    return 0

def MenuPrincipal(op):
    global angle
    if op == 0:
        angle = 45.0
        AlternarCamera(1)
    elif op == 1:
        if angle >= 15.0: angle -= 10.0
    elif op == 2:
        if angle <= 90.0: angle += 10.0
    elif op == 3:
        sys.exit(0)
    EspecificaParametrosVisualizacao()
    glutPostRedisplay()
    return 0

def CriaMenu():
    submenu1 = glutCreateMenu(MenuIluminacao)
    glutAddMenuEntry(b"Normal", 0)
    glutAddMenuEntry(b"Fraca (Penumbra)", 1)
    glutAddMenuEntry(b"Colorida (Vermelha)", 2)
    glutAddMenuEntry(b"Colorida (Verde)", 3)
    glutAddMenuEntry(b"Colorida (Azul)", 4)

    submenu2 = glutCreateMenu(MenuBrilho)
    glutAddMenuEntry(b"Menos Brilho (Escuro)", 0)
    glutAddMenuEntry(b"Brilho Normal", 1)
    glutAddMenuEntry(b"Mais Brilho (Intenso)", 2)

    submenu3 = glutCreateMenu(MenuCamera)
    glutAddMenuEntry(b"Angulo 1: Frontal", 0)
    glutAddMenuEntry(b"Angulo 2: Vista Superior", 1)
    glutAddMenuEntry(b"Angulo 3: Canto Esquerdo", 2)
    glutAddMenuEntry(b"Angulo 4: Canto Direito", 3)

    menu = glutCreateMenu(MenuPrincipal)
    glutAddSubMenu(b"Cor da Iluminacao", submenu1)
    glutAddSubMenu(b"Intensidade de Brilho", submenu2)
    glutAddSubMenu(b"Angulos de Visao (Camera)", submenu3)
    glutAddMenuEntry(b"Resetar Visualizacao", 0)
    glutAddMenuEntry(b"Aproximar (Zoom In)", 1)
    glutAddMenuEntry(b"Afastar (Zoom Out)", 2)
    glutAddMenuEntry(b"Desligar (Sair)", 3)
    glutAttachMenu(GLUT_RIGHT_BUTTON)
    return 0

# 
# CONFIGURAÇÃO DE JANELA E FUNÇÃO PRINCIPAL
# 

def AlteraTamanhoJanela(w, h):
    """Recalcula a razão de aspecto (fAspect = w/h) sempre que a janela é redimensionada."""
    global view_w, view_h, fAspect
    if h == 0:
        h = 1
    glViewport(0, 0, w, h)
    view_w, view_h = w, h
    fAspect = w / h
    EspecificaParametrosVisualizacao()

def Inicializa():
    global angle
    glClearColor(0.05, 0.05, 0.08, 1.0)
    angle = 45.0
    iluminacao()
    CriaMenu()

def main():
    glutInit(sys.argv)
    # GLUT_DOUBLE ativa o double-buffering (evita cintilação) e GLUT_DEPTH ativa o Z-buffer
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(800, 600)
    glutInitWindowPosition(50, 50)
    glutCreateWindow(b"Projeto CG - Parte 2: Ambiente 3D (Quarto)")

    glutDisplayFunc(Desenha)
    glutReshapeFunc(AlteraTamanhoJanela)
    glutKeyboardFunc(GerenciaTeclado)
    glutSpecialFunc(TeclasEspeciais)
    glutMotionFunc(MoveMouseBotaoPressionado)
    glutPassiveMotionFunc(MoveMouse)
    glutMouseFunc(GerenciaMouse)

    Inicializa()
    glutMainLoop()

main()
