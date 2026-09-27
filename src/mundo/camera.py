"""Camera que persegue o jogador e recorta o que esta fora da tela.

Toda entidade e desenhada em `pos - camera.offset`, portanto o offset e a
unica fonte de verdade de "onde estamos no mundo".

`escala` existe para o mundo pixelado: quando o jogo desenha num buffer
pequeno, a camera converte unidades de mundo em pixels desse buffer, e depois
o buffer e ampliado sem interpolacao.
"""
from __future__ import annotations

import pygame

from src.ui.config import TREINAMENTO_CAMERA


class Camera:
    def __init__(self, largura_tela: int, altura_tela: int, largura_mundo: int, altura_mundo: int):
        self.largura_tela = largura_tela
        self.altura_tela = altura_tela
        self.largura_mundo = largura_mundo
        self.altura_mundo = altura_mundo
        self.offset = pygame.Vector2(0, 0)
        self.escala = 1.0

    def seguir(self, alvo: pygame.Vector2, dt: float) -> None:
        """Persegue `alvo` com suavizacao e trava dentro dos limites do mundo."""
        desejado = pygame.Vector2(
            alvo.x - self.largura_tela / 2,
            alvo.y - self.altura_tela / 2,
        )
        self.offset.x += (desejado.x - self.offset.x) * min(1.0, TREINAMENTO_CAMERA * dt)
        self.offset.y += (desejado.y - self.offset.y) * min(1.0, TREINAMENTO_CAMERA * dt)
        self.offset.x = min(max(self.offset.x, 0.0), max(0.0, self.largura_mundo - self.largura_tela))
        self.offset.y = min(max(self.offset.y, 0.0), max(0.0, self.altura_mundo - self.altura_tela))

    # ------------------------------------------------------------- consultas
    def ponto_na_tela(self, ponto) -> tuple[int, int]:
        return (
            round((ponto[0] - self.offset.x) * self.escala),
            round((ponto[1] - self.offset.y) * self.escala),
        )

    def retangulo_na_tela(self, ret: pygame.Rect) -> pygame.Rect:
        escala = self.escala
        return pygame.Rect(
            round((ret.x - self.offset.x) * escala),
            round((ret.y - self.offset.y) * escala),
            max(1, round(ret.w * escala)),
            max(1, round(ret.h * escala)),
        )

    def escalar(self, superficie: pygame.Surface) -> pygame.Surface:
        """Aplica a escala da camera numa superficie (sprite)."""
        if self.escala == 1.0:
            return superficie
        return pygame.transform.scale(
            superficie,
            (max(1, round(superficie.get_width() * self.escala)),
             max(1, round(superficie.get_height() * self.escala))),
        )

    def visivel(self, ret: pygame.Rect, margem: int = 96) -> bool:
        """True se o retangulo toca a area visivel (culling)."""
        return (
            ret.right + margem > self.offset.x
            and ret.left - margem < self.offset.x + self.largura_tela
            and ret.bottom + margem > self.offset.y
            and ret.top - margem < self.offset.y + self.altura_tela
        )
