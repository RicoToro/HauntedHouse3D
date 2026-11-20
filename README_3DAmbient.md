# README - 3DAmbient.py

## Visao geral

`3DAmbient.py` cria uma cena tridimensional de um quarto com piso, paredes, cama, abajur, mesa, televisao, estante e armario. O programa usa uma perspectiva configurada por `gluPerspective`, permite mover a camera, alterar a luz e o brilho, girar a cena e abrir um menu com o botao direito do mouse.

## Executando

Instale as dependencias:

```bash
pip install PyOpenGL PyOpenGL_accelerate
```

Execute:

```bash
python 3DAmbient.py
```

## Variaveis globais e atributos

- `angle`: angulo vertical de campo de visao em graus usado por `gluPerspective`; valores menores aproximam a cena.
- `fAspect`: proporcao largura/altura da janela; evita distorcao do desenho.
- `view_w` e `view_h`: largura e altura atuais da area renderizavel.
- `texto`: texto usado no HUD para mostrar a posicao do mouse.
- `anguloX` e `anguloY`: rotacoes da cena nos eixos Y e X.
- `camX`, `camY` e `camZ`: coordenadas da camera usadas por `gluLookAt`.
- `cam_modo`: seleciona um dos quatro pontos de vista predefinidos.
- `modo_luz`: seleciona normal, fraca, vermelha, verde ou azul.
- `brilho_nivel`: seleciona baixo, normal ou alto para ambiente, difusa e especular.

## Metodos do programa

### `DesenhaTexto(string)`
Percorre os caracteres da string e desenha cada um como um bitmap. `glPushMatrix` e `glPopMatrix` isolam qualquer transformacao, e `glutBitmapCharacter` escolhe o desenho 2D do caractere.

### `DesenhaTextoPequeno(string)`
Faz a mesma operacao que `DesenhaTexto`, mas usa a fonte menor `GLUT_BITMAP_HELVETICA_12`.

### `Comentarios()`
Monta temporariamente uma projeção ortografica sobre a cena 3D para desenhar o HUD sem que ele gire junto com os objetos. Usa `GL_PROJECTION`, `GL_MODELVIEW`, `gluOrtho2D`, `glDisable` e `glEnable`.

### `iluminacao()`
Calcula os componentes ambiente, difuso e especular da luz conforme `modo_luz` e `brilho_nivel`. Configura o modelo de iluminacao, a posicao da `GL_LIGHT0`, o material e o Z-buffer.

### `chao_e_paredes()`
Desenha piso, tapete e tres paredes com cubos escalados.

### `cama()`
Desenha a cama, base, cabeceira, pes, colcha, cobertor e travesseiro.

### `abajur()`
Desenha criado-mudo, base, haste e cupula conica.

### `mesa()`
Desenha tampo, prateleira e quatro pernas da mesa.

### `televisao()`
Desenha pedestal, suporte, carcaca e display da TV.

### `estante()`
Desenha painel, laterais, prateleiras e livros coloridos.

### `armario()`
Desenha o guarda-roupa, duas portas e puxadores esfericos.

### `EspecificaParametrosVisualizacao()`
Define a matriz de projecao com `gluPerspective` e posiciona a camera com `gluLookAt`. A perspectiva usa o angulo `angle`, a proporcao `fAspect` e uma profundidade valida de 0.1 a 500 unidades.

### `Desenha()`
E a callback principal. Configura camera e iluminacao, limpa os buffers, aplica rotacoes da cena, chama todas as funcoes de modelagem e desenha o HUD. `glutSwapBuffers` apresenta a imagem pronta.

### `AlternarCamera(modo)`
Define um dos quatro pares preconfigurados de posicao da camera e orientacao da cena. O valor `cam_modo` permite identificar e alternar o angulo atual.

### `GerenciaTeclado(key, x, y)`
Le teclas normais:

- `1` a `5`: alteram a cor da luz.
- `Z` e `X`: aproximam ou afastam.
- `C`: muda para o proximo angulo de camera.
- `B`: percorre os niveis de brilho.
- `R`: restaura a visualizacao.
- `ESC`: encerra o programa.

### `TeclasEspeciais(key, x, y)`
Usa as setas para girar a cena nos eixos X e Y. Os limites impedem que a camera passe abaixo do piso ou exceda a rotacao lateral definida.

### `MoveMouseBotaoPressionado(x, y)`
Atualiza `texto` com a posicao quando o mouse esta sendo arrastado e solicita redesenho.

### `MoveMouse(x, y)`
Atualiza `texto` com a posicao do ponteiro sem pressionar botao.

### `GerenciaMouse(button, state, x, y)`
Mapeia botoes: esquerdo aproxima, meio afasta e direito abre o menu.

### `MenuIluminacao(op)`
Converte o item escolhido no submenu em `modo_luz`.

### `MenuBrilho(op)`
Converte o item escolhido no submenu em `brilho_nivel`.

### `MenuCamera(op)`
Chama `AlternarCamera` com o angulo selecionado.

### `MenuPrincipal(op)`
Executa reset da visualizacao, zoom, zoom out ou encerramento.

### `CriaMenu()`
Cria os submenus de iluminacao, brilho e camera e os itens principais de zoom, reset e saida. `glutAttachMenu` vincula o menu ao botao direito.

### `AlteraTamanhoJanela(w, h)`
Callback de redimensionamento. Atualiza o viewport e recalcula `fAspect`; uma altura zero vira 1 para evitar divisao por zero.

### `Inicializa()`
Define a cor de limpeza, o angulo inicial, os estados de iluminacao e cria o menu.

### `main()`
Inicializa GLUT, define double buffering com profundidade, cria a janela, registra callbacks e inicia `glutMainLoop`.

## Principais metodos das bibliotecas

### OpenGL.GL

- `glClearColor`: define a cor usada ao limpar a janela.
- `glClear`: limpa imagem e, por profundidade, Z-buffer.
- `glViewport`: mapeia coordenadas normalizadas para pixels da janela.
- `glMatrixMode`: seleciona matriz de projecao ou modelview.
- `glLoadIdentity`: reinicia a matriz ativa.
- `glPushMatrix` / `glPopMatrix`: preservam e restauram o estado geometrico.
- `glTranslatef`, `glRotatef` e `glScalef`: movem, giram e dimensionam objetos.
- `glColor3f`: define a cor dos primitivos.
- `glBegin` / `glEnd`: iniciam e encerram a descricao de primitivas.
- `glEnable` / `glDisable`: ativam ou desativam recursos.
- `glShadeModel(GL_SMOOTH)`: usa interpolacao suave de Gouraud.
- `glMaterialfv` / `glMateriali`: configuram reflexao especular do material.
- `glLightModelfv`, `glLightfv`: configuram ambiente global e propriedades da luz.
- `glLightf` nao é usado neste arquivo.

### OpenGL.GLU

- `gluPerspective`: cria projeção perspectiva com campo de visao, aspecto, plano proximo e plano distante.
- `gluLookAt`: posiciona a camera e define para onde ela olha.
- `gluOrtho2D`: cria a projecao ortografica usada pelo HUD.

### OpenGL.GLUT

- `glutInit`: inicializa GLUT.
- `glutInitDisplayMode`: habilita RGB, double buffering e profundidade.
- `glutInitWindowSize` / `glutInitWindowPosition`: dimensionam e posicionam a janela.
- `glutCreateWindow`: cria a janela.
- `glutDisplayFunc`: registra o redesenho da cena.
- `glutReshapeFunc`: registra ajustes de tamanho.
- `glutKeyboardFunc` / `glutSpecialFunc`: registram teclas normais e especiais.
- `glutMouseFunc`, `glutMotionFunc` / `glutPassiveMotionFunc`: registram interacao do mouse.
- `glutPostRedisplay`: solicita um novo desenho.
- `glutSwapBuffers`: troca os buffers de double buffering.
- `glutMainLoop`: entra no loop de eventos.
- `glutBitmapCharacter`: desenha caracteres 2D.
- `glutSolidCube`, `glutSolidCone` e `glutSolidSphere`: geram solidos basicos.
- `glutCreateMenu`, `glutAddSubMenu`, `glutAddMenuEntry` e `glutAttachMenu`: constroem o menu.
