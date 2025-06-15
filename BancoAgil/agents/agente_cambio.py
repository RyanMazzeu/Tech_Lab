# agents/agente_cambio.py

import json
import os
from dotenv import load_dotenv
from tavily import TavilyClient
from google.adk.agents import Agent
from google.adk.tools import FunctionTool

load_dotenv()

def obter_cotacao_dolar() -> str:
    """Busca a cotação atual do dólar."""
    try:
        client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        response = client.search(query="cotação do dólar comercial para real hoje")
        return json.dumps({"cotacao_info": response["results"][0]["content"]})
    except Exception as e:
        return json.dumps({"erro": f"Falha ao obter cotação: {e}"})

with open(os.path.join(os.path.dirname(__file__), "../descriptions/cambio.txt"), encoding="utf-8") as f:
    agent_description = f.read()


with open(os.path.join(os.path.dirname(__file__), "../instructions/cambio.txt"), encoding="utf-8") as f:
    agent_instruction = f.read()

def create_exchange_agent(llm_model):
    """Cria e retorna uma instância do Agente de Câmbio."""
    return Agent(
        name="agente_cambio",
        model=llm_model,
        description=agent_description,
        instruction=agent_instruction,

        tools=[FunctionTool(func=obter_cotacao_dolar)],
    )