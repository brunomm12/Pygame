
import sys
import pygame
from config import *


def renderizar_texto_central(tela, texto, fonte, cor, x, y):
    surf = fonte.render(texto, True, cor)
    rect = surf.get_rect(center=(x, y))
    tela.blit(surf, rect)


def main():
    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Lorenzo Magnus - Em Busca da Saída")
    clock = pygame.time.Clock()

    fonte_pequena = pygame.font.SysFont("consolas", 20, bold=True)
    fonte_media = pygame.font.SysFont("consolas", 28, bold=True)
    fonte_grande = pygame.font.SysFont("consolas", 48, bold=T    rue)

    btn_facil = pygame.Rect(LARGURA // 2 - 140, 250, 280, 60)
    btn_media = pygame.Rect(LARGURA // 2 - 140, 330, 280, 60)
    btn_dificil = pygame.Rect(LARGURA // 2 - 140, 410, 280, 60)

    estado = "MENU_NOME"
    nome_jogador = ""
    dificuldade_atual = ""



if __name__ == "__main__":
    main()
