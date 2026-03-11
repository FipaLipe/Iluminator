import uuid

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, session, url_for
import os
from upstash_redis import Redis
import json

load_dotenv()

redis_client = Redis.from_env()

def carregar_dataset():
    data = r.get("dataset:pessoas")
    return json.loads(data) if data else []

def salvar_dataset(pessoas):
    r.set("dataset:pessoas", json.dumps(pessoas))

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


def atualizar_dados(respostas, pessoa_nome):
    pessoas = carregar_dataset()

    for pessoa in pessoas:
        if pessoa["nome"] == pessoa_nome:
            for pergunta, valor in respostas.items():
                atual = pessoa["atributes"].get(pergunta, 0)
                pessoa["atributes"][pergunta] = atual + valor

    salvar_dataset(pessoas)


def calcular_q1(pergunta, pessoas):
    q1s = 0
    q1n = 0
    for pessoa in pessoas:
        if pergunta["atributes"][pessoa["nome"]] > 0.5:
            q1s += pessoa["prob"]
        elif pergunta["atributes"][pessoa["nome"]] < 0.5:
            q1n += pessoa["prob"]

    return max(q1s, q1n)


textos_perguntas = {

    # Identidade / natureza
    "pessoa": "Seu personagem é uma pessoa?",
    "maquina": "Seu personagem é uma maquina?",
    "pelucia": "Seu personagem é de pelúcia?",

    # Gênero
    "mulher": "Seu personagem é uma mulher?",
    "homem": "Seu personagem é um homem?",

    # Idade
    "mais_24_anos": "Seu personagem tem mais de 24 anos?",

    # Ocupação
    "professor": "Seu personagem é um professor da Ilum?",
    "aluno": "Seu personagem é um aluno da Ilum?",
    "estagiario": "Seu personagem é um estagiário da Ilum?",
    "funcionario": "Seu personagem é um funcionário da Ilum?",
    "tecnico": "Seu personagem trabalha como técnico de laboratório na Ilum?",

    # Área acadêmica
    "c_materia": "Seu personagem é da área de ciências da matéria?",
    "c_vida": "Seu personagem é da área de ciências da vida?",
    "c_humanas": "Seu personagem é da área de ciências humanas?",
    "c_dados": "Seu personagem é da área de ciências de dados?",
    "c_exatas": "Seu personagem é da área de ciências exatas?",
    "teorico": "Seu personagem é teórico?",
    "experimental": "Seu personagem é experimental?",

    # Turma
    "22": "Seu personagem é da turma 22?",
    "23": "Seu personagem é da turma 23?",
    "24": "Seu personagem é da turma 24?",
    "25": "Seu personagem é da turma 25?",
    "26": "Seu personagem é da turma 26?",

    # Moradia
    "luggo": "Seu personagem mora na luggo?",
    "v2": "Seu personagem mora no V2?",
    "v3": "Seu personagem mora no V3?",
    "v4": "Seu personagem mora no V4?",

    # Localização / rotina
    "ilum": f"Seu personagem fica 100% do tempo na Ilum?",
    "laboratorio": "Seu personagem é comumente visto no laboratório?",

    # Aparência
    "alto": "Seu personagem é alto?",
    "baixo": "Seu personagem é baixo?",
    "barba": "Seu personagem tem barba?",
    "oculos": "Seu personagem usa oculos?",
    "cabelo_longo": "Seu personagem tem cabelo longo?",
    "cabelo_curto": "Seu personagem tem cabelo curto?",
    "cabelo_cacheado": "Seu personagem tem cabelo cacheado?",
    "cabelo_liso": "Seu personagem tem cabelo liso?",
    "colorido": "Seu personagem já teve cabelo colorido?",
    "cabelo_escuro": "Seu personagem tem cabelo escuro?",
    "branco": "Seu personagem é branco?",
    "preto": "Seu personagem é preto?",
    "asiatico": "Seu personagem possui ascendência asiática?",
    "camisa": "Seu personagem é conhecido por usar camisa preta?",
    "bone": "Seu personagem usa boina ou boné?",

    # Origem
    "russo": "Seu personagem é russo?",
    "asia": "Seu personagem tem descendência asiática?",

    # Adoção
    "adotou": "Seu personagem já adotou algum calouro",
    "adotado": "Seu personagem foi adotado como calouro?",

    # Hobbies / interesses
    "volei": "Seu personagem joga volei?",
    "futebol": "Seu personagem joga futebol?",
    "truco": "Seu personagem joga truco?",
    "rpg": "Seu personagem joga RPG?",
    "magic": "Seu personagem joga Magic?",
    "animes": "Seu personagem assiste animes?",
    "reddit": "Seu personagem usa Reddit?",
    "ordem": "Seu personagem gosta de Ordem Paranormal?",
    "miku": "Seu personagem gosta de Hatsune Miku?",
    "tarot": "Seu personagem sabe ler tarot?",
    "academia": "Seu personagem frequenta alguma academia?",

    # Vida universitária
    "atletica": "Seu personagem já foi da Atlética?",
    "ca": "Seu personagem já foi do CA?",
    "3d": "Seu personagem é conhecido por usar impressora 3D?",
    "trancou": "Seu personagem já trancou o curso?",

    # Outras características
    "gatos": "Seu personagem é conhecido por gostar de gatos?",
    "bordao": "Seu personagem tem um bordão ou uma frase de efeito?",
    "moto": "Seu personagem tem uma moto?",
    "lgbt": "Seu personagem é da comunidade LGBT?",
    "nicho": "Seu personagem é d'O Nicho?",
    "filhos": "Seu personagem tem filhos?",
    "divulgação": "Seu personagem tem um Instagram de divulgação científica?"

}


def nova_pergunta(nome_atributo, pessoas):
    atributos = {}

    for pessoa in pessoas:
        atributos[pessoa["nome"]] = pessoa["atributes"].get(nome_atributo, 0.0)

    return {
        "nome": nome_atributo,
        "texto": textos_perguntas[nome_atributo],
        "atributes": atributos,
    }


def carregar_pessoas():
    pessoas = carregar_dataset()

    for pessoa in pessoas:
        pessoa["prob"] = 1.0

    return pessoas

def salvar_game(game_id, game):
    r.set(f"game:{game_id}", json.dumps(game))


def carregar_game(game_id):
    data = r.get(f"game:{game_id}")
    return json.loads(data) if data else None


def deletar_game(game_id):
    r.delete(f"game:{game_id}")


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

r = redis_client
app.config["SESSION_REDIS"] = redis_client

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/game")
def game():
    return render_template("game.html")


@app.route("/api/start", methods=["POST"])
def start_game():

    pessoas = carregar_pessoas()
    normalizar_pessoas(pessoas)

    perguntas = [nova_pergunta(nome, pessoas) for nome in textos_perguntas]

    perguntas = analisar_perguntas(perguntas, pessoas)

    game_id = str(uuid.uuid4())

    game = {
        "pessoas": pessoas,
        "perguntas": perguntas,
        "respostas": {},
        "contador": 0,
        "state": "playing",
    }

    session["game_id"] = game_id

    salvar_game(game_id, game)

    return {"message": "Jogo iniciado"}


@app.route("/api/pergunta")
def pergunta():
    game = carregar_game(session["game_id"])
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
    game = carregar_game(session["game_id"])

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

        salvar_game(session["game_id"], game)
        return {
            "state": game["state"],
            "pergunta": (
                game["perguntas"][0]["texto"] if game["state"] == "playing" else None
            ),
        }

    if game["state"] == "derrota":
        atualizar_dados(game["respostas"], resposta)
        deletar_game(session["game_id"])
        session.clear()
        return jsonify({"redirect": url_for("index")})

    if game["state"] == "vitoria":
        deletar_game(session["game_id"])
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

        salvar_game(session["game_id"], game)
        return {"state": "adivinhou", "chute": chute}

    # Checa se há perguntas disponíveis
    if len(game["perguntas"]) > 0:
        salvar_game(session["game_id"], game)
        return {"state": "playing", "pergunta": game["perguntas"][0]["texto"]}
    else:
        game["state"] = "derrota"
        salvar_game(session["game_id"], game)
        return {"state": "derrota"}

if __name__ == "__main__":
    app.run()