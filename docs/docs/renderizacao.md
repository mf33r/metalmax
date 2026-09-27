---
id: renderizacao
title: Renderização
sidebar_position: 5
---

# Renderização

O jogo desenha em **duas camadas com resoluções diferentes**, e essa é a decisão
central do visual.

## O mundo: buffer 1/3, ampliado sem interpolação

```
buffer 466x233  →  pygame.transform.scale(...)  →  tela 1400x700
```

O `transform.scale` do pygame é o de vizinho mais próximo; o `smoothscale` é o
que interpola. Como o primeiro faz o upscale por um fator inteiro de 3, cada
pixel vira um bloco de 3×3 — pixel art de verdade.

Para isso funcionar, a câmera precisa saber que está desenhando num buffer
pequeno:

```python
camera.escala = 1.0 / ESCALA_PIXEL
nivel.desenhar(buffer)
camera.escala = 1.0
```

Esquecer essa linha desenha o mundo 1:1 num buffer de 233 px de altura: tudo
abaixo do horizonte cai fora da tela e sobra só o céu.

## A interface: resolução cheia

O HUD, a capa e os painéis são desenhados numa superfície do tamanho da tela,
com alpha, e **misturados** por cima. Não passam pelo buffer pequeno.

O motivo é Practical: a 1/3 de resolução uma fonte de 20 px vira 7 px de altura,
e o texto fica ilegível — foi o que aconteceu com o inventário. O pixel art da
interface vem das **formas** (painéis com contorno grosso, corações em matriz de
pixels), não de reduzir a tela.

## Coração em pixel art

O ícone de vida é uma matriz de 7×7 caracteres desenhada bloco a bloco:

```
.##.##.
#######
#######
#######
.#####.
..###..
...#...
```

Escalada por 3, dá 21×21 px com borda dura. Nitido em qualquer tamanho e sem
nenhuma imagem involved.

## Desenho com medida proporcional

Toda arte do cenário usa **proporções do retângulo**, nunca pixels fixos. Um
valor fixo vale para a tela cheia e vira 3× maior no buffer — foi assim que a
faixa de grama do chão engoliu o chão inteiro numa iteração.

## Culling

A câmera sabe o que está visível e cada entidade é desenhada só se estiver
dentro da área visível (com uma margem). Num mapa de 3800 px isso corta a
maioria das entidades por quadro.

## Ordem de pintura

1. céu e camadas de fundo (parallax)
2. plataformas e obstáculos
3. itens
4. inimigos
5. porta
6. jogador (por cima de tudo)
