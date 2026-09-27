"""Animacao de sprite sheet: corta as celulas e controla o indice do frame.

Dois cuidados que o sheet do pug exige:

1. **Recorte em comum**: cada celula e cortada pela MESMA area (a uniao das
   areas opacas de todos os frames). Recortar cada frame pelo seu proprio
   contorno muda a largura de um frame para o outro e a animacao treme.
2. **Altura unica**: todos os frames sao normalizados na mesma altura.

O sheet nao tem ciclo de caminhada de verdade (as linhas 9 e 15 sao
identicas frame a frame), entao "andar" alterna duas poses com um bob curto.
"""
from __future__ import annotations

import pygame

from src.ui.config import CEL, DURACAO_FRAME


class Animacao:
    """Sequencia de frames tirados de um sprite sheet uniforme.

    `celulas` e uma lista de (linha, coluna) na grade do sheet.
    `altura_alvo` normaliza a altura de todos os frames (None = mantem a escala).
    """

    def __init__(
        self,
        sheet: pygame.Surface,
        celulas: list[tuple[int, int]],
        escala: float = 1.0,
        duracao_frame: float = DURACAO_FRAME,
        laco: bool = True,
        altura_alvo: int | None = None,
        tingimento: tuple[int, int, int] | None = None,
        bob: int = 0,
    ):
        cortadas = [
            pygame.transform.scale_by(
                sheet.subsurface(pygame.Rect(coluna * CEL, linha * CEL, CEL, CEL)),
                escala,
            )
            for linha, coluna in celulas
        ]
        recorte = self._recorte_comum(cortadas)
        self.frames = [
            self._preparar(sprites.subsurface(recorte), altura_alvo, tingimento)
            for sprites in cortadas
        ]
        self.bob = bob
        self.duracao_frame = duracao_frame
        self.laco = laco
        self.indice = 0
        self.tempo = 0.0

    @staticmethod
    def _recorte_comum(superficies: list[pygame.Surface]) -> pygame.Rect:
        """Uniao das areas opacas: garante que os frames fiquem alinhados."""
        uniao: pygame.Rect | None = None
        for superficie in superficies:
            area = superficie.get_bounding_rect()   # pygame-ce 2.5
            if area is None:
                continue
            uniao = pygame.Rect(area) if uniao is None else uniao.union(area)
        if uniao is None:
            maior = max(superficies, key=lambda s: s.get_width())
            return pygame.Rect((0, 0, maior.get_width(), maior.get_height()))
        return uniao

    @staticmethod
    def _preparar(
        sprite: pygame.Surface,
        altura_alvo: int | None,
        tingimento: tuple[int, int, int] | None,
    ) -> pygame.Surface:
        if altura_alvo and sprite.get_height() > 0:
            fator = altura_alvo / sprite.get_height()
            sprite = pygame.transform.scale(
                sprite, (max(1, round(sprite.get_width() * fator)), altura_alvo)
            )
        sprite = sprite.copy()
        if tingimento:
            # multiplica as cores: o inimigo nasce da mesma arte, so com a cor trocada
            sprite.fill(tingimento, special_flags=pygame.BLEND_RGB_MULT)
        return sprite

    def __len__(self) -> int:
        return len(self.frames)

    def reiniciar(self) -> None:
        self.indice = 0
        self.tempo = 0.0

    def avancar(self, dt: float) -> None:
        if len(self.frames) < 2:
            return
        self.tempo += dt
        while self.tempo >= self.duracao_frame:
            self.tempo -= self.duracao_frame
            self.indice += 1
            if self.indice >= len(self.frames):
                self.indice = 0 if self.laco else len(self.frames) - 1

    @property
    def frame(self) -> pygame.Surface:
        return self.frames[self.indice]

    @property
    def deslocamento_y(self) -> int:
        """Bob do ciclo: sobe a cada quadro par, como o corpo numa caminhada."""
        if not self.bob or self.indice % 2 == 0:
            return 0
        return self.bob
