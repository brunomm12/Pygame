
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
while True:
        tela.fill(PRETO)
        mouse_pos = pygame.mouse.get_pos()
        clique = False

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                clique = True

            if evento.type == pygame.KEYDOWN:
                if estado == "MENU_NOME":
                    if evento.key == pygame.K_RETURN and len(nome_jogador) > 0:
                        estado = "MENU_DIFICULDADE"
                    elif evento.key == pygame.K_BACKSPACE:
                        nome_jogador = nome_jogador[:-1]
                    elif len(nome_jogador) < 12 and evento.unicode.isprintable():
                        nome_jogador += evento.unicode

        if estado == "MENU_NOME":
            renderizar_texto_central(tela, "LORENZO MAGNUS", fonte_grande, BRANCO, LARGURA // 2, 120)
            renderizar_texto_central(tela, "EM BUSCA DA SAÍDA", fonte_media, AMARELO, LARGURA // 2, 175)
            renderizar_texto_central(tela, "Digite seu Nickname:", fonte_media, CINZA, LARGURA // 2, 250)

            caixa_texto = pygame.Rect(LARGURA // 2 - 150, 300, 300, 50)
            pygame.draw.rect(tela, BRANCO, caixa_texto, 2, border_radius=8)
            renderizar_texto_central(tela, nome_jogador, fonte_media, AMARELO, LARGURA // 2, 325)

            if len(nome_jogador) > 0:
                renderizar_texto_central(tela, "Pressione ENTER para continuar", fonte_pequena, VERDE, LARGURA // 2, 400)

        elif estado == "MENU_DIFICULDADE":
            renderizar_texto_central(tela, f"Jogador: {nome_jogador}", fonte_media, BRANCO, LARGURA // 2, 120)
            renderizar_texto_central(tela, "Escolha a Dificuldade:", fonte_media, CINZA, LARGURA // 2, 180)

            for btn, nome, cor in [
                (btn_facil, "Fácil (2:00)", VERDE),
                (btn_media, "Média (2:30)", AMARELO),
                (btn_dificil, "Difícil (3:15)", VERMELHO)
            ]:
                if btn.collidepoint(mouse_pos):
                    pygame.draw.rect(tela, BRANCO, btn.inflate(6, 6), border_radius=10)
                    if clique:
                        dificuldade_atual = nome.split(" ")[0]
                        print(f"Dificuldade selecionada: {dificuldade_atual}")

                pygame.draw.rect(tela, cor, btn, border_radius=10)
                renderizar_texto_central(tela, nome, fonte_pequena, PRETO, btn.centerx, btn.centery)

        pygame.display.flip()
        clock.tick(FPS)
