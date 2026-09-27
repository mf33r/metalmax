"""Porta de saida, grande e com bandeira: o objetivo nao pode se perder.

Fechada e solida (bloqueia o jogador); com a chave ela abre e o jogador vence.
"""
from __future__ import annotations

import pygame

from src.entidades.entidade import Entidade
from src.ui.config import CORES


class Porta(Entidade):
    """Portal de madeira com bandeira; abre quando recebe a chave."""

    def __init__(self, x: int, y: int, largura: int = 56, altura: int = 72):
        super().__init__(x, y, largura, altura)
        self.corpo = self.hitbox
        self.aberta = False
        self.animacao_abrindo = 0.0

    @property
    def solido(self) -> bool:
        """Solida enquanto fechada (a fisica le este atributo)."""
        return not self.aberta

    def abrir(self) -> None:
        self.aberta = True
        self.animacao_abrindo = 1.0

    def mover(self, dt: float) -> None:
        self.animacao_abrindo = max(0.0, self.animacao_abrindo - dt * 2.5)

    def atualizar(self, dt: float) -> None:
        self.mover(dt)

    # ------------------------------------------------------------ desenho
    def desenhar(self, tela: pygame.Surface, camera) -> None:
        alvo = camera.retangulo_na_tela(self.corpo)
        if self.aberta:
            self._vazio(tela, alvo)
        else:
            self._fechada(tela, alvo)
        self._bandeira(tela, alvo)

    def _fechada(self, tela: pygame.Surface, alvo: pygame.Rect) -> None:
        """Porta de madeira com fechadura brilhante."""
        pygame.draw.rect(tela, CORES["contorno"], alvo.move(0, max(2, alvo.h // 12)), border_radius=4)
        pygame.draw.rect(tela, CORES["madeira_escura"], alvo, border_radius=4)
        interna = pygame.Rect(alvo.x + 4, alvo.y + 4, max(2, alvo.w - 8), max(2, alvo.h - 6))
        pygame.draw.rect(tela, CORES["madeira"], interna, border_radius=3)
        for y in range(interna.y + 6, interna.bottom - 4, max(8, alvo.h // 4)):
            pygame.draw.line(tela, CORES["madeira_escura"], (interna.x + 2, y), (interna.right - 2, y), 2)
        pygame.draw.line(
            tela, CORES["madeira_escura"],
            (interna.centerx, interna.y), (interna.centerx, interna.bottom), 2,
        )
        fechadura = (interna.centerx, interna.centery)
        pygame.draw.circle(tela, CORES["contorno"], fechadura, max(3, alvo.w // 7))
        pygame.draw.circle(tela, CORES["moeda"], fechadura, max(2, alvo.w // 10))

    def _vazio(self, tela: pygame.Surface, alvo: pygame.Rect) -> None:
        """Passagem escura com luz vindo de dentro."""
        pygame.draw.rect(tela, (18, 14, 28), alvo, border_radius=4)
        brilho = pygame.Surface(alvo.size, pygame.SRCALPHA)
        for raio, cor in ((alvo.h // 3, (255, 236, 150, 60)), (alvo.h // 5, (255, 246, 210, 90))):
            pygame.draw.circle(brilho, cor, (alvo.w // 2, alvo.h - raio // 2), raio)
        tela.blit(brilho, alvo.topleft)
        pygame.draw.rect(tela, CORES["contorno"], alvo, width=2, border_radius=4)

    def _bandeira(self, tela: pygame.Surface, alvo: pygame.Rect) -> None:
        """Mastro e bandeira: marca a saida de longe."""
        mastro_x = alvo.right + max(3, alvo.w // 8)
        pygame.draw.line(
            tela, CORES["contorno"],
            (mastro_x, alvo.y - max(6, alvo.h // 6)), (mastro_x, alvo.bottom), 5,
        )
        largura = max(10, alvo.w // 2)
        altura = max(6, alvo.h // 4)
        bandeira = pygame.Rect(mastro_x, alvo.y - max(6, alvo.h // 6), largura, altura)
        pygame.draw.polygon(
            tela, CORES["coracao"] if self.aberta else CORES["moeda"],
            [(bandeira.x, bandeira.y), (bandeira.right, bandeira.centery), (bandeira.x, bandeira.bottom)],
        )
        pygame.draw.polygon(
            tela, CORES["contorno"],
            [(bandeira.x, bandeira.y), (bandeira.right, bandeira.centery), (bandeira.x, bandeira.bottom)],
            2,
        )
