"""Boss da fase 2: o robo "Big Robo", com dois modos de ataque.

- FLUTUA: paira alto, patrulha e, de tempos em tempos, mira o canhao no pug e
  dispara um orbe de laser que sai do canhao em direcao ao pug (acerta quem esta
  no chao, porque o tiro desce ate ele). Da para desviar correndo/pulando.
- MERGULHO: quando nao da para acertar de cima, ele se inclina e desce por ~3s,
  soltando laser numa frequencia que deixa aberturas para o pug pular entre os
  tiros e atirar nele, que fica baixo e vulneravel.

Usa so a aparencia (assets/imagens/boss.png) e o golpe de laser. O boss leva
dano dos projeteis do pug (tecla F).
"""
from __future__ import annotations

import math

import pygame

from src import assets
from src.entidades.entidade import Entidade

ALTURA_MUNDO = 240
VEL_LASER = 210.0
VEL_PATRULHA = 90.0

FLUTUA_Y = 230.0
MERGULHO_Y = 380.0
T_FLUTUA = 5.0
T_MERGULHO = 3.0
# intervalo entre tiros e telegrafo por fase
TIRO = {"flutua": 1.7, "mergulho": 0.85}
TELE = {"flutua": 0.9, "mergulho": 0.3}
ANGULO_MERGULHO = -14.0     # inclinacao (graus) ao mergulhar


class LaserChefe(Entidade):
    """Orbe de laser que sai do canhao numa direcao. Machuca o pug (1 vida)."""

    R = 15

    def __init__(self, x: float, y: float, vx: float, vy: float):
        super().__init__(x - self.R, y - self.R, self.R * 2, self.R * 2)
        self.hitbox = pygame.Rect(round(self.pos.x), round(self.pos.y), self.R * 2, self.R * 2)
        self.vx = vx
        self.vy = vy
        self.ativo = True
        self.t = 0.0

    def atualizar(self, dt: float) -> None:
        self.t += dt
        self.pos.x += self.vx * dt
        self.pos.y += self.vy * dt
        self.hitbox.topleft = (round(self.pos.x), round(self.pos.y))

    def desenhar(self, tela: pygame.Surface, camera) -> None:
        alvo = camera.retangulo_na_tela(self.hitbox)
        # rastro curto no sentido oposto ao movimento
        norm = math.hypot(self.vx, self.vy) or 1
        tx = alvo.centerx - round(self.vx / norm * alvo.w)
        ty = alvo.centery - round(self.vy / norm * alvo.h)
        pygame.draw.line(tela, (120, 230, 255), (tx, ty), alvo.center, max(1, alvo.w // 4))
        pygame.draw.circle(tela, (120, 230, 255), alvo.center, max(2, alvo.w // 2 + 1))
        pygame.draw.circle(tela, (210, 250, 255), alvo.center, max(2, alvo.w // 2 - 1))
        pygame.draw.circle(tela, (255, 255, 255), alvo.center, max(1, alvo.w // 4))


class Boss(Entidade):
    """Robo que patrulha, paira e mergulha, disparando laser mirado do canhao."""

    def __init__(self, x: int, y: int, vida: int = 8):
        img = assets.imagem("boss.png")
        escala = ALTURA_MUNDO / img.get_height()
        self.sprite = pygame.transform.scale(img, (round(img.get_width() * escala), ALTURA_MUNDO))
        largura = self.sprite.get_width()
        super().__init__(x, y, largura, ALTURA_MUNDO)
        self.hitbox = pygame.Rect(x + largura // 3, y + 30, largura - largura // 3 - 10, ALTURA_MUNDO - 70)
        self.x_min = x - 300
        self.x_max = x + 160
        self.vx = -VEL_PATRULHA
        self.vida_max = vida
        self.vida = vida
        self.ativo = False
        self.morto = False
        self.t = 0.0
        self.piscar = 0.0
        self.angulo = 0.0

        self.fase = "flutua"
        self.fase_tempo = T_FLUTUA
        self.recarga = TIRO["flutua"]
        self.carregando = False
        self.tele = 0.0
        self.mira = pygame.Vector2(x, y)
        self.lasers: list[LaserChefe] = []

    def acordar(self) -> None:
        self.ativo = True

    @property
    def muzzle(self) -> tuple[int, int]:
        return (self.hitbox.left - 6, self.hitbox.centery)

    def atualizar(self, dt: float, alvo: pygame.Rect | None = None) -> None:
        for laser in self.lasers:
            laser.atualizar(dt)
        self.lasers = [l for l in self.lasers if l.ativo and -220 < l.hitbox.x < 9000 and l.hitbox.y < 1200]
        if not self.ativo or self.morto:
            return
        self.t += dt
        self.piscar = max(0.0, self.piscar - dt)

        # alterna FLUTUA <-> MERGULHO
        self.fase_tempo -= dt
        if self.fase_tempo <= 0:
            if self.fase == "flutua":
                self.fase, self.fase_tempo = "mergulho", T_MERGULHO
            else:
                self.fase, self.fase_tempo = "flutua", T_FLUTUA
            self.recarga = TIRO[self.fase]

        # movimento horizontal (vai e volta) e vertical (sobe no flutua, desce no mergulho)
        self.pos.x += self.vx * dt
        if self.pos.x <= self.x_min:
            self.pos.x, self.vx = self.x_min, VEL_PATRULHA
        elif self.pos.x >= self.x_max:
            self.pos.x, self.vx = self.x_max, -VEL_PATRULHA
        alvo_y = (MERGULHO_Y if self.fase == "mergulho" else FLUTUA_Y) + math.sin(self.t * 1.4) * 18
        self.pos.y += (alvo_y - self.pos.y) * min(1.0, 3.0 * dt)
        alvo_ang = ANGULO_MERGULHO if self.fase == "mergulho" else 0.0
        self.angulo += (alvo_ang - self.angulo) * min(1.0, 4.0 * dt)
        self.hitbox.x = round(self.pos.x) + self.largura // 3
        self.hitbox.y = round(self.pos.y) + 30

        self._atacar(dt, alvo)

    def _atacar(self, dt: float, alvo: pygame.Rect | None) -> None:
        if self.carregando:
            self.tele -= dt
            if self.tele <= 0:
                self._disparar()
            return
        self.recarga -= dt
        if self.recarga <= 0:
            self.carregando = True
            self.tele = TELE[self.fase]
            mx, my = self.muzzle
            destino = alvo.center if alvo is not None else (mx - 200, my)
            self.mira.update(destino)

    def _disparar(self) -> None:
        self.carregando = False
        self.recarga = TIRO[self.fase]
        mx, my = self.muzzle
        dx, dy = self.mira.x - mx, self.mira.y - my
        norm = math.hypot(dx, dy) or 1
        self.lasers.append(LaserChefe(mx, my, dx / norm * VEL_LASER, dy / norm * VEL_LASER))

    def levar_dano(self, quantidade: int = 1) -> bool:
        if self.morto or self.piscar > 0 or not self.ativo:
            return False
        self.vida -= quantidade
        self.piscar = 0.18
        if self.vida <= 0:
            self.vida = 0
            self.morto = True
            self.ativo = False
        return True

    # ------------------------------------------------------------- desenho
    def desenhar(self, tela: pygame.Surface, camera) -> None:
        base = camera.escalar(self.sprite)
        if abs(self.angulo) > 0.5:
            base = pygame.transform.rotate(base, self.angulo)
        centro = camera.ponto_na_tela((self.pos.x + self.largura / 2, self.pos.y + self.altura / 2))
        rect = base.get_rect(center=centro)
        tela.blit(base, rect.topleft)
        if self.piscar > 0:
            clarao = base.copy()
            clarao.fill((255, 255, 255, 120), special_flags=pygame.BLEND_RGBA_ADD)
            tela.blit(clarao, rect.topleft)
        if self.ativo and self.carregando:
            self._telegrafo(tela, camera)
        for laser in self.lasers:
            laser.desenhar(tela, camera)

    def _telegrafo(self, tela: pygame.Surface, camera) -> None:
        """Mira do canhao ate o alvo + brilho crescente, enquanto carrega."""
        mx, my = self.muzzle
        prog = 1.0 - max(0.0, self.tele) / max(0.01, TELE[self.fase])
        if int(prog * 10) % 2 == 0:
            ini = camera.ponto_na_tela((mx, my))
            fim = camera.ponto_na_tela((self.mira.x, self.mira.y))
            pygame.draw.line(tela, (255, 80, 70), ini, fim, max(1, round(2 * camera.escala)))
        centro = camera.ponto_na_tela((mx, my))
        raio = max(1, round((3 + 9 * prog) * camera.escala))
        pygame.draw.circle(tela, (255, 90, 60), centro, raio)
        pygame.draw.circle(tela, (255, 220, 180), centro, max(1, raio // 2))
