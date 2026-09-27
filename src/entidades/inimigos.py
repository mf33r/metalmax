"""Inimigos: quatro comportamentos distintos, todos do mesmo sprite do pug.

Hierarquia: `Entidade` -> `CorpoFisico` -> `Personagem` -> `Inimigo`
-> `Soldado`, `Guarda`, `Voador`, `Saltitante`.

O inimigo nasce da mesma arte do jogador, so que com a cor trocada: textura,
luz e pintura iguais, cor diferente.
"""
from __future__ import annotations

import math

import pygame

from src.entidades.jogador import Personagem
from src.mundo.fisica import mover_e_colidir
from src.ui.config import (
    ALCANCE_PISAO,
    ALTURA_PERSONAGEM,
    DANO_INIMIGO,
    GRAVIDADE,
    LARGURA_PERSONAGEM,
)


class Inimigo(Personagem):
    """Base dos inimigos: patrulham e machucam no contato."""

    tingimento = (255, 118, 96)
    colisao_ativa = True      # se False, atravessa plataforma (voador)

    def __init__(self, x: float, y: float, alcance: float = 180.0, velocidade: float = 90.0):
        super().__init__(x, y, tingimento=self.tingimento)
        self.velocidade_andar = velocidade
        self.limite_esquerdo = x - alcance / 2
        self.limite_direito = x + alcance / 2
        self.dano = DANO_INIMIGO
        self.morto = False

    def atualizar(self, dt: float, plataformas: list, solidos: tuple = ()) -> None:
        if self.morto:
            return
        self.andar_para(-1 if self.virado else 1)
        self.aplicar_gravidade(dt)     # inimigos tambem caem
        mover_e_colidir(self, dt, plataformas, solidos)
        self._desbloquear()
        self._girar_nos_limites()
        self.definir_acao(self.acao_desejada())
        self.animacao.avancar(dt)

    def _desbloquear(self) -> None:
        """Travou numa borda baixa? Pula por cima em vez de ficar tremendo."""
        if self.vel.x == 0 and self.no_chao:
            self.pular(460.0)

    def _girar_nos_limites(self) -> None:
        """Vira no fim da ronda. Travado ele nao vira: quem resolve e o pulo."""
        if self.vel.x == 0:
            return
        if self.vel.x > 0 and self.hitbox.right >= self.limite_direito:
            self.virado = True
        elif self.vel.x < 0 and self.hitbox.left <= self.limite_esquerdo:
            self.virado = False

    def sair_da_fase(self) -> None:
        """Some do jogo: pisado ou caido no buraco."""
        self.morto = True
        self.ativo = False
        self.vel.update(0, 0)


class Soldado(Inimigo):
    """Patrulha curta e lenta: o inimigo basico."""

    tingimento = (255, 118, 96)

    def __init__(self, x: float, y: float, alcance: float = 70.0):
        super().__init__(x, y, alcance, velocidade=85.0)


class Guarda(Inimigo):
    """Patrulha longa e rapida: mais perigoso que o soldado."""

    tingimento = (104, 158, 255)

    def __init__(self, x: float, y: float, alcance: float = 110.0):
        super().__init__(x, y, alcance, velocidade=140.0)


class Voador(Inimigo):
    """Flutua em onda e ignora o cenario: atrapalha quem sobe de degrau."""

    tingimento = (168, 226, 140)
    colisao_ativa = False
    amplitude = 26.0            # quanto sobe e desce
    periodo = 2.4              # segundos por ciclo

    def __init__(self, x: float, y: float, alcance: float = 120.0):
        super().__init__(x, y, alcance, velocidade=70.0)
        self.base_y = float(y)
        self.tempo = 0.0
        self.virado = True

    def atualizar(self, dt: float, plataformas: list, solidos: tuple = ()) -> None:
        if self.morto:
            return
        self.tempo += dt
        self.vel.x = -self.velocidade_andar if self.virado else self.velocidade_andar
        self.pos.x += self.vel.x * dt
        self.pos.y = self.base_y + math.sin(self.tempo * 2 * math.pi / self.periodo) * self.amplitude
        self.vel.y = 0.0
        self.virado = self.vel.x < 0

        if self.hitbox.right >= self.limite_direito:
            self.virado = True
        elif self.hitbox.left <= self.limite_esquerdo:
            self.virado = False
        self.hitbox.topleft = (round(self.pos.x), round(self.pos.y))
        self.definir_acao("Andar")
        self.animacao.avancar(dt)


class Saltitante(Inimigo):
    """Pula sem parar e cobre terreno: e o mais chato de desviar."""

    tingimento = (236, 168, 96)
    forca_pulo = 620.0
    periodo_pulo = 0.9

    def __init__(self, x: float, y: float, alcance: float = 90.0):
        super().__init__(x, y, alcance, velocidade=110.0)
        self.espera = 0.0

    def atualizar(self, dt: float, plataformas: list, solidos: tuple = ()) -> None:
        if self.morto:
            return
        self.espera = max(0.0, self.espera - dt)
        if self.espera <= 0 and self.no_chao:
            self.pular(self.forca_pulo)
            self.espera = self.periodo_pulo
        self.aplicar_gravidade(dt)
        mover_e_colidir(self, dt, plataformas, solidos)
        self._desbloquear()      # na espera do proximo pulo ele nao pode ficar preso
        self._girar_nos_limites()
        self.definir_acao("Andar" if self.vel.x else "Parado")
        self.animacao.avancar(dt)
