"""Lava: perigo que explode o corpo igual ao espinho (morte instantanea).

Preenche os buracos entre os chaos e forra o corredor impossivel. So a
invencibilidade do cogumelo marrom deixa o pug atravessar.
"""
from __future__ import annotations

import math

import pygame

from src.entidades.entidade import Entidade

VERMELHO_FUNDO = (120, 24, 12)
LARANJA = (232, 92, 24)
BRILHO = (255, 190, 70)


class Lava(Entidade):
    """Poca de lava borbulhante. `perigoso` para o nivel tratar como morte."""

    solido = False
    perigoso = True

    def __init__(self, x: int, y: int, largura: int, altura: int):
        super().__init__(x, y, largura, altura)
        self.corpo = self.hitbox
        self.t = 0.0

    def atualizar(self, dt: float) -> None:
        self.t += dt

    def desenhar(self, tela: pygame.Surface, camera) -> None:
        """Poca de lava: paredes escuras de rocha e a lava recuada do topo."""
        alvo = camera.retangulo_na_tela(self.corpo)
        # parede/rocha escura da piscina (o buraco)
        pygame.draw.rect(tela, (54, 22, 18), alvo)
        # lava recuada do topo -> da a ideia de superficie abaixo da borda
        recuo = max(2, alvo.h // 5)
        poca = pygame.Rect(alvo.x + 2, alvo.top + recuo, max(2, alvo.w - 4), max(2, alvo.h - recuo))
        pygame.draw.rect(tela, VERMELHO_FUNDO, poca)
        meio = pygame.Rect(poca.x + 2, poca.top + max(1, poca.h // 6), max(2, poca.w - 4), max(2, poca.h // 2))
        pygame.draw.rect(tela, LARANJA, meio)
        # bolhas brilhando na superficie da lava
        passo = max(8, alvo.h)
        raio = max(1, poca.h // 6)
        for i, x in enumerate(range(poca.left, poca.right, passo)):
            oy = math.sin(self.t * 3.0 + i * 0.9) * max(1, poca.h // 8)
            pygame.draw.circle(tela, BRILHO, (x + passo // 2, int(poca.top + oy)), raio)
        # lip claro na borda de cima da piscina
        pygame.draw.line(tela, (96, 44, 32), (alvo.left, alvo.top), (alvo.right, alvo.top), max(1, alvo.h // 14))
