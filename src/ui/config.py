"""Constantes globais do METAL MAX: dimensoes, fisica, arte e assets.

A paleta e a arte sao do proprio sprite do pug (creme, contorno escuro, gola
vermelha e tag dourada); o cenario e pintado com essas mesmas cores.
"""
from pathlib import Path

from src.ui.cores import CORES

# ---------------------------------------------------------------- estrutura
BASE_DIR = Path(__file__).resolve().parent          # src/ui
RAIZ = BASE_DIR.parent.parent                       # raiz do projeto
ASSETS_DIR = RAIZ / "assets" / "imagens"

# ------------------------------------------------------------------ janela
LARGURA = 1400
ALTURA = 700
FPS = 60
CAPTION = "METAL MAX"

# As cores estao em src/ui/cores.py

# ------------------------------------------------------------------- mundo
CHAO_Y = ALTURA - 44
LARGURA_MUNDO = 3830     # 6 trechos de 520 + 5 buracos de 130 = 3770 de mapa
ALTURA_PLATAFORMA = 12
ALTURA_CHAO = 90              # o chao e desenhado alto; a colisao so usa o topo
ALTURA_ESPINHO = 16
ALTURA_CAIXA = 30
ALTURA_PORTA = 46

# ------------------------------------------------------------------ fisica
GRAVIDADE = 2000.0
VEL = 260.0
IMPULSO_PULO = 560.0
IMPULSO_SEGUNDO_PULO = 480.0   # salto duplo, mais fraco que o primeiro
IMPULSO_PISÃO = 500.0        # salto ao cair em cima do inimigo
IMPULSO_DANO = 220.0
TETO_QUEDA = 1500.0
# Investida: rajada horizontal rapida, o que da o ritmo de arcade
VEL_INVESTIDA = 580.0
TEMPO_INVESTIDA = 0.14
RECARGA_INVESTIDA = 0.55
COYOTE = 0.12
BUFFER_PULO = 0.14
DURACAO_ATRAVESSAR = 0.25
ALCANCE_PISAO = 0.55          # fracao da altura do inimigo contada como "cabeca"

# ------------------------------------------------------------- personagem
CEL = 128                     # celula do sprite sheet (16x16)
ALTURA_PERSONAGEM = 34
LARGURA_PERSONAGEM = 30
ESCALA_PERSONAGEM = ALTURA_PERSONAGEM / CEL
DURACAO_FRAME = 0.09
ESCALA_PIXEL = 3              # o mundo e desenhado em 1/3 da resolucao e ampliado
SPRITE_PUG = "pug.png"

# (linha, coluna) no sheet do pug.
# Atencao: a linha 0 olha para a ESQUERDA e a linha 9 para a DIREITA.
# O sheet inteiro e desenhado olhando para a DIREITA; para a esquerda o sprite
# e espelhado. Nao ha ciclo de caminhada no sheet (as linhas 9 e 15 sao
# identicas frame a frame), entao "andar" alterna duas poses da linha 0 com um
# bob curto, que e o que da a sensacao de passo.
CELULAS_PUG = {
    "Parado": [(0, coluna) for coluna in range(2)],
    "Andar": [(0, coluna) for coluna in (0, 1)],
    "Bravo": [(11, coluna) for coluna in range(4)],
}
BOB_PASSO = 2                # px que o corpo sobe a cada quadro da caminhada
DURACAO_FRAME_ANDAR = 0.16
CELULA_CORACAO = (11, 1)     # coracao vermelho
CELULA_MOEDA = (13, 0)       # moeda dourada
CELULA_PEDRA = (11, 2)       # pedra escura (item raro)

# ------------------------------------------------------------------ camera
TREINAMENTO_CAMERA = 7.0

# -------------------------------------------------------------------- vidas
VIDAS_MAX = 3
INVULNERABILIDADE = 1.2
DANO_INIMIGO = 1
PONTOS_PISAO = 200

# ----------------------------------------------------------------- coletaveis
MOEDA_VALOR = 10
PEDRA_VALOR = 100
ALTURA_COLETAVEL = 26
