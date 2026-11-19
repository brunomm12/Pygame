import random
import pygame
from config import *

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



