from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, session, url_for
from flask_session import Session
import pandas as pd
import os


# Organiza as perguntas por ordem de entropia
def analisar_perguntas(perguntas, pessoas):
    """Coloca as perguntas em ordem de entropia"""
    for pergunta in perguntas:
        q1 = calcular_q1(pergunta, pessoas)
        pergunta["beta"] = abs(0.5 - q1)
    return sorted(perguntas, key=lambda x: x["beta"])


# Normaliza a probabilidade das pessoas
def normalizar_pessoas(pessoas):
    prob_total = 0
    for pessoa in pessoas:
        prob_total += pessoa["prob"]
    for pessoa in pessoas:
        pessoa["prob"] = pessoa["prob"] / prob_total


def analisar_pessoas(pessoas):
    return sorted(pessoas, key=lambda x: x["prob"], reverse=True)


def atualizar_dados(respostas, pessoa):
    df = pd.read_excel("Dados_Iluminator.xlsx")
    if pessoa not in df["Nome"].values:
        nova_pessoa = {col: 0 for col in df.columns}
        nova_pessoa["Nome"] = pessoa
        df = pd.concat([df, pd.DataFrame([nova_pessoa])], ignore_index=True)

    for pergunta_nome, valor in respostas.items():
        df.loc[df["Nome"] == pessoa, pergunta_nome] += valor

    df.to_excel("Dados_Iluminator.xlsx", index=False)


def obter_dicionario_pessoa(df, nome_pessoa):
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


def nova_pessoa(df, nome_pessoa, prob):
    return {
        "nome": nome_pessoa,
        "prob": prob,
        "atributes": obter_dicionario_pessoa(df, nome_pessoa),
    }


def calcular_q1(pergunta, pessoas):
    q1s = 0
    q1n = 0
    for pessoa in pessoas:
        if pergunta["atributes"][pessoa["nome"]] > 0.5:
            q1s += pessoa["prob"]
        elif pergunta["atributes"][pessoa["nome"]] < 0.5:
            q1n += pessoa["prob"]

    return max(q1s, q1n)


def obter_dicionario_atributo(df, nome_atributo):
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


perguntas = {
    "3d": "Seu personagem é conhecido por usar impressoras 3D?",
    "22": "Seu personagem é da turma 22?",
    "23": "Seu personagem é da turma 23?",
    "24": "Seu personagem é da turma 24?",
    "25": "Seu personagem é da turma 25?",
    "26": "Seu personagem é da turma 26?",
    "adotado": "Seu personagem foi adotado como calouro?",
    "alto": "Seu personagem é alto?",
    "aluno": "Seu personagem é um aluno?",
    "atletica": "Seu personagem Já fez parte da atlética?",
    "baixo": "Seu personagem é baixo?",
    "barba": "Seu personagem tem barba?",
    "bone": "Seu personagem gosta de usar boiná/boné?",
    "bordao": "Seu personagem tem uma frase de efeito ou bordão?",
    "branco": "Seu personagem é branco?",
    "c_dados": "Seu personagem é da área de ciência de dados?",
    "c_humanas": "Seu personagem é da área de ciências humanas?",
    "c_materia": "Seu personagem é da área de ciências da matéria?",
    "c_vida": "Seu personagem é da área de ciências da vida?",
    "ca": "Seu personagem já fez parte do CA?",
    "cabelo_cacheado": "Seu personagem tem cabelo cacheado?",
    "cabelo_curto": "Seu personagem tem cabelo curto?",
    "cabelo_liso": "Seu personagem tem cabelo liso?",
    "cabelo_longo": "Seu personagem tem cabelo longo?",
    "camisa": "Seu personagem usa muita camisa preta?",
    "colorido": "Seu personagem já teve cabelo colorido?",
    "estagiario": "Seu personagem é um estagiário?",
    "experimental": "Seu personagem é experimental?",
    "filhos": "Seu personagem tem filhos?",
    "funcionario": "Seu personagem é um funcionário?",
    "futebol": "Seu personagem joga futebol?",
    "gatos": "Seu personagem é conhecido por gostar de gatos?",
    "ilum": "Seu personagem fica 100% do tempo na ILUM?",
    "laboratorio": "Seu personagem é visto no laboratório?",
    "luggo": "Seu personagem mora na Luggo?",
    "mais_24_anos": "Seu personagem tem mais de 24 anos?",
    "maquina": "Seu personagem é uma máquina?",
    "moto": "Seu personagem anda de moto?",
    "mulher": "Seu personagem é mulher?",
    "oculos": "Seu personagem usa óculos?",
    "pelucia": "Seu personagem é de pelúcia?",
    "pessoa": "Seu personagem é uma pessoa?",
    "preto": "Seu personagem é preto?",
    "professor": "Seu personagem é um professor?",
    "russo": "Seu personagem é russo?",
    "tarot": "Seu personagem sabe ler tarot?",
    "tecnico": "Seu personagem trabalha como técnico de laboratório?",
    "teorico": "Seu personagem é teórico?",
    "v2": "Seu personagem mora no V2?",
    "v3": "Seu personagem mora no V3?",
    "v4": "Seu personagem mora no V4?",
    "volei": "Seu personagem joga vôlei?",
}


def nova_pergunta(df, nome_atributo):
    return {
        "nome": nome_atributo,
        "texto": perguntas[str(nome_atributo)],
        "atributes": obter_dicionario_atributo(df, nome_atributo),
    }


load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_FILE_DIR"] = "./flask_session"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_USE_SIGNER"] = True

Session(app)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/game")
def game():
    return render_template("game.html")


@app.route("/api/start", methods=["POST"])
def start_game():
    df = pd.read_excel("Dados_Iluminator.xlsx")

    # Gerar pessoas
    pessoas = []
    for pessoa in df.iloc[:, 0]:
        pessoas.append(nova_pessoa(df, pessoa, 1))

    normalizar_pessoas(pessoas)

    # Gerar perguntas
    perguntas = []
    for atributo in df.columns[1:]:
        perguntas.append(nova_pergunta(df, atributo))

    perguntas = analisar_perguntas(perguntas, pessoas)

    session["game"] = {
        "pessoas": pessoas,
        "perguntas": perguntas,
        "respostas": {},
        "contador": 0,
        "state": "playing",
    }

    return {"message": "Jogo iniciado"}


@app.route("/api/pergunta")
def pergunta():
    game = session["game"]
    if game["perguntas"]:
        return {"pergunta": game["perguntas"][0]["texto"]}
    return {"pergunta": "Nenhuma pergunta disponível"}


valores_respostas = {
    "SIM": 0.95,
    "PROVAVELMENTE_SIM": 0.75,
    "NAO_SEI": 0,
    "PROVAVELMENTE_NAO": -0.75,
    "NAO": -0.95,
}


@app.route("/api/resposta", methods=["POST"])
def resposta():
    data = request.json
    resposta = data.get("resposta")
    game = session["game"]

    if game["state"] == "adivinhou":
        if resposta == "SIM":
            atualizar_dados(game["respostas"], game["pessoas"][0]["nome"])
            game["state"] = "vitoria"
        else:
            game["contador"] += 1
            if game["contador"] >= 5:
                game["state"] = "derrota"
            else:
                game["pessoas"][0]["prob"] = 0
                game["state"] = "playing"

        session["game"] = game
        return {
            "state": game["state"],
            "pergunta": (
                game["perguntas"][0]["texto"] if game["state"] == "playing" else None
            ),
        }

    if game["state"] == "derrota":
        atualizar_dados(game["respostas"], resposta)
        session.clear()
        return jsonify({"redirect": url_for("index")})

    if game["state"] == "vitoria":
        return {"state": game["state"]}

    if not resposta:
        return {"message": "Resposta inválida"}

    pergunta_atual = game["perguntas"][0]["nome"]
    valor_resposta = valores_respostas[resposta]

    # Guarda a resposta
    game["respostas"][pergunta_atual] = valor_resposta

    # Atualiza as probabilidades
    if valor_resposta > 0:
        for pessoa in game["pessoas"]:
            if game["perguntas"][0]["atributes"][pessoa["nome"]] > 0.5:
                pessoa["prob"] = pessoa["prob"] * valor_resposta
            elif game["perguntas"][0]["atributes"][pessoa["nome"]] < 0.5:
                pessoa["prob"] = pessoa["prob"] * (1 - valor_resposta)
    elif valor_resposta < 0:
        for pessoa in game["pessoas"]:
            if game["perguntas"][0]["atributes"][pessoa["nome"]] > 0.5:
                pessoa["prob"] = pessoa["prob"] * (1 + valor_resposta)
            elif game["perguntas"][0]["atributes"][pessoa["nome"]] < 0.5:
                pessoa["prob"] = pessoa["prob"] * abs(valor_resposta)

    normalizar_pessoas(game["pessoas"])

    # Remove pergunta e reorganiza
    game["perguntas"].pop(0)

    game["perguntas"] = analisar_perguntas(game["perguntas"], game["pessoas"])

    # Checa se as probabilidades estão favoráveis para um chute
    game["pessoas"] = analisar_pessoas(game["pessoas"])
    if game["pessoas"][0]["prob"] - game["pessoas"][1]["prob"] > 0.5:
        chute = game["pessoas"][0]["nome"]
        game["state"] = "adivinhou"

        session["game"] = game
        return {"state": "adivinhou", "chute": chute}

    # Checa se há perguntas disponíveis
    if len(game["perguntas"]) > 0:
        session["game"] = game
        return {"state": "playing", "pergunta": game["perguntas"][0]["texto"]}
    else:
        game["state"] = "derrota"
        session["game"] = game
        return {"state": "derrota"}
