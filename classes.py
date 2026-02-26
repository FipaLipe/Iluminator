import numpy as np
import pandas as pd
import pygame

df = pd.read_excel("Dados_Iluminator.xlsx")

class Botao_hover:
    def __init__(self, tamanho = None, tamanho_hover = None, pos = None, imagem = None):

        # Define imagens (normal e hover), caso hajam
        if imagem != None:
            img = pygame.image.load(f"Imagens/{imagem}.png") 
            img_hover = pygame.image.load(f"Imagens/{imagem}_hover.png")
        else:
            img = None
            img_hover = None
        
        # Calcula posições
        pos_normal = (pos[0]-tamanho[0]//2, pos[1]-tamanho[1]//2) if pos != None else None
        pos_hover = (pos[0]-tamanho_hover[0]//2, pos[1]-tamanho_hover[1]//2) if pos != None else None
        
        # Define os rects (região interativa)
        rect = pygame.Rect(pos_normal, tamanho) if tamanho != None and pos_normal != None else None
        rect_hover =  pygame.Rect(pos_hover, tamanho_hover) if tamanho_hover != None and pos_hover != None else None
        self.rect = rect #Rect inicial


        # Armazena parâmetros
        self.imgs = (img, img_hover)
        self.rects = (rect, rect_hover)
        self.tamanhos = (tamanho, tamanho_hover)
        self.posicoes = (pos_normal, pos_hover)


    def draw(self, surface):
        """Essa função desenha o botão na região especificada"""

        mouse_pos = pygame.mouse.get_pos()

        hovering = self.rect.collidepoint(mouse_pos)

        # Checa se o mouse está sobre o botão e define os parâmetros utilizados (normal ou hover)
        if hovering: 
            self.img = self.imgs[1] 
            self.pos = self.posicoes[1] 
            self.rect = self.rects[1]  
        else:
            self.img = self.imgs[0] 
            self.pos = self.posicoes[0] 
            self.rect = self.rects[0]

        # Desenha botão
        surface.blit(self.img, self.pos)

class CaixaTexto:
    def __init__(self, x, y, largura, altura):
        self.rect = pygame.Rect(x, y, largura, altura)
        self.texto = ""
        self.ativo = False
        self.cursor_visivel = True
        self.tempo_cursor = 0
        
    def manipular_evento(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN:
            # Verificar se clicou na caixa de texto
            if self.rect.collidepoint(evento.pos):
                self.ativo = True
            else:
                self.ativo = False
        
        if evento.type == pygame.KEYDOWN and self.ativo:
            if evento.key == pygame.K_BACKSPACE: # Apertou a tecla de apagar
                self.texto = self.texto[:-1] # Apagar último caractere
            else:
                # Adicionar caractere (limitar a 18 caracteres)
                if len(self.texto) < 18:
                    self.texto += evento.unicode
        return False  # Retorna False por padrão
    
    def atualizar(self):
        # Piscar o cursor
        self.tempo_cursor += 1
        if self.tempo_cursor > 360:  # A cada 360 frames
            self.cursor_visivel = not self.cursor_visivel
            self.tempo_cursor = 0
    
    def draw(self, fonte, superficie):
        # Definir texto exibido
        if self.texto == "" and not self.ativo:
            texto_render = fonte.render("Escreva aqui", True, (242, 237, 219))
        else:
            texto_render = fonte.render(self.texto, True, (242, 237, 219))

        # Centralizar texto na caixa
        texto_rect = texto_render.get_rect(center=self.rect.center)
        superficie.blit(texto_render, texto_rect)

        # Cursor
        if self.ativo and self.cursor_visivel:
            cursor_x = texto_rect.right + 2
            cursor_top = texto_rect.top
            cursor_bottom = texto_rect.bottom

            pygame.draw.line(
                superficie,
                (242, 237, 219),
                (cursor_x, cursor_top),
                (cursor_x, cursor_bottom),
                2
            )
            

class Pergunta:
    def __init__(self, df, id):
        self.nome = id
        self.img = pygame.transform.scale(pygame.image.load(f"Imagens/perguntas/{id}.png"), (666, 194))  
        self.atributes = self.obter_dicionario_atributo(df, id)
    
    def calcular_q1(self, pessoas):
        q1s = 0
        q1n = 0
        for pessoa in pessoas:
            if self.atributes[pessoa.nome] > 0.5:
                q1s += pessoa.prob
            elif self.atributes[pessoa.nome] < 0.5:
                q1n += pessoa.prob
        
        return max(q1s, q1n)

    def obter_dicionario_atributo(self, df, nome_atributo):
        # Verificar se o atributo existe
        if nome_atributo not in df.columns:
            print(f"Atributo '{nome_atributo}' não encontrado!")
            return None
        
        # Criar dicionário de mapeamento
        nomes_para_valores = {}
        
        for _, row in df.iterrows():
            nome = row.iloc[0]  # Primeira coluna é o nome
            valor = row[nome_atributo]
            
            if pd.isna(valor):  # Usando pd.isna() que funciona melhor com pandas
                nomes_para_valores[nome] = 0
            else:
                nomes_para_valores[nome] = float(valor)  
        
        return nomes_para_valores

class Pessoa:
    def __init__(self, df, nome_pessoa, prob):
        self.nome = nome_pessoa
        self.atributes = self.obter_dicionario_pessoa(df, nome_pessoa)
        self.prob = prob

    def obter_dicionario_pessoa(self, df, nome_pessoa):
        
        # Buscar a pessoa pelo nome
        pessoa_df = df[df.iloc[:, 0] == nome_pessoa]
        
        if pessoa_df.empty:
            print(f"Pessoa '{nome_pessoa}' não encontrada!")
            return None
        
        # Extrair a linha da pessoa
        row = pessoa_df.iloc[0]
        pessoa_dict = {}
        
        for atributo, valor in row[1:].items():  # Pula a coluna de nome
            
            if pd.isna(valor):  # Usando pd.isna() que funciona melhor com pandas
                pessoa_dict[atributo] = 0
            else:
                pessoa_dict[atributo] = float(valor)
        
        return pessoa_dict

    """def sortear_inverso(perguntas):
        epsilon=1e-10
        pesos_seguros = [p.beta + epsilon for p in perguntas]
        pesos_inversos = 1 / np.array(pesos_seguros)
        probabilidades = pesos_inversos / pesos_inversos.sum()
        
        return np.random.choice(perguntas, p=probabilidades)"""