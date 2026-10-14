"""Nivel: monta a fase a partir do mapa (um JSON com a lista de objetos).

Nao ha geometria escrita no codigo: `mundo/mapa.py` le o arquivo e daqui saem as
entidades — chao, plataformas, blocos, caixas, espinhos, molas, chave e porta.
O mapmaker (`Desktop/mapmaker`) grava exatamente esse formato, entao o que se
edita la e o que se joga aqui.
"""
from __future__ import annotations

import pygame

from src import sons
from src.entidades.jogador import Jogador
from src.entidades.particulas import Explosao
from src.entidades.obstaculos import Mola
from src.entidades.ponte import Plataforma
from src.mundo import mapa as mapa_mod
from src.mundo.camera import Camera
from src.mundo.cenario import Cenario
from src.mundo.portao import Porta
from src.ui.config import ALTURA, ALTURA_PERSONAGEM, LARGURA

_LIMITE_QUEDA = 80   # abaixo disso o corpo saiu do mundo (caiu por uma das bordas)
_NASCER = 80         # x do jogador quando o mapa nao diz outra coisa


class Nivel:
    """A fase jogavel: entidades montadas a partir de um mapa."""

    def __init__(self, largura: int = LARGURA, altura: int = ALTURA, mapa: dict | None = None):

        self.largura = largura
        self.altura = altura
        self.mapa = mapa if mapa is not None else mapa_mod.carregar()
        self.largura_mundo = int(self.mapa["largura_mundo"])
        self.chao_y = int(self.mapa["chao_y"])

        self.plataformas: list[Plataforma] = []
        self.obstaculos: list = []
        self.molas: list[Mola] = []
        self.itens: list = []
        self.inimigos: list = []
        self.explosoes: list[Explosao] = []
        self.porta = None
        self._montar()

        self.jogador = Jogador(*self._nascimento())
        self.camera = Camera(largura, altura, self.largura_mundo, altura)
        self.cenario = Cenario(largura, altura)

        self.solidos = (*tuple(o for o in self.obstaculos if o.solido), self.porta)
        self.perigosos = tuple(o for o in self.obstaculos if o.perigoso)
        self.pontos = 0
        self.moedas = 0
        self.pisados = 0
        self.coletados = {"moeda": 0, "chave": 0}
        self.tem_chave = False
        self.venceu = False

    # ----------------------------------------------------------- montagem
    def _nascimento(self) -> tuple[float, float]:
        """Onde o pug aparece: o mapa manda; sem isso, no comeco do chao."""
        nascer = self.mapa.get("nascer") or {}
        x = nascer.get("x", _NASCER)
        y = nascer.get("y", self.chao_y - ALTURA_PERSONAGEM)
        return float(x), float(y)

    def _montar(self) -> None:
        """Cria uma entidade para cada objeto do mapa, na lista certa."""
        for o in self.mapa["objetos"]:
            destino, entidade = mapa_mod.construir(o)
            if destino == "porta":
                self.porta = entidade
            elif destino is not None:
                getattr(self, destino).append(entidade)
        if self.porta is None:      # mapa sem porta: uma no fim do chao, para a fase fechar
            self.porta = Porta(self.largura_mundo - 84, self.chao_y - 104, 72, 104)

    # ------------------------------------------------------------- ciclo
    def atualizar(self, dt: float, keys) -> None:
        for plataforma in self.plataformas:
            plataforma.atualizar(dt)
        for obstaculo in self.obstaculos:
            obstaculo.mover(dt)
        for mola in self.molas:
            mola.mover(dt)

        # a mola precisa saber onde o corpo estava: o gatilho e o cruzamento
        anterior = self.jogador.hitbox.copy()
        self.jogador.controlar(keys)
        self.jogador.atualizar(dt, self.plataformas, self.solidos)
        for item in self.itens:
            if item.ativo:
                item.atualizar(dt)

        self._verificar_molas(anterior)
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

    def _verificar_molas(self, anterior: pygame.Rect) -> None:
        """Mola cruzada: lanca o corpo, toca o boing e devolve um pulo no ar."""
        jogador = self.jogador
        if jogador.explodido:
            return
        for mola in self.molas:
            if mola.lancar(jogador, anterior):
                if mola.direcao == "cima":
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
