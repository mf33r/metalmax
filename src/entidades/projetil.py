"""Projetil do pug: o tiro disparado no F depois de pegar o cogumelo "tiro"."""
from __future__ import annotations

import pygame

from src.entidades.entidade import Entidade

VEL = 640.0
NUCLEO = (255, 244, 150)
CASCA = (255, 140, 50)


class Projetil(Entidade):
    """Bala rapida horizontal. Some ao sair do mundo ou acertar o boss."""

    def __init__(self, x: float, y: float, direcao: int):
        super().__init__(x, y, 18, 10)
        self.hitbox = pygame.Rect(round(x), round(y), 18, 10)
        self.direcao = 1 if direcao >= 0 else -1
        self.ativo = True

    def atualizar(self, dt: float) -> None:
        self.pos.x += VEL * self.direcao * dt
        self.hitbox.x = round(self.pos.x)

    def desenhar(self, tela: pygame.Surface, camera) -> None:
        alvo = camera.retangulo_na_tela(self.hitbox)
        pygame.draw.ellipse(tela, CASCA, alvo)
        pygame.draw.ellipse(tela, NUCLEO, alvo.inflate(-max(2, alvo.w // 3), -max(1, alvo.h // 3)))
