"""Obstaculos pintados: espinhos que explodem o corpo e caixas que bloqueiam."""
from __future__ import annotations

import pygame

from src.entidades.entidade import Entidade
from src.ui.config import (
    ALTURA_ESPINHO,
    ALTURA_MOLA,
    DURACAO_ESTICAR,
    IMPULSO_MOLA,
    LARGURA_MOLA,
)
from src.ui.cores import CORES


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
    """Serra de espinhos no chao: quem encosta explode em terra.

    Nao bloqueia a passagem — o corpo atravessa o retangulo e morre no mesmo
    quadro. Pular por cima e a unica saida.
    """

    perigoso = True

    def __init__(self, x: int, y: int, largura: int, altura: int = ALTURA_ESPINHO):
        super().__init__(x, y, largura, altura)

    def desenhar(self, tela: pygame.Surface, camera) -> None:
        """Dentes proporcionais a altura da serra.

        As medidas saem do retangulo, nao de constantes: um contorno fixo de
        4 px numa serra de 16 px engolia o vermelho e o espinho virava um
        borrao escuro.
        """
        alvo = camera.retangulo_na_tela(self.corpo)
        passo = max(6, round(alvo.h * 1.4))
        sombra = max(1, round(alvo.h / 5))
        contorno = max(1, round(alvo.h / 6))
        for esquerda in range(alvo.left, alvo.right, passo):
            largura = min(passo, alvo.right - esquerda)
            pontos = [(esquerda, alvo.bottom), (esquerda + largura / 2, alvo.top), (esquerda + largura, alvo.bottom)]
            pygame.draw.polygon(tela, CORES["espinho_escura"], [(x, y + sombra) for x, y in pontos])
            pygame.draw.polygon(tela, CORES["espinho"], pontos)
            pygame.draw.polygon(tela, CORES["contorno"], pontos, contorno)


class Mola(Obstaculo):
    """Mola vermelha no chao: quem cai em cima vai para o alto.

    Nao bloqueia e nao machuca — de lado passa reto, por baixo tambem. So quem
    **chega caindo** e lancado; e por isso que quem chama precisa informar onde
    o corpo estava no quadro anterior (ver `lancar`).
    """

    def __init__(self, x: int, y: int, largura: int = LARGURA_MOLA, altura: int = ALTURA_MOLA):
        super().__init__(x, y, largura, altura)
        self.esticar = 0.0          # tempo restante com a espiral comprimida

    def mover(self, dt: float) -> None:
        super().mover(dt)
        self.esticar = max(0.0, self.esticar - dt)

    def lancar(self, corpo, base_anterior: int) -> bool:
        """Lanca `corpo` se ele cruzou o topo da mola neste quadro.

        O teste e pelo topo **cruzado** (base anterior acima, base atual abaixo)
        e nao por sobreposicao nem por velocidade: numa queda a 25 px de quadro
        o corpo atravessa a mola e toca o chao no mesmo quadro, e ai `vel.y` ja
        zerou — a mola passaria em branco. O cruzamento tambem dispensa saber a
        direcao: subindo por baixo, a base anterior ja esta abaixo do topo.
        """
        if base_anterior > self.corpo.top:
            return False
        if corpo.hitbox.bottom < self.corpo.top:
            return False
        if corpo.hitbox.right <= self.corpo.left or corpo.hitbox.left >= self.corpo.right:
            return False
        self.esticar = DURACAO_ESTICAR
        corpo.vel.y = -IMPULSO_MOLA
        corpo.no_chao = False
        return True

    def desenhar(self, tela: pygame.Surface, camera) -> None:
        """Dois pratos com as espiras no meio; medidas proporcionais ao corpo.

        O contorno e desenhado como borda do retangulo colorido, e nao como
        retangulo preto com um colorido por dentro: no buffer de 1/3 da tela o
        prato tem 2 px e o preto de dentro engolia o vermelho.

        Depois do salto o prato de cima desce e as espiras encolhem — e a unica
        pista visual de que a mola disparou.
        """
        alvo = camera.retangulo_na_tela(self.corpo)
        contorno = 1
        prato = max(2, round(alvo.h * 0.3))
        topo = alvo.top + (round(alvo.h * 0.3) if self.esticar > 0 else 0)
        primeiro = topo + prato
        ultimo = max(primeiro + 1, alvo.bottom - prato)
        for volta in range(3):
            y = primeiro + round((ultimo - primeiro) * (volta + 0.5) / 3)
            recuo = contorno + (contorno if volta % 2 else 0)
            pygame.draw.line(tela, CORES["mola_escura"], (alvo.left + recuo, y), (alvo.right - recuo, y), 1)
        for y in (topo, alvo.bottom - prato):
            caixa = pygame.Rect(alvo.left, y, alvo.w, prato)
            pygame.draw.rect(tela, CORES["mola"], caixa)
            pygame.draw.line(tela, CORES["contorno"], caixa.topleft, (caixa.right - 1, caixa.top), contorno)


class CaixaSolida(Obstaculo):
    """Bloco solido: bloqueia o jogador por todos os lados."""

    solido = True

    def desenhar(self, tela: pygame.Surface, camera) -> None:
        alvo = camera.retangulo_na_tela(self.corpo)
        pygame.draw.rect(tela, CORES["contorno"], alvo, border_radius=4)
        pygame.draw.rect(tela, CORES["caixa"], alvo.inflate(-4, -4), border_radius=3)
        pygame.draw.line(tela, CORES["caixa_escura"], alvo.topleft, alvo.bottomright, 2)
