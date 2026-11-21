import random
import pygame
from config import *
from collections import deque

class Porta:
    def _init_(self, vida_maxima):
        self.vida_maxima = vida_maxima
        self.vida_atual = vida_maxima
        self.rect_base = pygame.Rect(LARGURA // 2 - 100, 130, 200, 310)
        self.rect = self.rect_base.copy()
        self.tremer_x = 0
        self.tremer_y = 0

    def configurar_dificuldade(self, nova_vida_maxima):
        self.vida_maxima = nova_vida_maxima
        self.vida_atual = nova_vida_maxima

    def receber_dano(self, dano):
        self.vida_atual = max(0, self.vida_atual - dano)
        self.rect = self.rect_base.inflate(-15, -15)
        self.tremer_x = random.randint(-6, 6)
        self.tremer_y = random.randint(-6, 6)

    def resetar_impacto(self):
        self.rect = self.rect_base.copy()
        self.tremer_x = 0
        self.tremer_y = 0

    def desenhar(self, tela):
        rect_desenho = self.rect.move(self.tremer_x, self.tremer_y)
        pygame.draw.rect(tela, MARROM, rect_desenho, border_radius=5)
        pygame.draw.circle(tela, BRANCO, (rect_desenho.right - 25, rect_desenho.centery), 10)

        largura_barra = 400
        pct_vida = max(self.vida_atual / self.vida_maxima, 0)
        barra_x = LARGURA // 2 - largura_barra // 2
        pygame.draw.rect(tela, PRETO, (barra_x - 3, 107, largura_barra + 6, 31), border_radius=6)
        pygame.draw.rect(tela, VERMELHO, (barra_x, 110, largura_barra, 25), border_radius=5)
        pygame.draw.rect(tela, VERDE, (barra_x, 110, largura_barra * pct_vida, 25), border_radius=5)


class LojaUpgrades:
    def _init_(self):
        self.itens = [
            {"nome": "Tênis Novo", "custo": 10, "dano": 1, "tipo": "dano", "rect": pygame.Rect(20, 500, 175, 70)},
            {"nome": "Soco Inglês", "custo": 50, "dano": 5, "tipo": "dano", "rect": pygame.Rect(215, 500, 175, 70)},
            {"nome": "Pé de Cabra", "custo": 200, "dano": 25, "tipo": "dano", "rect": pygame.Rect(410, 500, 175, 70)},
            {"nome": "Auto-Chute", "custo": 50, "dano": 0, "tipo": "auto", "comprado": False, "rect": pygame.Rect(605, 500, 175, 70)}
        ]

    def resetar_precos(self):
        self.itens[0]["custo"] = 10
        self.itens[1]["custo"] = 50
        self.itens[2]["custo"] = 200
        self.itens[3]["comprado"] = False

    def tentar_comprar(self, mouse_pos, clique, dinheiro, dano_atual, tem_auto_clique):
        for item in self.itens:
            if item["rect"].collidepoint(mouse_pos) and clique:
                if item["tipo"] == "auto":
                    if not item["comprado"] and dinheiro >= item["custo"]:
                        dinheiro -= item["custo"]
                        item["comprado"] = True
                        tem_auto_clique = True
                elif dinheiro >= item["custo"]:
                    dinheiro -= item["custo"]
                    dano_atual += item["dano"]
                    item["custo"] = int(item["custo"] * 1.5)
        return dinheiro, dano_atual, tem_auto_clique

    def desenhar(self, tela, mouse_pos, dinheiro, fonte_pequena):
        for item in self.itens:
            if item["tipo"] == "auto" and item["comprado"]:
                cor_botao = (0, 160, 0)
                texto_info = "ATIVADO (10/s)"
            else:
                pode_comprar = dinheiro >= item["custo"]
                cor_botao = AZUL if pode_comprar else CINZA
                texto_info = f"R$ {item['custo']} | 10/seg" if item["tipo"] == "auto" else f"R$ {item['custo']} | +{item['dano']}"

            if item["rect"].collidepoint(mouse_pos):
                pygame.draw.rect(tela, BRANCO, item["rect"].inflate(4, 4), border_radius=10)

            pygame.draw.rect(tela, cor_botao, item["rect"], border_radius=10)

            surf_nome = fonte_pequena.render(item["nome"], False, BRANCO)
            surf_info = fonte_pequena.render(texto_info, False, AMARELO)
            tela.blit(surf_nome, (item["rect"].centerx - surf_nome.get_width() // 2, item["rect"].centery - 15))
            tela.blit(surf_info, (item["rect"].centerx - surf_info.get_width() // 2, item["rect"].centery + 5))
            tela.blit(surf_info, (item["rect"].centerx - surf_info.get_width() // 2, item["rect"].centery + 5)) 


        class FaseLabirinto:
    def __init__(self):
        self.tamanho_bloco = 40
        self.matriz_mapa = [
            "WWWWWWWWWWWWWWWWWWWW",
            "W       W   W      W",
            "W WWWWW W W W WWWW W",
            "W     W   W   W    W",
            "WWWWW WWWWWWWWW WWWW",
            "W           W      W",
            "W W WWWWWWW W WWWW W",
            "W W       W W W    W",
            "W WWWWWWW W W W WWWW",
            "W       W W   W    W",
            "W WWWWW W WWWWWWWW W",
            "W     W W        W W",
            "WWWWW W WWWWWWWW W W",
            "W       W        E W",
            "WWWWWWWWWWWWWWWWWWWW"
        ]

        self.cor_jogador = (50, 150, 255)
        self.cor_inimigo = (255, 0, 0)

        self.sprites = {'baixo': [], 'cima': [], 'esquerda': [], 'direita': []}
        self.direcao_atual = 'baixo'
        self.frame_atual = 0
        self.tem_sprite = self._carregar_spritesheet("spritesheet.png", self.sprites, colunas_totais=8)

        self.sprites_inimigo = {'baixo': [], 'cima': [], 'esquerda': [], 'direita': []}
        self.direcao_inimigo = 'baixo'
        self.frame_inimigo = 0
        self.tem_sprite_inimigo = self._carregar_spritesheet("inimigo_spritesheet.png", self.sprites_inimigo, colunas_totais=8)

        try:
            img_din = pygame.image.load("dinheiro.png").convert_alpha()
            borda = img_din.get_bounding_rect()
            if borda.width > 0 and borda.height > 0:
                img_din = img_din.subsurface(borda)
            self.img_dinheiro = pygame.transform.scale(img_din, (38, 24))
        except (FileNotFoundError, pygame.error):
            self.img_dinheiro = None

        self.resetar()

    def _carregar_spritesheet(self, caminho, dicionario_destino, colunas_totais=8, linhas_totais=4):
        try:
            sheet = pygame.image.load(caminho).convert_alpha()
            largura_sheet, altura_sheet = sheet.get_size()
            largura_frame = largura_sheet // colunas_totais
            altura_frame = altura_sheet // linhas_totais

            direcoes = ['baixo', 'cima', 'esquerda', 'direita']

            for linha in range(linhas_totais):
                for coluna in range(4):
                    rect = pygame.Rect(coluna * largura_frame, linha * altura_frame, largura_frame, altura_frame)
                    img_cortada = sheet.subsurface(rect)
                    img_redimensionada = pygame.transform.scale(img_cortada, (self.tamanho_bloco, self.tamanho_bloco))
                    dicionario_destino[direcoes[linha]].append(img_redimensionada)
            return True
        except (FileNotFoundError, pygame.error):
            return False



    def resetar(self):
        self.pos_x = 1
        self.pos_y = 1
        self.inimigo_x = 9
        self.inimigo_y = 7
        self.direcao_atual = 'baixo'
        self.direcao_inimigo = 'baixo'
        self.dinheiros = [(18, 1), (5, 3), (1, 9), (16, 11), (1, 13)]

    def mover_jogador(self, dx, dy):
        if dx == 1:
            self.direcao_atual = 'direita'
        elif dx == -1:
            self.direcao_atual = 'esquerda'
        elif dy == 1:
            self.direcao_atual = 'baixo'
        elif dy == -1:
            self.direcao_atual = 'cima'

        self.frame_atual = (self.frame_atual + 1) % 4

        novo_x = self.pos_x + dx
        novo_y = self.pos_y + dy
        if self.matriz_mapa[novo_y][novo_x] != 'W':
            self.pos_x = novo_x
            self.pos_y = novo_y

    def checar_dinheiro(self):
        pos = (self.pos_x, self.pos_y)
        if pos in self.dinheiros:
            self.dinheiros.remove(pos)
            return 5
        return 0

    def mover_inimigo(self):
        if self.inimigo_x == self.pos_x and self.inimigo_y == self.pos_y:
            return

        fila = deque([(self.inimigo_x, self.inimigo_y, [])])
        visitados = {(self.inimigo_x, self.inimigo_y)}
        movimentos = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        caminho_escolhido = []

        while fila:
            atual_x, atual_y, caminho = fila.popleft()

            if atual_x == self.pos_x and atual_y == self.pos_y:
                caminho_escolhido = caminho
                break

            for dx, dy in movimentos:
                nx, ny = atual_x + dx, atual_y + dy
                if 0 <= ny < len(self.matriz_mapa) and 0 <= nx < len(self.matriz_mapa[0]):
                    if self.matriz_mapa[ny][nx] != 'W' and (nx, ny) not in visitados:
                        visitados.add((nx, ny))
                        fila.append((nx, ny, caminho + [(nx, ny)]))

        if caminho_escolhido:
            prox_x, prox_y = caminho_escolhido[0]
            dx = prox_x - self.inimigo_x
            dy = prox_y - self.inimigo_y

            if dx == 1:
                self.direcao_inimigo = 'direita'
            elif dx == -1:
                self.direcao_inimigo = 'esquerda'
            elif dy == 1:
                self.direcao_inimigo = 'baixo'
            elif dy == -1:
                self.direcao_inimigo = 'cima'

            self.frame_inimigo = (self.frame_inimigo + 1) % 4
            self.inimigo_x, self.inimigo_y = prox_x, prox_y





    def checar_morte(self):
        return self.pos_x == self.inimigo_x and self.pos_y == self.inimigo_y

    def checar_saida(self):
        return self.matriz_mapa[self.pos_y][self.pos_x] == 'E'

    def desenhar(self, tela):
        for linha_idx, linha in enumerate(self.matriz_mapa):
            for col_idx, celula in enumerate(linha):
                x = col_idx * self.tamanho_bloco
                y = linha_idx * self.tamanho_bloco
                rect = pygame.Rect(x, y, self.tamanho_bloco, self.tamanho_bloco)

                if celula == 'W':
                    pygame.draw.rect(tela, (80, 85, 90), rect)
                    pygame.draw.rect(tela, (40, 45, 50), rect, 2)
                    pygame.draw.line(tela, (40, 45, 50), (x, y + 20), (x + 40, y + 20), 2)
                    pygame.draw.line(tela, (40, 45, 50), (x + 20, y), (x + 20, y + 20), 2)
                elif celula == 'E':
                    pygame.draw.rect(tela, (139, 69, 19), rect)
                    pygame.draw.circle(tela, (255, 215, 0), (x + 10, y + 20), 4)

        for dx, dy in self.dinheiros:
            if self.img_dinheiro:
                centro_x = dx * self.tamanho_bloco + self.tamanho_bloco // 2
                centro_y = dy * self.tamanho_bloco + self.tamanho_bloco // 2
                rect_din = self.img_dinheiro.get_rect(center=(centro_x, centro_y))
                tela.blit(self.img_dinheiro, rect_din)
            else:
                px = dx * self.tamanho_bloco + 5
                py = dy * self.tamanho_bloco + 10
                pygame.draw.rect(tela, (0, 200, 0), (px, py, 30, 18), border_radius=3)

        if self.tem_sprite_inimigo:
            img_inimigo = self.sprites_inimigo[self.direcao_inimigo][self.frame_inimigo]
            tela.blit(img_inimigo, (self.inimigo_x * self.tamanho_bloco, self.inimigo_y * self.tamanho_bloco))
        else:
            rect_inimigo = pygame.Rect(self.inimigo_x * self.tamanho_bloco, self.inimigo_y * self.tamanho_bloco, self.tamanho_bloco, self.tamanho_bloco)
            pygame.draw.rect(tela, self.cor_inimigo, rect_inimigo)

        if self.tem_sprite:
            img_jogador = self.sprites[self.direcao_atual][self.frame_atual]

class FaseParkour:
    def __init__(self):
        self.largura_mapa = 3200
        self.tamanho_sprite = 44
        self.gravidade = 0.7
        self.forca_pulo = -14
        self.vel_jogador = 5

        self.img_fundo = None
        for nome in ["fundo_parkour.png", "fundo_parkour.jpg", "fundo_parkour.jpeg"]:
            try:
                img = pygame.image.load(nome).convert()
                self.img_fundo = pygame.transform.scale(img, (LARGURA, ALTURA))
                break
            except (FileNotFoundError, pygame.error):
                continue

        self.sprites_jogador = {'esquerda': [], 'direita': []}
        self.tem_sprite_jogador = self._carregar_sprites_laterais("spritesheet.png", self.sprites_jogador)

        self.sprites_inimigo = {'esquerda': [], 'direita': []}
        self.tem_sprite_inimigo = self._carregar_sprites_laterais("inimigo_spritesheet.png", self.sprites_inimigo)

        try:
            img_din = pygame.image.load("dinheiro.png").convert_alpha()
            borda = img_din.get_bounding_rect()
            if borda.width > 0 and borda.height > 0:
                img_din = img_din.subsurface(borda)
            self.img_dinheiro = pygame.transform.scale(img_din, (36, 22))
        except (FileNotFoundError, pygame.error):
            self.img_dinheiro = None

        self.plataformas = [
            pygame.Rect(0, 500, 320, 100),
            pygame.Rect(420, 460, 220, 30),
            pygame.Rect(730, 400, 260, 30),
            pygame.Rect(1080, 480, 280, 120),
            pygame.Rect(1450, 420, 220, 30),
            pygame.Rect(1760, 350, 260, 30),
            pygame.Rect(2110, 450, 260, 150),
            pygame.Rect(2460, 390, 200, 30),
            pygame.Rect(2750, 460, 450, 140),
        ]

        self.porta_saida = pygame.Rect(3080, 370, 55, 90)
        self.resetar("Fácil")

    def _carregar_sprites_laterais(self, caminho, destino):
        try:
            sheet = pygame.image.load(caminho).convert_alpha()
            largura_sheet, altura_sheet = sheet.get_size()
            largura_frame = largura_sheet // 8
            altura_frame = altura_sheet // 4
            for linha, direcao in [(2, 'esquerda'), (3, 'direita')]:
                for coluna in range(4):
                    rect = pygame.Rect(coluna * largura_frame, linha * altura_frame, largura_frame, altura_frame)
                    img = pygame.transform.scale(sheet.subsurface(rect), (self.tamanho_sprite, self.tamanho_sprite))
                    destino[direcao].append(img)
            return True
        except (FileNotFoundError, pygame.error):
            return False

    def resetar(self, dificuldade="Fácil"):
        self.vidas = 3
        self.player_rect = pygame.Rect(60, 420, 34, 44)
        self.vel_y = 0
        self.no_chao = False
        self.direcao = 'direita'
        self.frame = 0
        self.contador_anim = 0
        self.invencivel_ate = 0
        self.camera_x = 0

        posicoes_dinheiro = [
            (250, 460), (520, 420), (850, 360), (1200, 440),
            (1550, 380), (1880, 310), (2230, 410), (2550, 350)
        ]
        self.dinheiros = [pygame.Rect(x, y, 36, 22) for x, y in posicoes_dinheiro]

        todas_inimigas = [
            (480, 416, 420, 606, 2),
            (780, 356, 730, 956, 2),
            (1130, 436, 1080, 1326, 2.5),
            (1240, 436, 1080, 1326, -2),
            (1500, 376, 1450, 1636, 2),
            (1820, 306, 1760, 1986, 2.5),
            (2150, 406, 2110, 2336, 2),
            (2260, 406, 2110, 2336, -2.5),
            (2500, 346, 2460, 2626, 2),
            (2830, 416, 2750, 3020, 3),
        ]

        if dificuldade == "Fácil":
            indices = [0, 4, 9]
        elif dificuldade == "Média":
            indices = [0, 1, 2, 5, 6, 9]
        else:
            indices = list(range(10))

        self.inimigas = []
        for i in indices:
            x, y, lim_esq, lim_dir, vel = todas_inimigas[i]
            self.inimigas.append({
                "rect": pygame.Rect(x, y, 34, 44),
                "lim_esq": lim_esq,
                "lim_dir": lim_dir,
                "vel": vel,
                "frame": 0,
                "anim": 0
            })
            tela.blit(img_jogador, (self.pos_x * self.tamanho_bloco, self.pos_y * self.tamanho_bloco))
        else:
            rect_jogador = pygame.Rect(self.pos_x * self.tamanho_bloco, self.pos_y * self.tamanho_bloco, self.tamanho_bloco, self.tamanho_bloco)
            pygame.draw.rect(tela, self.cor_jogador, rect_jogador)
