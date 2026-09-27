"""Raiz da hierarquia do jogo: `Entidade` e o mixin `CorpoFisico`.

Toda coisa que existe no mundo e herda de `Entidade`. Coisas que caem e
colidem herdam tambem de `CorpoFisico`, que concentra posicao, velocidade,
gravidade e hitbox.
"""
from __future__ import annotations

import pygame

from src.ui.config import TETO_QUEDA

class Entidade:
    """Base de tudo que tem posicao no mundo e sabe se desenhar."""

    def __init__(self, x: float, y: float, largura: int, altura: int):
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2()
        self.largura = largura
        self.altura = altura
        self.hitbox = pygame.Rect(round(x), round(y), largura, altura)
        self.ativo = True

    def sincronizar_hitbox(self) -> None:
        self.hitbox.topleft = (round(self.pos.x), round(self.pos.y))

    def sincronizar_posicao(self) -> None:
        """Copia o hitbox de volta para `pos` (a colisao manda no movimento)."""
        self.pos.update(self.hitbox.x, self.hitbox.y)

    # -------------------------------------------------------- ciclo base
    def atualizar(self, dt: float) -> None:
        self.mover(dt)
        self.sincronizar_hitbox()

    def mover(self, dt: float) -> None:
        self.pos += self.vel * dt

    def desenhar(self, tela: pygame.Surface, camera) -> None:
        raise NotImplementedError

    def __repr__(self) -> str:  # pragma: no cover - depuracao
        return f"<{type(self).__name__} pos=({self.pos.x:.0f}, {self.pos.y:.0f})>"


class CorpoFisico(Entidade):
    """Entidade com velocidade, gravidade e movimento por teclado ou IA."""

    velocidade_andar: float = 0.0
    teto_queda: float = TETO_QUEDA

    def __init__(self, x: float, y: float, largura: int, altura: int, gravidade: float = 1800.0):
        super().__init__(x, y, largura, altura)
        self.gravidade = gravidade
        self.virado = False
        self.no_chao = False

    def aplicar_gravidade(self, dt: float) -> None:
        self.vel.y = min(self.vel.y + self.gravidade * dt, self.teto_queda)

    def andar_para(self, direcao: int) -> None:
        """Define a horizontal; `direcao` em {-1, 0, 1}."""
        self.vel.x = direcao * self.velocidade_andar
        if direcao:
            self.virado = direcao < 0

    def pular(self, forca: float) -> None:
        self.vel.y = -forca
        self.no_chao = False
