from collections import deque
import random
import pygame
from config import *


class Porta:
    """Representa a porta final que o jogador precisa destruir na fase clicker."""

    def __init__(self, vida_maxima):
        """Inicializa a porta com a vida máxima definida e carrega o fundo da fase."""
        self.vida_maxima = vida_maxima
        self.vida_atual = vida_maxima
        self.rect_base = pygame.Rect(LARGURA // 2 - 100, 130, 200, 310)
        self.rect = self.rect_base.copy()
        self.tremer_x = 0
        self.tremer_y = 0

        self.img_fundo = None
        for nome_arquivo in ["fundo_porta.png", "fundo_porta.jpg", "fundo_porta.jpeg"]:
            try:
                img = pygame.image.load(nome_arquivo).convert()
                self.img_fundo = pygame.transform.scale(img, (LARGURA + 16, ALTURA + 16))
                break
            except (FileNotFoundError, pygame.error):
                continue

    def configurar_dificuldade(self, nova_vida_maxima):
        """Redefine a vida máxima e atual da porta conforme a dificuldade escolhida."""
        self.vida_maxima = nova_vida_maxima
        self.vida_atual = nova_vida_maxima

    def receber_dano(self, dano):
        """Aplica dano à porta e gera o efeito visual de impacto e tremor."""
        self.vida_atual = max(0, self.vida_atual - dano)
        self.rect = self.rect_base.inflate(-15, -15)
        self.tremer_x = random.randint(-6, 6)
        self.tremer_y = random.randint(-6, 6)

    def resetar_impacto(self):
        """Restaura a posição e o tamanho originais da porta após o impacto."""
        self.rect = self.rect_base.copy()
        self.tremer_x = 0
        self.tremer_y = 0

    def desenhar(self, tela):
        """Renderiza o cenário da porta e a barra de vida na tela."""
        if self.img_fundo:
            tela.blit(self.img_fundo, (-8 + self.tremer_x, -8 + self.tremer_y))
        else:
            pygame.draw.rect(tela, MARROM, self.rect, border_radius=5)
            pygame.draw.circle(tela, BRANCO, (self.rect.right - 25, self.rect.centery), 10)

        largura_barra = 400
        pct_vida = max(self.vida_atual / self.vida_maxima, 0)
        barra_x = LARGURA // 2 - largura_barra // 2
        pygame.draw.rect(tela, PRETO, (barra_x - 3, 107, largura_barra + 6, 31), border_radius=6)
        pygame.draw.rect(tela, VERMELHO, (barra_x, 110, largura_barra, 25), border_radius=5)
        pygame.draw.rect(tela, VERDE, (barra_x, 110, largura_barra * pct_vida, 25), border_radius=5)


class LojaUpgrades:
    """Gerencia os itens de melhoria de dano e auto-chute da fase da porta."""

    def __init__(self):
        """Inicializa a lista de upgrades com seus custos, bônus e áreas clicáveis."""
        self.itens = [
            {"nome": "Tênis Novo", "custo": 10, "dano": 1, "tipo": "dano", "rect": pygame.Rect(20, 500, 175, 70)},
            {"nome": "Soco Inglês", "custo": 50, "dano": 5, "tipo": "dano", "rect": pygame.Rect(215, 500, 175, 70)},
            {"nome": "Pé de Cabra", "custo": 200, "dano": 25, "tipo": "dano", "rect": pygame.Rect(410, 500, 175, 70)},
            {"nome": "Auto-Chute", "custo": 50, "dano": 0, "tipo": "auto", "comprado": False, "rect": pygame.Rect(605, 500, 175, 70)}
        ]

    def resetar_precos(self):
        """Restaura os preços iniciais e o estado dos upgrades para uma nova partida."""
        self.itens[0]["custo"] = 10
        self.itens[1]["custo"] = 50
        self.itens[2]["custo"] = 200
        self.itens[3]["comprado"] = False

    def tentar_comprar(self, mouse_pos, clique, dinheiro, dano_atual, tem_auto_clique, som_compra=None):
        """Processa a compra de um item caso o jogador clique sobre ele e tenha saldo."""
        for item in self.itens:
            if item["rect"].collidepoint(mouse_pos) and clique:
                if item["tipo"] == "auto":
                    if not item["comprado"] and dinheiro >= item["custo"]:
                        dinheiro -= item["custo"]
                        item["comprado"] = True
                        tem_auto_clique = True
                        if som_compra:
                            som_compra.play()
                elif dinheiro >= item["custo"]:
                    dinheiro -= item["custo"]
                    dano_atual += item["dano"]
                    item["custo"] = int(item["custo"] * 1.5)
                    if som_compra:
                        som_compra.play()
        return dinheiro, dano_atual, tem_auto_clique

    def desenhar(self, tela, mouse_pos, dinheiro, fonte_pequena):
        """Desenha os botões da loja indicando disponibilidade e efeito de hover."""
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


class FaseLabirinto:
    """Controla a primeira fase: fuga em labirinto com inimiga perseguidora (BFS)."""

    def __init__(self):
        """Inicializa o mapa em grade, carrega spritesheets e posiciona entidades."""
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
        """Recorta uma spritesheet em frames direcionais e armazena no dicionário."""
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
        """Reposiciona jogador, inimiga e notas de dinheiro para o início da fase."""
        self.pos_x = 1
        self.pos_y = 1
        self.inimigo_x = 9
        self.inimigo_y = 7
        self.direcao_atual = 'baixo'
        self.direcao_inimigo = 'baixo'
        self.dinheiros = [(18, 1), (5, 3), (1, 9), (16, 11), (1, 13)]

    def mover_jogador(self, dx, dy):
        """Move o jogador na grade respeitando colisões com paredes e atualiza animação."""
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
        """Verifica coleta de dinheiro na posição atual e retorna o valor coletado."""
        pos = (self.pos_x, self.pos_y)
        if pos in self.dinheiros:
            self.dinheiros.remove(pos)
            return 5
        return 0

    def mover_inimigo(self):
        """Calcula o menor caminho até o jogador usando Busca em Largura (BFS) e avança 1 passo."""
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
        """Retorna True se a inimiga alcançou a mesma célula do jogador."""
        return self.pos_x == self.inimigo_x and self.pos_y == self.inimigo_y

    def checar_saida(self):
        """Retorna True se o jogador alcançou a célula de saída ('E') do labirinto."""
        return self.matriz_mapa[self.pos_y][self.pos_x] == 'E'

    def desenhar(self, tela):
        """Renderiza paredes, saída, coletáveis, inimiga e jogador na tela."""
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
            tela.blit(img_jogador, (self.pos_x * self.tamanho_bloco, self.pos_y * self.tamanho_bloco))
        else:
            rect_jogador = pygame.Rect(self.pos_x * self.tamanho_bloco, self.pos_y * self.tamanho_bloco, self.tamanho_bloco, self.tamanho_bloco)
            pygame.draw.rect(tela, self.cor_jogador, rect_jogador)


class FaseParkour:
    """Controla a segunda fase: plataforma lateral com gravidade, câmera, vidas e inimigas."""

    def __init__(self):
        """Inicializa física, plataformas, fundo com parallax e sprites laterais."""
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
        """Carrega os frames de caminhada para esquerda e direita a partir da spritesheet."""
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
        """Reinicia vidas, posição do jogador, coletáveis e quantidade de inimigas por dificuldade."""
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

    def atualizar(self, teclas, tempo_atual_ms, som_pulo=None, som_dano=None):
        """Atualiza física, colisões, patrulha das inimigas, câmera e retorna dinheiro coletado."""
        ganho_dinheiro = 0
        dx = 0

        if teclas[pygame.K_a] or teclas[pygame.K_LEFT]:
            dx = -self.vel_jogador
            self.direcao = 'esquerda'
        if teclas[pygame.K_d] or teclas[pygame.K_RIGHT]:
            dx = self.vel_jogador
            self.direcao = 'direita'

        if (teclas[pygame.K_w] or teclas[pygame.K_UP] or teclas[pygame.K_SPACE]) and self.no_chao:
            self.vel_y = self.forca_pulo
            self.no_chao = False
            if som_pulo:
                som_pulo.play()

        if dx != 0:
            self.contador_anim += 1
            if self.contador_anim >= 6:
                self.frame = (self.frame + 1) % 4
                self.contador_anim = 0
        else:
            self.frame = 0

        self.player_rect.x += dx
        self.player_rect.left = max(0, self.player_rect.left)
        self.player_rect.right = min(self.largura_mapa, self.player_rect.right)

        for plat in self.plataformas:
            if self.player_rect.colliderect(plat):
                if dx > 0:
                    self.player_rect.right = plat.left
                elif dx < 0:
                    self.player_rect.left = plat.right

        self.vel_y = min(self.vel_y + self.gravidade, 16)
        self.player_rect.y += self.vel_y
        self.no_chao = False

        for plat in self.plataformas:
            if self.player_rect.colliderect(plat):
                if self.vel_y > 0:
                    self.player_rect.bottom = plat.top
                    self.vel_y = 0
                    self.no_chao = True
                elif self.vel_y < 0:
                    self.player_rect.top = plat.bottom
                    self.vel_y = 0

        if self.player_rect.top > ALTURA + 40:
            self.vidas -= 1
            self.player_rect.topleft = (60, 420)
            self.vel_y = 0
            self.invencivel_ate = tempo_atual_ms + 1500
            if som_dano and self.vidas > 0:
                som_dano.play()

        for din in self.dinheiros[:]:
            if self.player_rect.colliderect(din):
                self.dinheiros.remove(din)
                ganho_dinheiro += 3

        for ini in self.inimigas:
            ini["rect"].x += ini["vel"]
            if ini["rect"].left <= ini["lim_esq"] or ini["rect"].right >= ini["lim_dir"]:
                ini["vel"] *= -1
            ini["anim"] += 1
            if ini["anim"] >= 8:
                ini["frame"] = (ini["frame"] + 1) % 4
                ini["anim"] = 0

            if self.player_rect.colliderect(ini["rect"]) and tempo_atual_ms > self.invencivel_ate:
                self.vidas -= 1
                self.invencivel_ate = tempo_atual_ms + 1500
                self.vel_y = -8
                if som_dano and self.vidas > 0:
                    som_dano.play()

        self.camera_x = max(0, min(self.player_rect.centerx - LARGURA // 2, self.largura_mapa - LARGURA))
        return ganho_dinheiro

    def checar_morte(self):
        """Retorna True quando o jogador perde todas as vidas."""
        return self.vidas <= 0

    def checar_saida(self):
        """Retorna True quando o jogador alcança a porta no final do parkour."""
        return self.player_rect.colliderect(self.porta_saida)

    def desenhar(self, tela, tempo_atual_ms):
        """Desenha o cenário com parallax, plataformas, coletáveis, inimigas e jogador."""
        if self.img_fundo:
            offset = -(int(self.camera_x * 0.4) % LARGURA)
            tela.blit(self.img_fundo, (offset, 0))
            tela.blit(self.img_fundo, (offset + LARGURA, 0))
        else:
            tela.fill((25, 25, 35))

        for plat in self.plataformas:
            r = plat.move(-self.camera_x, 0)
            pygame.draw.rect(tela, (90, 95, 105), r, border_radius=4)
            pygame.draw.rect(tela, (40, 45, 55), r, 3, border_radius=4)
            pygame.draw.rect(tela, (125, 130, 140), (r.x + 2, r.y + 2, r.width - 4, 6))

        r_porta = self.porta_saida.move(-self.camera_x, 0)
        pygame.draw.rect(tela, MARROM, r_porta, border_radius=6)
        pygame.draw.rect(tela, (60, 30, 10), r_porta, 3, border_radius=6)
        pygame.draw.circle(tela, AMARELO, (r_porta.right - 12, r_porta.centery), 5)

        for din in self.dinheiros:
            r_din = din.move(-self.camera_x, 0)
            if self.img_dinheiro:
                tela.blit(self.img_dinheiro, r_din)
            else:
                pygame.draw.rect(tela, VERDE, r_din, border_radius=3)

        for ini in self.inimigas:
            r_ini = ini["rect"].move(-self.camera_x, 0)
            dir_ini = 'direita' if ini["vel"] > 0 else 'esquerda'
            if self.tem_sprite_inimigo:
                img = self.sprites_inimigo[dir_ini][ini["frame"]]
                tela.blit(img, (r_ini.x - 5, r_ini.y))
            else:
                pygame.draw.rect(tela, VERMELHO, r_ini)

        piscando = tempo_atual_ms < self.invencivel_ate and (tempo_atual_ms // 100) % 2 == 0
        if not piscando:
            r_jog = self.player_rect.move(-self.camera_x, 0)
            if self.tem_sprite_jogador:
                img = self.sprites_jogador[self.direcao][self.frame]
                tela.blit(img, (r_jog.x - 5, r_jog.y))
            else:
                pygame.draw.rect(tela, (50, 150, 255), r_jog)
