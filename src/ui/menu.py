"""Capa de inicio: o ceu do jogo, o titulo e o pug esperando.

Sem botao e sem efeito: qualquer clique ou tecla comeca o jogo, com fade.
"""
from __future__ import annotations

import pygame

from src import assets
from src.entidades.animacao import Animacao
from src.mundo.camera import Camera
from src.mundo.cenario import Cenario
from src.ui.estilo import fonte, texto
from src.ui.config import ALTURA, CELULAS_PUG, CORES, ESCALA_PERSONAGEM, LARGURA, SPRITE_PUG

TEXTO_TITULO = "METAL MAX"
CHAMADA = "CLIQUE PARA COMECAR"
OPCOES = "F2 - CONTROLES      ESC - SAIR"
ALTURA_HEROI = 228   # multipla de 3: mantem o pixel da arte ao desenhar


class Menu:
    """Tela de abertura: o heroi parado esperando o jogador comecar."""

    def __init__(self) -> None:
        self.fonte_titulo = fonte(72, bold=True)
        self.fonte_chamada = fonte(22)
        self.fonte_opcoes = fonte(15)

        self.cenario = Cenario(LARGURA, ALTURA)
        self.camera = Camera(LARGURA, ALTURA, LARGURA, ALTURA)

        sheet = assets.imagem(SPRITE_PUG)
        self.andando = Animacao(
            sheet, CELULAS_PUG["Andar"], ESCALA_PERSONAGEM, altura_alvo=ALTURA_HEROI, bob=3,
        )
        self.parado = Animacao(
            sheet, CELULAS_PUG["Parado"], ESCALA_PERSONAGEM,
            altura_alvo=ALTURA_HEROI, laco=False,
        ).frames[0]
        self.raiva = Animacao(
            sheet, CELULAS_PUG["Bravo"], ESCALA_PERSONAGEM,
            altura_alvo=ALTURA_HEROI, duracao_frame=0.22,
        )
        self.tempo = 0.0
        self.abrindo = False

    # ------------------------------------------------------------- entrada
    def atualizar(self, evento, dt: float = 0.0) -> str | None:
        """Move o heroi. Devolve a acao do clique/tecla, ou None."""
        if self.abrindo:
            return None
        self.tempo += dt
        if self.tempo > 9.0:      # parado tempo demais, ele fica com raiva
            self.raiva.avancar(dt)
        else:
            self.andando.avancar(dt)
        if evento is not None and evento.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_F2:
                return "CONTROLES"
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                return "SAIR"
            self.abrindo = True
            return "INICIAR"
        return None

    def reiniciar(self) -> None:
        """Volta a capa depois de uma partida."""
        self.abrindo = False
        self.tempo = 0.0

    # ------------------------------------------------------------ desenho
    def desenhar(self, tela) -> None:
        """Ceu do jogo, titulo grande e o pug parado no chao."""
        self.cenario.desenhar(tela, self.camera)
        self._heroi(tela)
        self._letreiro(tela)
        if int(self.tempo * 1.6) % 2 == 0 and not self.abrindo:
            texto(tela, self.fonte_chamada, CHAMADA, CORES["texto"], contorno=2,
                  centro=(tela.get_width() // 2, tela.get_height() - 56))
        texto(tela, self.fonte_opcoes, OPCOES, (236, 232, 220), contorno=2,
              centro=(tela.get_width() // 2, tela.get_height() - 26))

    def _heroi(self, tela) -> None:
        """O pug no centro-baixo, virado para o jogador."""
        if self.tempo > 9.0:
            sprite, anim = self.raiva.frame, self.raiva
        elif int(self.tempo * 1.2) % 7 == 0:
            sprite, anim = self.parado, None
        else:
            sprite, anim = self.andando.frame, self.andando
        x = tela.get_width() // 2 - sprite.get_width() // 2
        y = int(tela.get_height() * 0.72) - sprite.get_height()
        tela.blit(sprite, (x, y - (anim.deslocamento_y if anim else 0)))

    def _letreiro(self, tela) -> None:
        """Titulo grande com sombra dura, no alto da tela."""
        centro = (tela.get_width() // 2, 96)
        texto(tela, self.fonte_titulo, TEXTO_TITULO, (36, 24, 40), contorno=4,
              centro=(centro[0] + 4, centro[1] + 5))
        texto(tela, self.fonte_titulo, TEXTO_TITULO, CORES["moeda"], contorno=3, centro=centro)
