import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # Carrega variáveis do .env

def get_client() -> OpenAI:
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
