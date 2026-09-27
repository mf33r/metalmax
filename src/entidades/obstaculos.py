"""Obstaculos pintados: espinhos que machucam e caixas que bloqueiam."""
from __future__ import annotations

import pygame

from src.entidades.entidade import Entidade
from src.ui.cores import CORES, ESPESSURA_CONTORNO


class Obstaculo(Entidade):
    """Base dos obstaculos do cenario."""

    solido = False
    perigoso = False
    dano = 1

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
    """Serra de espinhos no chao: causa dano, nao impede a passagem."""

    perigoso = True
    dano = 1

    def __init__(self, x: int, y: int, largura: int, altura: int = 26):
        super().__init__(x, y, largura, altura)

    def desenhar(self, tela: pygame.Surface, camera) -> None:
        alvo = camera.retangulo_na_tela(self.corpo)
        passo = 22
        for esquerda in range(alvo.left, alvo.right, passo):
            largura = min(passo, alvo.right - esquerda)
            pontos = [(esquerda, alvo.bottom), (esquerda + largura / 2, alvo.top), (esquerda + largura, alvo.bottom)]
            pygame.draw.polygon(tela, CORES["espinho_escura"], [(x, y + 3) for x, y in pontos])
            pygame.draw.polygon(tela, CORES["espinho"], pontos)
            pygame.draw.polygon(tela, CORES["contorno"], pontos, ESPESSURA_CONTORNO)


class CaixaSolida(Obstaculo):
    """Bloco solido: bloqueia o jogador por todos os lados."""

    solido = True

    def desenhar(self, tela: pygame.Surface, camera) -> None:
        alvo = camera.retangulo_na_tela(self.corpo)
        pygame.draw.rect(tela, CORES["contorno"], alvo, border_radius=4)
        pygame.draw.rect(tela, CORES["caixa"], alvo.inflate(-4, -4), border_radius=3)
        pygame.draw.line(tela, CORES["caixa_escura"], alvo.topleft, alvo.bottomright, 2)
