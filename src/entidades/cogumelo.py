"""Cogumelos de poder: dois itens que o pug pega ao passar por cima.

- "brilho": deixa o pug invencivel e brilhando em cores por 15s (cruzar a lava).
- "tiro":   desbloqueia o disparo no F (permanente), usado contra o boss.

Desenhados em codigo (chapeu + pe), sem depender de sprite.
"""
from __future__ import annotations

import math

import pygame

from src.entidades.entidade import Entidade

PE = (238, 230, 206)
PE_SOMBRA = (198, 188, 164)
CONTORNO = (46, 40, 38)
# chapeu por tipo
CHAPEU = {"brilho": (150, 92, 52), "tiro": (214, 58, 58)}
CHAPEU_CLARO = {"brilho": (190, 128, 80), "tiro": (248, 108, 104)}
PINTA = (245, 240, 230)


class Cogumelo(Entidade):
    """Item parado no chao; o nivel checa a coleta pelo hitbox."""

    LARGURA = 46
    ALTURA = 50

    def __init__(self, x: int, y: int, tipo: str):
        super().__init__(x, y, self.LARGURA, self.ALTURA)
        self.hitbox = pygame.Rect(x, y, self.LARGURA, self.ALTURA)
        self.tipo = tipo
        self.ativo = True
        self.t = 0.0

    def atualizar(self, dt: float) -> None:
        self.t += dt

    def desenhar(self, tela: pygame.Surface, camera) -> None:
        if not self.ativo:
            return
        alvo = camera.retangulo_na_tela(self.hitbox)
        bob = round(math.sin(self.t * 3.0) * max(1, alvo.h * 0.07))
        alvo = alvo.move(0, bob)
        cor = CHAPEU[self.tipo]
        claro = CHAPEU_CLARO[self.tipo]

        # pe gordinho (ocupa a metade de baixo)
        pe_w = max(4, alvo.w // 2)
        pe = pygame.Rect(alvo.centerx - pe_w // 2, alvo.centery - 2, pe_w, alvo.bottom - alvo.centery + 2)
        pygame.draw.rect(tela, PE_SOMBRA, pe.move(max(1, alvo.w // 20), 0), border_radius=max(2, pe_w // 3))
        pygame.draw.rect(tela, PE, pe, border_radius=max(2, pe_w // 3))
        pygame.draw.rect(tela, CONTORNO, pe, width=max(1, alvo.w // 22), border_radius=max(2, pe_w // 3))

        # chapeu: meia-cupula bem visivel
        chapeu = pygame.Rect(alvo.x, alvo.y, alvo.w, max(6, int(alvo.h * 0.58)))
        pygame.draw.ellipse(tela, cor, chapeu)
        base = pygame.Rect(chapeu.x, chapeu.centery, chapeu.w, chapeu.h // 2)
        pygame.draw.rect(tela, cor, base)
        # brilho no alto do chapeu
        topo = chapeu.inflate(-max(3, alvo.w // 4), 0)
        topo.height = max(3, chapeu.h // 2)
        topo.top = chapeu.top + max(1, chapeu.h // 8)
        pygame.draw.ellipse(tela, claro, topo)
        # contorno do chapeu inteiro
        pygame.draw.ellipse(tela, CONTORNO, chapeu, max(1, alvo.w // 20))
        pygame.draw.line(tela, CONTORNO, (base.left, base.bottom - 1), (base.right, base.bottom - 1), max(1, alvo.w // 22))
        # pintas brancas
        for dx, dy in ((-0.26, -0.05), (0.14, -0.12), (-0.02, 0.12)):
            c = (chapeu.centerx + int(chapeu.w * dx), chapeu.centery + int(chapeu.h * dy))
            pygame.draw.circle(tela, PINTA, c, max(2, alvo.w // 9))

    def coletar(self) -> None:
        self.ativo = False
