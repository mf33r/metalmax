"""Terra que voa quando um corpo explode.

Nao e sangue: o respingo e marrom, feito de grumos de terra. Cada particula e
balistica pura — so gravidade, sem colisao — e encolhe ate sumir; a explosao
inteira e uma lista que o nivel descarta quando esvazia.
"""
from __future__ import annotations

import math
import random

import pygame

from src.entidades.entidade import Entidade
from src.ui.config import (
    GRAVIDADE_PARTICULA,
    PARTICULAS_EXPLOSAO,
    TAMANHO_PARTICULA,
    VEL_PARTICULA,
    VIDA_PARTICULA,
)
from src.ui.cores import CORES

# Tons de terra: marrom, nunca vermelho.
CORES_TERRA = (CORES["terra"], CORES["terra_escura"], CORES["madeira"], CORES["madeira_escura"])

# Teto de queda das particulas: menor que o `TETO_QUEDA` dos corpos, para a
# terra nao sumir da tela como um raio.
_TETO_QUEDA = 900.0


class Particula(Entidade):
    """Grumo de terra: sai voando, cai com a gravidade e encolhe ate sumir."""

    def __init__(self, x: float, y: float, cor, tamanho: int, velocidade, vida: float):
        super().__init__(x, y, tamanho, tamanho)
        self.cor = cor
        self.vel.update(velocidade)
        self.vida = vida
        self.vida_maxima = vida

    def atualizar(self, dt: float) -> bool:
        """Integra o voo; devolve False quando a particula ja morreu."""
        self.vel.y = min(self.vel.y + GRAVIDADE_PARTICULA * dt, _TETO_QUEDA)
        self.pos += self.vel * dt
        self.vida -= dt
        self.sincronizar_hitbox()
        return self.vida > 0

    def desenhar(self, tela: pygame.Surface, camera) -> None:
        """Encolhe com a idade: no buffer pixelado, o tamanho e o visual."""
        restante = max(0.0, self.vida / self.vida_maxima)
        alvo = camera.retangulo_na_tela(self.hitbox)
        lado = max(1, round(min(alvo.w, alvo.h) * restante))
        pygame.draw.rect(
            tela, self.cor,
            pygame.Rect(alvo.centerx - lado // 2, alvo.centery - lado // 2, lado, lado),
        )


class Explosao:
    """Nuvem de terra de um corpo que explodiu; se apaga sozinha."""

    def __init__(
        self,
        x: float,
        y: float,
        raio: float = 0.0,
        quantidade: int = PARTICULAS_EXPLOSAO,
        semente: int | None = None,
    ):
        """Sorteia um disparo em todas as direcoes, dentro de `raio` do centro."""
        sorteio = random.Random(semente)
        self.particulas = [self._criar(x, y, raio, sorteio) for _ in range(quantidade)]

    @staticmethod
    def _criar(x: float, y: float, raio: float, sorteio: random.Random) -> Particula:
        angulo = sorteio.uniform(0.0, math.tau)
        cos, sen = math.cos(angulo), math.sin(angulo)
        distancia = raio * math.sqrt(sorteio.random())   # area do circulo, sem empilhar no centro
        velocidade = VEL_PARTICULA * sorteio.uniform(0.35, 1.0)
        return Particula(
            x + cos * distancia,
            y + sen * distancia,
            sorteio.choice(CORES_TERRA),
            sorteio.randint(TAMANHO_PARTICULA - 1, TAMANHO_PARTICULA + 2),
            (cos * velocidade, sen * velocidade - VEL_PARTICULA * 0.35),   # viés para cima
            VIDA_PARTICULA * sorteio.uniform(0.7, 1.3),
        )

    @property
    def viva(self) -> bool:
        return bool(self.particulas)

    def atualizar(self, dt: float) -> bool:
        """Avança as particulas; devolve False quando todas ja morreram."""
        self.particulas = [p for p in self.particulas if p.atualizar(dt)]
        return self.viva

    def desenhar(self, tela: pygame.Surface, camera) -> None:
        for particula in self.particulas:
            particula.desenhar(tela, camera)
