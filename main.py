import pygame, sys
from pygame.locals import *
from config import window_width, window_height, screen, clock
from classes import Botao_hover
from jogo import run
import time

pygame.display.set_caption("Iluminator")

while True:
    # --- CARREGAR IMAGENS ---
    background = pygame.image.load("Imagens/main_menu.png").convert()
    background = pygame.transform.scale(background, (window_width, window_height))

    # Posição do botão
    botao_center = (815, 503)  # (628 + 373/2, 468 + 69/2)

    # Botão de jogar (uso da classe Botao_hover)
    jogar = Botao_hover((373, 69), (444, 100), botao_center, "jogar")

    # Pega a posição do mouse
    mouse_pos = pygame.mouse.get_pos()

    # --- EVENTOS ---
    for event in pygame.event.get():
        if event.type == QUIT: #Sair do jogo
            pygame.quit(); sys.exit()
        if event.type == KEYDOWN and event.key == K_ESCAPE: #ESC
            pygame.quit(); sys.exit()
        if event.type == MOUSEBUTTONDOWN and event.button == 1:  #Clicou no botão
            if jogar.rect.collidepoint(mouse_pos):
                run(screen, clock)

    # --- DESENHO  ---
    screen.blit(background, (0, 0)) # fundo
    jogar.draw(screen) # botão

    pygame.display.flip()
    clock.tick(60)
