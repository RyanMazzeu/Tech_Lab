import os
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime
from typing import Dict

from google.adk.agents import Agent
from google.adk.tools import FunctionTool


# Carrega variáveis de ambiente
load_dotenv()


def solicitar_novo_limite(cpf: str, novo_limite: float) -> Dict:
    """
    Processa uma solicitação de aumento de limite de crédito.

    Args:
        cpf (str): CPF do cliente.
        novo_limite (float): Novo limite solicitado.

    Returns:
        dict: Resultado da operação com status, mensagem e dados.
    """
    try:
        # Caminhos dos arquivos
        script_dir = os.path.dirname(__file__)
        dados_dir = os.path.abspath(os.path.join(script_dir, '..', 'dados'))

        clientes_path = os.path.join(dados_dir, 'clientes.csv')
        score_limites_path = os.path.join(dados_dir, 'score_limites.csv')
        solicitacoes_path = os.path.join(dados_dir, 'solicitacoes_aumento_limite.csv')

        # Ler dados
        df_clientes = pd.read_csv(clientes_path, dtype={'cpf': str})
        df_score_limites = pd.read_csv(score_limites_path)

        dados_cliente = df_clientes[df_clientes['cpf'] == cpf]

        if dados_cliente.empty:
            return {'status': 'erro', 'mensagem': f"Cliente com CPF {cpf} não encontrado."}

        limite_atual = dados_cliente['limite_atual'].iloc[0]
        score_cliente = dados_cliente['score'].iloc[0]

        # Regras de negócio
        if novo_limite <= limite_atual:
            status = 'rejeitado'
            mensagem = "Operação não permitida: não é possível solicitar redução de limite."
        else:
            # Buscar limite máximo permitido pelo score
            limite_maximo_score = None
            for _, row in df_score_limites.iterrows():
                faixa = row['faixa_score']
                min_score, max_score = map(int, faixa.split('-'))
                if min_score <= score_cliente <= max_score:
                    limite_maximo_score = row['limite_maximo']
                    break

            if limite_maximo_score is None:
                return {'status': 'erro', 'mensagem': 'Faixa de score não encontrada.'}

            if novo_limite <= limite_maximo_score:
                status = 'aprovado'
                mensagem = f"Pedido APROVADO! O novo limite de R$ {novo_limite:.2f} foi concedido."

                # Atualiza limite no CSV
                index_cliente = dados_cliente.index[0]
                df_clientes.loc[index_cliente, 'limite_atual'] = novo_limite
                df_clientes.to_csv(clientes_path, index=False)

            else:
                status = 'rejeitado'
                mensagem = (f"Pedido REJEITADO. O limite solicitado (R$ {novo_limite:.2f}) "
                            f"excede o máximo permitido (R$ {limite_maximo_score:.2f}) "
                            f"para sua faixa de score.")

        # Registrar solicitação
        nova_solicitacao = {
            'cpf_cliente': cpf,
            'data_hora_solicitacao': datetime.now().isoformat(),
            'limite_atual': limite_atual,
            'novo_limite_solicitado': novo_limite,
            'status_pedido': status
        }
        df_solicitacao = pd.DataFrame([nova_solicitacao])
        header = not os.path.exists(solicitacoes_path)
        df_solicitacao.to_csv(solicitacoes_path, mode='a', header=header, index=False)

        return {
            'status': status,
            'mensagem': mensagem,
            'cpf': cpf,
            'limite_atual': limite_atual,
            'novo_limite_solicitado': novo_limite
        }

    except FileNotFoundError as e:
        return {'status': 'erro', 'mensagem': f"Arquivo não encontrado: {e.filename}"}
    except Exception as e:
        return {'status': 'erro', 'mensagem': f"Ocorreu um erro: {e}"}


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


with open(os.path.join(os.path.dirname(__file__), "../descriptions/credito.txt"), encoding="utf-8") as f:
    agent_description = f.read()


with open(os.path.join(os.path.dirname(__file__), "../instructions/credito.txt"), encoding="utf-8") as f:
    agent_instruction = f.read()


def create_credit_agent(llm_model):
    return Agent(
        name="agente_credito",
        model=llm_model,
        description=agent_description,
        instruction=agent_instruction,
        tools=[
            FunctionTool(func=solicitar_novo_limite),
            FunctionTool(func=consultar_dados_cliente)
        ]
    )
