"""Plataformas: superficie estatica e plataforma movel.

A espessura e a escala: com o personagem em 34 px, uma tabua grossa demais
come o cenario. `espessura` define tanto o retangulo de colisao quanto o
desenho, e todas as medidas do desenho sao proporcionais a ele — assim a arte
fica igual no buffer pixelado e na tela cheia.
"""
from __future__ import annotations

import pygame

from src.entidades.entidade import Entidade
from src.ui.config import CORES


class Plataforma(Entidade):
    """Superficie solida de sentido unico: da para pular atraves dela."""

    def __init__(self, x: int, y: int, largura: int, espessura: int = 12, chao: bool = False):
        super().__init__(x, y, largura, espessura)
        self.corpo = self.hitbox
        self.espessura = espessura
        self.chao = chao
        self.dx = 0.0
        self.dy = 0.0

    def mover(self, dt: float) -> None:
        self.dx = 0.0
        self.dy = 0.0

    # -------------------------------------------------------------- desenho
    def desenhar(self, tela: pygame.Surface, camera) -> None:
        alvo = camera.retangulo_na_tela(self.corpo)
        if self.chao:
            self._desenhar_chao(tela, alvo)
        else:
            self._desenhar_tabuado(tela, alvo)

    def _desenhar_tabuado(self, tela: pygame.Surface, alvo: pygame.Rect) -> None:
        """Tabua com topo iluminado, contorno e sombra embaixo."""
        sombra = pygame.Rect(alvo.x, alvo.y + max(1, alvo.h // 5), alvo.w, alvo.h)
        pygame.draw.rect(tela, CORES["contorno"], sombra, border_radius=max(2, alvo.h // 2))
        pygame.draw.rect(tela, CORES["madeira_escura"], alvo, border_radius=max(2, alvo.h // 3))
        topo = pygame.Rect(alvo.x + 2, alvo.y + 1, max(1, alvo.w - 4), max(1, alvo.h // 2))
        pygame.draw.rect(tela, CORES["plataforma_topo"], topo, border_radius=max(1, alvo.h // 4))

    def _desenhar_chao(self, tela: pygame.Surface, alvo: pygame.Rect) -> None:
        """Terra com faixa de grama; medidas proporcionais ao retangulo."""
        pygame.draw.rect(tela, CORES["terra_escura"], alvo)
        pygame.draw.rect(tela, CORES["terra"], pygame.Rect(alvo.x, alvo.y, alvo.w, max(1, alvo.h - 2)))
        altura_grama = max(2, round(alvo.h * 0.10))
        pedrinho = max(1, round(alvo.h * 0.05))
        largura_pedrinho = max(3, round(alvo.w * 0.02))
        for x in range(alvo.x + 6, alvo.right, 22):
            pygame.draw.rect(
                tela, CORES["terra_escura"],
                pygame.Rect(x, alvo.y + altura_grama + pedrinho * 3, largura_pedrinho, pedrinho),
            )
        pygame.draw.rect(tela, CORES["grama"], pygame.Rect(alvo.x, alvo.y, alvo.w, altura_grama))


class PlataformaMovel(Plataforma):
    """Plataforma que percorre um trecho e volta (ida e volta infinita)."""

    EIXOS = {"h": "x", "v": "y"}

    def __init__(
        self,
        x: int,
        y: int,
        largura: int,
        alcance: int,
        velocidade: float = 70.0,
        eixo: str = "h",
        espessura: int = 10,
    ):
        super().__init__(x, y, largura, espessura)
        self.eixo = eixo
        self.componente = self.EIXOS[eixo]
        self.alcance = alcance
        self.velocidade = velocidade
        self.origem = pygame.Vector2(x, y)
        self.direcao = 1 if alcance > 0 else -1

    def mover(self, dt: float) -> None:
        origem = getattr(self.origem, self.componente)
        novo = getattr(self.pos, self.componente) + self.direcao * self.velocidade * dt
        if abs(novo - origem) > self.alcance:
            novo = origem + self.alcance * self.direcao
            self.direcao *= -1
        setattr(self.pos, self.componente, novo)

        # delta sem arredondar: arredondado aqui, o corpo carregado acumularia
        # meio pixel de erro por quadro e escorregaria da plataforma
        self.dx = self.pos.x - self.corpo.x
        self.dy = self.pos.y - self.corpo.y
        self.corpo.topleft = (round(self.pos.x), round(self.pos.y))

    def desenhar(self, tela: pygame.Surface, camera) -> None:
        alvo = camera.retangulo_na_tela(self.corpo)
        pygame.draw.rect(tela, CORES["contorno"], alvo.move(0, max(1, alvo.h // 4)), border_radius=4)
        pygame.draw.rect(tela, CORES["ponte"], alvo, border_radius=max(2, alvo.h // 2))
        pygame.draw.rect(
            tela, CORES["nuvem"],
            pygame.Rect(alvo.x + 3, alvo.y + 1, max(1, alvo.w - 6), max(1, alvo.h // 3)),
            border_radius=2,
        )
        for deslocamento in (-1, 1):   # tracinhos de "isto se move"
            pygame.draw.circle(
                tela, CORES["contorno"],
                (alvo.centerx + deslocamento * max(3, alvo.w // 5), alvo.centery),
                max(1, alvo.h // 10),
            )
