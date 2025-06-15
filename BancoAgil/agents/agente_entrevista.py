import csv
import json
import os
from dotenv import load_dotenv
import pandas as pd
from tavily import TavilyClient
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from datetime import datetime
from typing import Dict, Tuple

import pandas as pd
from datetime import datetime
from typing import Dict


def consultar_dados_cliente(cpf: str) -> Dict:
    """
    Consulta os dados de um cliente.

    Args:
        cpf (str): CPF do cliente.

    Returns:
        dict: Dados do cliente ou mensagem de erro.
    """
    try:
        script_dir = os.path.dirname(__file__)
        dados_dir = os.path.abspath(os.path.join(script_dir, '..', 'dados'))
        clientes_path = os.path.join(dados_dir, 'clientes.csv')

        df_clientes = pd.read_csv(clientes_path, dtype={'cpf': str})
        dados_cliente = df_clientes[df_clientes['cpf'] == cpf]

        if dados_cliente.empty:
            return {'status': 'erro', 'mensagem': f"Cliente com CPF {cpf} não encontrado."}

        return dados_cliente.to_dict(orient='records')[0]

    except FileNotFoundError as e:
        return {'status': 'erro', 'mensagem': f"Arquivo não encontrado: {e.filename}"}
    except Exception as e:
        return {'status': 'erro', 'mensagem': f"Ocorreu um erro: {e}"}


def calcular_score(cpf: str,
                   renda_mensal: float,
                   despesas_mensais: float,
                   tipo_emprego: str,
                   num_dependentes: int,
                   tem_dividas: str):
    tipo_emprego = tipo_emprego.lower()
    tem_dividas = tem_dividas.lower()
    peso_renda = 30
    peso_emprego = {
        "formal": 300,
        "autônomo": 200,
        "desempregado": 0
    }
    peso_dependentes = {
        0: 100,
        1: 80,
        2: 60,
        "3+": 30
    }
    peso_dividas = {
        "sim": -100,
        "s": -100,
        "não": 100,
        "nao": 100,
        "n": 100
    }

    if num_dependentes >= 3:
        dependente_score = peso_dependentes["3+"]
    else:
        dependente_score = peso_dependentes[num_dependentes]

    score = (
        (renda_mensal / (despesas_mensais + 1)) * peso_renda +
        peso_emprego[tipo_emprego] +
        dependente_score +
        peso_dividas[tem_dividas]
    )

    score = max(0, min(1000, score))
    return score


def atualizar_score_cliente(cpf: str, novo_score: float) -> bool:
 
    script_dir = os.path.dirname(__file__)
    dados_dir = os.path.abspath(os.path.join(script_dir, '..', 'dados'))
    
    caminho_arquivo = os.path.join(dados_dir, 'clientes.csv')
    try:
        # Lê todos os clientes
        with open(caminho_arquivo, mode='r', encoding='utf-8') as f:
            clientes = list(csv.DictReader(f))
        cpf_limpo = ''.join(filter(str.isdigit, cpf))
        atualizado = False
        # Atualiza o score do cliente correto
        for cliente in clientes:
            if cliente['cpf'] == cpf_limpo:
                cliente['score'] = str(int(novo_score))
                atualizado = True
                break
        if not atualizado:
            return False
        # Escreve de volta no CSV
        with open(caminho_arquivo, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=clientes[0].keys())
            writer.writeheader()
            writer.writerows(clientes)
        return True
    except Exception as e:
        print(f"Erro ao atualizar score: {e}")
        return False


def calcular_e_atualizar_score(cpf: str,
                                renda_mensal: float,
                                despesas_mensais: float,
                                tipo_emprego: str,
                                num_dependentes: int,
                                tem_dividas: str) -> Tuple[bool, float]:
    """
    Calcula o score do cliente e atualiza o valor no arquivo clientes.csv.
    Retorna True se atualizar, False caso contrário.
    # Especificação clara dos inputs esperados:
    # - cpf: str, deve ser o CPF do cliente no formato "XXX.XXX.XXX-YY" ou apenas números.
    # - renda_mensal: float, valor da renda mensal do cliente (ex: 3500.0).
    # - despesas_mensais: float, valor das despesas mensais do cliente (ex: 1200.0).
    # - tipo_emprego: str, deve ser OBRIGATÓRIAMENTE E APENAS um dos valores: "formal", "autônomo" ou "desempregado".
    # - num_dependentes: int, número de dependentes do cliente (ex: 0, 1, 2, 3...).
    # - tem_dividas: str, deve ser "sim" ou "não" indicando se o cliente possui dívidas.
     # Exemplo de uso das funções de score
    cpf = "123.456.789-00"
    renda_mensal = 5000.0
    despesas_mensais = 2000.0
    tipo_emprego = "formal"
    num_dependentes = 1
    tem_dividas = "não"

    # Exemplo usando calcular_e_atualizar_score
    sucesso = calcular_e_atualizar_score(
        cpf=cpf,
        renda_mensal=renda_mensal,
        despesas_mensais=despesas_mensais,
        tipo_emprego=tipo_emprego,
        num_dependentes=num_dependentes,
        tem_dividas=tem_dividas
    )
    if sucesso:
        print("Score atualizado com sucesso!")
    else:
        print("Falha ao atualizar o score do cliente.")
    """
    score = calcular_score(
        cpf=cpf,
        renda_mensal=renda_mensal,
        despesas_mensais=despesas_mensais,
        tipo_emprego=tipo_emprego,
        num_dependentes=num_dependentes,
        tem_dividas=tem_dividas
    )
    return atualizar_score_cliente(cpf, score), score
    
with open(os.path.join(os.path.dirname(__file__), "../descriptions/entrevista.txt"), encoding="utf-8") as f:
    agent_description = f.read()


with open(os.path.join(os.path.dirname(__file__), "../instructions/entrevista.txt"), encoding="utf-8") as f:
    agent_instruction = f.read()

def create_interview_agent(llm_model) -> Agent:
   return Agent(
    name="agente_entrevista",
    model=llm_model,
    description=agent_description,
    instruction=agent_instruction,
    tools=[FunctionTool(func=calcular_e_atualizar_score), 
           FunctionTool(func=consultar_dados_cliente)],
)

