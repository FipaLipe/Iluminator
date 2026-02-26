import pygame, sys
import pandas as pd
import numpy as np
from classes import Pessoa, Pergunta, Botao_hover, CaixaTexto
from pygame.locals import *
from config import window_width, window_height

pygame.display.set_caption("Iluminator")

def run(screen, clock):
    # --- CARREGAR IMAGENS ---
    background = pygame.image.load("Imagens/bg_jogo.png").convert()
    background = pygame.transform.scale(background, (window_width, window_height))
    foreground = pygame.Surface((window_width, window_height), pygame.SRCALPHA)
    fundo_chute = pygame.image.load("Imagens/fundo_chute.png").convert()
    fundo_vitoria = pygame.image.load("Imagens/vitoria.png").convert()
    fundo_derrota = pygame.image.load("Imagens/derrota.png").convert()

    # Gerar botões
    sim = Botao_hover((373, 69), (420, 77), (858, 315), "sim")
    prov_sim = Botao_hover((373, 69), (420, 77), (858, 408), "prov_sim")
    nao_sei = Botao_hover((373, 69), (420, 77), (858, 500), "nao_sei")
    prov_nao = Botao_hover((373, 69), (420, 77), (858, 593), "prov_nao")
    nao = Botao_hover((373, 69), (420, 77), (858, 686), "nao")

    sim_chute = Botao_hover((373, 69), (420, 77), (858, 460), "sim")
    nao_chute = Botao_hover((373, 69), (420, 77), (858, 553), "nao")

    sim_vitoria = Botao_hover((373, 69), (420, 77), (858, 481), "sim")
    nao_vitoria = Botao_hover((373, 69), (420, 77), (858, 575), "nao")

    enviar = Botao_hover((313, 69), (351, 77), (1044, 696), "enviar")
    sair = Botao_hover((313, 69), (351, 77), (673, 696), "sair")

    caixa_texto = CaixaTexto(516, 541, 684, 69)

    # Carregar fonte
    fonte = pygame.font.Font("JetBrainsMono-Bold.ttf", 33)
    fonte_mini = pygame.font.Font("JetBrainsMono-Bold.ttf", 20)

    # Gerar pessoas
    pessoas = []
    df = pd.read_excel("Dados_Iluminator.xlsx")
    for pessoa in df.iloc[:, 0]:
        pessoas.append(Pessoa(df, pessoa, 1))

    # Normaliza a probabilidade das pessoas
    def normalizar_pessoas(pessoas):
        prob_total = 0
        for pessoa in pessoas:
            prob_total += pessoa.prob
        for pessoa in pessoas:
            pessoa.prob = pessoa.prob/prob_total
    
    normalizar_pessoas(pessoas)

    # Gerar perguntas
    perguntas = []
    for atributo in df.columns[1:]:
        perguntas.append(Pergunta(df, atributo))
    

    # Organiza as perguntas por ordem de entropia
    def analisar_perguntas(perguntas, pessoas):
        """Coloca as perguntas em ordem de entropia"""
        for pergunta in perguntas:
            q1 = pergunta.calcular_q1(pessoas)
            pergunta.beta = abs(0.5-q1)
        return sorted(perguntas, key=lambda x: x.beta)
    
    perguntas = analisar_perguntas(perguntas, pessoas)

    # Organiza as pessoas por ordem de probabilidade
    def analisar_pessoas(pessoas):
        return sorted(pessoas, key=lambda x: x.prob, reverse=True)
    
    # Atualiza o dataset após o término do jogo
    def atualizar_dados(respostas, pessoa):
        df = pd.read_excel("Dados_Iluminator.xlsx")
        if pessoa not in df["Nome"].values:
            nova_pessoa = {col: 0 for col in df.columns}
            nova_pessoa["Nome"] = pessoa
            df = pd.concat([df, pd.DataFrame([nova_pessoa])], ignore_index=True)

        for pergunta in respostas.keys():
            df.loc[df["Nome"] == pessoa, pergunta.nome] += respostas[pergunta]

        df.to_excel("Dados_Iluminator.xlsx", index=False)

    def quebra_de_linha(text, font, color, max_width):
        words = text.split(' ')
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + word + " "
            test_width, _ = font.size(test_line)

            if test_width <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + " "

        lines.insert(0, current_line)

        # Renderiza cada linha
        rendered_lines = [font.render(line.strip(), True, color) for line in lines]

        return rendered_lines

    # Guarda as respostas do jogador
    respostas = {}
    contador = 0

    running = True
    state = "plain"

    while running:
        # --- EVENTOS ---
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():

            if event.type == QUIT: # Sair do sistema
                pygame.quit(); sys.exit()

            if event.type == KEYDOWN and event.key == K_ESCAPE: #ESC
                return False

            if event.type == MOUSEBUTTONDOWN and event.button == 1: #Clique com botão esquerdo

                # SIM
                if sim.rect.collidepoint(mouse_pos):
                    # Guarda a resposta
                    respostas[perguntas[0]] = 0.95

                    # Atualiza as probabilidades
                    for pessoa in pessoas:
                        if perguntas[0].atributes[pessoa.nome] > 0.5:
                            pessoa.prob = pessoa.prob*0.95
                        elif perguntas[0].atributes[pessoa.nome] < 0.5:
                            pessoa.prob = pessoa.prob*0.05
                    normalizar_pessoas(pessoas)

                    # Remove pergunta e reorganiza
                    perguntas.pop(0)

                    perguntas = analisar_perguntas(perguntas, pessoas)

                # PROVAVELMENTE SIM
                if prov_sim.rect.collidepoint(mouse_pos):
                    # Guarda a resposta
                    respostas[perguntas[0]] = 0.75

                    # Atualiza as probabilidades
                    for pessoa in pessoas:
                        if perguntas[0].atributes[pessoa.nome] > 0.5:
                            pessoa.prob = pessoa.prob*0.75
                        elif perguntas[0].atributes[pessoa.nome] < 0.5:
                            pessoa.prob = pessoa.prob*0.25
                    normalizar_pessoas(pessoas)

                    # Remove pergunta e reorganiza
                    perguntas.pop(0)

                    perguntas = analisar_perguntas(perguntas, pessoas)

                # NÃO SEI
                if nao_sei.rect.collidepoint(mouse_pos):
                    # Guarda a resposta
                    respostas[perguntas[0]] = 0

                    # Remove pergunta e reorganiza
                    perguntas.pop(0)

                    perguntas = analisar_perguntas(perguntas, pessoas)

                # PROVAVELMENTE NÃO
                if prov_nao.rect.collidepoint(mouse_pos):   
                    # Guarda a resposta
                    respostas[perguntas[0]] = -0.75

                    # Atualiza as probabilidades
                    for pessoa in pessoas:
                        if perguntas[0].atributes[pessoa.nome] > 0.5:
                            pessoa.prob = pessoa.prob*0.25
                        elif perguntas[0].atributes[pessoa.nome] < 0.5:
                            pessoa.prob = pessoa.prob*0.75
                    normalizar_pessoas(pessoas)

                    # Remove pergunta e reorganiza
                    perguntas.pop(0)

                    perguntas = analisar_perguntas(perguntas, pessoas)

                # NÃO
                if nao.rect.collidepoint(mouse_pos):
                    # Guarda a resposta
                    respostas[perguntas[0]] = -0.95

                    # Atualiza as probabilidades
                    for pessoa in pessoas:
                        if perguntas[0].atributes[pessoa.nome] > 0.5:
                            pessoa.prob = pessoa.prob*0.05
                        elif perguntas[0].atributes[pessoa.nome] < 0.5:
                            pessoa.prob = pessoa.prob*0.95
                    normalizar_pessoas(pessoas)

                    # Remove pergunta e reorganiza
                    perguntas.pop(0)

                    perguntas = analisar_perguntas(perguntas, pessoas)

        # Checa se as probabilidades estão favoráveis para um chute
        pessoas = analisar_pessoas(pessoas)
        if pessoas[0].prob - pessoas[1].prob > 0.5:
            chute = pessoas[0].nome
            state = "adivinhou"
            textos = quebra_de_linha(f"Seu personagem é {chute}?", fonte, (183, 110, 34), 600)
            n_linhas = len(textos)
            pos_linhas =[]
            for i, linha in enumerate(textos):
                x_linha = 868-linha.get_width()//2
                y_linha = 303-(linha.get_height()*n_linhas//2)*i
                pos_linhas.append((x_linha, y_linha))


        # Checa se há perguntas disponíveis
        if len(perguntas) > 0:
            # --- DESENHO  ---
            screen.blit(background, (0, 0))    
            foreground.fill((0, 0, 0, 0))  
            sim.draw(foreground)
            prov_sim.draw(foreground)
            nao_sei.draw(foreground)
            prov_nao.draw(foreground)
            nao.draw(foreground)

            foreground.blit(perguntas[0].img, (535, 63)) 
            screen.blit(foreground, (0, 0)) 
            pygame.display.flip()
            clock.tick(60)
        else:
            state = "derrota"

        #-----TELA DE CHUTE-----
        while state == "adivinhou":
            screen.blit(fundo_chute, (0, 0))    
            for texto, pos_texto in zip(textos, pos_linhas):
                screen.blit(texto, pos_texto)
            sim_chute.draw(screen)
            nao_chute.draw(screen)

            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():

                if event.type == QUIT: # Sair do sistema
                    pygame.quit(); sys.exit()

                if event.type == KEYDOWN and event.key == K_ESCAPE: #ESC
                    return False

                if event.type == MOUSEBUTTONDOWN and event.button == 1: #Clique com botão esquerdo

                    # SIM
                    if sim_chute.rect.collidepoint(mouse_pos):
                        atualizar_dados(respostas, chute)
                        state = "vitoria"
                    
                    # NÃO
                    if nao_chute.rect.collidepoint(mouse_pos):
                        contador += 1
                        if contador >= 5:
                            state = "derrota"
                        else:
                            pessoas[0].prob = 0
                            state = "plain"


            pygame.display.flip()
            clock.tick(60)

        #-----TELA DE VITÓRIA-----
        while state == "vitoria":
            screen.blit(fundo_vitoria, (0, 0))  
            sim_vitoria.draw(screen)
            nao_vitoria.draw(screen)  

            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():

                if event.type == QUIT: # Sair do sistema
                    pygame.quit(); sys.exit()

                if event.type == KEYDOWN and event.key == K_ESCAPE: #ESC
                    return False

                if event.type == MOUSEBUTTONDOWN and event.button == 1: #Clique com botão esquerdo

                    # SIM
                    if sim_vitoria.rect.collidepoint(mouse_pos):
                        return False
                    
                    # NÃO
                    if nao_vitoria.rect.collidepoint(mouse_pos):
                        return False

            pygame.display.flip()
            clock.tick(60)

        #-----TELA DE DERROTA-----
        while state == "derrota":
            screen.blit(fundo_derrota, (0, 0))  
            caixa_texto.draw(fonte, screen)
            enviar.draw(screen)
            sair.draw(screen)
            
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():

                if event.type == QUIT: # Sair do sistema
                    pygame.quit(); sys.exit()

                if event.type == KEYDOWN and event.key == K_ESCAPE: #ESC
                    return False

                caixa_texto.manipular_evento(event)

                if event.type == MOUSEBUTTONDOWN and event.button == 1: #Clique com botão esquerdo

                    # ENVIAR
                    if enviar.rect.collidepoint(mouse_pos):
                        gabarito = caixa_texto.texto.title()
                        atualizar_dados(respostas, gabarito)
                        return False
                    
                    # SAIR
                    if sair.rect.collidepoint(mouse_pos):
                        return False

            pygame.display.flip()
            clock.tick(60)
        
