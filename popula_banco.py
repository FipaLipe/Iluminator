import os
import json

from dotenv import load_dotenv
import pandas as pd
from upstash_redis import Redis

load_dotenv()

r = Redis.from_env()

df = pd.read_excel("Dados_Iluminator.xlsx")

pessoas = []

for _, row in df.iterrows():
    nome = row["Nome"]

    atributos = row.drop("Nome").to_dict()

    atributos = {k: float(v) for k, v in atributos.items()}

    pessoas.append({
        "nome": nome,
        "atributes": atributos
    })

r.set("dataset:pessoas", json.dumps(pessoas))

print("Dataset salvo no Redis!")

print("Todos os dados foram enviados para o Redis!")
