import uuid

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, session, url_for
from flask_session import Session
import os
from redis import Redis

load_dotenv()

redis_host = os.environ.get("REDIS_HOST")
redis_port = int(os.environ.get("REDIS_PORT", 6379))
redis_password = os.environ.get("REDIS_PASSWORD", None)

r = Redis(
    host=redis_host,
    port=redis_port,
    password=redis_password,
    decode_responses=True,
)

games_cache = {}


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
    chave_pessoa = f"pessoa:{pessoa}"
    if not r.exists(chave_pessoa):
        inicial = {pergunta: 0 for pergunta in respostas.keys()}
        r.hset(chave_pessoa, mapping=inicial)

    for pergunta_nome, valor in respostas.items():
        r.hincrbyfloat(chave_pessoa, pergunta_nome, valor)


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
    pessoas = []

    for chave in r.scan_iter("pessoa:*"):
        nome = chave.split("pessoa:")[1]
        dados = r.hgetall(chave)
        dados.pop("Nome", None)

        atributos = {k: float(v) for k, v in dados.items()}

        pessoas.append({"nome": nome, "prob": 1.0, "atributes": atributos})

    return pessoas


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

app.config["SESSION_TYPE"] = "redis"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_USE_SIGNER"] = True

app.config["SESSION_REDIS"] = Redis(
    host=os.environ.get("REDIS_HOST"),
    port=int(os.environ.get("REDIS_PORT", 6379)),
    password=os.environ.get("REDIS_PASSWORD"),
)

Session(app)


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

    games_cache[game_id] = {
        "pessoas": pessoas,
        "perguntas": perguntas,
        "respostas": {},
        "contador": 0,
        "state": "playing",
    }

    session["game_id"] = game_id

    return {"message": "Jogo iniciado"}


@app.route("/api/pergunta")
def pergunta():
    game = games_cache[session["game_id"]]
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
    game = games_cache[session["game_id"]]

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

        games_cache[session["game_id"]] = game
        return {
            "state": game["state"],
            "pergunta": (
                game["perguntas"][0]["texto"] if game["state"] == "playing" else None
            ),
        }

    if game["state"] == "derrota":
        atualizar_dados(game["respostas"], resposta)
        games_cache.pop(session["game_id"], None)
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

        games_cache[session["game_id"]] = game
        return {"state": "adivinhou", "chute": chute}

    # Checa se há perguntas disponíveis
    if len(game["perguntas"]) > 0:
        games_cache[session["game_id"]] = game
        return {"state": "playing", "pergunta": game["perguntas"][0]["texto"]}
    else:
        game["state"] = "derrota"
        games_cache[session["game_id"]] = game
        return {"state": "derrota"}
