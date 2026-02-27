import os

from dotenv import load_dotenv
import pandas as pd
import redis

load_dotenv()

redis_host = os.environ.get("REDIS_HOST")
redis_port = int(os.environ.get("REDIS_PORT", 6379))
redis_password = os.environ.get("REDIS_PASSWORD", None)

r = redis.Redis(
    host=redis_host,
    port=redis_port,
    password=redis_password,
    decode_responses=True,
)

df = pd.read_excel("Dados_Iluminator.xlsx")

for _, row in df.iterrows():
    pessoa_nome = row["Nome"]
    pessoa_data = row.to_dict()

    r.hset(f"pessoa:{pessoa_nome}", mapping=pessoa_data)

print("Todos os dados foram enviados para o Redis!")
