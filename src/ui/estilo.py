"""Estilo da interface, no mesmo modo pixelado do mundo.

A interface e desenhada num buffer 1/3 da resolucao e ampliada sem
interpolacao, igual ao cenario. Entao as fontes sao criadas pequenas e os
tamanhos passam por `px()`: o resultado e pixel de verdade, nao texto suave.
"""
from __future__ import annotations

import pygame

from src.ui.config import ESCALA_PIXEL
from src.ui.cores import CORES, ESPESSURA_CONTORNO

def px(valor: float) -> int:
    """Tamanho de tela em pixels de tela.

    A interface e desenhada em resolucao cheia (o pixel art fica so no mundo
    e nos icones); reduzir a fonte a um terco deixava o texto ilegivel.
    """
    return max(1, round(valor))


def fonte(tamanho: int, bold: bool = True) -> pygame.font.Font:
    """Fonte no tamanho informado, com o peso de cartaz de fliperama."""
    return pygame.font.SysFont(None, max(8, tamanho), bold=bold)


def _cor(cor) -> tuple:
    """Aceita uma cor ou a chave de CORES."""
    return CORES[cor] if isinstance(cor, str) else cor


def sombrear(cor, fator: float = 0.75) -> tuple[int, int, int]:
    return tuple(max(0, min(255, round(c * fator))) for c in _cor(cor))


def clarear(cor, fator: float = 0.3) -> tuple[int, int, int]:
    return tuple(max(0, min(255, round(c + (255 - c) * fator))) for c in _cor(cor))


# ------------------------------------------------------------------ formas
def painel(
    tela: pygame.Surface,
    rect: pygame.Rect,
    cor,
    *,
    borda=None,
    raio: int = 4,
) -> None:
    """Caixa de interface com contorno grosso e sombra dura."""
    cor_borda = CORES[borda] if isinstance(borda, str) else (borda or CORES["painel_borda"])
    pygame.draw.rect(tela, CORES["sombra"], rect.move(0, max(1, rect.h // 12)), border_radius=raio)
    pygame.draw.rect(tela, cor_borda, rect, border_radius=raio)
    pygame.draw.rect(tela, _cor(cor), rect.inflate(-3, -3), border_radius=max(1, raio - 1))


def bola(tela: pygame.Surface, centro: tuple[int, int], raio: int, cor, contorno: bool = True) -> None:
    """Circulo com sombra, brilho e contorno."""
    pygame.draw.circle(tela, sombrear(cor, 0.6), (centro[0], centro[1] + 1), raio)
    pygame.draw.circle(tela, _cor(cor), centro, raio)
    pygame.draw.circle(tela, clarear(cor, 0.45), (centro[0] - raio // 3, centro[1] - raio // 3), max(1, raio // 3))
    if contorno:
        pygame.draw.circle(tela, CORES["contorno"], centro, raio, 1)


def caixa_item(tela: pygame.Surface, rect: pygame.Rect, cor_tarja, *, contorno=2) -> None:
    """Caixa coletavel: madeira, tarja colorida e contorno grosso.

    desenhada em codigo, e nao recortada do sheet: em qualquer tamanho sai
    nitida, e o inventario mostra exatamente a mesma peca do cenario.
    """
    largura = max(3, rect.w)
    altura = max(3, rect.h)
    caixa = pygame.Rect(rect.x, rect.y, largura, altura)
    pygame.draw.rect(tela, CORES["sombra"], caixa.move(0, max(1, altura // 5)), border_radius=max(1, altura // 5))
    pygame.draw.rect(tela, (168, 122, 78), caixa, border_radius=max(1, altura // 5))
    tarja = pygame.Rect(caixa.x + 2, caixa.y + max(1, altura // 3), largura - 4, max(2, altura // 3))
    pygame.draw.rect(tela, _cor(cor_tarja), tarja)
    pygame.draw.rect(tela, CORES["contorno"], caixa, width=contorno, border_radius=max(1, altura // 5))


# Coracao em pixel art: cada caractere e um pixel do sprite.
CORACAO_PIXEL = (
    ".##.##.",
    "#######",
    "#######",
    "#######",
    ".#####.",
    "..###..",
    "...#...",
)


def coracao(tela: pygame.Surface, centro: tuple[int, int], escala: int, cor, *, vazio=False) -> None:
    """Coracao pixelado, desenhado de uma matriz: sem suavizar nada."""
    largura = len(CORACAO_PIXEL[0]) * escala
    altura = len(CORACAO_PIXEL) * escala
    x0 = centro[0] - largura // 2
    y0 = centro[1] - altura // 2
    cor = CORES["painel_borda"] if vazio else cor
    for linha, texto_linha in enumerate(CORACAO_PIXEL):
        for coluna, caractere in enumerate(texto_linha):
            if caractere == "#":
                pygame.draw.rect(
                    tela, cor,
                    pygame.Rect(x0 + coluna * escala, y0 + linha * escala, escala, escala),
                )


def texto(
    tela: pygame.Surface,
    fonte_atual: pygame.font.Font,
    conteudo: str,
    cor,
    *,
    contorno: int = 1,
    cor_contorno=None,
    centro: tuple[int, int] | None = None,
    pos: tuple[int, int] | None = None,
) -> pygame.Rect:
    """Desenha texto com contorno e devolve o retangulo ocupado.

    `cor_contorno` existe porque texto escuro precisa de contorno claro: com
    contorno escuro a letra fecha os vazios e vira um borrao.
    """
    frente = fonte_atual.render(conteudo, True, _cor(cor))
    sombra = fonte_atual.render(conteudo, True, _cor(cor_contorno) if cor_contorno else CORES["texto_sombra"])
    largura = frente.get_width() + contorno * 2
    altura = frente.get_height() + contorno * 2

    alvo = pygame.Surface((largura, altura), pygame.SRCALPHA)
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)):
        alvo.blit(sombra, (dx * contorno + contorno, dy * contorno + contorno))
    alvo.blit(frente, (contorno, contorno))

    destino = pygame.Rect(0, 0, largura, altura)
    if centro is not None:
        destino.center = centro
    elif pos is not None:
        destino.topleft = pos
    tela.blit(alvo, destino)
    return destino
