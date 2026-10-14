---
id: intro
slug: /
title: METAL MAX
sidebar_position: 1
---

# METAL MAX

Jogo de plataforma escrito em **pygame-ce**. O cenário é pintado em código com a
paleta do próprio sprite do pug, e o mundo é desenhado num buffer com um terço da
resolução, ampliado sem interpolação — pixel art de verdade, sem ser uma imagem.

## Rodar

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Só isso: nada de build, nenhum passo extra. O jogo abre uma janela de
1400×700 e roda a 60 fps.

## Controles

| Tecla | Ação |
|---|---|
| `A` / `D` ou setas | andar |
| `W` / `Espaço` | pular — de novo no ar faz o **pulo duplo** |
| `S` / `↓` | descer da plataforma em que está |
| `Shift` / `K` | **investida** (rajada rápida com recarga) |
| `Esc` | pausar / voltar para a capa |
| `R` | recomeçar a fase |
| `F2` | tela de controles |

Na capa, qualquer clique ou tecla começa o jogo, com um fade para preto.

## O jogo em uma frase

Você atravessa um chão reto, sem buraco e sem plataforma, pulando as serras de
**espinhos** que explodem o pug em terra, junta a **chave** e chega à **porta de
saída**. Sem a chave a porta é sólida e barra o caminho; com a chave ela abre e a
fase é vencida.

## Onde começa

- [Estrutura de arquivos](./estrutura.md) — o que mora onde
- [Classes e herança](./classes.md) — a hierarquia inteira
- [Física e regras](./fisica.md) — o que faz o personagem "sentir bem"
- [Renderização](./renderizacao.md) — como o pixel art é produzido
- [Nível](./niveis.md) — o mapa e o fim de fase
- [Decisões e armadilhas](./decisoes.md) — os bugs que jáagdaram este código
