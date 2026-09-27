---
id: classes
title: Classes e herança
sidebar_position: 3
---

# Classes e herança

Tudo no jogo descende de `Entidade`. A árvore completa:

```
Entidade
├── Coletavel ─── Moeda · Coracao · Pedra · Chave
├── Obstaculo ─── Espinhos · Caixa
├── Plataforma ── PlataformaMovel
└── CorpoFisico
    ├── Personagem ── Jogador
    └── Inimigo ───── Soldado · Guarda · Voador · Saltitante
```

Fora da árvore, mas usando o mesmoVocabulário: `Camera`, `Cenario`, `Nivel`,
`Porta`, `Hud`, `Menu`, `Aviso` e `Jogo`.

## A base

`Entidade` guarda o mínimo: `pos` (vetor), `hitbox` (retângulo), tamanho e um
sinalizador de atividade. Todo mundo sabe onde está e se desenha.

`CorpoFisico` acrescenta o que cai: velocidade, gravidade, `no_chao`, virada e o
método `pular()`. Personagens e inimigos nascem daqui.

## Personagens

`Personagem` junta a física com a arte: monta as animações a partir do sprite
sheet, escolhe a animação pelo estado (`Parado`, `Andar`, `Bravo`) e ancora o
sprite pelos pés, para ele não flutuar acima do chão.

`Jogador` é a controlável. Tem o que o resto não tem:

- **coyote time** e **buffer de pulo** (ver [Física](./fisica.md))
- **pulo duplo** — no máximo dois saltos por ciclo
- **investida** — rajada horizontal com recarga
- vida, invulnerabilidade depois de levar dano, e `pular` para descer da plataforma

## Inimigos

`Inimigo` patrulha entre dois limites e machuca no contato. As quatro subclasses
mudar só o comportamento, não a arte:

| Classe | Comportamento |
|---|---|
| `Soldado` | patrulha curta e lenta |
| `Guarda` | ronda longa e rápida |
| `Voador` | flutua em onda, ignora o cenário |
| `Saltitante` | pula sem parar, cobrindo mais terreno |

Todos nascem do mesmo sprite do jogador, com a cor trocada por multiplicação:
mesma textura, mesma luz, mesma pintura.

## O que a base não faz

`Entidade` não sabe nada de colisão. Quem resolve é `mundo/fisica.py`, que recebe
o corpo e a lista de plataformas. A separação existe para que desenhar não
dependa de saber como a colisão foi calculada.

## Coletáveis

`Coletavel` centraliza o que todo item tem: flutuar, sumir ao ser pego, e um
registro no nível. As subclasses só dizem a cor da tarja e o valor. No
cenário, **todo item é uma caixa** desenhada em código — os recortes do sprite
ficavam pequenos demais e pareciam machados.

## Portas e plataformas

`Plataforma` é a superfície de sentido único. `PlataformaMovel` acrescento
movimento pingue-pongue e os deltas `dx`/`dy` do passo — é com eles que o
jogador é carregado junto, sem escorregar.
