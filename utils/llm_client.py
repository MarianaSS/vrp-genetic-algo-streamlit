import streamlit as st

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # Carrega variáveis do .env

def get_client() -> OpenAI:
    return OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
