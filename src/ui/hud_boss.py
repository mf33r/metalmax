"""HUD extra da fase 2: barra de vida do boss e avisos de poder.

Desenhada na superficie de interface (resolucao cheia), por cima do mundo.
"""
from __future__ import annotations

import pygame

from src.ui.estilo import fonte, painel, texto
from src.ui.config import CORES

_fonte_nome = None
_fonte_aviso = None


def _fontes():
    global _fonte_nome, _fonte_aviso
    if _fonte_nome is None:
        _fonte_nome = fonte(22, bold=True)
        _fonte_aviso = fonte(30, bold=True)
    return _fonte_nome, _fonte_aviso


def barra_boss(ui: pygame.Surface, nome: str, vida: int, vida_max: int) -> None:
    """Barra de vida do chefe, no topo-centro."""
    f_nome, _ = _fontes()
    largura = 440
    altura = 26
    x = ui.get_width() // 2 - largura // 2
    y = 18
    fundo = pygame.Rect(x - 6, y - 6, largura + 12, altura + 30)
    painel(ui, fundo, CORES["painel"], borda="painel_borda", raio=8)
    texto(ui, f_nome, nome, "texto", contorno=2, centro=(ui.get_width() // 2, y + 2))
    barra = pygame.Rect(x, y + 16, largura, altura)
    pygame.draw.rect(ui, (40, 16, 20), barra, border_radius=6)
    frac = max(0.0, vida / max(1, vida_max))
    if frac > 0:
        cheia = pygame.Rect(barra.x + 2, barra.y + 2, int((barra.w - 4) * frac), barra.h - 4)
        pygame.draw.rect(ui, CORES["mola"], cheia, border_radius=5)
        topo = pygame.Rect(cheia.x, cheia.y, cheia.w, max(1, cheia.h // 3))
        pygame.draw.rect(ui, (255, 150, 150), topo, border_radius=4)
    pygame.draw.rect(ui, CORES["contorno"], barra, width=2, border_radius=6)


def aviso_poder(ui: pygame.Surface, mensagem: str, segundos_restantes: float, cor="moeda") -> None:
    """Mensagem estatica no centro-alto da tela (ex.: poder adquirido)."""
    _, f_aviso = _fontes()
    piscar = segundos_restantes > 0.6 and int(segundos_restantes * 3) % 2 == 0
    if piscar:
        return
    texto(ui, f_aviso, mensagem, cor, contorno=3,
          centro=(ui.get_width() // 2, ui.get_height() // 2 - 60))


def selo_invencivel(ui: pygame.Surface, segundos: float) -> None:
    """Contador do brilho/invencibilidade no canto superior direito."""
    f_nome, _ = _fontes()
    cores = [(255, 80, 80), (255, 200, 60), (120, 240, 120), (120, 200, 255), (200, 120, 255)]
    cor = cores[int(segundos * 6) % len(cores)]
    texto(ui, f_nome, f"INVENCIVEL {segundos:0.0f}", cor, contorno=2, cor_contorno="texto_sombra",
          pos=(ui.get_width() - 190, 20))
