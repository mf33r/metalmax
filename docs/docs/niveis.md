---
id: niveis
title: Nível
sidebar_position: 6
---

# Nível

Um mapa **reto**: um chão único de ponta a ponta, sem buraco, sem plataforma,
sem caixa e sem inimigo. O único obstáculo é a fileira de espinhos — e cada um
deles mata. No fim do caminho ficam a chave e a porta de saída.

## Geometria

| Peça | Valor |
|---|---|
| chão | 1 trecho de 3830 px, sempre na mesma altura |
| espinhos | 6 serras de 64 a 72 px, coladas no chão |
| altura do espinho | 16 px |
| molas | 4, de 32×28 px, coladas no chão |
| itens no mapa | só a chave |
| mundo | 3830 px |

Tudo fica em listas curtas no topo de `mundo/nivel.py` (`_TRECHOS`, `_ESPINHOS`,
`_MOLAS`, `_CHAVE`), para ajustar sem caçar pelo arquivo.

## Espinhos

Encostar num espinho **não tira vida: explode o corpo** (ver
[Física](./fisica.md)). O espinho não bloqueia a passagem — o corpo atravessa o
retângulo e morre no mesmo quadro — então pular é a única saída. São a única peça
do cenário fora da paleta do pug: **cinza de metal**, para o perigo saltar aos
olhos.

A largura sai da física, não do gosto: um pulo simples cobre ~130 px no ar
(0,5 s a 260 px/s) e o corpo tem 30 px de largura. Uma serra de `W` px precisa de
`W` px de deslocamento aéreo para o corpo passar por cima, então 72 px é o teto
com folga. O pulo duplo cobre quase o dobro disso e a investida estica o salto,
mas nenhum dos dois é obrigatório.

## Molas

Quatro molas vermelhas no chão, nos vãos livres entre as serras. Quem **cai em
cima** vai para o alto: 900 px/s de impulso, uns 200 px de altura, quase o triplo
do pulo simples. Não machucam e não bloqueiam — de lado passa reto, por baixo
também — e a mola devolve um pulo no ar, então dá para emendar o pulo duplo logo
depois do lançamento.

Depois de disparar, o prato de cima desce e as espiras encolhem por 0,18 s: é a
única pista visual de que a mola fez efeito.

## Posições importantes

O jogador nasce em `x=80`. Duas coisas são garantidas por construção:

- **nascer seguro**: nenhum espinho cobre o ponto de nascimento (já aconteceu de
  o jogador nascer em cima de uma serra e morrer sozinho);
- **porta apoiada no chão**: ela fica em `fim - largura - 12`, dentro do trecho.
  Mais à direita, a porta empurrava o jogador para fora do chão.

## Chave e porta

O objetivo da fase:

1. a **chave** flutua a 110 px do chão, no fim do caminho reto — um pulo simples
   já alcança;
2. sem a chave a porta é sólida — o jogador bate e para;
3. com a chave a porta abre, e encostar nela vence a fase.

Chegar perto da porta com a chave também abre: não é preciso ficar em cima dela.

## Queda

Cair tira toda a vida e vai para a tela de fim de jogo. Com o chão reto não há
buraco: só se cai andando ou pulando para fora do mundo, pelas bordas. A regra é
simples: se o corpo passar de 80 px abaixo da tela, acabou.

## Por que sem inimigos no mapa

As quatro classes de inimigo existem e são exercitadas pelos testes, incluindo
o pisão estilo Mario. Mas o mapa atual é um tabuleiro para validar movimento,
colisão, espinhos e o fim de fase — inimigos entram quando o ritmo da fase pedir.
