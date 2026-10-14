"""Nivel: mapa reto — um chao unico, espinhos e molas no caminho e a saida.

O chao nao tem buraco, plataforma nem caixa: os desafios sao a fileira de
espinhos, que explode o corpo de quem encosta, e as molas, que jogam o pug para
o alto. Sem inimigo e sem plataforma movel: e um tabuleiro para validar
movimento, pulo, mola, espinhos e o fim de fase (chave + porta).
"""
from __future__ import annotations

import pygame

from src import sons
from src.entidades.itens import Chave
from src.entidades.jogador import Jogador
from src.entidades.particulas import Explosao
from src.mundo.camera import Camera
from src.mundo.cenario import Cenario
from src.entidades.obstaculos import BlocoGrama, Espinhos, Mola
from src.entidades.ponte import Plataforma
from src.mundo.portao import Porta
from src.ui.config import (
    ALTURA,
    ALTURA_CHAO,
    ALTURA_ESPINHO,
    ALTURA_MOLA,
    ALTURA_PERSONAGEM,
    CHAO_Y,
    LARGURA,
    LARGURA_MUNDO,
)

# Chao reto: um trecho so, sem buracos e sem plataforma.
_TRECHOS = [(0, LARGURA_MUNDO)]

# Espinhos no chao: (x, largura). 56 px e o teto confortavel: o pulo simples
# fica 130 px no ar (0,5 s a 260 px/s) e precisa cobrir a serra mais o corpo
# (56 + 30), sobrando ~10 quadros de folga para o dedo. Nenhuma fileira fica
# embaixo do "C": a serra pendurada la em cima comeria a cabeca de quem pula.
_ESPINHOS = [(430, 56), (900, 56), (1620, 56), (2250, 56), (2880, 56), (3400, 56)]

# Molas no chao: (x). 1150 e 2530 sao lancadoras: ficam 90 px antes de um pilar
# de 130 px, que e alto demais para subir de pulo — o jeito e cair na mola. A
# distancia e essa porque o voo da mola so passa dos 146 px (o topo da serra)
# depois de 40 px: mais perto que isso, o pug bate na serra subindo.
_MOLAS = [700, 1150, 1420, 1880, 2530]

# Blocos solidos de grama: (x, altura da base acima do chao, largura, espessura).
_BLOCOS = [
    (1240, 0, 60, 130),        # pilar 1: alto, topo todo coberto de serra
    (2620, 0, 60, 130),        # pilar 2: idem
    (3000, 0, 260, 45),        # plataforma baixa, com serra no meio do topo
    # o "C" suspenso, de boca para a esquerda: o pug entra voando pela mola de
    # 1880 e pousa na barra de baixo. Os vaos internos tem 55 px, o suficiente
    # para o pug (34 px) andar dentro sem encostar na barra de cima.
    (2000, 155, 230, 45),      # barra de baixo
    (2175, 155, 55, 255),      # perna direita, do chao da barra ao topo
    (2000, 365, 230, 45),      # barra de cima
    (2080, 255, 95, 45),       # barra do meio: a prateleira de dentro
]

# Serra presa em cima de um bloco: (x, altura da base acima do chao, largura)
_ESPINHOS_ALTOS = [
    (1240, 130, 60),           # topo do pilar 1
    (2620, 130, 60),           # topo do pilar 2
    (3140, 45, 50),            # topo da plataforma baixa: 140 px de pouso a esquerda
    (2000, 410, 230),          # topo da barra de cima do "C"
]

# Serra pendurada, apontando para o chao: (x, altura da base, largura)
_ESPINHOS_BAIXOS = [(2000, 139, 230)]      # embaixo da barra de baixo do "C"

# A chave: (x, altura acima do chao) do centro. Fica no meio do trecho reto.
_CHAVE = [(3560, 110)]

PORTA_L = 72
PORTA_A = 104
_LIMITE_QUEDA = 80   # abaixo disso o corpo saiu do mundo (caiu por uma das bordas)


class Nivel:
    """Mapa reto: chao unico com espinhos, molas e a saida."""

    def __init__(self, largura: int = LARGURA, altura: int = ALTURA, largura_mundo: int = LARGURA_MUNDO):

        self.largura = largura
        self.altura = altura
        self.largura_mundo = largura_mundo
        # a porta precisa caber DENTRO do chao: se passar da borda, o jogador
        # e expulso para fora dele quando bate nela
        self.fim = _TRECHOS[-1][0] + _TRECHOS[-1][1] - PORTA_L - 12

        self.jogador = Jogador(80, CHAO_Y - ALTURA_PERSONAGEM)
        self.camera = Camera(largura, altura, largura_mundo, altura)
        self.cenario = Cenario(largura, altura)

        self.plataformas: list[Plataforma] = []
        self.obstaculos: list = []
        self.molas: list[Mola] = []
        self.itens: list = []
        self.inimigos: list = []
        self.explosoes: list[Explosao] = []
        self._montar(ALTURA_CHAO)

        self.solidos = (*tuple(o for o in self.obstaculos if o.solido), self.porta)
        self.perigosos = tuple(o for o in self.obstaculos if o.perigoso)
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
        for x, largura in _ESPINHOS:
            self.obstaculos.append(Espinhos(x, CHAO_Y - ALTURA_ESPINHO, largura))
        for x, altura, largura, espessura in _BLOCOS:
            self.obstaculos.append(BlocoGrama(x, CHAO_Y - altura - espessura, largura, espessura))
        for x, altura, largura in _ESPINHOS_ALTOS:
            self.obstaculos.append(Espinhos(x, CHAO_Y - altura - ALTURA_ESPINHO, largura))
        for x, altura, largura in _ESPINHOS_BAIXOS:
            self.obstaculos.append(Espinhos(x, CHAO_Y - altura - ALTURA_ESPINHO, largura, para_baixo=True))
        for x in _MOLAS:
            self.molas.append(Mola(x, CHAO_Y - ALTURA_MOLA))

        # a porta fica EM CIMA do chao reto: no plinto ela ficava acima da
        # cabeca do jogador e ele passava por baixo sem esbarrar
        self.porta = Porta(self.fim, CHAO_Y - PORTA_A, PORTA_L, PORTA_A)

        for x, altura in _CHAVE:
            self.itens.append(Chave(x - 11, CHAO_Y - altura - 13))

    # ------------------------------------------------------------- ciclo
    def atualizar(self, dt: float, keys) -> None:
        for plataforma in self.plataformas:
            plataforma.atualizar(dt)
        for obstaculo in self.obstaculos:
            obstaculo.mover(dt)
        for mola in self.molas:
            mola.mover(dt)

        base_anterior = self.jogador.hitbox.bottom   # a mola precisa do topo cruzado
        self.jogador.controlar(keys)
        self.jogador.atualizar(dt, self.plataformas, self.solidos)
        for item in self.itens:
            if item.ativo:
                item.atualizar(dt)

        self._verificar_molas(base_anterior)
        self._verificar_espinhos()
        self.explosoes = [explosao for explosao in self.explosoes if explosao.atualizar(dt)]
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

    def _verificar_molas(self, base_anterior: int) -> None:
        """Mola pisada: lanca o corpo, toca o boing e devolve um pulo no ar."""
        jogador = self.jogador
        if jogador.explodido:
            return
        for mola in self.molas:
            if mola.lancar(jogador, base_anterior):
                jogador.saltos_usados = min(jogador.saltos_usados, 1)   # sobra um pulo
                sons.mola()
                return

    def _verificar_espinhos(self) -> None:
        """Encostar num espinho explode o corpo e deixa terra no lugar dele."""
        jogador = self.jogador
        if jogador.explodido:
            return
        for espinho in self.perigosos:
            if jogador.hitbox.colliderect(espinho.corpo):
                if jogador.explodir():
                    sons.explosao()
                    self.explosoes.append(Explosao(*jogador.hitbox.center, raio=jogador.hitbox.w / 2))
                return

    def _coletar(self) -> None:
        jogador = self.jogador
        if jogador.explodido:
            return      # o corpo virou terra: nao ha mais quem colete
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
        for mola in self.molas:
            if self.camera.visivel(mola.corpo):
                mola.desenhar(tela, self.camera)
        for item in self.itens:
            if item.ativo and self.camera.visivel(item.hitbox):
                item.desenhar(tela, self.camera)
        if self.camera.visivel(self.porta.corpo):
            self.porta.desenhar(tela, self.camera)
        self.jogador.desenhar(tela, self.camera)
        for explosao in self.explosoes:
            explosao.desenhar(tela, self.camera)

    @property
    def morto(self) -> bool:
        # a explosao segura o fim de jogo: a terra precisa voar antes da tela
        return self.jogador.vidas <= 0 and not self.explosoes
