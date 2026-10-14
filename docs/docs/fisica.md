---
id: fisica
title: Física e regras
sidebar_position: 4
---

# Física e regras

A física vive inteira em `mundo/fisica.py`, resolvida **eixo a eixo**: primeiro
o horizontal, depois o vertical. É o jeito mais barato e mais estável de impedir
atravessamento.

## Plataformas de sentido único

Dá para pular através de uma plataforma e pousar em cima. Três regras fazem isso
funcionar:

1. **Só pousa descendo.** Se a base do corpo já estava abaixo do topo, ele
   continua atravessando.
2. **A travessia é lembrada, não inferida.** Enquanto o corpo sobe atravessando
   uma plataforma, ela entra num conjunto e a colisão lateral é ignorada até o
   corpo sair de dentro dela.
3. **Subir ignora a lateral.** Com o corpo subindo, plataforma de sentido único
   não barra.

> A regra 2 existe porque um teste de velocidade não funciona: no ápice do pulo a
> gravidade deixa `vel.y` positivo por um quadro, a colisão lateral disparava e o
> jogador era arremessado dezenas de pixels para fora. Foi um teleport de 78 px.

## Degrau automático

Se os pés estiverem a até `min(6, espessura/3)` pixels do topo, o corpo sobe em
vez de travar na parede. A tolerância é **relativa à espessura**: um valor fixo
que servia para uma tabua de 26 px afundava o jogador até a metade de uma de
12 px.

## Coyote time e buffer

O pulo "some" de dois jeitos: pulando no instante em que sai da borda, ou pulando
um quadro antes de tocar o chão.

- **coyote time** (0,12 s): o chão continua valendo um instante depois de sair da
  borda.
- **buffer** (0,14 s): o comando fica guardado um instante antes de tocar o
  chão.

O buffer **não** é cancelado ao soltar a tecla — se fosse, não serviria para
nada.

## Pulo duplo

No máximo dois saltos por ciclo: o primeiro do chão (ou do coyote), o segundo no
ar com força menor. O contador zera ao tocar o chão.

## Investida

`Shift` ou `K` dá uma rajada horizontal a 580 px/s por 0,14 s, com recarga de
0,55 s. During a rajada o movimento normal é ignorado; se bater em parede, ela
acaba.

## Molas

A mola é a única peça que devolve movimento ao jogador. O gatilho é o **topo
cruzado**: se a base do corpo estava acima do topo da mola no quadro anterior e
está abaixo agora (com sobreposição horizontal), o lançamento acontece — sem
olhar a velocidade. Isso resolve dois casos de uma vez:

- andar de lado por cima da mola não dispara nada (a base já estava abaixo do
  topo desde o começo);
- numa queda a 25 px de quadro o corpo atravessa a mola **e** encosta no chão no
  mesmo quadro. Nessa hora `vel.y` já zerou, e um teste de velocidade deixaria a
  mola passar em branco.

Subir por baixo também não dispara: a base anterior já está abaixo do topo.

O impulso é `IMPULSO_MOLA` (900 px/s, ~200 px de altura) e a mola ainda devolve
um salto no ar — `saltos_usados` volta para 1, nunca para 0, para não virar
super-salto encadeado.

## Dano

Encostar de lado num inimigo tira uma vida e dá um repique. O repique **não
cancela um pulo mais forte** — ser machucado no mesmo quadro do salto não pode
apagar o salto. Depois de levar dano há 1,2 s de invulnerabilidade, e o corpo
pisca.

**Espinho é outra coisa: não tira vida, mata.** Encostar numa serra explode o
corpo na hora (`Jogador.explodir`): a vida vai a zero, o sprite do pug some e o
que sobra no lugar dele é uma nuvem de **terra** — nunca sangue. São 64 grumos
marrom da paleta do cenário, disparados em todas as direções com um viés para
cima, cada um com gravidade e vida própria; eles encolhem até sumir. A morte
também toca um estouro sintetizado em `sons.py` (ver
[Estrutura](./estrutura.md)).

A explosão também segura o fim de jogo: `Nivel.morto` só é verdade depois que a
última partícula morre, senão a tela de fim de jogo cobria a terra no primeiro
quadro. Enquanto a terra voa, o corpo explodido não anda, não cai e não coleta
nada.

## Constantes

Todas vivem em `ui/config.py`:

| Constante | Valor | Papel |
|---|---|---|
| `GRAVIDADE` | 2000 | queda |
| `VEL` | 260 | corrida |
| `IMPULSO_PULO` | 560 | primeiro pulo |
| `IMPULSO_SEGUNDO_PULO` | 480 | pulo duplo |
| `VEL_INVESTIDA` | 580 | rajada |
| `IMPULSO_MOLA` | 900 | mola pisada |
| `DURACAO_ESTICAR` | 0,18 | tempo com a mola esmagada |
| `COYOTE` | 0,12 | tolerância na borda |
| `BUFFER_PULO` | 0,14 | tolerância antes de tocar o chão |
| `TETO_QUEDA` | 1500 | velocidade máxima de queda |

O primeiro pulo rende ~78 px de altura, o duplo ~136 px. Os degraus do mapa têm
40 px: sobra margem, então dá para_errar o salto sem ficar preso.
