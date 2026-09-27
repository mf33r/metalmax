"""Carregamento de imagens com cache, resolvendo caminhos a partir de config.

Evita que cada entidade carregue o mesmo arquivo do disco.
"""
from __future__ import annotations

import pygame

from src.ui.config import ASSETS_DIR, CEL

_cache: dict[tuple[str, tuple[int, int] | None], pygame.Surface] = {}
_icones: dict[tuple[tuple[int, int], int], pygame.Surface] = {}


def icone(celula: tuple[int, int], tamanho: int) -> pygame.Surface:
    """Recorta um icone do sprite sheet e ajusta na medida pedida.

    A arte do icone fica no centro da celula de 128 px; sem recortar, o item
    sai pequeno e deslocado.
    """
    chave = (celula, tamanho)
    if chave not in _icones:
        celula_png = imagem("pug.png").subsurface(
            pygame.Rect(celula[1] * CEL, celula[0] * CEL, CEL, CEL)
        )
        recorte = celula_png.get_bounding_rect()
        if recorte:
            celula_png = celula_png.subsurface(recorte)
        largura = celula_png.get_width()
        escala = tamanho / max(1, largura)
        _icones[chave] = pygame.transform.smoothscale(
            celula_png, (tamanho, max(1, round(celula_png.get_height() * escala)))
        )
    return _icones[chave]


def caminho(nome_arquivo: str):
    """Retorna o caminho absoluto de um asset."""
    return ASSETS_DIR / nome_arquivo


def imagem(nome_arquivo: str, escala: tuple[int, int] | None = None) -> pygame.Surface:
    """Carrega (uma unica vez) uma imagem, opcionalmente escalada."""
    chave = (nome_arquivo, escala)
    if chave not in _cache:
        superficie = pygame.image.load(caminho(nome_arquivo)).convert_alpha()
        if escala is not None:
            superficie = pygame.transform.scale(superficie, escala)
        _cache[chave] = superficie
    return _cache[chave]
