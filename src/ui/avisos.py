"""Paineis de aviso pixelados: pausa, controles, fim de jogo e vitoria."""
from __future__ import annotations

import pygame

from src.ui.estilo import fonte, painel, px, texto
from src.ui.config import CORES

OPACIDADE = 185


class Aviso:
    """Caixa central de madeira com titulo e subtitulo."""

    def __init__(self) -> None:
        self.fonte_titulo = fonte(52)
        self.fonte_subtitulo = fonte(20)
        self._titulo = ""
        self._subtitulo = ""

    def mostrar(self, titulo: str, subtitulo: str = "") -> None:
        """`subtitulo` aceita varias linhas separadas por \\n."""
        self._titulo = titulo
        self._subtitulo = subtitulo

    def esconder(self) -> None:
        self.mostrar("")

    def desenhar(self, tela: pygame.Surface) -> None:
        if not self._titulo:
            return

        largura, altura = tela.get_size()
        sombra = pygame.Surface((largura, altura), pygame.SRCALPHA)
        sombra.fill((16, 10, 20, OPACIDADE))
        tela.blit(sombra, (0, 0))

        linhas = [linha for linha in self._subtitulo.split("\n") if linha]
        caixa = pygame.Rect(0, 0, px(460), px(90) + len(linhas) * px(22))
        caixa.center = (largura // 2, altura // 2)
        painel(tela, caixa, CORES["painel"], borda="contorno", raio=px(10))

        texto(tela, self.fonte_titulo, self._titulo, CORES["moeda"],
              contorno=1, centro=(caixa.centerx, caixa.y + px(24)))
        for indice, linha in enumerate(linhas):
            texto(tela, self.fonte_subtitulo, linha, CORES["texto"],
                  contorno=1, centro=(caixa.centerx, caixa.y + px(50) + indice * px(22)))
