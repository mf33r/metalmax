"""Personagens: o pug controlavel, com animacoes do sprite sheet.

Hierarquia: `Entidade` -> `CorpoFisico` -> `Personagem` -> `Jogador`.
O sheet tem arte para as duas direcoes (linha 0 olha para a direita, linha 9
para a esquerda), entao nada e espelhado: usamos a arte correta.
"""
from __future__ import annotations

import pygame

from src import assets
from src.entidades.entidade import CorpoFisico
from src.entidades.animacao import Animacao
from src.mundo.fisica import mover_e_colidir
from src.ui.config import (
    ALTURA_PERSONAGEM,
    BUFFER_PULO,
    BOB_PASSO,
    CELULAS_PUG,
    COYOTE,
    DURACAO_ATRAVESSAR,
    DURACAO_FRAME,
    DURACAO_FRAME_ANDAR,
    ESCALA_PERSONAGEM,
    GRAVIDADE,
    IMPULSO_DANO,
    IMPULSO_PULO,
    IMPULSO_SEGUNDO_PULO,
    INVULNERABILIDADE,
    LARGURA_PERSONAGEM,
    RECARGA_INVESTIDA,
    SPRITE_PUG,
    TEMPO_INVESTIDA,
    VEL,
    VEL_INVESTIDA,
    VIDAS_MAX,
)

_sheets: dict[str, pygame.Surface] = {}


def carregar_sheet(arquivo: str = SPRITE_PUG) -> pygame.Surface:
    """Carrega (uma vez) o sprite sheet."""
    if arquivo not in _sheets:
        _sheets[arquivo] = assets.imagem(arquivo)
    return _sheets[arquivo]


def montar_animacoes(altura: int, tingimento=None) -> dict:
    """Dicionario nome -> Animacao com as celulas do pug."""
    sheet = carregar_sheet()
    return {
        nome: Animacao(
            sheet, celulas, ESCALA_PERSONAGEM,
            DURACAO_FRAME if nome == "Parado" else DURACAO_FRAME_ANDAR,
            altura_alvo=altura, tingimento=tingimento,
            bob=BOB_PASSO if nome == "Andar" else 0,
        )
        for nome, celulas in CELULAS_PUG.items()
    }


class Personagem(CorpoFisico):
    """Personagem com gravidade, colisao e animacao de sprite."""

    velocidade_andar = VEL

    def __init__(
        self,
        x: float,
        y: float,
        largura: int = LARGURA_PERSONAGEM,
        altura: int = ALTURA_PERSONAGEM,
        tingimento=None,
    ):
        super().__init__(x, y, largura, altura, gravidade=GRAVIDADE)
        self.plataforma_apoio = None
        self.apoio_desvio = None    # distancia do corpo em relacao a plataforma de apoio
        self.atravessando = 0.0
        self.atravessados = set()   # plataformas que o corpo esta atravessando
        self.animacoes = montar_animacoes(altura, tingimento)
        self.acao = "Parado"
        self.acao_forcada = ""      # ex.: "Bravo" enquanto leva dano
        self.animacao = self.animacoes["Parado"]

    # ------------------------------------------------------------- controle
    def acao_desejada(self) -> str:
        """Animacao pelo movimento; a direcao vem do espelhamento, nao do sheet."""
        if self.acao_forcada:
            return self.acao_forcada
        return "Andar" if self.vel.x != 0 else "Parado"

    def definir_acao(self, nome: str) -> None:
        if nome == self.acao:
            return
        self.acao = nome
        self.animacao = self.animacoes[nome]
        self.animacao.reiniciar()

    # --------------------------------------------------------------- ciclo
    def atualizar(self, dt: float, plataformas: list, solidos: tuple = ()) -> None:
        self.atravessando = max(0.0, self.atravessando - dt)
        self.aplicar_gravidade(dt)
        mover_e_colidir(self, dt, plataformas, solidos)
        self.definir_acao(self.acao_desejada())
        self.animacao.avancar(dt)

    def desenhar(self, tela: pygame.Surface, camera) -> None:
        sprite = self.animacao.frame
        if self.virado:
            sprite = pygame.transform.flip(sprite, True, False)   # arte olha so pra direita
        sprite = camera.escalar(sprite)   # buffer pixelado: entra na escala
        alvo = camera.retangulo_na_tela(self.hitbox)
        x = alvo.centerx - sprite.get_width() // 2
        y = alvo.bottom - sprite.get_height() - round(self.animacao.deslocamento_y * camera.escala)
        tela.blit(sprite, (x, y))


class Jogador(Personagem):
    """Controlavel pelo teclado, com pulo tolerante, dano e invulnerabilidade.

    O pulo usa *coyote time* (aceita o comando logo apos sair da borda) e
    *buffer* (guarda o comando apertado um instante antes de tocar o chao).
    """

    def __init__(self, x: float, y: float, vidas: int = VIDAS_MAX):
        super().__init__(x, y)
        self.vidas = vidas
        self.invulneravel = 0.0
        self.coyote = 0.0
        self.pulo_pendente = 0.0
        self.pulo_anterior = False
        self.baixo_anterior = False
        self.saltos_usados = 0          # 0 no chao, 1 depois do primeiro pulo
        self.investida = 0.0           # tempo restante de investida
        self.recarga_investida = 0.0   # espera ate poder investir de novo
        self.investida_anterior = False
        self.mostrar_investida = False
        self.ultimo_dt = 0.0

    def controlar(self, keys) -> None:
        direcao = keys[pygame.K_d] + keys[pygame.K_RIGHT] - keys[pygame.K_a] - keys[pygame.K_LEFT]
        self._controlar_investida(keys, direcao)
        if self.investida <= 0:
            self.andar_para(direcao)
        self._controlar_pulo(keys)
        self._controlar_descida(keys)

    def _controlar_investida(self, keys, direcao: int) -> None:
        """SHIFT ou K: rajada horizontal curta, com recarga. E o que da ritmo."""
        self.investida = max(0.0, self.investida - self.ultimo_dt)
        self.recarga_investida = max(0.0, self.recarga_investida - self.ultimo_dt)
        apertado = bool(keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT] or keys[pygame.K_k])
        if apertado and not self.investida_anterior and self.recarga_investida <= 0 and direcao != 0:
            self.investida = TEMPO_INVESTIDA
            self.recarga_investida = RECARGA_INVESTIDA
            self.vel.x = VEL_INVESTIDA * direcao
            self.virado = direcao < 0
            self.mostrar_investida = True
        self.investida_anterior = apertado

    def _controlar_pulo(self, keys) -> None:
        apertado = bool(keys[pygame.K_w] or keys[pygame.K_UP] or keys[pygame.K_SPACE])
        if apertado and not self.pulo_anterior:
            self.pulo_pendente = BUFFER_PULO   # guarda o comando; soltar a tecla
        self.pulo_anterior = apertado          # nao cancela, so o tempo acaba

    def _controlar_descida(self, keys) -> None:
        descendo = bool(keys[pygame.K_s] or keys[pygame.K_DOWN])
        if descendo and not self.baixo_anterior and self.no_chao and self.plataforma_apoio is not None:
            self.atravessando = DURACAO_ATRAVESSAR   # desce atraves da plataforma
        self.baixo_anterior = descendo

    def atualizar(self, dt: float, plataformas: list, solidos: tuple = ()) -> None:
        self.invulneravel = max(0.0, self.invulneravel - dt)
        self.ultimo_dt = dt
        self.coyote = COYOTE if self.no_chao else max(0.0, self.coyote - dt)
        self.pulo_pendente = max(0.0, self.pulo_pendente - dt)
        direcao_anterior = self.vel.x
        super().atualizar(dt, plataformas, solidos)
        if self.no_chao:
            self.saltos_usados = 0
        if self.investida > 0 and abs(direcao_anterior) < VEL_INVESTIDA and self.vel.x == 0:
            self.investida = 0.0     # bateu em parede: a rajada acaba
        self._tentar_pulo()

    def _tentar_pulo(self) -> None:
        """Consome o pulo guardado: no chao, no coyote ou como segundo pulo."""
        if self.pulo_pendente <= 0:
            return
        if self.no_chao or self.coyote > 0:
            self.pulo_pendente = 0.0
            self.coyote = 0.0
            self.saltos_usados = 1
            self.pular(IMPULSO_PULO)
        elif self.saltos_usados < 2:
            self.pulo_pendente = 0.0
            self.saltos_usados = 2
            self.pular(IMPULSO_SEGUNDO_PULO)   # pulo duplo no ar

    # ----------------------------------------------------------------- dano
    def desenhar(self, tela: pygame.Surface, camera) -> None:
        """Mesma arte da base, mais o rastro da investida."""
        if self.investida <= 0:
            super().desenhar(tela, camera)
            return
        sprite = self.animacao.frame
        if self.virado:
            sprite = pygame.transform.flip(sprite, True, False)
        sprite = camera.escalar(sprite)
        alvo = camera.retangulo_na_tela(self.hitbox)
        x = alvo.centerx - sprite.get_width() // 2
        y = alvo.bottom - sprite.get_height()
        for passo in (2, 1):   # copias atras: da para ver a velocidade
            copia = sprite.copy()
            copia.set_alpha(70 - passo * 26)
            tela.blit(copia, (x + round(self.vel.x * 0.02 * passo), y))
        tela.blit(sprite, (x, y))

    # ----------------------------------------------------------------- dano
    def levar_dano(self, quantidade: int = 1) -> bool:
        """Aplica dano se estiver vulnavel. Devolve True se o dano entrou."""
        if self.invulneravel > 0 or self.vidas <= 0:
            return False
        self.vidas -= quantidade
        self.invulneravel = INVULNERABILIDADE
        # repique para sair do obstaculo, mas sem apagar um pulo mais forte:
        # levar dano no mesmo quadro do salto nao pode cancelar o pulo
        self.vel.y = min(self.vel.y, -IMPULSO_DANO)
        self.no_chao = False
        self.coyote = 0.0
        return True

    def curar(self, quantidade: int = 1) -> bool:
        """Recupera vidas ate o maximo. Devolve True se recuperou."""
        if self.vidas >= VIDAS_MAX:
            return False
        self.vidas = min(VIDAS_MAX, self.vidas + quantidade)
        return True
