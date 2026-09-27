"""Colisao AABB contra o cenario, resolvida eixo a eixo.

Convencoes do modulo:
- `plataformas`/`solidos` sao listas de objetos com atributo `corpo`
  (pygame.Rect) e deltas opcionais `dx`/`dy` (quanto se moveram no passo).
- Plataforma e de "sentido unico": so pode ser atravessada subindo. O pouso
  vale quando o corpo estava acima do topo no passo anterior.
- Obstaculo solido bloqueia nos dois eixos.
"""
from __future__ import annotations

import pygame

from src.entidades.entidade import CorpoFisico

# Margem para "subir degrau": se os pes estao um pouco abaixo do topo, o corpo
# entra em cima em vez de travar na parede. Ela e relativa a espessura da
# plataforma: um valor fixo que servia para tabua de 26 px afundava o jogador
# ate a metade de uma tabua de 12 px.
_TOLERANCIA_MAXIMA = 6.0
_FRACAO_ESPESSURA = 3.0


def _tolerancia(plataforma) -> float:
    """Quanto o corpo pode afundar na plataforma antes de contar como degrau."""
    return min(_TOLERANCIA_MAXIMA, plataforma.corpo.h / _FRACAO_ESPESSURA)


def mover_e_colidir(
    corpo: CorpoFisico,
    dt: float,
    plataformas: list,
    solidos: tuple = (),
    *,
    colisao_horizontal: bool = True,
    unilateral: bool = True,
) -> None:
    """Aplica o movimento de `corpo` e resolve a colisao com o cenario.

    Ao final `corpo.no_chao` diz se houve pouso neste passo.
    """
    _atualizar_apoio(corpo)
    _mover_x(corpo, dt, plataformas, solidos, colisao_horizontal)
    _mover_y(corpo, dt, plataformas, solidos, unilateral)
    corpo.sincronizar_posicao()


# ------------------------------------------------------------------ eixo X
def _assume_apoio(corpo: CorpoFisico, plataforma) -> None:
    """Trocou de plataforma de apoio: o desvio para colar precisa recomecar."""
    if corpo.plataforma_apoio is not plataforma:
        corpo.apoio_desvio = None
    corpo.plataforma_apoio = plataforma


def _atualizar_apoio(corpo: CorpoFisico) -> None:
    """Carrega o corpo junto da plataforma de apoio; solta quando nao ha mais.

    Sem isso o personagem escorrega de plataformas moveis: o unico empurrao
    existente viria da resolucao vertical do passo anterior.
    """
    apoio = getattr(corpo, "plataforma_apoio", None)
    if apoio is None:
        return

    pe = corpo.hitbox.bottom
    piseira = pygame.Rect(corpo.hitbox.x, pe - 1, corpo.hitbox.w, 2)
    tolerancia = _tolerancia(apoio) + max(0, round(getattr(apoio, "dy", 0.0)))
    if piseira.colliderect(apoio.corpo) and abs(pe - apoio.corpo.top) <= tolerancia:
        moveu_x = round(getattr(apoio, "dx", 0.0))
        moveu_y = round(getattr(apoio, "dy", 0.0))
        if moveu_x or moveu_y:
            # Cola o corpo na plataforma em vez de somar o deslocamento: somar
            # um delta fracionario a cada quadro acumula o erro e o corpo
            # escorrega. Em plataforma estatica nao mexe em nada, senao o
            # jogador ficaria preso no lugar.
            if corpo.apoio_desvio is None:
                corpo.apoio_desvio = corpo.hitbox.x - apoio.corpo.x
            corpo.hitbox.x = round(apoio.corpo.x + corpo.apoio_desvio)
    else:
        corpo.plataforma_apoio = None
        corpo.apoio_desvio = None


def _mover_x(corpo: CorpoFisico, dt: float, plataformas: list, solidos: tuple, resolver: bool) -> None:
    corpo.hitbox.x += round(corpo.vel.x * dt)
    if not resolver:
        return

    # Plataforma atravessada na subida fica "ignorada" ate o corpo sair de
    # dentro dela. Inferir pela velocidade nao funciona: no apice do pulo a
    # gravidade deixa vel.y positivo por um quadro e a colisao lateral
    # disparava, jogando o jogador dozens de pixels para fora.
    atravessados = corpo.atravessados
    for alvo in list(atravessados):
        if not corpo.hitbox.colliderect(alvo.corpo):
            atravessados.discard(alvo)

    for plataforma in plataformas:
        if plataforma in atravessados:
            continue
        if not corpo.hitbox.colliderect(plataforma.corpo):
            continue
        if _encostado_no_topo(corpo, plataforma):
            _subir_degrau(corpo, plataforma)   # degrau baixo: sobe em vez de travar
            continue
        _empurrar(corpo, plataforma)
    for solido in solidos:
        if not getattr(solido, "solido", True):
            continue          # solido que pode abrir (a porta com a chave)
        if not corpo.hitbox.colliderect(solido.corpo):
            continue
        if corpo.hitbox.bottom < solido.corpo.top and corpo.vel.y < 0:
            continue          # corpo inteiro acima e subindo: pulo por cima, nao parede
        _empurrar(corpo, solido)


def _resolver_menor_penetracao(corpo: CorpoFisico, solido, deslocamento: int) -> None:
    """Sai do solido pelo eixo do movimento; em encaixe fundo, pelo lado mais curto.

    Resolver sempre na vertical teleportava: batendo a cabeca o corpo descia
    dezenas de pixels de uma vez, acabava dentro do chao e no quadro seguinte
    era expulso para longe.
    """
    caixa = corpo.hitbox
    alvo = solido.corpo

    if deslocamento > 0:
        correcao, lado = caixa.bottom - alvo.top, "baixo"
    elif deslocamento < 0:
        correcao, lado = alvo.bottom - caixa.top, "cima"
    else:
        correcao, lado = 0, ""

    if correcao <= caixa.h:
        if lado == "baixo":
            caixa.bottom = alvo.top
            corpo.vel.y = 0.0
            corpo.no_chao = True
            corpo.plataforma_apoio = None
        elif lado == "cima":
            caixa.top = alvo.bottom
            corpo.vel.y = 0.0
        return

    # ja estava fundo dentro: sai pelo lado mais proximo, sem atravessar
    acima = (caixa.centery < alvo.centery)
    esquerda = (caixa.centerx < alvo.centerx)
    opcoes = [
        (alvo.bottom - caixa.top if acima else caixa.bottom - alvo.top, "cima" if acima else "baixo"),
        (alvo.right - caixa.left if esquerda else caixa.right - alvo.left, "esquerda" if esquerda else "direita"),
    ]
    penetracao, saida = min(opcoes, key=lambda opcao: opcao[0])
    if saida == "cima":
        caixa.top = alvo.bottom
        corpo.vel.y = 0.0
    elif saida == "baixo":
        caixa.bottom = alvo.top
        corpo.vel.y = 0.0
        corpo.no_chao = True
        corpo.plataforma_apoio = None
    elif saida == "esquerda":
        caixa.right = alvo.left
        corpo.vel.x = 0.0
    else:
        caixa.left = alvo.right
        corpo.vel.x = 0.0


def _subir_degrau(corpo: CorpoFisico, plataforma) -> None:
    """Encaixa o corpo em cima da plataforma quando ele ja quase encostou nela.

    E o degrau automatico: correr contra uma borda baixa levanta o jogador em
    vez de segura-lo na parede.
    """
    corpo.hitbox.bottom = plataforma.corpo.top
    corpo.vel.y = 0.0
    corpo.no_chao = True
    _assume_apoio(corpo, plataforma)


def _empurrar(corpo: CorpoFisico, alvo) -> None:
    if corpo.vel.x > 0:
        corpo.hitbox.right = alvo.corpo.left
    elif corpo.vel.x < 0:
        corpo.hitbox.left = alvo.corpo.right
    corpo.vel.x = 0.0


def _encostado_no_topo(corpo: CorpoFisico, plataforma) -> bool:
    """True quando o corpo apenas esta apoiado no topo (pode sair andando)."""
    return abs(corpo.hitbox.bottom - plataforma.corpo.top) <= _tolerancia(plataforma)


# ------------------------------------------------------------------ eixo Y
def _mover_y(corpo: CorpoFisico, dt: float, plataformas: list, solidos: tuple, unilateral: bool) -> None:
    velocidade_y = corpo.vel.y
    deslocamento = round(velocidade_y * dt)
    base_anterior = corpo.hitbox.bottom
    corpo.hitbox.y += deslocamento
    corpo.no_chao = False

    for solido in solidos:
        if not getattr(solido, "solido", True):
            continue
        if not corpo.hitbox.colliderect(solido.corpo):
            continue
        _resolver_menor_penetracao(corpo, solido, deslocamento)
        return

    if not unilateral or corpo.atravessando > 0:
        return
    if velocidade_y < 0:
        # subindo: registra quais plataformas esta atravessando, para que a
        # colisao lateral do proximo quadro nao o empurre para fora delas
        for plataforma in plataformas:
            if corpo.hitbox.colliderect(plataforma.corpo):
                corpo.atravessados.add(plataforma)
        return
    for plataforma in plataformas:
        _pousar(corpo, plataforma, base_anterior, deslocamento)


def _pousar(corpo: CorpoFisico, plataforma, base_anterior: int, deslocamento: int) -> None:
    """Pousa o corpo no topo da plataforma, se o topo subiu ate ele neste passo."""
    if deslocamento < 0:
        return

    topo = plataforma.corpo.top
    subida_plataforma = max(0, getattr(plataforma, "dy", 0))
    if base_anterior > topo + subida_plataforma:
        return
    if corpo.hitbox.bottom < topo:
        return
    if corpo.hitbox.right <= plataforma.corpo.left or corpo.hitbox.left >= plataforma.corpo.right:
        return

    corpo.hitbox.bottom = topo
    corpo.vel.y = 0.0
    corpo.no_chao = True
    _assume_apoio(corpo, plataforma)
