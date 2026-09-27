"""HUD em uma linha so: coracoes, pontos, itens com quantidade e a chave.

Tudo numa barra horizontal unica, no canto superior esquerdo.
"""
from __future__ import annotations

import pygame

from src.ui import config
from src.ui.estilo import caixa_item, coracao, fonte, painel, texto
from src.ui.config import CORES

ESCALA_CORACAO = 3            # cada pixel do coracao com 3 px de tela
ESCALA_ICONE = 3              # mesma escala da caixa coletavel do cenario
LARGURA_CORACAO = 7 * ESCALA_CORACAO
ALTURA_BARRA = 44
MARGEM = 16          # folga esquerda e direita dentro da barra
FOLGA = 14          # folga entre os blocos
PERIODO_PISCADA_MS = 130
ITENS_HUD = [("moeda", (255, 214, 60))]


class Hud:
    """Barra unica com o status do jogador."""

    def __init__(self) -> None:
        self.fonte = fonte(20)
        self._vidas = 0
        self.pontos = 0
        self._coletados = {"moeda": 0, "chave": 0}
        self._chave = False
        self.invulneravel = False

    def atualizar(
        self,
        vidas: int,
        pontos: int,
        moedas: int = 0,
        pisados: int = 0,
        invulneravel: bool = False,
        tem_chave: bool = False,
    ) -> None:
        """Guarda os valores exibidos no proximo desenho."""
        self._vidas = vidas
        self.pontos = pontos
        self._coletados["moeda"] = moedas
        self._chave = tem_chave

    def atualizar_itens(self, coletados: dict, tem_chave: bool) -> None:
        """Recebe o registro de coleta da fase (itens e chave)."""
        self._coletados = dict(coletados)
        self._chave = tem_chave

    def piscando(self) -> bool:
        """True quando os coracoes devem piscar neste instante."""
        return self.invulneravel and (pygame.time.get_ticks() // PERIODO_PISCADA_MS) % 2 == 0

    # ------------------------------------------------------------ desenho
    def desenhar(self, tela) -> None:
        """Desenha a barra unica no canto superior esquerdo."""
        largura = self._largura()
        margem = 14
        barra = pygame.Rect(margem, margem, largura, ALTURA_BARRA)
        painel(tela, barra, CORES["painel"], borda="painel_borda", raio=12)

        centro_y = barra.centery
        x = self._coracoes(tela, barra)
        x = self._divisor(tela, x, barra)
        x = self._pontos(tela, x, centro_y)
        for indice, (chave, cor) in enumerate(ITENS_HUD):
            x = self._item(tela, x, centro_y, chave, cor)
        if self._chave:
            self._chave_icone(tela, barra.right - 20, centro_y)

    def _largura(self) -> int:
        """Largura da barra, somando exatamente o que cada parte desenha.

        As medidas precisam bater com `desenhar`: um item ocupa caixa + folga +
        numero + folga, e errar aqui pune o numero para fora do painel.
        """
        coracoes = config.VIDAS_MAX * (LARGURA_CORACAO + 6) - 6
        pontos = self.fonte.size(str(self.pontos))[0] + 18
        itens = sum(
            6 * ESCALA_ICONE + 5 + self.fonte.size(str(self._coletados.get(chave, 0)))[0] + 16
            for chave, _ in ITENS_HUD
        )
        return MARGEM * 2 + coracoes + FOLGA + pontos + itens + (30 if self._chave else 0)

    def _coracoes(self, tela, barra: pygame.Rect) -> int:
        mostrar = not self.piscando()
        x = barra.x + 16 + LARGURA_CORACAO // 2
        for indice in range(config.VIDAS_MAX):
            cheio = indice < self._vidas
            cor = CORES["coracao"] if cheio and mostrar else (
                CORES["coracao_escura"] if cheio else CORES["painel_borda"]
            )
            coracao(tela, (x, barra.centery), ESCALA_CORACAO, cor)
            x += LARGURA_CORACAO + 6
        return x + 6

    def _divisor(self, tela, x: int, barra: pygame.Rect) -> int:
        """Barra vertical separando as duas metades."""
        pygame.draw.rect(
            tela, CORES["painel_borda"],
            pygame.Rect(x, barra.y + 12, 2, barra.h - 24),
        )
        return x + 14

    def _pontos(self, tela, x: int, centro_y: int) -> int:
        texto(tela, self.fonte, str(self.pontos), "moeda", contorno=2,
              pos=(x, centro_y - self.fonte.get_height() // 2))
        return x + self.fonte.size(str(self.pontos))[0] + 18

    def _item(self, tela, x: int, centro_y: int, chave: str, cor) -> int:
        """Caixa do item com a quantidade ao lado."""
        tamanho = 6 * ESCALA_ICONE
        caixa_item(
            tela, pygame.Rect(x, centro_y - tamanho // 2, tamanho, tamanho), cor, contorno=2,
        )
        valor = str(self._coletados.get(chave, 0))
        texto(tela, self.fonte, valor, "texto", contorno=2,
              pos=(x + tamanho + 5, centro_y - self.fonte.get_height() // 2))
        return x + tamanho + 5 + self.fonte.size(valor)[0] + 14

    def _chave_icone(self, tela, x: int, centro_y: int) -> None:
        """A chave aparece no fim da barra so quando o jogador a tem."""
        pygame.draw.circle(tela, CORES["contorno"], (x, centro_y), 8)
        pygame.draw.circle(tela, CORES["moeda"], (x, centro_y), 5)
        pygame.draw.rect(tela, CORES["contorno"], pygame.Rect(x - 2, centro_y, 4, 10), border_radius=2)
        pygame.draw.rect(tela, CORES["moeda"], pygame.Rect(x - 1, centro_y, 2, 9), border_radius=1)
        pygame.draw.rect(tela, CORES["contorno"], pygame.Rect(x - 1, centro_y + 5, 6, 3))
