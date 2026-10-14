---
id: estrutura
title: Estrutura de arquivos
sidebar_position: 2
---

# Estrutura de arquivos

```
metal-max/
├── main.py                 ponto de entrada: só cria e roda o jogo
├── README.md
├── requirements.txt        pygame-ce
├── .gitignore
├── assets/
│   └── imagens/            pug.png (sprite sheet) e fundos
└── src/
    ├── main.py             mesmo jogo, callable por dentro de src/
    ├── assets.py           cache de imagens
    ├── sons.py             sons sintetizados em codigo (o estouro do espinho)
    ├── entidades/          os atores, cada um em seu arquivo
    ├── mundo/              cenário, câmera, física, nível e a porta
    └── ui/                 config, cores, HUD, capa e o loop
```

## Por que `src` é um pacote

`src` tem `__init__.py`, então todo import é absoluto a partir dele:

```python
from src.ui.config import CHAO_Y, ALTURA_PERSONAGEM
from src.mundo.fisica import mover_e_colidir
```

Com isso os dois pontos de entrada funcionam igual: `python main.py` na raiz e
`python src/main.py`. O da raiz não precisa mexer em `sys.path` — o do `src` se
adiciona sozinho para o caso de alguém rodar por ele.

## O que mora em cada lugar

| Arquivo | Responsabilidade |
|---|---|
| `entidades/entidade.py` | base de tudo: posição, hitbox, velocidade |
| `entidades/animacao.py` | recorta as células do sprite sheet e anima |
| `entidades/jogador.py` | classe `Jogador`: input, pulo, dano, investida |
| `entidades/obstaculos.py` | `Obstaculo` (base) + `Espinhos` (explodem o corpo), `Mola`, `CaixaSolida` |
| `entidades/particulas.py` | `Particula` + `Explosao`: a terra que voa quando um corpo explode |
| `entidades/ponte.py` | `Plataforma` (superfície) + plataforma móvel |
| `entidades/itens.py` | `Coletavel` (base) + moeda, coração, pedra, chave |
| `entidades/inimigos.py` | `Inimigo` (base) + 4 comportamentos |
| `mundo/fisica.py` | colisão AABB, eixo a eixo |
| `mundo/cenario.py` | fundo com parallax |
| `mundo/camera.py` | segue o jogador e recorta o que está fora da tela |
| `mundo/nivel.py` | monta o mapa e resolve as interações |
| `mundo/portao.py` | a saída da fase |
| `ui/config.py` | constantes: janela, física, biomas |
| `ui/cores.py` | paleta, tirada da arte do pug |
| `ui/jogo.py` | classe `Jogo`: o loop principal e os estados |
| `ui/hud.py` | barra de status em uma linha |
| `ui/menu.py` | capa de início |
| `ui/avisos.py` | pausa, controles, vitória |

## Sobre `assets.py`

Um cache simples de imagem: `imagem("pug.png")` carrega do disco uma vez só e
devolve a mesma `Surface` para todo mundo. Sem ele, cada entidade abriria o
arquivo de novo.

O caminho dos assets é resolvido a partir de `src/ui/config.py`, que conhece a
raiz do projeto — então o jogo roda de qualquer diretório.

## Sobre `sons.py`

O projeto não tem arquivo de áudio: os dois sons são **sintetizados**, somas de
ruído e seno feitas na mão.

- **estouro da morte**: ruído filtrado (o corpo grave), estalo no ataque e um
  assobio que cai de tom, com saturação para engordar;
- **boing da mola**: um tom que sobe de 180 para ~1080 Hz e treme enquanto sobe
  (vibrato de 26 Hz) — o tremor é o que faz soar molenga em vez de assobio.

As amostras viram um `Sound` uma única vez, já com o volume de cada um, e ficam
em cache. A taxa, os bits e os canais saem de `pygame.mixer.get_init()` — nada de
supor 44100 Hz estéreo. Sem placa de som, ou com o mixer falhando, `explosao()` e
`mola()` não fazem nada e o jogo segue mudo em vez de quebrar.
