# 👻 Haunted House (Casa Assombrada) — OpenGL em Python

Projeto desenvolvido para a disciplina de **Computação Gráfica (Engenharia da Computação - UNIVAP)**, ministrada pelo **Prof. Dr. Valdir Gil Pillat**.

O projeto consiste na implementação do **Tema 4 (Haunted House — Casa Assombrada)** utilizando a biblioteca **PyOpenGL (GL, GLU e GLUT)** em Python, dividido em duas abordagens:
1. **Parte 2D — Fuga dos Fantasmas:** Jogo de colisão em projeção ortográfica (`gluOrtho2D`) com obstáculos, coleta de chaves e inteligência artificial de patrulha/bote.
2. **Parte 3D — Casa Mal-Assombrada Interativa:** Ambiente tridimensional em perspectiva (`gluPerspective` e `gluLookAt`) contendo 5 móveis sólidos (Sofá, Mesa, Estante, Abajur e Porta), variações de iluminação de Gouraud (`GL_SMOOTH`), controle de câmera e o jogo integrado em 3D.

---

## ✨ Funcionalidades e Requisitos Atendidos

### 🎮 Sistema de Jogo e Física (2D e 3D)
- **Movimentação Fluida com Inércia:** O personagem principal utiliza vetores de velocidade e atrito atualizados diretamente na callback `glutTimerFunc(33, Timer, 1)`, garantindo um deslocamento suave sem travamentos de repetição de tecla.
- **Colisão Sólida (AABB - *Axis-Aligned Bounding Box*):** Tanto o jogador quanto os fantasmas respeitam os limites da janela e não atravessam os móveis/obstáculos do cenário, deslizando suavemente pelas bordas (*Wall Sliding*).
- **Inteligência Artificial por Estados:**
  - **Estado de Ronda (Olhos Brancos):** Cada fantasma possui um padrão matemático próprio de patrulha (rotas por *waypoints*, órbita elíptica ao redor dos móveis, exploração curva e proteção em espiral ao redor da chave).
  - **Estado de Bote/Ataque (Olhos Amarelos):** Ao detectar aproximação do jogador ou por gatilho temporal, até 2 fantasmas entram em modo de perseguição temporária antes de cansarem e retornarem à ronda.
- **HUD e Placar Dinâmico:** Exibição em tempo real do número de vidas (`||| - Numero de Vidas`), pontuação por chaves coletadas e coordenadas `(x, y)` do cursor do mouse utilizando `glutBitmapCharacter` e `glRasterPos2f`.

### 💡 Ambiente 3D, Câmera e Iluminação
- **Modelagem Hierárquica:** Construção da sala e dos **5 objetos obrigatórios** (Sofá, Mesa de centro, Estante com livros coloridos, Abajur de pé e Porta com maçaneta) utilizando transformações geométricas (`glTranslatef`, `glRotatef`, `glScalef`) isoladas por `glPushMatrix()` e `glPopMatrix()`.
- **Variações de Luminosidade (`GL_LIGHT0`):** Alternância em tempo real entre iluminação **Normal**, **Fraca (Penumbra)** e **Colorida (Vermelha, Verde e Azul)**, além de controle de brilho especular (`glMaterialfv` / `glMateriali`).
- **Controle de Câmera e Visão:** Rotação completa do cenário nos eixos $X$ e $Y$ pelas setas direcionais, *Zoom In / Zoom Out* alterando o ângulo do `gluPerspective` e alternância entre múltiplos ângulos de câmera.
- **Menu Interativo GLUT:** Menu pop-up acionado pelo botão direito do mouse (`glutCreateMenu`, `glutAddSubMenu`, `glutAddMenuEntry`) permitindo:
  - Selecionar a **Dificuldade** (Fácil: 2 fantasmas | Médio: 3 fantasmas | Difícil: 4 fantasmas);
  - Alterar a **Iluminação / Brilho** da cena;
  - **Iniciar / Reiniciar**, **Pausar / Continuar** e **Desligar** o jogo.

---

## 🛠️ Pré-requisitos e Instalação

Certifique-se de ter o **Python 3.x** instalado em sua máquina. Para instalar o PyOpenGL, execute no terminal:

```bash
pip install PyOpenGL PyOpenGL_accelerate
```

> **Nota para usuários Windows:** Caso ocorra erro de DLL do FreeGLUT ao abrir a janela, certifique-se de instalar a versão compatível do pacote `PyOpenGL` ou posicionar a `freeglut.dll` no diretório do script.

---

## 🚀 Como Executar

Para rodar a **versão 3D completa** (Ambiente 3D + Jogo integrado):
```bash
python haunted_house_oficial.py
```

Para rodar a **versão 2D clássica** (Projeção Ortográfica 2D):
```bash
python haunted_house_2d.py
```

---

## 🕹️ Controles

| Comando / Entrada | Ação no Jogo (3D e 2D) |
| :--- | :--- |
| **`W`, `A`, `S`, `D`** | Movimenta o personagem principal pelo cenário |
| **Setas Direcionais (`↑`, `↓`, `←`, `→`)** | Rotaciona a cena 3D (`anguloX` e `anguloY`) / Move o personagem no 2D |
| **Botão Direito do Mouse** | Abre o **Menu Interativo** (Dificuldade, Luz/Brilho, Pausar, Reiniciar, Sair) |
| **Botão Esquerdo / Central do Mouse** | *Zoom In* e *Zoom Out* na câmera 3D |
| **Teclas `Z` e `X`** | Atalho no teclado para *Zoom In* e *Zoom Out* no 3D |
| **Teclas `1`, `2`, `3`, `4`, `5`** | Alterna a iluminação 3D (1: Normal, 2: Fraca, 3: Vermelha, 4: Verde, 5: Azul) |
| **Tecla `C`** | Alterna entre 3 ângulos de visão da câmera no 3D (Padrão, Topo/Arcade e Diagonal) |
| **Tecla `P`** | Pausa / Continua a partida |
| **Tecla `R`** | Reinicia a partida rapidamente |

---

## 📂 Estrutura Técnica (Principais Funções OpenGL Utilizadas)

- **Inicialização e Janela:** `glutInit`, `glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)`, `glutCreateWindow`, `glViewport`.
- **Projeção e Câmera:** `gluOrtho2D` (2D e HUD), `gluPerspective` e `gluLookAt` (3D).
- **Primitivas e Modelagem:** `glBegin` / `glEnd` (`GL_QUADS`, `GL_TRIANGLES`, `GL_POLYGON`, `GL_LINE_LOOP`), `glutSolidCube`, `glutSolidSphere`, `glutSolidCone`, `glutSolidTorus`.
- **Iluminação e Profundidade:** `glShadeModel(GL_SMOOTH)`, `glLightModelfv`, `glLightfv`, `glMaterialfv`, `glMateriali`, `glEnable(GL_DEPTH_TEST)`, `glEnable(GL_COLOR_MATERIAL)`.
- **Eventos e Animação:** `glutDisplayFunc`, `glutReshapeFunc`, `glutKeyboardFunc`, `glutSpecialFunc`, `glutMouseFunc`, `glutMotionFunc`, `glutPassiveMotionFunc`, `glutTimerFunc`.

---

## 👥 Autores

Projeto desenvolvido para a disciplina de Computação Gráfica:
- *[Insira seu Nome Completo aqui]*
- *[Insira o Nome do Integrante 2, se houver]*
- *[Insira o Nome do Integrante 3, se houver]*

**Professor Orientador:** Prof. Dr. Valdir Gil Pillat