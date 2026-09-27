---
id: niveis
title: Nível
sidebar_position: 6
---

# Nível

Um mapa de teste: chão, algumas plataformas, caixas, itens e uma saída com chave.
Sem inimigo — as classes existem e são testadas, mas o mapa não as coloca.

## Geometria

| Peça | Valor |
|---|---|
| trechos de chão | 3, de 1300 px cada |
| buraco entre trechos | 200 px |
| plataformas | 10, em 3 alturas diferentes |
| degrau | 40 px |
| largura da plataforma | 170 px |
| mundo | 3830 px |

Os números ficam em listas curtas no topo de `mundo/nivel.py`, para ajustar sem
caçar pelo arquivo.

## Posições importantes

O jogador nasce em `x=80`. Três coisas são garantidas por construção:

- **nascer seguro**: nenhum espinho ou caixa cobre o ponto de nascimento (já
  aconteceu de o jogador nascer em cima de uma serra e morrer sozinho);
- **porta apoiada no chão**: ela fica em `fim - largura - 12`, dentro do último
  trecho. Mais à direita, a porta empurrava o jogador para fora do chão;
- **corredor limpo**: nada de sólido entre a última plataforma e a porta, para o
  jogador não ficar preso antes de chegar.

## Chave e porta

O objetivo da fase:

1. a **chave** fica no alto do penúltimo trecho;
2. sem a chave a porta é sólida — o jogador bate e para;
3. com a chave a porta abre, e encostar nela vence a fase.

Chegar perto da porta com a chave também abre: não é preciso ficar em cima
dela.

## Buracos

Cair de um buraco tira toda a vida e vai para a tela de fim de jogo. A regra é
simples: se o corpo passar de 80 px abaixo da tela, acabou.

## Por que sem inimigos no mapa

As quatro classes de inimigo existem e são exercitadas pelos testes, incluindo
o pisão estilo Mario. Mas o mapa atual é um tabuleiro para validar movimento,
colisão, itens e o fim de fase — inimigos entram quando o ritmo da fase pedir.
