import sys
import time
import pygame
from config import *
from objetos_jogo import FaseLabirinto, FaseParkour


CORACAO_MATRIZ = [
    " 11   11 ",
    "1221 1221",
    "122212221",
    "122222221",
    " 1222221 ",
    "  12221  ",
    "   121   ",
    "    1    ",
]


def desenhar_coracao_pixel(tela, x, y, cheio=True, tam_px=3):
    cor_borda = (0, 0, 0) if cheio else (80, 80, 80)
    cor_miolo = (220, 20, 40) if cheio else (15, 15, 15)

    for linha_idx, linha in enumerate(CORACAO_MATRIZ):
        for col_idx, char in enumerate(linha):
            if char == "1":
                pygame.draw.rect(tela, cor_borda, (x + col_idx * tam_px, y + linha_idx * tam_px, tam_px, tam_px))
            elif char == "2":
                pygame.draw.rect(tela, cor_miolo, (x + col_idx * tam_px, y + linha_idx * tam_px, tam_px, tam_px))


def renderizar_texto_central(tela, texto, fonte, cor, x, y):
    surf = fonte.render(texto, True, cor)
    rect = surf.get_rect(center=(x, y))
    tela.blit(surf, rect)


def main():
    pygame.init()
    pygame.key.set_repeat(200, 120)

    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Lorenzo Magnus - Em Busca da Saída")
    clock = pygame.time.Clock()

    fonte_pequena = pygame.font.SysFont("consolas", 20, bold=True)
    fonte_media = pygame.font.SysFont("consolas", 28, bold=True)
    fonte_grande = pygame.font.SysFont("consolas", 48, bold=True)

    labirinto = FaseLabirinto()
    parkour = FaseParkour()

    btn_facil = pygame.Rect(LARGURA // 2 - 140, 250, 280, 60)
    btn_media = pygame.Rect(LARGURA // 2 - 140, 330, 280, 60)
    btn_dificil = pygame.Rect(LARGURA // 2 - 140, 410, 280, 60)

    estado = "MENU_NOME"
    nome_jogador = ""
    dificuldade_atual = ""
    dinheiro = 0
    motivo_game_over = "VOCÊ PERDEU!"
    intervalo_inimigo = 500
    tempo_ultimo_mov_inimigo = 0
    tempo_inicio_contagem = 0

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
                if estado == "LABIRINTO":
                    if evento.key in [pygame.K_w, pygame.K_UP]:
                        labirinto.mover_jogador(0, -1)
                    elif evento.key in [pygame.K_s, pygame.K_DOWN]:
                        labirinto.mover_jogador(0, 1)
                    elif evento.key in [pygame.K_a, pygame.K_LEFT]:
                        labirinto.mover_jogador(-1, 0)
                    elif evento.key in [pygame.K_d, pygame.K_RIGHT]:
                        labirinto.mover_jogador(1, 0)

                elif estado == "MENU_NOME":
                    if evento.key == pygame.K_RETURN and len(nome_jogador) > 0:
                        estado = "MENU_DIFICULDADE"
                    elif evento.key == pygame.K_BACKSPACE:
                        nome_jogador = nome_jogador[:-1]
                    elif len(nome_jogador) < 12 and evento.unicode.isprintable():
                        nome_jogador += evento.unicode

                elif estado == "GAME_OVER":
                    if evento.key in [pygame.K_RETURN, pygame.K_SPACE]:
                        estado = "MENU_DIFICULDADE"

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

            for btn, nome, cor, vel_ms in [
                (btn_facil, "Fácil (2:00)", VERDE, 500),
                (btn_media, "Média (2:30)", AMARELO, 250),
                (btn_dificil, "Difícil (3:15)", VERMELHO, 167)
            ]:
                if btn.collidepoint(mouse_pos):
                    pygame.draw.rect(tela, BRANCO, btn.inflate(6, 6), border_radius=10)
                    if clique:
                        dificuldade_atual = nome.split(" ")[0]
                        intervalo_inimigo = vel_ms
                        dinheiro = 0
                        labirinto.resetar()
                        parkour.resetar(dificuldade_atual)
                        estado = "CONTAGEM"
                        tempo_inicio_contagem = time.time()

                pygame.draw.rect(tela, cor, btn, border_radius=10)
                renderizar_texto_central(tela, nome, fonte_pequena, PRETO, btn.centerx, btn.centery)

        elif estado == "CONTAGEM":
            restante = 3 - int(time.time() - tempo_inicio_contagem)
            labirinto.desenhar(tela)

            overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            tela.blit(overlay, (0, 0))

            if restante > 0:
                renderizar_texto_central(tela, "PREPARE-SE!", fonte_media, AMARELO, LARGURA // 2, ALTURA // 2 - 50)
                renderizar_texto_central(tela, str(restante), fonte_grande, BRANCO, LARGURA // 2, ALTURA // 2 + 20)
            else:
                estado = "LABIRINTO"
                tempo_ultimo_mov_inimigo = pygame.time.get_ticks()

        elif estado == "LABIRINTO":
            tempo_atual = pygame.time.get_ticks()

            ganho = labirinto.checar_dinheiro()
            if ganho > 0:
                dinheiro += ganho

            if tempo_atual - tempo_ultimo_mov_inimigo > intervalo_inimigo:
                labirinto.mover_inimigo()
                tempo_ultimo_mov_inimigo = tempo_atual

            labirinto.desenhar(tela)
            tela.blit(fonte_pequena.render("FUJA ATÉ A SAÍDA!", True, BRANCO), (10, 10))
            tela.blit(fonte_pequena.render(f"Caixa: R$ {dinheiro}", True, VERDE), (LARGURA - 180, 10))

            if labirinto.checar_morte():
                motivo_game_over = "VOCÊ FOI PEGO!"
                estado = "GAME_OVER"
            elif labirinto.checar_saida():
                parkour.resetar(dificuldade_atual)
                estado = "PARKOUR"

        elif estado == "PARKOUR":
            tempo_atual_ms = pygame.time.get_ticks()
            teclas = pygame.key.get_pressed()

            ganho = parkour.atualizar(teclas, tempo_atual_ms)
            if ganho > 0:
                dinheiro += ganho

            parkour.desenhar(tela, tempo_atual_ms)

            for i in range(3):
                desenhar_coracao_pixel(tela, 20 + i * 36, 16, cheio=(i < parkour.vidas), tam_px=3)

            tela.blit(fonte_pequena.render(f"Caixa: R$ {dinheiro}", True, VERDE), (LARGURA - 180, 18))
            renderizar_texto_central(tela, "A/D: Correr | W/ESPAÇO: Pular", fonte_pequena, BRANCO, LARGURA // 2, 52)

            if parkour.checar_morte():
                motivo_game_over = "VOCÊ PERDEU!"
                estado = "GAME_OVER"
            elif parkour.checar_saida():
                estado = "MENU_DIFICULDADE"

        elif estado == "GAME_OVER":
            renderizar_texto_central(tela, motivo_game_over, fonte_grande, VERMELHO, LARGURA // 2, ALTURA // 2 - 40)
            renderizar_texto_central(tela, "Pressione ENTER para tentar novamente", fonte_pequena, CINZA, LARGURA // 2, ALTURA // 2 + 40)

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
