"""Cenario pintado com a paleta do pug, desenhado em coordenadas de mundo.

Tudo aqui e ancorado no mundo (y do chao, altura das montanhas), e convertido
em pixels pela camera. Assim o fundo funciona igual no buffer pixelado e numa
tela de resolucao cheia.
"""
from __future__ import annotations

import math

import pygame

from src.ui.config import CHAO_Y, CORES

# (fator de parallax, base no mundo, altura, cor) — de longe para perto
MONTANHAS = [
    (0.18, 500, 140, CORES["montanha_escura"]),
    (0.32, 570, 100, CORES["montanha"]),
]
NUVENS = [
    (0.12, 130, 34, 1.0),
    (0.22, 250, 26, 0.8),
]
COLINAS = (0.5, 84, CORES["colina_escura"], CORES["colina"])


class Cenario:
    """Fundo em camadas: ceu, sol, nuvens, montanhas e colinas."""

    def __init__(self, largura: int = 1400, altura: int = 700):
        self.largura = largura
        self.altura = altura

    def desenhar(self, tela: pygame.Surface, camera) -> None:
        _ceu(tela)
        _sol(tela, camera)
        _nuvens(tela, camera)
        _montanhas(tela, camera)
        _colinas(tela, camera)


def _px(camera, x: float, y: float) -> tuple[int, int]:
    """Converte ponto de mundo em pixel da superficie."""
    return camera.ponto_na_tela((x, y))


def _ceu(tela: pygame.Surface) -> None:
    """Gradiente de ceu de tarde, do azul alto ate o creme do horizonte."""
    altura = tela.get_height()
    topo, base = CORES["ceu_alto"], CORES["ceu_baixo"]
    for linha in range(altura):
        t = linha / max(1, altura - 1)
        cor = tuple(round(topo[i] + (base[i] - topo[i]) * (t ** 0.7)) for i in range(3))
        pygame.draw.line(tela, cor, (0, linha), (tela.get_width(), linha))


def _sol(tela: pygame.Surface, camera) -> None:
    """Sol baixo a esquerda, com halo suave."""
    centro = _px(camera, 250, 150)
    for raio, cor in ((86, (248, 222, 162)), (64, (252, 236, 186)), (46, (253, 246, 214))):
        pygame.draw.circle(tela, cor, centro, max(2, round(raio * camera.escala)))


def _nuvens(tela: pygame.Surface, camera) -> None:
    """Nuvens fofas em duas alturas, com parallax proprio."""
    largura_mundo = camera.offset.x + camera.largura_tela + 200
    for indice, (fator, base_y, raio, escala) in enumerate(NUVENS):
        deslocamento = camera.offset.x * fator
        passo = 620
        primeiro = int(deslocamento // passo) - 1
        for repeticao in range(primeiro, primeiro + int(largura_mundo / passo) + 3):
            centro_x = repeticao * passo - deslocamento + 140
            centro_y = base_y + math.sin(repeticao * 1.7 + indice) * 26
            for deslocado, raio_parte in ((-58, 0.8), (0, 1.0), (58, 0.82)):
                centro = _px(camera, centro_x + deslocado, centro_y)
                pygame.draw.circle(
                    tela, CORES["nuvem"], centro,
                    max(2, round(raio * raio_parte * escala * camera.escala)),
                )


def _montanhas(tela: pygame.Surface, camera) -> None:
    """Silhueta de montanhas em duas fileiras, com parallax."""
    for indice, (fator, base, pico, cor) in enumerate(MONTANHAS):
        deslocamento = camera.offset.x * fator
        passo = 340
        primeiro = int(deslocamento // passo) - 1
        pontos = [_px(camera, -60, base + 200)]
        for repeticao in range(primeiro, primeiro + int(camera.largura_tela / passo) + 4):
            centro_x = repeticao * passo - deslocamento
            altura_local = pico * (0.7 if (repeticao + indice) % 2 else 1.0)
            pontos.append(_px(camera, centro_x - passo / 2, base))
            pontos.append(_px(camera, centro_x, base - altura_local))
            pontos.append(_px(camera, centro_x + passo / 2, base))
        pontos.append(_px(camera, camera.offset.x + camera.largura_tela + 60, base + 200))
        pygame.draw.polygon(tela, cor, pontos)


def _colinas(tela: pygame.Surface, camera) -> None:
    """Morroes arredondados logo atras do chao."""
    deslocamento = camera.offset.x * COLINAS[0]
    passo = 300
    primeiro = int(deslocamento // passo) - 1
    escuro, claro = COLINAS[2], COLINAS[3]
    for indice in range(primeiro, primeiro + int(camera.largura_tela / passo) + 3):
        centro_x = indice * passo - deslocamento
        pygame.draw.circle(tela, escuro, _px(camera, centro_x, CHAO_Y + 40), round(COLINAS[1] * camera.escala))
        pygame.draw.circle(tela, claro, _px(camera, centro_x, CHAO_Y + 32), round((COLINAS[1] - 10) * camera.escala))
