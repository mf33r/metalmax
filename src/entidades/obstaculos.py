"""Obstaculos pintados: espinhos que explodem o corpo e caixas que bloqueiam."""
from __future__ import annotations

import pygame

from src.entidades.entidade import Entidade
from src.ui.config import ALTURA_ESPINHO, ALTURA_MOLA, DURACAO_ESTICAR, IMPULSO_MOLA, LARGURA_MOLA
from src.ui.cores import CORES

DIRECOES_ESPINHO = ("cima", "baixo", "esquerda", "direita")


class Obstaculo(Entidade):
    """Base dos obstaculos do cenario."""

    solido = False
    perigoso = False

    def __init__(self, x: int, y: int, largura: int, altura: int):
        super().__init__(x, y, largura, altura)
        self.corpo = self.hitbox
        self.dx = 0
        self.dy = 0

    def mover(self, dt: float) -> None:
        self.dx = 0
        self.dy = 0

    def desenhar(self, tela: pygame.Surface, camera) -> None:
        alvo = camera.retangulo_na_tela(self.corpo)
        pygame.draw.rect(tela, CORES["contorno"], alvo, border_radius=6)
        pygame.draw.rect(tela, CORES["caixa"], alvo.inflate(-6, -6), border_radius=4)


class Espinhos(Obstaculo):
    """Serra de espinhos: quem encosta explode em terra.

    Nao bloqueia a passagem — o corpo atravessa o retangulo e morre no mesmo
    quadro. A `direcao` diz para onde os dentes apontam: `cima` e `baixo` para
    serra no chao ou pendurada, `esquerda` e `direita` para serra de parede.
    """

    perigoso = True

    def __init__(
        self,
        x: int,
        y: int,
        largura: int,
        altura: int = ALTURA_ESPINHO,
        direcao: str = "cima",
    ):
        super().__init__(x, y, largura, altura)
        self.direcao = direcao if direcao in DIRECOES_ESPINHO else "cima"

    def _dente(self, alvo: pygame.Rect, inicio: int, passo: int) -> list:
        """Um dente da serra, apontando para o lado da `direcao`."""
        meio = passo / 2
        if self.direcao == "baixo":
            return [(inicio, alvo.top), (inicio + meio, alvo.bottom), (inicio + passo, alvo.top)]
        if self.direcao == "esquerda":
            return [(alvo.right, inicio), (alvo.left, inicio + meio), (alvo.right, inicio + passo)]
        if self.direcao == "direita":
            return [(alvo.left, inicio), (alvo.right, inicio + meio), (alvo.left, inicio + passo)]
        return [(inicio, alvo.bottom), (inicio + meio, alvo.top), (inicio + passo, alvo.bottom)]

    def desenhar(self, tela: pygame.Surface, camera) -> None:
        """Dentes proporcionais ao lado por onde a serra corre.

        As medidas saem do retangulo, nao de constantes: um contorno fixo de
        4 px numa serra de 16 px engolia a cor e o espinho virava um borrao
        escuro.
        """
        alvo = camera.retangulo_na_tela(self.corpo)
        vertical = self.direcao in ("cima", "baixo")
        comprimento = alvo.h if vertical else alvo.w
        passo = max(6, round(comprimento * 1.4))
        sombra = max(1, round(comprimento / 5))
        contorno = max(1, round(comprimento / 6))
        deslocamento = -sombra if self.direcao in ("baixo", "direita") else sombra
        inicio, fim = (alvo.left, alvo.right) if vertical else (alvo.top, alvo.bottom)
        for canto in range(inicio, fim, passo):
            pontos = self._dente(alvo, canto, min(passo, fim - canto))
            pygame.draw.polygon(tela, CORES["espinho_escura"], [(x + deslocamento, y) for x, y in pontos])
            pygame.draw.polygon(tela, CORES["espinho"], pontos)
            pygame.draw.polygon(tela, CORES["contorno"], pontos, contorno)


class Mola(Obstaculo):
    """Mola vermelha: quem chega de um lado e lancado para o outro.

    Nao bloqueia e nao machuca — de lado passa reto. A `direcao` diz para onde
    ela joga: `cima` (quem cai em cima sobe) ou `baixo` (quem bate de baixo para
    cima desce). So o **cruzamento** da face dispara; e por isso que quem chama
    precisa informar onde o corpo estava no quadro anterior (ver `lancar`).
    """

    def __init__(
        self,
        x: int,
        y: int,
        largura: int = LARGURA_MOLA,
        altura: int = ALTURA_MOLA,
        direcao: str = "cima",
    ):
        super().__init__(x, y, largura, altura)
        self.direcao = "baixo" if direcao == "baixo" else "cima"
        self.esticar = 0.0          # tempo restante com a espiral comprimida

    def mover(self, dt: float) -> None:
        super().mover(dt)
        self.esticar = max(0.0, self.esticar - dt)

    def lancar(self, corpo, anterior: pygame.Rect) -> bool:
        """Lanca `corpo` se ele cruzou a face da mola neste quadro.

        O teste e pela face **cruzada** (o corpo estava do lado de fora antes e
        ja entrou agora) e nao por sobreposicao nem por velocidade: numa queda a
        25 px de quadro o corpo atravessa a mola e toca o chao no mesmo quadro,
        e ai `vel.y` ja zerou — a mola passaria em branco. O cruzamento tambem
        dispensa saber o sentido: quem vem do lado errado nao cruza a face.
        """
        if corpo.hitbox.right <= self.corpo.left or corpo.hitbox.left >= self.corpo.right:
            return False
        if self.direcao == "baixo":
            if anterior.top < self.corpo.bottom or corpo.hitbox.top > self.corpo.bottom:
                return False
            impulso = IMPULSO_MOLA
        else:
            if anterior.bottom > self.corpo.top or corpo.hitbox.bottom < self.corpo.top:
                return False
            impulso = -IMPULSO_MOLA
        self.esticar = DURACAO_ESTICAR
        corpo.vel.y = impulso
        corpo.no_chao = False
        return True

    def desenhar(self, tela: pygame.Surface, camera) -> None:
        """Dois pratos com as espiras no meio; medidas proporcionais ao corpo.

        O contorno e desenhado como borda do retangulo colorido, e nao como
        retangulo preto com um colorido por dentro: no buffer de 1/3 da tela o
        prato tem 2 px e o preto de dentro engolia o vermelho.

        Depois do salto o prato de saida recua e as espiras encolhem — e a unica
        pista visual de que a mola disparou.
        """
        alvo = camera.retangulo_na_tela(self.corpo)
        virada = self.direcao == "baixo"
        contorno = 1
        prato = max(2, round(alvo.h * 0.3))
        recuo = round(alvo.h * 0.3) if self.esticar > 0 else 0
        if virada:
            saida, fixa = alvo.bottom - prato - recuo, alvo.top
        else:
            saida, fixa = alvo.top + recuo, alvo.bottom - prato
        primeiro = min(saida, fixa) + prato
        ultimo = max(primeiro + 1, max(saida, fixa))
        for volta in range(3):
            y = primeiro + round((ultimo - primeiro) * (volta + 0.5) / 3)
            afastamento = contorno + (contorno if volta % 2 else 0)
            pygame.draw.line(tela, CORES["mola_escura"], (alvo.left + afastamento, y), (alvo.right - afastamento, y), 1)
        for y, face in ((saida, not virada), (fixa, virada)):
            caixa = pygame.Rect(alvo.left, y, alvo.w, prato)
            pygame.draw.rect(tela, CORES["mola"], caixa)
            linha = caixa.top if face else caixa.bottom - 1
            pygame.draw.line(tela, CORES["contorno"], (caixa.left, linha), (caixa.right - 1, linha), contorno)


class BlocoGrama(Obstaculo):
    """Bloco solido de grama: pilar, degrau, viga suspensa ou plataforma.

    E o tijolo do cenario: bloqueia por todos os lados e da para pousar em
    cima. O desenho e proporcional ao retangulo — a mesma peca serve para um
    degrau de 80 px e para uma viga de 235 px.
    """

    solido = True

    def desenhar(self, tela: pygame.Surface, camera) -> None:
        alvo = camera.retangulo_na_tela(self.corpo)
        borda = max(1, round(min(alvo.w, alvo.h) * 0.08))
        pygame.draw.rect(tela, CORES["contorno"], alvo)
        corpo = alvo.inflate(-2 * borda, -2 * borda)
        pygame.draw.rect(tela, CORES["colina_escura"], corpo)
        nucleo = corpo.inflate(-2 * borda, -2 * borda)
        if nucleo.w > 0 and nucleo.h > 0:
            pygame.draw.rect(tela, CORES["colina"], nucleo)
        faixa = max(2, round(alvo.h * 0.16))
        pygame.draw.rect(
            tela, CORES["grama"],
            pygame.Rect(alvo.x + borda, alvo.y + borda, alvo.w - 2 * borda, faixa),
        )


class CaixaSolida(Obstaculo):
    """Bloco solido: bloqueia o jogador por todos os lados."""

    solido = True

    def desenhar(self, tela: pygame.Surface, camera) -> None:
        alvo = camera.retangulo_na_tela(self.corpo)
        pygame.draw.rect(tela, CORES["contorno"], alvo, border_radius=4)
        pygame.draw.rect(tela, CORES["caixa"], alvo.inflate(-4, -4), border_radius=3)
        pygame.draw.line(tela, CORES["caixa_escura"], alvo.topleft, alvo.bottomright, 2)
