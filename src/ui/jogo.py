"""Controlador do jogo: janela, loop principal e maquina de estados.

Estados: MENU -> JOGANDO -> (PAUSADO | FIM_DE_JOGO | VITORIA) -> MENU.
No MENU, `opcoes_abertas` sobrepoe o painel de controles ao fundo do menu.

O cenario e a interface sao desenhados num buffer 1/3 da resolucao e ampliados
sem interpolacao. O cenario e opaco e substitui a tela; a interface tem alpha e
e misturada por cima.
"""
from __future__ import annotations

import pygame

from src.mundo.nivel import Nivel
from src.ui.avisos import Aviso
from src.ui.hud import Hud
from src.ui.menu import Menu
from src.ui.config import ALTURA, CAPTION, ESCALA_PIXEL, FPS, LARGURA

DURACAO_FADE = 0.45

CONTROLES = "\n".join([
    "A / D  ou  SETAS: andar",
    "W  ou  ESPACO: pular (2x = pulo duplo)",
    "SHIFT  ou  K: INVESTIDA rapida",
    "S  ou  BAIXO: descer da plataforma",
    "F2: esta tela",
    "ESC: pausar / voltar      R: recomecar",
])


class Jogo:
    """Dono da tela e do loop; delega o conteudo para Menu, Nivel, Hud e Aviso."""

    MENU = "MENU"
    ESCURECENDO = "ESCURECENDO"   # fade entre a capa e o jogo
    JOGANDO = "JOGANDO"
    PAUSADO = "PAUSADO"
    FIM_DE_JOGO = "FIM_DE_JOGO"
    VITORIA = "VITORIA"

    def __init__(self) -> None:
        pygame.init()
        self.tela = self._abrir_janela()
        # cenario em 1/3 (pixel art); interface em resolucao cheia (legivel)
        self.buffer = pygame.Surface((LARGURA // ESCALA_PIXEL, ALTURA // ESCALA_PIXEL))
        self.ui = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        self._tela_preta = pygame.Surface((LARGURA, ALTURA))
        pygame.display.set_caption(CAPTION)

        self.relogio = pygame.time.Clock()
        self.menu = Menu()
        self.hud = Hud()
        self.aviso = Aviso()
        self.nivel: Nivel | None = None
        self.estado = self.MENU
        self.opcoes_abertas = False
        self.fade = 0.0             # 0 = visivel, 1 = preto total
        self.rodando = True
        self._avisou_chave = False

    @staticmethod
    def _abrir_janela():
        """Abre a janela no tamanho do projeto, com saida menor se nao couber."""
        try:
            return pygame.display.set_mode((LARGURA, ALTURA))
        except pygame.error:
            return pygame.display.set_mode((LARGURA // 2, ALTURA // 2))

    # ---------------------------------------------------------------- loop
    def rodar(self) -> None:
        while self.rodando:
            dt = self.relogio.tick(FPS) / 1000.0
            for evento in pygame.event.get():
                self.tratar_evento(evento)
            self.atualizar(dt)
            self.desenhar()
            pygame.display.flip()
        pygame.quit()

    def tratar_evento(self, evento: pygame.event.Event) -> None:
        if evento.type == pygame.QUIT:
            self.rodando = False
            return

        if self.opcoes_abertas and evento.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):
            self._fechar_opcoes()
            return

        if self.estado == self.MENU:
            self._tratar_menu(evento)
        elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_F2:
            self.estado = self.PAUSADO
            self._abrir_opcoes()
        elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            self._voltar_ao_menu()
        elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_r:
            self._recomecar()

    def _tratar_menu(self, evento: pygame.event.Event) -> None:
        acao = self.menu.atualizar(evento)
        if acao == "INICIAR":
            self.estado = self.ESCURECENDO     # fade para preto -> jogo aparece
        elif acao == "CONTROLES":
            self._abrir_opcoes()
        elif acao == "SAIR":
            self.rodando = False

    def _abrir_opcoes(self) -> None:
        self.opcoes_abertas = True
        self.aviso.mostrar("CONTROLES", CONTROLES)

    def _fechar_opcoes(self) -> None:
        self.opcoes_abertas = False
        self.aviso.esconder()

    def _recomecar(self) -> None:
        if self.estado in (self.FIM_DE_JOGO, self.VITORIA, self.PAUSADO):
            self.iniciar_fase()
        elif self.estado == self.JOGANDO:
            self.estado = self.PAUSADO
            self.aviso.mostrar("PAUSA", "ESC para continuar, R para recomecar")

    def _voltar_ao_menu(self) -> None:
        self.estado = self.PAUSADO if self.estado == self.JOGANDO else self.MENU
        if self.estado == self.MENU:
            self._fechar_opcoes()
            self.nivel = None

    def _terminar_fade(self) -> None:
        """A tela ja esta preta: comeca a fase e clareia de novo."""
        self.iniciar_fase()
        self.menu.reiniciar()

    def iniciar_fase(self) -> None:
        self.nivel = Nivel()
        self.estado = self.JOGANDO
        self.opcoes_abertas = False
        self._avisou_chave = False
        self.aviso.esconder()

    # ------------------------------------------------------------- update
    def atualizar(self, dt: float) -> None:
        if self.estado == self.ESCURECENDO:
            self.fade = min(1.0, self.fade + dt / DURACAO_FADE)
            if self.fade >= 1.0:
                self._terminar_fade()
            return
        if self.fade > 0.0:          # clareando depois da transicao
            self.fade = max(0.0, self.fade - dt / DURACAO_FADE)

        if self.estado == self.MENU:
            self.menu.atualizar(None, dt)   # so anima o heroi do menu
            return
        if self.estado != self.JOGANDO or self.nivel is None:
            return

        self.nivel.atualizar(dt, pygame.key.get_pressed())
        jogador = self.nivel.jogador
        self.hud.atualizar(
            jogador.vidas, self.nivel.pontos, self.nivel.moedas, self.nivel.pisados,
            jogador.invulneravel > 0, self.nivel.tem_chave,
        )
        self.hud.atualizar_itens(self.nivel.coletados, self.nivel.tem_chave)

        if self.nivel.morto:
            self.estado = self.FIM_DE_JOGO
            self.aviso.mostrar("FIM DE JOGO", "R para tentar de novo, ESC para o menu")
        elif self.nivel.venceu:
            self.estado = self.VITORIA
            self.aviso.mostrar("VITORIA!", f"{self.nivel.pontos} pontos - R para jogar de novo")
        elif self.nivel.tem_chave and not self._avisou_chave:
            self._avisou_chave = True
            self.aviso.mostrar("CHAVE!", "a porta de saida abriu - chegue nela")

    # ------------------------------------------------------------- desenho
    def desenhar(self) -> None:
        """Cenario e interface no buffer pequeno, ampliados sem interpolacao."""
        self.ui.fill((0, 0, 0, 0))
        so_interface = self.nivel is None or self.estado in (self.MENU, self.ESCURECENDO)

        if so_interface:
            self.menu.desenhar(self.ui)
        else:
            self._desenhar_mundo()
            self.hud.desenhar(self.ui)
            if self.estado in (self.PAUSADO, self.FIM_DE_JOGO, self.VITORIA):
                self.aviso.desenhar(self.ui)

        if self.opcoes_abertas:
            self.aviso.desenhar(self.ui)
        self.tela.blit(self.ui, (0, 0))
        self._desenhar_fade()

    def _desenhar_mundo(self) -> None:
        """Mundo no buffer 1/3, ampliado sem interpolacao.

        A camera precisa estar na escala do buffer durante o desenho: sem isso
        o cenario e desenhado 1:1 num buffer de 233 px de altura e tudo que
        fica abaixo do horizonte (chao, plataformas, personagem) sai da tela.
        """
        camera = self.nivel.camera
        camera.escala = 1.0 / ESCALA_PIXEL
        self.nivel.desenhar(self.buffer)
        camera.escala = 1.0
        pygame.transform.scale(self.buffer, self.tela.get_size(), self.tela)

    def _desenhar_fade(self) -> None:
        """Escurece a tela inteira durante a transicao."""
        if self.fade <= 0.0:
            return
        self._tela_preta.set_alpha(round(255 * self.fade))
        self.tela.blit(self._tela_preta, (0, 0))
