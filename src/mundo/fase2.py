"""Fase 2: travessia espacial com lava, dois cogumelos de poder e o boss no fim.

Herda de `Nivel` para reusar fisica, colisao, camera e montagem do mapa. Os
elementos novos (lava, cogumelos, tiro do pug, boss e a trava da arena) sao
proprios daqui e nao tocam no restante do jogo. O mapa e `assets/mapas/fase2.json`:
os objetos padrao (chao, plataforma, espinho) passam pelo `Nivel`; os extras
(lava, cogumelos, boss) sao lidos a parte.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import pygame

from src import sons
from src.entidades.boss import Boss
from src.entidades.cogumelo import Cogumelo
from src.entidades.lava import Lava
from src.entidades.particulas import Explosao
from src.entidades.projetil import Projetil
from src.mundo.cenario_espaco import CenarioEspaco
from src.mundo.nivel import Nivel
from src.ui.config import ALTURA, LARGURA, RAIZ
from src.ui import hud_boss

_LIMITE_QUEDA = 80
BRILHO_SEG = 15.0            # invencibilidade do cogumelo marrom
AVISO_SEG = 6.0             # tempo que a mensagem de poder fica na tela
RECARGA_TIRO = 0.3
CORES_BRILHO = [(255, 70, 70), (255, 180, 50), (120, 240, 120), (90, 200, 255), (200, 110, 255)]


def _carregar_bruto() -> dict:
    caminho = RAIZ / "assets" / "mapas" / "fase2.json"
    return json.loads(caminho.read_text(encoding="utf-8"))


class Fase2(Nivel):
    """A fase do pug: percorre o espaco e enfrenta o boss."""

    def __init__(self):
        bruto = _carregar_bruto()
        extra = bruto.get("extra", {})
        mapa = {
            "versao": bruto.get("versao", 1),
            "nome": bruto.get("nome", "fase2"),
            "largura_mundo": bruto["largura_mundo"],
            "chao_y": bruto["chao_y"],
            "nascer": bruto.get("nascer"),
            "objetos": bruto["objetos"],
        }
        super().__init__(LARGURA, ALTURA, mapa=mapa)

        # fundo espacial no lugar do campo
        self.cenario = CenarioEspaco(LARGURA, ALTURA)

        # extras da fase
        self.lava = [Lava(o["x"], o["y"], o["w"], o["h"]) for o in extra.get("lava", [])]
        self.cogumelos = [Cogumelo(c["x"], c["y"], c["tipo"]) for c in extra.get("cogumelos", [])]
        dados_boss = extra.get("boss", {"x": 4600, "y": 300, "vida": 8})
        self.boss = Boss(dados_boss["x"], dados_boss["y"], dados_boss.get("vida", 8))
        self.trava_x = extra.get("trava_x", 3650)
        self.arena_esq = extra.get("arena_esq", 3560)
        self.arena_offset = max(0, self.arena_esq - 300)

        # sem porta/chave nesta fase: quem fecha a fase e o boss
        self.solidos = tuple(o for o in self.obstaculos if o.solido)
        self.perigos = list(self.perigosos) + self.lava

        # estado dos poderes
        self.brilho = 0.0           # tempo restante de invencibilidade
        self.pode_atirar = False
        self.aviso = 0.0            # tempo restante da mensagem "poder adquirido"
        self.aviso_texto = ""
        self.recarga = 0.0
        self.projeteis: list[Projetil] = []
        self.travado = False
        self._f_anterior = False

    # --------------------------------------------------------------- ciclo
    @property
    def invencivel(self) -> bool:
        return self.brilho > 0

    def atualizar(self, dt: float, keys) -> None:
        self.cenario.atualizar(dt, self.camera)
        for lava in self.lava:
            lava.atualizar(dt)
        for cogumelo in self.cogumelos:
            cogumelo.atualizar(dt)

        anterior = self.jogador.hitbox.copy()
        self.jogador.controlar(keys)
        self.jogador.atualizar(dt, self.plataformas, self.solidos)

        self._cogumelos()
        self._perigos()
        self._tiro(dt, keys)
        self._boss(dt)
        self._trava()

        self.brilho = max(0.0, self.brilho - dt)
        self.aviso = max(0.0, self.aviso - dt)
        self.explosoes = [e for e in self.explosoes if e.atualizar(dt)]

        if self.jogador.hitbox.top > self.altura + _LIMITE_QUEDA and not self.invencivel:
            self.jogador.vidas = 0   # invencivel nao morre de queda: pousa no fundo da poca

        self.camera.seguir(self.jogador.pos, dt)
        if self.travado:
            self.camera.offset.x = max(self.camera.offset.x, self.arena_offset)

        if self.boss.morto and not self.venceu:
            self.explosoes.append(Explosao(*self.boss.hitbox.center, raio=self.boss.hitbox.w / 2))
            sons.explosao()
            self.venceu = True

    def _cogumelos(self) -> None:
        for cogumelo in self.cogumelos:
            if not cogumelo.ativo or not self.jogador.hitbox.colliderect(cogumelo.hitbox):
                continue
            cogumelo.coletar()
            if cogumelo.tipo == "brilho":
                self.brilho = BRILHO_SEG
                self.aviso_texto = "INVENCIVEL! ATRAVESSE A LAVA"
            else:
                self.pode_atirar = True
                self.aviso_texto = "PODER ADQUIRIDO - F PARA ATIRAR"
            self.aviso = AVISO_SEG

    def _perigos(self) -> None:
        """Espinho e lava explodem o pug — a nao ser que esteja invencivel."""
        if self.jogador.explodido or self.invencivel:
            return
        for perigo in self.perigos:
            if self.jogador.hitbox.colliderect(perigo.corpo):
                if self.jogador.explodir():
                    sons.explosao()
                    self.explosoes.append(
                        Explosao(*self.jogador.hitbox.center, raio=self.jogador.hitbox.w / 2)
                    )
                return

    def _tiro(self, dt: float, keys) -> None:
        self.recarga = max(0.0, self.recarga - dt)
        for projetil in self.projeteis:
            projetil.atualizar(dt)
        # acerto no boss
        for projetil in self.projeteis:
            if projetil.ativo and self.boss.ativo and projetil.hitbox.colliderect(self.boss.hitbox):
                if self.boss.levar_dano(1):
                    projetil.ativo = False
        # some ao sair do mundo
        self.projeteis = [
            p for p in self.projeteis if p.ativo and -50 < p.hitbox.x < self.largura_mundo + 50
        ]
        if self.pode_atirar and keys[pygame.K_f] and self.recarga <= 0 and not self.jogador.explodido:
            self.recarga = RECARGA_TIRO
            direcao = -1 if self.jogador.virado else 1
            x = self.jogador.hitbox.right if direcao > 0 else self.jogador.hitbox.left - 18
            self.projeteis.append(Projetil(x, self.jogador.hitbox.centery - 5, direcao))

    def _boss(self, dt: float) -> None:
        self.boss.atualizar(dt, self.jogador.hitbox)
        if self.jogador.explodido or self.invencivel:
            return
        for laser in self.boss.lasers:
            if laser.ativo and self.jogador.hitbox.colliderect(laser.hitbox):
                if self.jogador.levar_dano(1):
                    laser.ativo = False

    def _trava(self) -> None:
        """Ao entrar na arena, acorda o boss e impede voltar atras."""
        if not self.travado and self.jogador.hitbox.centerx >= self.trava_x:
            self.travado = True
            self.boss.acordar()
        if self.travado and self.jogador.hitbox.left < self.arena_esq:
            self.jogador.hitbox.left = self.arena_esq
            self.jogador.pos.x = self.jogador.hitbox.x

    # --------------------------------------------------------------- desenho
    def desenhar(self, tela: pygame.Surface) -> None:
        self.cenario.desenhar(tela, self.camera)
        for plataforma in self.plataformas:
            if self.camera.visivel(plataforma.corpo):
                plataforma.desenhar(tela, self.camera)
        for lava in self.lava:          # depois do piso: cobre o fundo da bacia
            if self.camera.visivel(lava.corpo):
                lava.desenhar(tela, self.camera)
        for obstaculo in self.obstaculos:
            if self.camera.visivel(obstaculo.corpo):
                obstaculo.desenhar(tela, self.camera)
        for cogumelo in self.cogumelos:
            if cogumelo.ativo and self.camera.visivel(cogumelo.hitbox):
                cogumelo.desenhar(tela, self.camera)
        for projetil in self.projeteis:
            projetil.desenhar(tela, self.camera)
        if self.camera.visivel(self.boss.hitbox) or self.boss.lasers:
            self.boss.desenhar(tela, self.camera)
        if self.invencivel:
            self._aura(tela)
        self.jogador.desenhar(tela, self.camera)
        if self.invencivel:
            self._pug_colorido(tela)
        for explosao in self.explosoes:
            explosao.desenhar(tela, self.camera)

    def _aura(self, tela: pygame.Surface) -> None:
        """Brilho em cores atras do pug enquanto invencivel."""
        cor = CORES_BRILHO[int(self.brilho * 6) % len(CORES_BRILHO)]
        centro = self.camera.ponto_na_tela(self.jogador.hitbox.center)
        raio = max(3, round(self.jogador.hitbox.w * 1.0 * self.camera.escala))
        aura = pygame.Surface((raio * 2, raio * 2), pygame.SRCALPHA)
        pygame.draw.circle(aura, (*cor, 120), (raio, raio), raio)
        pygame.draw.circle(aura, (*cor, 80), (raio, raio), raio, max(1, raio // 3))
        tela.blit(aura, (centro[0] - raio, centro[1] - raio))

    def _pug_colorido(self, tela: pygame.Surface) -> None:
        """Pinta o proprio sprite do pug com a cor do arco-iris (aditivo)."""
        jogador = self.jogador
        if jogador.explodido:
            return
        sprite = jogador.animacao.frame
        if jogador.virado:
            sprite = pygame.transform.flip(sprite, True, False)
        sprite = self.camera.escalar(sprite)
        alvo = self.camera.retangulo_na_tela(jogador.hitbox)
        x = alvo.centerx - sprite.get_width() // 2
        y = alvo.bottom - sprite.get_height() - round(jogador.animacao.deslocamento_y * self.camera.escala)
        cor = CORES_BRILHO[int(self.brilho * 8) % len(CORES_BRILHO)]
        tint = sprite.copy()
        tint.fill((*cor, 0), special_flags=pygame.BLEND_RGB_ADD)
        tela.blit(tint, (x, y))

    def desenhar_hud(self, ui: pygame.Surface) -> None:
        """Chamado pelo Jogo na camada de interface (resolucao cheia)."""
        if self.boss.ativo or self.boss.morto:
            hud_boss.barra_boss(ui, "BIG ROBO", self.boss.vida, self.boss.vida_max)
        if self.brilho > 0:
            hud_boss.selo_invencivel(ui, self.brilho)
        if self.aviso > 0 and self.aviso_texto:
            hud_boss.aviso_poder(ui, self.aviso_texto, self.aviso)
