"""Cenario espacial da fase 2: fundo que muda conforme anda.

Camadas, de longe para perto: gradiente do espaco, nebulosas suaves, tres
camadas de estrelas com parallax, estrelas cadentes riscando o ceu e planetas
que surgem e explodem ao fundo. Tudo ancorado no mundo e convertido pela camera,
igual ao `Cenario` do campo — funciona no buffer pixelado e na tela cheia.
"""
from __future__ import annotations

import math
import random

import pygame

CEU_TOPO = (8, 6, 24)
CEU_BASE = (26, 14, 48)
NEBULOSAS = [
    (0.08, 300, 180, 150, (60, 30, 90)),
    (0.10, 1600, 420, 190, (30, 50, 100)),
    (0.08, 3200, 240, 170, (90, 34, 70)),
    (0.10, 4600, 460, 200, (28, 60, 86)),
]
CORES_PLANETA = [(214, 120, 80), (120, 170, 230), (150, 220, 160), (210, 180, 110), (180, 130, 220)]


class CenarioEspaco:
    """Fundo espacial animado em camadas com parallax."""

    def __init__(self, largura: int = 1400, altura: int = 700):
        self.largura = largura
        self.altura = altura
        rnd = random.Random(7)
        self.rnd = rnd
        self.camadas = []
        for fator, qtd, rmax in ((0.12, 90, 2), (0.26, 70, 2), (0.5, 55, 3)):
            estrelas = [
                (rnd.uniform(0, 6000), rnd.uniform(0, altura), rnd.randint(1, rmax), rnd.uniform(0, 6.28))
                for _ in range(qtd)
            ]
            self.camadas.append((fator, estrelas))
        self.t = 0.0
        self.cadentes: list[list] = []    # [x_mundo, y_mundo, vx, vy, idade, vida]
        self.planetas: list[list] = []    # [x_mundo, y_mundo, raio, cor, idade, vida]
        self._prox_cadente = 0.4
        self._prox_planeta = 1.5

    # ------------------------------------------------------------ animacao
    def atualizar(self, dt: float, camera) -> None:
        self.t += dt
        self._cadentes_spawn(dt, camera)
        self._planetas_spawn(dt, camera)

    def _cadentes_spawn(self, dt: float, camera) -> None:
        self._prox_cadente -= dt
        if self._prox_cadente <= 0:
            self._prox_cadente = self.rnd.uniform(0.5, 1.6)
            x = camera.offset.x + self.rnd.uniform(-100, self.largura)
            y = self.rnd.uniform(0, self.altura * 0.45)
            vel = self.rnd.uniform(520, 760)
            ang = self.rnd.uniform(0.5, 0.9)      # desce para a direita
            vida = self.rnd.uniform(0.6, 1.0)
            self.cadentes.append([x, y, math.cos(ang) * vel, math.sin(ang) * vel, 0.0, vida])
        for c in self.cadentes:
            c[0] += c[2] * dt
            c[1] += c[3] * dt
            c[4] += dt
        self.cadentes = [c for c in self.cadentes if c[4] < c[5]]

    def _planetas_spawn(self, dt: float, camera) -> None:
        self._prox_planeta -= dt
        if self._prox_planeta <= 0:
            self._prox_planeta = self.rnd.uniform(2.2, 4.0)
            x = camera.offset.x + self.rnd.uniform(0, self.largura)
            y = self.rnd.uniform(self.altura * 0.18, self.altura * 0.6)
            raio = self.rnd.uniform(20, 40)
            self.planetas.append([x, y, raio, self.rnd.choice(CORES_PLANETA), 0.0, 2.6])
        for p in self.planetas:
            p[4] += dt
        self.planetas = [p for p in self.planetas if p[4] < p[5]]

    # ------------------------------------------------------------- desenho
    def desenhar(self, tela: pygame.Surface, camera) -> None:
        self._ceu(tela)
        self._nebulosas(tela, camera)
        self._planetas(tela, camera)
        self._estrelas(tela, camera)
        self._cadentes(tela, camera)

    def _tela(self, camera, wx: float, wy: float, fator: float) -> tuple[int, int]:
        return (
            round((wx - camera.offset.x * fator) * camera.escala),
            round((wy - camera.offset.y * fator) * camera.escala),
        )

    def _ceu(self, tela: pygame.Surface) -> None:
        altura = tela.get_height()
        for linha in range(altura):
            t = linha / max(1, altura - 1)
            cor = tuple(round(CEU_TOPO[i] + (CEU_BASE[i] - CEU_TOPO[i]) * t) for i in range(3))
            pygame.draw.line(tela, cor, (0, linha), (tela.get_width(), linha))

    def _nebulosas(self, tela: pygame.Surface, camera) -> None:
        w = tela.get_width()
        for fator, wx, wy, raio, cor in NEBULOSAS:
            cx, cy = self._tela(camera, wx, wy, fator)
            r = max(4, round(raio * camera.escala))
            if cx + r < 0 or cx - r > w:
                continue
            nuvem = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            for passo, alpha in ((1.0, 40), (0.7, 50), (0.4, 60)):
                pygame.draw.circle(nuvem, (*cor, alpha), (r, r), max(1, int(r * passo)))
            tela.blit(nuvem, (cx - r, cy - r))

    def _estrelas(self, tela: pygame.Surface, camera) -> None:
        w, h = tela.get_width(), tela.get_height()
        for fator, estrelas in self.camadas:
            for wx, wy, raio, fase in estrelas:
                sx, sy = self._tela(camera, wx, wy, fator)
                if sx < 0 or sx > w or sy < 0 or sy > h:
                    continue
                brilho = 0.55 + 0.45 * math.sin(self.t * 2.2 + fase)
                c = round(180 + 75 * brilho)
                pygame.draw.circle(tela, (c, c, min(255, c + 20)), (sx, sy), max(1, round(raio * camera.escala)))

    def _cadentes(self, tela: pygame.Surface, camera) -> None:
        """Estrelas cadentes: cabeca brilhante com um rastro atras."""
        w, h = tela.get_width(), tela.get_height()
        for x, y, vx, vy, idade, vida in self.cadentes:
            cx, cy = self._tela(camera, x, y, 0.5)
            if cx < -40 or cx > w + 40 or cy > h + 40:
                continue
            fade = max(0.0, 1.0 - idade / vida)
            comp = max(4, round(22 * camera.escala))
            norm = math.hypot(vx, vy) or 1
            tx = cx - round(vx / norm * comp)
            ty = cy - round(vy / norm * comp)
            cor = (255, round(230 * fade + 25), round(180 * fade + 20))
            pygame.draw.line(tela, (180, 180, 220), (tx, ty), (cx, cy), max(1, round(2 * camera.escala)))
            pygame.draw.circle(tela, cor, (cx, cy), max(1, round(2 * camera.escala)))

    def _planetas(self, tela: pygame.Surface, camera) -> None:
        """Planetas que surgem e explodem: planeta inteiro, clarao e onda de choque."""
        w = tela.get_width()
        for wx, wy, raio, cor, idade, vida in self.planetas:
            cx, cy = self._tela(camera, wx, wy, 0.2)
            r = max(2, round(raio * camera.escala))
            if cx + r * 4 < 0 or cx - r * 4 > w:
                continue
            estourar = 1.6              # segundo em que explode
            if idade < estourar:
                # planeta inteiro com sombra de um lado
                pygame.draw.circle(tela, cor, (cx, cy), r)
                sombra = tuple(max(0, c - 70) for c in cor)
                sombra_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
                pygame.draw.circle(sombra_surf, (*sombra, 160), (int(r * 1.3), r), r)
                tela.blit(sombra_surf, (cx - r, cy - r))
                if idade > estourar - 0.25:                     # pisca antes de explodir
                    pygame.draw.circle(tela, (255, 255, 255), (cx, cy), r)
            else:
                prog = (idade - estourar) / (vida - estourar)
                onda = round(r * (1 + 3.5 * prog))
                alpha = max(0, round(220 * (1 - prog)))
                surf = pygame.Surface((onda * 2 + 4, onda * 2 + 4), pygame.SRCALPHA)
                pygame.draw.circle(surf, (255, 230, 160, alpha), (onda + 2, onda + 2), onda, max(1, onda // 4))
                tela.blit(surf, (cx - onda, cy - onda))
                for k in range(8):               # estilhacos do planeta
                    ang = k * math.pi / 4 + idade
                    px = cx + round(math.cos(ang) * onda)
                    py = cy + round(math.sin(ang) * onda)
                    pygame.draw.circle(tela, cor, (px, py), max(1, round(2 * camera.escala)))
