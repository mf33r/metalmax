---
id: decisoes
title: Decisões e armadilhas
sidebar_position: 7
---

# Decisões e armadilhas

Os bugs que já morderam este código, e por que o código é do jeito que é. Vale
ler antes de mexer em qualquer coisa aqui.

## A tela preta da capa

O menu era desenhado só na camada de interface, mas o buffer do cenário —
vazio e preto — era ampliado por cima da tela. O menu sumia.

Para cima de tudo, a interface estava sendo **sobrescrita** no lugar de
misturada. Agora ela tem alpha e é blitada por cima.

**Como isso passou no teste:** o loop rodava 200 quadros sem exceção, com o
estado correto, e a tela ainda assim era preta. Só apareceu quando alguém mediu o
brilho médio da imagem (0,0). Daí vieram as checagens de brilho.

## O teleport de 436 px

Cadeia de três bugs:

1. A plataforma atravessada era inferida pela velocidade. No ápice do pulo a
   gravidade deixa `vel.y` positivo por um quadro — a colisão lateral
   disparava e o corpo era arremessado 78 px para fora.
2. Bater a cabeça numa caixa deslocava o corpo **51 px para baixo** de uma vez,
   porque a resolução de AABB empurrava pela vertical sem medir.
3. Já dentro do chão, o corpo era expulso para fora do mundo pela borda.

Correção: a travessia passou a ser **lembrada**, a resolução de sólido escolhe o
**menor eixo de penetração**, e o salto extra só bloqueia quem está de fato
cruzando.

Para achar isso, o teste simula o jogo de verdade — andar, pular, spam de A e D
— e falha se algum quadro mover o corpo mais de 12 px.

## O mapa injogável

O pulo rendia 132 px e a plataforma mais próxima estava a 150 px. **Nenhuma**
plataforma era alcançável: o nível inteiro era impossível.

Dois consertos: o pulo foi para 78 px com degraus de 40 px, e o teste passa a
garantir que toda plataforma tem um apoio abaixo dentro do alcance.

## O vão de 28 px

Entre duas plataformas havia 28 px livres e o boneco tem 34. Ele não cabia —
a escada era uma parede sólida, e subir parecia quebrado.

## A tela em branco de nada

O sprite é recortado do sprite sheet e reduzido por `smoothscale` antes de ser
ampliado 3×. O blur é ampliado: o ícone vira uma mancha. Reduzir sem interpolação
resolve — e o pixel art volta a aparecer.

## O item que parecia machado

A chave era um círculo com uma haste na diagonal. Numa olhada, isso lê como
machado. Redesenhada com argola em cima, haste vertical e dentes para a direita.

## A porta que não bloqueava

A porta estava num plinto, **acima da cabeça** do jogador. Ele passava por baixo
e caía da borda do chão. Agora ela se apoia no chão, com um degrau de acesso
logo antes.

## Inimigos sem gravidade

`Inimigo` sobrescreve o `atualizar` do personagem e chamava a física direto —
`aplicar_gravidade` nunca rodava. O `Saltitante` subia para `y = -1768` e
flutuava no teto.

## A legenda que vazava

A largura da barra do HUD era 3 px curta por item, e o número da quantidade
saía do painel por cima do céu. Agora a largura soma exatamente o que cada
parte desenha, e o teste confere cada peça contra o retângulo interno.

## Regras que valem para o futuro

- **Meça a tela, não confie no olho.** Brilho médio e variação de pixel pegaram
  a tela preta e o mundo sumido.
- **Teste a mecânica num nível limpo.** Quando a física é testada no mapa real,
  o teste falha por estar em cima de uma caixa, não por estar errado.
- **Fixe a versão das dependências** e instale com `--ignore-scripts` quando o
  pacote não é do projeto.
