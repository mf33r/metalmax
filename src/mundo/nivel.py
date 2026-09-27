"""Nivel: um mapa de teste bem simples — chao, algumas plataformas e caixas.

Sem inimigo, sem espinho e sem plataforma movel: e um tabuleiro para validar
movimento, pulo, colisao, itens, HUD e o fim de fase (chave + porta).
"""
from __future__ import annotations

import pygame

from src.entidades.itens import Chave, Moeda
from src.entidades.jogador import Jogador
from src.mundo.camera import Camera
from src.mundo.cenario import Cenario
from src.entidades.obstaculos import CaixaSolida
from src.entidades.ponte import Plataforma
from src.mundo.portao import Porta
from src.ui.config import (
    ALTURA_CHAO,
    ALTURA,
    ALTURA_CAIXA,
    ALTURA_PERSONAGEM,
    ALTURA_PLATAFORMA,
    CHAO_Y,
    LARGURA,
    LARGURA_MUNDO,
)

# Trechos de chao, separados por buracos.
_TRECHOS = [(0, 1300), (1500, 1300), (3000, 1200)]
LARGURA_BURACO = 200

# Plataformas: (x, altura acima do chao, largura)
_PLATAFORMAS = [
    (260, 70, 170),
    (600, 130, 150),
    (900, 70, 170),
    (1620, 90, 170),
    (2000, 150, 150),
    (2380, 80, 170),
    (3120, 100, 170),
    (3460, 160, 150),
    (3800, 100, 170),
]

# Caixas no chao: (x)
_CAIXAS = [520, 1150, 1780, 2560, 3260, 3980]

# Itens: (x, altura acima do chao) do centro
_MOEDAS = [(340, 130), (1000, 130), (1700, 150), (3200, 160), (3880, 160)]
_CHAVE = [(3530, 240)]

_LIMITE_QUEDA = 80
PORTA_L = 72
PORTA_A = 104
PEDESTAL = 56       # a porta fica numa plinto, para nao se perder no cenario


class Nivel:
    """Mapa de teste: pouco chaco, poucas plataformas, caixa, itens e a saida."""

    def __init__(self, largura: int = LARGURA, altura: int = ALTURA, largura_mundo: int = LARGURA_MUNDO):

        self.largura = largura
        self.altura = altura
        self.largura_mundo = largura_mundo
        # a porta precisa caber DENTRO do chao: se passar da borda, o jogador
        # e expulso para o buraco quando bate nela
        self.fim = _TRECHOS[-1][0] + _TRECHOS[-1][1] - PORTA_L - 12

        self.jogador = Jogador(80, CHAO_Y - ALTURA_PERSONAGEM)
        self.camera = Camera(largura, altura, largura_mundo, altura)
        self.cenario = Cenario(largura, altura)

        self.plataformas: list[Plataforma] = []
        self.obstaculos: list = []
        self.itens: list = []
        self.inimigos: list = []
        self._montar(ALTURA_CHAO)

        self.solidos = (*tuple(o for o in self.obstaculos if o.solido), self.porta)
        self.perigosos = ()
        self.pontos = 0
        self.moedas = 0
        self.pisados = 0
        self.coletados = {"moeda": 0, "chave": 0}
        self.tem_chave = False
        self.venceu = False

    # ----------------------------------------------------------- montagem
    def _montar(self, altura_chao: int) -> None:
        for x, comprimento in _TRECHOS:
            self.plataformas.append(Plataforma(x, CHAO_Y, comprimento, altura_chao, chao=True))
        for x, altura, comprimento in _PLATAFORMAS:
            self.plataformas.append(Plataforma(x, CHAO_Y - altura, comprimento, ALTURA_PLATAFORMA))
        for x in _CAIXAS:
            self.obstaculos.append(CaixaSolida(x, CHAO_Y - ALTURA_CAIXA, ALTURA_CAIXA, ALTURA_CAIXA))

        # a porta fica EM CIMA do chao: no plinto ela ficava acima da cabeca
        # do jogador, nao bloqueava e ele caia pela borda
        self.plataformas.append(
            Plataforma(self.fim - PORTA_L - 60, CHAO_Y - PEDESTAL, 100, ALTURA_PLATAFORMA)
        )
        self.porta = Porta(self.fim, CHAO_Y - PORTA_A, PORTA_L, PORTA_A)

        for x, altura in _MOEDAS:
            self.itens.append(Moeda(x - 13, CHAO_Y - altura - 13))
        for x, altura in _CHAVE:
            self.itens.append(Chave(x - 11, CHAO_Y - altura - 13))

    # ------------------------------------------------------------- ciclo
    def atualizar(self, dt: float, keys) -> None:
        for plataforma in self.plataformas:
            plataforma.atualizar(dt)
        for obstaculo in self.obstaculos:
            obstaculo.mover(dt)

        self.jogador.controlar(keys)
        self.jogador.atualizar(dt, self.plataformas, self.solidos)
        for item in self.itens:
            if item.ativo:
                item.atualizar(dt)

        self._coletar()
        self.camera.seguir(self.jogador.pos, dt)

        if self.jogador.hitbox.top > self.altura + _LIMITE_QUEDA:
            self.jogador.vidas = 0
            self.jogador.invulneravel = 0.0
        self.porta.mover(dt)
        if not self.porta.aberta and self.tem_chave and self.jogador.hitbox.right >= self.porta.corpo.left - 8:
            self.porta.abrir()
        if self.porta.aberta and self.jogador.hitbox.colliderect(self.porta.corpo):
            self.venceu = True

    def _coletar(self) -> None:
        jogador = self.jogador
        for item in self.itens:
            if not item.ativo or not jogador.hitbox.colliderect(item.hitbox):
                continue
            item.coletar()
            if getattr(item, "chave", False):
                self.tem_chave = True
                self.coletados["chave"] += 1
            else:
                self.moedas += 1
                self.pontos += item.valor
                self.coletados["moeda"] += 1

    # ----------------------------------------------------------- desenho
    def desenhar(self, tela: pygame.Surface) -> None:
        self.cenario.desenhar(tela, self.camera)
        for plataforma in self.plataformas:
            if self.camera.visivel(plataforma.corpo):
                plataforma.desenhar(tela, self.camera)
        for obstaculo in self.obstaculos:
            if self.camera.visivel(obstaculo.corpo):
                obstaculo.desenhar(tela, self.camera)
        for item in self.itens:
            if item.ativo and self.camera.visivel(item.hitbox):
                item.desenhar(tela, self.camera)
        if self.camera.visivel(self.porta.corpo):
            self.porta.desenhar(tela, self.camera)
        self.jogador.desenhar(tela, self.camera)

    @property
    def morto(self) -> bool:
        return self.jogador.vidas <= 0
