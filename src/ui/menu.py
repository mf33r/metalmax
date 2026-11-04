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
OPCOES = "F2 - CONTROLES      L - LEADERBOARD      ESC - SAIR"
ALTURA_HEROI = 228   # multipla de 3: mantem o pixel da arte ao desenhar


class Menu:
    """Tela de abertura: o heroi parado esperando o jogador comecar."""

    def __init__(self) -> None:
        self.fonte_titulo = fonte(72, bold=True)
        self.fonte_chamada = fonte(22)
        self.fonte_opcoes = fonte(15)
        self.fonte_leaderboard_titulo = fonte(34)
        self.fonte_leaderboard_linha = fonte(21)
        self.fonte_leaderboard_ajuda = fonte(18)

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
        self.leaderboard_aberta = False
        self.nome_input_ativo = False
        self.nome_input = ""
        self.leaderboard = []
        self.controles_visiveis = False
        self.aguardando_inicio = False

    # ------------------------------------------------------------- entrada
    def atualizar(self, evento, dt: float = 0.0) -> str | None:
        """Move o heroi e trata nome, controles e início da partida."""
        if self.abrindo:
            return None
        self.tempo += dt
        if self.tempo > 9.0:
            self.raiva.avancar(dt)
        else:
            self.andando.avancar(dt)
        if evento is None:
            return None
        if self.leaderboard_aberta:
            if evento.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                self.leaderboard_aberta = False
            return None
        if self.nome_input_ativo:
            if evento.type == pygame.TEXTINPUT:
                self.nome_input = (self.nome_input + evento.text)[:16]
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_BACKSPACE:
                    self.nome_input = self.nome_input[:-1]
                elif evento.key == pygame.K_RETURN and self.nome_input.strip():
                    self.nome_input_ativo = False
                    self.controles_visiveis = True
                    self.aguardando_inicio = True
                    pygame.key.stop_text_input()
                    return "NOME_CONFIRMADO"
                elif evento.key == pygame.K_ESCAPE:
                    self.nome_input_ativo = False
                    pygame.key.stop_text_input()
            return None
        if self.controles_visiveis:
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_RETURN:
                self.controles_visiveis = False
                self.aguardando_inicio = False
                return "INICIAR"
            return None
        if self.aguardando_inicio:
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_RETURN:
                self.aguardando_inicio = False
                return "INICIAR"
            return None
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_F2:
            return "CONTROLES"
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            return "SAIR"
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_l:
            self.leaderboard_aberta = True
            return None
        if evento.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):
            self.nome_input_ativo = True
            self.nome_input = ""
            pygame.key.start_text_input()
        return None

    def reiniciar(self) -> None:
        """Volta a capa e limpa o fluxo de início da próxima partida."""
        self.abrindo = False
        self.tempo = 0.0
        self.controles_visiveis = False
        self.aguardando_inicio = False
    # ------------------------------------------------------------ desenho
    def desenhar(self, tela) -> None:
        """Ceu do jogo, titulo grande e o pug parado no chao."""
        self.cenario.desenhar(tela, self.camera)
        self._heroi(tela)
        self._letreiro(tela)
        estado_tutorial = self.nome_input_ativo or self.controles_visiveis or self.aguardando_inicio
        if not estado_tutorial and int(self.tempo * 1.6) % 2 == 0 and not self.abrindo:
            texto(tela, self.fonte_chamada, CHAMADA, CORES["texto"], contorno=2,
                  centro=(tela.get_width() // 2, tela.get_height() - 56))
        if self.leaderboard_aberta:
            self._desenhar_leaderboard(tela)
        elif self.nome_input_ativo:
            self._desenhar_nome(tela)
        elif self.controles_visiveis:
            self._desenhar_controles(tela)
        if self.aguardando_inicio and not self.nome_input_ativo and int(self.tempo * 2) % 2 == 0:
            texto(tela, self.fonte_chamada, "Aperte Enter Para Começar", CORES["moeda"],
                  contorno=2, centro=(tela.get_width() // 2, tela.get_height() - 56))
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

    def _desenhar_controles(self, tela) -> None:
        linhas = (
            "CONTROLES",
            "A / D ou SETAS: andar",
            "W / ESPACO: pular (2x = pulo duplo)",
            "SHIFT ou K: investida",
            "S / BAIXO: descer da plataforma",
            "F2: ver controles",
            "ESC: voltar ao menu  |  R: recomecar",
        )
        caixa = pygame.Rect(tela.get_width() // 2 - 300, 170, 600, 360)
        pygame.draw.rect(tela, (30, 24, 42, 235), caixa, border_radius=12)
        pygame.draw.rect(tela, CORES["moeda"], caixa, 3, border_radius=12)
        for indice, linha in enumerate(linhas):
            fonte_atual = self.fonte_chamada if indice == 0 else self.fonte_opcoes
            cor = CORES["moeda"] if indice == 0 else CORES["texto"]
            texto(tela, fonte_atual, linha, cor, centro=(caixa.centerx, caixa.y + 36 + indice * 44))

    def _desenhar_leaderboard(self, tela) -> None:
        caixa = pygame.Rect(tela.get_width() // 2 - 320, 125, 640, 450)
        pygame.draw.rect(tela, (30, 24, 42, 235), caixa, border_radius=12)
        pygame.draw.rect(tela, CORES["moeda"], caixa, 3, border_radius=12)
        texto(tela, self.fonte_leaderboard_titulo, "LEADERBOARD", CORES["moeda"],
              centro=(caixa.centerx, caixa.y + 40))
        texto(tela, self.fonte_leaderboard_linha, "NOME                         TEMPO", CORES["texto"],
              centro=(caixa.centerx, caixa.y + 86))
        if not self.leaderboard:
            texto(tela, self.fonte_leaderboard_linha, "Ainda sem tempos registrados", CORES["texto"],
                  centro=(caixa.centerx, caixa.y + 145))
        for indice, registro in enumerate(self.leaderboard[:8]):
            linha = f"{indice + 1:>2}. {registro['nome'][:16]:<16}  {registro['tempo']}"
            texto(tela, self.fonte_leaderboard_linha, linha, CORES["texto"],
                  centro=(caixa.centerx, caixa.y + 132 + indice * 34))
        texto(tela, self.fonte_leaderboard_ajuda, "L ou qualquer tecla para voltar", CORES["texto"],
              centro=(caixa.centerx, caixa.bottom - 24))

    def _desenhar_nome(self, tela) -> None:
        caixa = pygame.Rect(tela.get_width() // 2 - 250, 220, 500, 190)
        pygame.draw.rect(tela, (30, 24, 42, 235), caixa, border_radius=12)
        pygame.draw.rect(tela, CORES["moeda"], caixa, 3, border_radius=12)
        texto(tela, self.fonte_chamada, "DIGITE SEU NOME", CORES["texto"], centro=(caixa.centerx, caixa.y + 45))
        exibido = self.nome_input or "_"
        texto(tela, self.fonte_chamada, exibido, CORES["moeda"], centro=(caixa.centerx, caixa.y + 95))
        texto(tela, self.fonte_opcoes, "ENTER para confirmar o nome", CORES["texto"],
              centro=(caixa.centerx, caixa.y + 145))
