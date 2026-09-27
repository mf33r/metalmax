"""Coletaveis tirados do proprio sprite sheet: moeda, coracao e gema.

`Coletavel` concentra o que todo item tem (flutuar, sumir ao ser pego, valor)
e as subclasses so dizem qual celula do sheet desenhar e que efeito tem.
"""
from __future__ import annotations

import math

import pygame

from src.entidades.entidade import Entidade
from src.ui.estilo import caixa_item
from src.ui.config import (
    CORES,
    ALTURA_COLETAVEL,
    CELULA_CORACAO,
    CELULA_PEDRA,
    CELULA_MOEDA,
    PEDRA_VALOR,
    MOEDA_VALOR,
)

_FLUTUACAO = 5.0
_VELOCIDADE_FLUTUACAO = 3.0


class Coletavel(Entidade):
    """Item que fica parado no ar, flutuando, ate ser coletado."""

    cor_tarja = (168, 122, 78)   # madeira; cada subclasse define a sua

    def __init__(self, x: float, y: float, largura: int, altura: int, valor: int):
        super().__init__(x, y, largura, altura)
        self.valor = valor
        self.coletado = False
        self.fase = (x * 0.017) % (2 * math.pi)
        self.base_y = float(y)

    def atualizar(self, dt: float) -> None:
        self.fase += _VELOCIDADE_FLUTUACAO * dt
        self.pos.y = self.base_y + math.sin(self.fase) * _FLUTUACAO
        self.sincronizar_hitbox()

    def coletar(self) -> None:
        self.coletado = True
        self.ativo = False

    def desenhar(self, tela: pygame.Surface, camera) -> None:
        """No cenario todo item e uma caixa com tarja colorida.

        Os icones recortados do sheet ficavam pequenos e pareciam machados; a
        caixa e a mesma peca de obstaculo do jogo, entao a leitura e imediata.
        """
        if getattr(self, "chave", False):
            self._desenhar_chave(tela, camera)
            return
        x, y = camera.ponto_na_tela(self.pos)
        escala = max(0.34, camera.escala)
        largura = max(3, round(self.largura * escala))
        altura = max(3, round(self.altura * escala))
        caixa_item(
            tela,
            pygame.Rect(x, y + self.altura * camera.escala - altura, largura, altura),
            self.cor_tarja,
            contorno=1,
        )


    def _desenhar_chave(self, tela, camera) -> None:
        """Chave vertical: argola em cima, haste para baixo e dentes a direita.

        Antes era circulo com haste na diagonal, que se lia como machado.
        """
        escala = max(0.6, camera.escala * 3)
        x, y = camera.ponto_na_tela(self.pos)
        centro = (x + 8, y + 7)
        pygame.draw.circle(tela, CORES["contorno"], centro, max(3, round(5 * escala)))
        pygame.draw.circle(tela, CORES["moeda"], centro, max(2, round(3 * escala)))
        largura = max(2, round(3 * escala))
        haste = pygame.Rect(centro[0] - largura // 2, centro[1], largura, max(6, round(9 * escala)))
        pygame.draw.rect(tela, CORES["contorno"], haste.inflate(2, 2), border_radius=2)
        pygame.draw.rect(tela, CORES["moeda"], haste, border_radius=1)
        for deslocamento in (3, 6):
            pygame.draw.rect(
                tela, CORES["contorno"],
                pygame.Rect(haste.right, haste.y + round(deslocamento * escala), round(4 * escala), largura + 2),
            )


class Moeda(Coletavel):
    """Caixa com tarja dourada: soma pontos."""

    cor_tarja = (232, 190, 74)
    celula = CELULA_MOEDA

    def __init__(self, x: float, y: float):
        super().__init__(x, y, 26, ALTURA_COLETAVEL, MOEDA_VALOR)


class Coracao(Coletavel):
    """Caixa com tarja vermelha: recupera uma vida em vez de dar pontos."""

    cor_tarja = (214, 68, 72)
    celula = CELULA_CORACAO

    def __init__(self, x: float, y: float):
        super().__init__(x, y, 26, ALTURA_COLETAVEL, 0)


class Chave(Coletavel):
    """Chave da porta de saida: o que transforma o mapa em fase com objetivo."""

    cor_tarja = (255, 214, 92)
    celula = CELULA_PEDRA

    def __init__(self, x: float, y: float):
        super().__init__(x, y, 22, ALTURA_COLETAVEL, 0)
        self.chave = True


class Pedra(Coletavel):
    """Caixa com tarja escura: item raro, vale muito mais que a moeda."""

    cor_tarja = (120, 96, 74)
    celula = CELULA_PEDRA

    def __init__(self, x: float, y: float):
        super().__init__(x, y, 26, ALTURA_COLETAVEL, PEDRA_VALOR)
