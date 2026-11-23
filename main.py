import json
import os
import sys
import time
import pygame
from config import *
from objetos_jogo import Porta, LojaUpgrades, FaseLabirinto, FaseParkour


class FontePixel:
    """Renderiza textos com visual pixelado retrô sem depender de arquivos .ttf."""

    def __init__(self, tamanho_base, escala=2):
        """Configura o tamanho base da fonte monoespaçada e o fator de ampliação."""
        self.fonte = pygame.font.SysFont("consolas", tamanho_base, bold=True)
        self.escala = escala

    def render(self, texto, antialias, cor):
        """Renderiza o texto sem suavização e amplia preservando os pixels quadrados."""
        surf = self.fonte.render(str(texto), False, cor)
        larg = surf.get_width() * self.escala
        alt = surf.get_height() * self.escala
        return pygame.transform.scale(surf, (larg, alt))


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
    """Desenha um coração em pixel art (vermelho se cheio, preto se perdido)."""
    cor_borda = (0, 0, 0) if cheio else (80, 80, 80)
    cor_miolo = (220, 20, 40) if cheio else (15, 15, 15)

    for linha_idx, linha in enumerate(CORACAO_MATRIZ):
        for col_idx, char in enumerate(linha):
            if char == "1":
                pygame.draw.rect(tela, cor_borda, (x + col_idx * tam_px, y + linha_idx * tam_px, tam_px, tam_px))
            elif char == "2":
                pygame.draw.rect(tela, cor_miolo, (x + col_idx * tam_px, y + linha_idx * tam_px, tam_px, tam_px))


def carregar_fundo(nomes_possiveis):
    """Tenta carregar uma imagem de fundo da lista e redimensiona para a tela."""
    for nome_arq in nomes_possiveis:
        try:
            img = pygame.image.load(nome_arq).convert()
            return pygame.transform.scale(img, (LARGURA, ALTURA))
        except (FileNotFoundError, pygame.error):
            continue
    return None


def carregar_som(caminho, volume=1.0):
    """Carrega um efeito sonoro com tratamento de erro e ajuste de volume."""
    try:
        som = pygame.mixer.Sound(caminho)
        som.set_volume(volume)
        return som
    except (FileNotFoundError, pygame.error):
        return None


def formatar_timer(segundos):
    """Formata segundos no padrão MM:SS para exibição no HUD."""
    segundos = max(0, int(segundos))
    minutos = segundos // 60
    segs = segundos % 60
    return f"{minutos:02d}:{segs:02d}"


def formatar_tempo_ranking(segundos):
    """Formata o tempo total gasto no padrão MM:SS.d para o Hall da Fama."""
    minutos = int(segundos // 60)
    segs = segundos % 60
    return f"{minutos:02d}:{segs:04.1f}"


def carregar_tierlist():
    """Lê o arquivo JSON do ranking, retornando lista vazia se inexistente ou corrompido."""
    if os.path.exists(ARQUIVO_TIERLIST):
        try:
            with open(ARQUIVO_TIERLIST, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []


def salvar_tierlist(nome, tempo, dificuldade):
    """Registra uma nova conclusão no ranking ordenado por menor tempo."""
    rank = carregar_tierlist()
    rank.append({"nome": nome, "tempo": round(tempo, 3), "dificuldade": dificuldade})
    rank = sorted(rank, key=lambda x: x["tempo"])
    with open(ARQUIVO_TIERLIST, "w", encoding="utf-8") as f:
        json.dump(rank, f)


def renderizar_texto_central(tela, texto, fonte, cor, x, y):
    """Renderiza e desenha um texto centralizado na coordenada (x, y)."""
    surf = fonte.render(texto, False, cor)
    rect = surf.get_rect(center=(x, y))
    tela.blit(surf, rect)


def main():
    """Inicializa o Pygame, carrega recursos e executa o loop principal do jogo."""
    pygame.init()
    pygame.key.set_repeat(200, 120)
    pygame.mixer.init()

    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Lorenzo Magnus - Em Busca da Saída")
    clock = pygame.time.Clock()

    fonte_pequena = FontePixel(9, escala=2)
    fonte_media = FontePixel(13, escala=2)
    fonte_grande = FontePixel(17, escala=3)

    # Efeitos sonoros e música de fundo
    som_hit = carregar_som("hit.wav", 1.0)
    som_compra = carregar_som("caixa.wav", 1.0)
    som_pulo = carregar_som("pulo.wav", 0.6)
    som_moeda = carregar_som("moeda.wav", 0.6)
    som_dano = carregar_som("dano.wav", 0.7)
    som_gameover = carregar_som("gameover.wav", 0.7)

    try:
        pygame.mixer.music.load("galaxy.mp3")
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
    except (FileNotFoundError, pygame.error):
        print("Aviso: galaxy.mp3 não encontrado na pasta do jogo.")

    try:
        img_hit = pygame.image.load("hit_efeito.png").convert_alpha()
        img_hit = pygame.transform.scale(img_hit, (50, 50))
    except (FileNotFoundError, pygame.error):
        img_hit = None

    # Telas de fundo (Início, Modos e Fim)
    img_inicio = carregar_fundo(["inicio.png", "inicio.jpg", "inicio.jpeg"])
    img_modos = carregar_fundo(["modos.png", "modos.jpg", "modos.jpeg"])
    img_fim = carregar_fundo(["fim.png", "fim.jpg", "fim.jpeg"])

    porta = Porta(vida_maxima=2000)
    loja = LojaUpgrades()
    labirinto = FaseLabirinto()
    parkour = FaseParkour()

    btn_facil = pygame.Rect(40, 440, 215, 65)
    btn_media = pygame.Rect(292, 440, 215, 65)
    btn_dificil = pygame.Rect(545, 440, 215, 65)

    estado = "MENU_NOME"
    nome_jogador = ""
    dificuldade_atual = ""
    dinheiro = 0
    dano_por_hit = 1
    tempo_inicio = 0
    tempo_limite = 120
    tempo_final = 0
    motivo_game_over = "VOCÊ PERDEU!"

    tempo_ultimo_mov_inimigo = 0
    intervalo_inimigo = 500
    tempo_inicio_contagem = 0
    efeitos_hit = []
    tem_auto_clique = False
    tempo_ultimo_auto_clique = 0

    def acionar_game_over(motivo):
        """Transiciona para o estado de Game Over e dispara o efeito sonoro."""
        nonlocal estado, motivo_game_over
        motivo_game_over = motivo
        estado = "GAME_OVER"
        if som_gameover:
            som_gameover.play()

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

                elif estado == "TIERLIST":
                    if evento.key in [pygame.K_RETURN, pygame.K_SPACE]:
                        estado = "MENU_NOME"
                        nome_jogador = ""

                elif estado == "GAME_OVER":
                    if evento.key in [pygame.K_RETURN, pygame.K_SPACE]:
                        estado = "MENU_DIFICULDADE"

        # MÁQUINA DE ESTADOS
        if estado == "MENU_NOME":
            if img_inicio:
                tela.blit(img_inicio, (0, 0))
                overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 110))
                tela.blit(overlay, (0, 0))

            renderizar_texto_central(tela, "LORENZO MAGNUS", fonte_grande, BRANCO, LARGURA // 2, 120)
            renderizar_texto_central(tela, "EM BUSCA DA SAÍDA", fonte_media, AMARELO, LARGURA // 2, 175)
            renderizar_texto_central(tela, "Digite seu Nickname:", fonte_media, BRANCO, LARGURA // 2, 260)

            caixa_texto = pygame.Rect(LARGURA // 2 - 150, 300, 300, 50)
            fundo_caixa = pygame.Surface((300, 50), pygame.SRCALPHA)
            fundo_caixa.fill((0, 0, 0, 180))
            tela.blit(fundo_caixa, caixa_texto.topleft)
            pygame.draw.rect(tela, BRANCO, caixa_texto, 2, border_radius=8)
            renderizar_texto_central(tela, nome_jogador, fonte_media, AMARELO, LARGURA // 2, 325)

            if len(nome_jogador) > 0:
                renderizar_texto_central(tela, "Pressione ENTER para continuar", fonte_pequena, VERDE, LARGURA // 2, 400)

        elif estado == "MENU_DIFICULDADE":
            if img_modos:
                tela.blit(img_modos, (0, 0))
                overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 85))
                tela.blit(overlay, (0, 0))

            renderizar_texto_central(tela, f"Jogador: {nome_jogador}", fonte_media, BRANCO, LARGURA // 2, 65)
            renderizar_texto_central(tela, "Escolha sua Entrada:", fonte_media, AMARELO, LARGURA // 2, 115)

            for btn, nome, hp, cor, vel_ms, limite_seg in [
                (btn_facil, "Fácil (2:00)", 500, VERDE, 500, 120),
                (btn_media, "Média (2:30)", 2000, AMARELO, 250, 150),
                (btn_dificil, "Difícil (3:15)", 10000, VERMELHO, 167, 195)
            ]:
                if btn.collidepoint(mouse_pos):
                    pygame.draw.rect(tela, BRANCO, btn.inflate(6, 6), border_radius=10)
                    if clique:
                        dificuldade_atual = nome.split(" ")[0]
                        intervalo_inimigo = vel_ms
                        tempo_limite = limite_seg
                        porta.configurar_dificuldade(hp)
                        dinheiro = 0
                        dano_por_hit = 1
                        loja.resetar_precos()
                        efeitos_hit = []
                        tem_auto_clique = False

                        labirinto.resetar()
                        parkour.resetar(dificuldade_atual)
                        estado = "CONTAGEM"
                        tempo_inicio_contagem = time.time()

                pygame.draw.rect(tela, cor, btn, border_radius=10)
                pygame.draw.rect(tela, PRETO, btn, 3, border_radius=10)
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
                tempo_inicio = time.time()
                tempo_ultimo_mov_inimigo = pygame.time.get_ticks()

        elif estado == "LABIRINTO":
            tempo_atual = pygame.time.get_ticks()
            tempo_decorrido = time.time() - tempo_inicio
            tempo_restante = tempo_limite - tempo_decorrido

            ganho = labirinto.checar_dinheiro()
            if ganho > 0:
                dinheiro += ganho
                if som_moeda:
                    som_moeda.play()

            if tempo_atual - tempo_ultimo_mov_inimigo > intervalo_inimigo:
                labirinto.mover_inimigo()
                tempo_ultimo_mov_inimigo = tempo_atual

            labirinto.desenhar(tela)

            cor_timer = VERMELHO if tempo_restante <= 30 else AMARELO
            tela.blit(fonte_pequena.render("FUJA ATÉ A SAÍDA!", False, BRANCO), (10, 10))
            renderizar_texto_central(tela, formatar_timer(tempo_restante), fonte_media, cor_timer, LARGURA // 2, 20)
            tela.blit(fonte_pequena.render(f"Caixa: R$ {dinheiro}", False, VERDE), (LARGURA - 180, 10))

            if tempo_restante <= 0:
                acionar_game_over("TEMPO ESGOTADO!")
            elif labirinto.checar_morte():
                acionar_game_over("VOCÊ FOI PEGO!")
            elif labirinto.checar_saida():
                parkour.resetar(dificuldade_atual)
                estado = "PARKOUR"

        elif estado == "PARKOUR":
            tempo_atual_ms = pygame.time.get_ticks()
            tempo_decorrido = time.time() - tempo_inicio
            tempo_restante = tempo_limite - tempo_decorrido

            teclas = pygame.key.get_pressed()
            ganho = parkour.atualizar(teclas, tempo_atual_ms, som_pulo, som_dano)
            if ganho > 0:
                dinheiro += ganho
                if som_moeda:
                    som_moeda.play()

            parkour.desenhar(tela, tempo_atual_ms)

            for i in range(3):
                desenhar_coracao_pixel(tela, 20 + i * 36, 16, cheio=(i < parkour.vidas), tam_px=3)

            cor_timer = VERMELHO if tempo_restante <= 30 else AMARELO
            renderizar_texto_central(tela, formatar_timer(tempo_restante), fonte_media, cor_timer, LARGURA // 2, 24)
            tela.blit(fonte_pequena.render(f"Caixa: R$ {dinheiro}", False, VERDE), (LARGURA - 180, 18))
            renderizar_texto_central(tela, "A/D: Correr | W/ESPAÇO: Pular", fonte_pequena, BRANCO, LARGURA // 2, 52)

            if tempo_restante <= 0:
                acionar_game_over("TEMPO ESGOTADO!")
            elif parkour.checar_morte():
                acionar_game_over("VOCÊ PERDEU!")
            elif parkour.checar_saida():
                efeitos_hit = []
                estado = "JOGO"

        elif estado == "GAME_OVER":
            renderizar_texto_central(tela, motivo_game_over, fonte_grande, VERMELHO, LARGURA // 2, ALTURA // 2 - 40)
            renderizar_texto_central(tela, "Pressione ENTER para tentar novamente", fonte_pequena, CINZA, LARGURA // 2, ALTURA // 2 + 40)

        elif estado == "JOGO":
            tempo_decorrido = time.time() - tempo_inicio
            tempo_restante = tempo_limite - tempo_decorrido
            tempo_atual_ms = pygame.time.get_ticks()

            bateu_na_porta = False

            # Clique manual do jogador
            if porta.rect.collidepoint(mouse_pos) and clique:
                porta.receber_dano(dano_por_hit)
                dinheiro += dano_por_hit
                efeitos_hit.append((mouse_pos[0], mouse_pos[1], tempo_atual_ms))
                bateu_na_porta = True
                if som_hit:
                    som_hit.play()

            # Auto-Chute automático (10 cliques/s = a cada 100 ms)
            if tem_auto_clique and tempo_atual_ms - tempo_ultimo_auto_clique >= 100:
                porta.receber_dano(dano_por_hit)
                dinheiro += dano_por_hit
                efeitos_hit.append((porta.rect.centerx, porta.rect.centery, tempo_atual_ms))
                tempo_ultimo_auto_clique = tempo_atual_ms
                bateu_na_porta = True
                if som_hit:
                    som_hit.play()

            if not bateu_na_porta:
                porta.resetar_impacto()

            if tempo_restante <= 0:
                acionar_game_over("TEMPO ESGOTADO!")
            elif porta.vida_atual <= 0:
                tempo_final = tempo_decorrido
                salvar_tierlist(nome_jogador, tempo_final, dificuldade_atual)
                estado = "TIERLIST"

            porta.desenhar(tela)

            cor_timer = VERMELHO if tempo_restante <= 30 else AMARELO
            tela.blit(fonte_pequena.render(f"Jogador: {nome_jogador}", False, BRANCO), (20, 20))
            tela.blit(fonte_pequena.render(f"Caixa: R$ {dinheiro}", False, VERDE), (20, 50))
            tela.blit(fonte_pequena.render(f"Dano/Hit: {dano_por_hit}", False, AMARELO), (20, 80))
            renderizar_texto_central(tela, formatar_timer(tempo_restante), fonte_media, cor_timer, LARGURA - 90, 35)

            efeitos_hit = [e for e in efeitos_hit if tempo_atual_ms - e[2] < 150]
            if img_hit:
                for ex, ey, _ in efeitos_hit:
                    rect_hit = img_hit.get_rect(center=(ex, ey))
                    tela.blit(img_hit, rect_hit)

            dinheiro, dano_por_hit, tem_auto_clique = loja.tentar_comprar(
                mouse_pos, clique, dinheiro, dano_por_hit, tem_auto_clique, som_compra
            )
            loja.desenhar(tela, mouse_pos, dinheiro, fonte_pequena)

        elif estado == "TIERLIST":
            if img_fim:
                tela.blit(img_fim, (0, 0))
                overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 110))
                tela.blit(overlay, (0, 0))

            renderizar_texto_central(tela, "HALL DA FAMA", fonte_grande, BRANCO, LARGURA // 2, 65)
            rank = carregar_tierlist()

            rank_facil = [r for r in rank if r.get('dificuldade', 'Média') == 'Fácil'][:5]
            rank_media = [r for r in rank if r.get('dificuldade', 'Média') == 'Média'][:5]
            rank_dificil = [r for r in rank if r.get('dificuldade', 'Média') == 'Difícil'][:5]

            renderizar_texto_central(tela, "FÁCIL", fonte_media, VERDE, 165, 145)
            renderizar_texto_central(tela, "MÉDIA", fonte_media, AMARELO, LARGURA // 2, 145)
            renderizar_texto_central(tela, "DIFÍCIL", fonte_media, VERMELHO, LARGURA - 165, 145)

            colunas = [(rank_facil, 165), (rank_media, LARGURA // 2), (rank_dificil, LARGURA - 165)]

            for lista, x_pos in colunas:
                y_pos = 195
                for i, registro in enumerate(lista):
                    tempo_fmt = formatar_tempo_ranking(registro['tempo'])
                    texto_rank = f"{i + 1}º {registro['nome']} ({tempo_fmt})"

                    eh_run_atual = (
                        registro['nome'] == nome_jogador
                        and registro['tempo'] == round(tempo_final, 3)
                        and registro.get('dificuldade', 'Média') == dificuldade_atual
                    )

                    cor = VERDE if eh_run_atual else BRANCO
                    renderizar_texto_central(tela, texto_rank, fonte_pequena, cor, x_pos, y_pos)
                    y_pos += 35

            renderizar_texto_central(tela, "Pressione ENTER para jogar novamente", fonte_pequena, BRANCO, LARGURA // 2, 565)

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
