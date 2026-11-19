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



