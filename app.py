import os

from dotenv import load_dotenv
from langchain_ollama import ChatOllama

load_dotenv()

api_key = os.getenv("OLLAMA_API_KEY")

if not api_key:
    raise ValueError("OLLAMA_API_KEY est introuvable dans .env")

llm = ChatOllama(
    base_url="https://api.ollama.com",
    model="gemma4:31b-cloud",
    temperature=0,
)

response = llm.invoke(
    "Explique-moi simplement ce qu'est le machine learning."
)

print(response.content)