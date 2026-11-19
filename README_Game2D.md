# README - Game2D.py

## Visao geral

`Game2D.py` implementa um jogo 2D em PyOpenGL usando uma projecao ortografica. O jogador coleta uma chave, evita fantasmas e move-se dentro de uma sala com obstaculos. Os fantasmas possuem estados de ronda e ataque e seguem quatro padroes de movimento.

## Executando

```bash
pip install PyOpenGL PyOpenGL_accelerate
python Game2D.py
```

## Variaveis globais e atributos

### Mundo e visualizacao

- `win`: limite do mundo ortografico: de `-150` a `150`.
- `view_w` e `view_h`: tamanho atual da janela.
- `texto`: coordenadas exibidas do mouse ou estado do botao.

### Estado da partida

- `vidas`: numero de vidas restante.
- `qtdcolisao`: espelho usado no HUD para representar vidas; recebe o mesmo valor de `vidas`.
- `pontos`: pontuacao ganha ao coletar a chave.
- `estado_jogo`: `1` jogando, `2` pausado, `3` game over e `0` sair.
- `qtd_fantasmas`: 2, 3 ou 4 fantasmas, conforme a dificuldade.
- `brilho_nivel`: `1` escuro, `2` normal e `3` claro.

### Jogador

- `player_x` e `player_y`: posicao atual.
- `player_step_x` e `player_step_y`: inercia atual aplicada por cada passo.
- `passos_fluidos`: quantos quadros ainda recebem o movimento com inercia.
- `player_raio`: raio usado em limites e colisoes.

### Chave e limites

- `chave_x` e `chave_y`: posicao atual da chave.
- `LIMITE_MIN_X`, `LIMITE_MAX_X`, `LIMITE_MIN_Y` e `LIMITE_MAX_Y`: limites internos da sala.
- `OBSTACULOS_2D`: lista de caixas retangulares que representam moveis.
- `WAYPOINTS_2D`: destinos usados pelo fantasma com padrao `waypoints`.
- `FANTASMA_RAIO`: raio usado nas colisoes com fantasmas.
- `fantasmas`: lista de dicionarios. Cada item possui `x`, `y`, `vel`, `cor`, `padrao`, `estado`, `timer`, `cd`, `wp`, `fase` e `theta`.

Os atributos dos fantasmas controlam:

- `x` e `y`: posicao.
- `vel`: velocidade de ronda.
- `cor`: cor RGB.
- `padrao`: `waypoints`, `orbita`, `curvo` ou `espiral`.
- `estado`: `ronda` ou `ataque`.
- `timer`: tempo restante para mudar de estado ou reavaliar uma ronda.
- `cd`: tempo de espera antes de iniciar outro ataque.
- `wp`: indice do waypoint atual.
- `fase`: fase usada em movimentos oscilatorios.
- `theta`: angulo usado em orbitas e espirais.

## Metodos do programa

### `VerificaColisao2D(x, y, raio)`
Retorna verdadeiro quando o circulo definido pelo ponto e raio invade um retangulo em `OBSTACULOS_2D`. A expansao dos limites pelo raio evita que personagens atravessem os obstaculos.

### `SorteiaChave()`
Gera uma posicao aleatoria dentro da sala e repete o sorteio ate que a chave nao esteja em um obstaculo nem muito perto do jogador.

### `PosicionaPersonagens()`
Restabelece o jogador na parte inferior da sala e envia os quatro fantasmas aos cantos. Tambem remove o movimento anterior e volta todos os fantasmas ao estado de ronda.

### `DesenhaTexto(string)`
Desenha texto grande com `glutBitmapCharacter` e `GLUT_BITMAP_HELVETICA_18`.

### `DesenhaTextoPequeno(string)`
Desenha instrucoes e coordenadas com a fonte menor `GLUT_BITMAP_HELVETICA_12`.

### `Comentarios()`
Desenha placar, vidas, pontos, quantidade de fantasmas, controles, coordenadas e mensagens de pausa ou game over.

### `DesenhaMapa2D()`
Desenha o fundo ladrilhado, o contorno da sala e todos os obstaculos usando primitivos retangulares e linhas. Aplica o fator de brilho ao mapa.

### `DesenhaJogador2D()`
Desenha corpo, cabeca e chapeu do personagem com transformacao aplicada pela posicao atual.

### `DesenhaChave2D()`
Desenha o objeto coletavel com argola em poligono e haste/dentes em quadriculos.

### `DesenhaFantasmas2D()`
Desenha ate `qtd_fantasmas` personagens. Cada fantasma recebe sua cor, corpo, olhos e pupilas; olhos ficam amarelos no estado `ataque`.

### `Desenha()`
E a callback principal. Trata a saida, limpa a imagem, desenha mapa, chave, jogador, fantasmas e HUD e mostra a imagem com double buffering.

### `Timer(value)`
E a callback periodica executada a cada 33 ms. Atualiza movimento do jogador, atrito, inteligencia artificial, colisoes com chave e fantasmas e agenda o proximo timer.

As colisoes em X e Y sao testadas separadamente, permitindo deslizar pelas bordas dos moveis.

Os estados da inteligencia artificial sao:

- `ronda`: segue waypoint, orbita, curva ou espiral.
- `ataque`: segue o jogador com pequena oscilacao e velocidade multiplicada por 1.25.

No maximo dois fantasmas ficam em ataque ao mesmo tempo.

### `GerenciaTeclado(key, x, y)`
Controla jogador com `W`, `A`, `S` e `D`; `P` pausa/continua e `R` reinicia a partida.

### `TeclasEspeciais(key, x, y)`
Permite usar as setas no lugar de WASD.

### `MoveMouseBotaoPressionado(x, y)`
Guarda uma mensagem indicando que o botao foi pressionado na coordenada informada.

### `MoveMouse(x, y)`
Atualiza `texto` com a posicao atual do ponteiro.

### `GerenciaMouse(button, state, x, y)`
Ao detectar clique direito, abre o menu GLUT.

### `MenuDificuldade(op)`
Define a quantidade de fantasmas e reinicia a partida.

### `MenuCorBrilho(op)`
Define o nivel de brilho usado no mapa e nos personagens.

### `MenuPrincipal(op)`
Inicia/reinicia, alterna pausa/continuacao ou define `estado_jogo` como 0 para sair.

### `CriaMenu()`
Cria submenus de dificuldade e brilho e vincula acoes principais ao botao direito.

### `AlteraTamanhoJanela(w, h)`
Atualiza o viewport e define a projecao ortografica sobre o mundo 2D.

### `Inicializa()`
Define cores iniciais, valores da partida, personagens e menu.

### `main()`
Inicializa GLUT, cria a janela, registra callbacks, inicia o timer e entra no loop principal.

## Principais metodos das bibliotecas

### OpenGL.GL

- `glClearColor`: define a cor usada ao limpar a janela.
- `glClear`: limpa os buffers de cor.
- `glViewport`: ajusta a area de desenho ao tamanho da janela.
- `glMatrixMode(GL_PROJECTION)`: ativa a matriz de projecao.
- `glMatrixMode(GL_MODELVIEW)`: ativa a matriz de objetos.
- `glLoadIdentity`: reinicia uma matriz.
- `glPushMatrix` / `glPopMatrix`: preservam e restauram transformacoes.
- `glTranslatef`: move uma figura para sua posicao no mundo.
- `glColor3f`: define RGB normalizado de cada primitivo.
- `glBegin` / `glEnd`: iniciam e encerram grupos de vertices.
- `glVertex2f`: fornece uma coordenada X/Y.
- `glLineWidth`: define espessura das linhas da moldura.
- `glRasterPos2f`: posiciona os caracteres 2D do texto.

### OpenGL.GLU

- `gluOrtho2D`: define uma projecao ortografica sem distorcao de perspectiva.

### OpenGL.GLUT

- `glutInit`: inicializa a biblioteca GLUT.
- `glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)`: cria janela RGB com double buffering.
- `glutInitWindowSize` / `glutInitWindowPosition`: dimensionam e posicionam a janela.
- `glutCreateWindow`: cria a janela com o titulo informado.
- `glutDisplayFunc`: registra `Desenha`.
- `glutReshapeFunc`: registra `AlteraTamanhoJanela`.
- `glutKeyboardFunc` / `glutSpecialFunc`: registram teclas normais e setas.
- `glutMouseFunc`, `glutMotionFunc` / `glutPassiveMotionFunc`: registram eventos do mouse.
- `glutTimerFunc`: agenda `Timer` a cada 33 ms.
- `glutPostRedisplay`: solicita novo redesenho.
- `glutSwapBuffers`: apresenta o buffer desenhado.
- `glutMainLoop`: inicia o loop de eventos.
- `glutBitmapCharacter`: imprime cada caractere como bitmap.
- `glutCreateMenu`, `glutAddSubMenu`, `glutAddMenuEntry` e `glutAttachMenu`: constroem o menu pop-up.
