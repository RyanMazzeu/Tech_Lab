#agent.py
import json
import os
import csv
from dotenv import load_dotenv
import dateparser

# Importações do ADK
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService  # <-- Classe CORRETA
from google.adk.tools import FunctionTool, agent_tool
from google.adk.models.lite_llm import LiteLlm

# .agents para rodar com adk web e agents para rodar com server
from agents.agente_cambio import create_exchange_agent  # type: ignore
from agents.agente_credito import create_credit_agent  # type: ignore
from agents.agente_entrevista import create_interview_agent  # type: ignore

load_dotenv()
APP_NAME = "BancoAgil"
USER_ID = "12345"
SESSION_ID = "123344"

# --- 1. Configuração Inicial --- https://docs.litellm.ai/docs/providers/
llm_model = LiteLlm(model='mistral/mistral-large-latest', api_key=os.getenv('MISTRAL_API_KEY'))
#https://console.mistral.ai/api-keys
#https://mistral.ai/pricing#api-pricing

#llm_model = 'gemini-2.0-flash'
#https://aistudio.google.com/app/apikey
#https://ai.google.dev/gemini-api/docs/models

session_service = InMemorySessionService()
session = session_service.create_session(
    app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
)

# --- 2. Ferramentas de Negócio (As Funções Puras) ---

def autenticar_usuario(cpf: str, data_nascimento: str) -> str:
  """
  Verifica as credenciais do cliente em um arquivo CSV.
  Retorna um JSON com o status da autenticação, nome, CPF, score e limite_atual do cliente.
  """
  # Cria o arquivo de dados de exemplo se não existir, para garantir a execução.
  caminho_dados = os.path.join(os.path.dirname(__file__), "dados")
  if not os.path.exists(caminho_dados):
    os.makedirs(caminho_dados)
  caminho_csv = os.path.join(caminho_dados, "clientes.csv")

  try:
    cpf_limpo = ''.join(filter(str.isdigit, cpf))
    data_nasc_usuario_obj = dateparser.parse(data_nascimento, languages=['pt'])
    if not data_nasc_usuario_obj:
      return json.dumps({"autenticado": False, "mensagem": "Formato de data inválido."})

    with open(caminho_csv, mode='r', newline='', encoding='utf-8') as f:
      reader = csv.DictReader(f)
      for row in reader:
        data_nasc_csv_obj = dateparser.parse(row["data_nascimento"].strip())
        if row["cpf"].strip() == cpf_limpo and data_nasc_csv_obj.date() == data_nasc_usuario_obj.date():
          # Retorna todos os dados do usuário autenticado
          resultado = {"autenticado": True}
          resultado.update(row)
          return json.dumps(resultado)

    return json.dumps({"autenticado": False, "mensagem": "CPF ou data de nascimento não correspondem."})
  except Exception as e:
    return json.dumps({"autenticado": False, "mensagem": f"Erro técnico: {e}"})


cambio = create_exchange_agent(llm_model)
credito = create_credit_agent(llm_model)
entrevista = create_interview_agent(llm_model)

# --- 3. Os Trabalhadores Especialistas (Sub-Agentes) ---
from google.genai import types

#Não funciona!
def encerrar_sessao():
    """
    Encerra a sessão atual. SÓ DEVE SER CHAMADA SE O USUÁRIO QUISER ENCERRAR A SESSÃO.
    """
    session_service.delete_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    
    return "Sessão encerrada com sucesso."

# Lê a descrição do arquivo externo
with open(os.path.join(os.path.dirname(__file__), "descriptions", "root.txt"), encoding="utf-8") as f:
  root_description = f.read()
with open(os.path.join(os.path.dirname(__file__), "instructions", "root.txt"), encoding="utf-8") as f:
  root_instruction = f.read()


root_agent = Agent(
  name="root_agent",
  model=llm_model,
  description=root_description,
  instruction=root_instruction,
  generate_content_config=types.GenerateContentConfig(
  temperature=0.2,  # More deterministic output
  max_output_tokens=250

  ),
  tools=[FunctionTool(func=autenticar_usuario), 
         FunctionTool(func=encerrar_sessao)],
  sub_agents=[entrevista, credito, cambio]
)

# --- 5. Runner (Executor) ---
# Este objeto 'runner' é tudo que precisa ser exportado deste arquivo.
runner = Runner(
  agent=root_agent,
  app_name=APP_NAME,
  session_service=session_service,
)

