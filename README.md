# 💡 Desafio Técnico: Agente Bancário Inteligente

![image](https://github.com/user-attachments/assets/dd9dcd0c-c51d-4398-b353-1a3dcbefacf6)

Um agente de IA conversacional para o banco fictício _Banco Ágil, construído com o \*\*Google Agents Development Kit (ADK)_ e _modelos de linguagem avançados (LLMs)_.  
O agente é capaz de autenticar clientes, analisar pedidos de crédito, realizar cotações de câmbio e conduzir entrevistas para coleta de dados.

---

## 🗂️ Sumário

[📄 Visão Geral do Projeto](#visao-geral-do-projeto)

[🏛️ Arquitetura do Sistema](#arquitetura-do-sistema)

[🔑 Configuração de APIs](#configuracao-de-apis)

[🔗 Como rodar a Aplicação](#como-rodar-a-aplicacao)

---

<a id="desafio-proposto"></a>

## Desafio Proposto

### 🔹 Cenário

Criar um sistema de atendimento para um banco digital fictício (**Banco Ágil**) utilizando agentes de IA.  
Cada agente tem uma função específica, e o atendimento simula uma interação única, mesmo com múltiplos agentes atuando nos bastidores.

---

### 🤖 Agentes do Sistema

<a id="agente-triagem"></a>

#### 🔑 Agente de Triagem

- Autentica o cliente (CPF e data de nascimento, usando `clientes.csv`).
- Fluxo:
  1. Saudação
  2. Coleta CPF e data de nascimento
  3. Validação na base
  4. Redireciona ao agente adequado
  5. Até 3 tentativas de autenticação

---

<a id="agente-credito"></a>

#### 💳 Agente de Crédito

- Consulta limite de crédito atual.
- Solicitação de aumento de limite:
  - Registra pedido em `solicitacoes_aumento_limite.csv`.
  - Aprova ou rejeita com base no score (`score_limite.csv`).
- Se rejeitado, oferece redirecionamento para o Agente de Entrevista de Crédito.

---

<a id="agente-entrevista"></a>

#### 🗣️ Agente de Entrevista de Crédito

- Coleta dados financeiros para recalcular o score:
  - Renda mensal
  - Tipo de emprego
  - Despesas fixas
  - Número de dependentes
  - Dívidas ativas
- Calcula novo score (0 a 1000) e atualiza `clientes.csv`.

---

<a id="agente-cambio"></a>

#### 💱 Agente de Câmbio

- Consulta cotação do dolar em tempo real via API externa.

---

### 📜 Regras Gerais

- Atendimento único, mesmo com múltiplos agentes atuando.
- Tom educado, objetivo e controle de erros.
- Usuário pode encerrar a qualquer momento.
- Agentes agem dentro de seus escopos.

---

<a id="visao-geral-do-projeto"></a>

## 📄 Visão Geral do Projeto

Este projeto é uma solução para o _"Desafio Técnico: Agente Bancário Inteligente", que visa criar um sistema de atendimento ao cliente para um banco digital fictício, o \*\*Banco Ágil_.

A solução utiliza o _Google ADK_, um framework para desenvolver e implementar agentes de IA.  
O sistema interpreta as intenções do cliente e aciona as ferramentas e subagentes apropriados para cada tarefa, simulando um time de especialistas em:

- _Crédito_
- _Câmbio_
- _Entrevistas_

---

<a id="arquitetura-do-sistema"></a>

## 🏛️ Arquitetura do Sistema

A espinha dorsal deste projeto é construída sobre o _Google Agents Development Kit (ADK)_, que permite a criação de sistemas de agentes complexos e modulares.

### Estrutura Geral:

- Um _agente principal (root_agent)_ que orquestra a interação.
- Vários _subagentes especialistas_ para tarefas específicas.
- Integração com _diferentes LLMs_ via _LiteLLM_.

### Principais Arquivos:

- agent.py → Onde todos os agentes e ferramentas são definidos e conectados.
- server.py → Camada de API para comunicação externa (ex: frontend ou chatbot UI).
- agente_cambio.py
- agente_credito.py
- agente_entrevista.py
- descrições e instruções em arquivos separados (pasta descriptions e instructions).
- Frontend básico usando o vite como acelerador.

- #### Agent.py:
  Nesse arquivo foi definido o agente autenticador

---

<a id="configuracao-de-apis"></a>

## 🔑 Configuração de APIs

O projeto é flexível quanto ao LLM que você pode usar, graças ao _LiteLLM_, que oferece compatibilidade com diversas APIs do mercado.

Para este projeto, utilizei _APIs gratuitas, como o \*\*Mistral_.

> _Observação:_ Usando um modelo pago, a precisão e performance podem melhorar consideravelmente.

### ✅ Variáveis necessárias (.env)

Crie um arquivo chamado .env no mesmo diretório do server.py com o seguinte conteúdo:

MISTRAL_API_KEY=xxxx  
TAVILY_API_KEY=xxxx  
GOOGLE_API_KEY=xxxx

### 📌 Links úteis para gerar suas API Keys:

- [🔑 Obter API Key do Mistral](https://console.mistral.ai/api-keys)
- [📈 Tabela de Preços do Mistral](https://mistral.ai/pricing#api-pricing)
- [🔑 Gerar API Key do Google Gemini](https://aistudio.google.com/app/apikey)
- [📚 Documentação dos Modelos Gemini](https://ai.google.dev/gemini-api/docs/models)
- [✅ Lista de LLMs suportados pelo LiteLLM](https://docs.litellm.ai/docs/providers/)

<a id="como-rodar-a-aplicacao"></a>

## 🔗 Como rodar a Aplicação

1. **Clone o repositório:**

```bash
git clone https://github.com/RyanMazzeu/Tech_Lab.git
cd Tech_Lab-main
```

2. **Instale as dependências do backend:**

```bash
cd BancoAgil
pip install -r requirements.txt
```

3. **Configure as variáveis de ambiente:**

- Crie um arquivo `.env` na pasta `BancoAgil` com suas chaves de API (veja seção anterior).

4. **Execute o backend:**

- Para testes com a ferramenta nativa do ADK:
  ```bash
  adk web
  ```
- Para rodar o servidor de API:
  ```bash
  python server.py
  ```

5. **(Opcional) Rode o frontend:**

```bash
cd ../BancoAgil_Front
npm install
npm run dev
```

6. **Acesse a aplicação:**

- Use o link gerado pelo ADK ou acesse o frontend em `http://localhost:5173`.

---

Para executar o projeto, primeiramente é necessário instalar todas as dependências Python listadas no arquivo requirements.txt localizado na pasta BancoAgil.
Caso deseje utilizar o frontend desenvolvido, basta acessar a pasta BancoAgil_Front e executar o comando npm install para instalar todas as dependências do projeto frontend.
Como o sistema foi desenvolvido utilizando o Google Agents Development Kit (ADK), a forma mais prática de realizar testes é por meio da ferramenta nativa do ADK. Para isso, basta executar o comando adk web na raiz do projeto, que irá disponibilizar um link com o agente “BancoAgil” ativo. Essa ferramenta permite visualizar e depurar todo o fluxo de atendimento do agente, facilitando o processo de desenvolvimento.
Para rodar a aplicação integrada com o frontend, é necessário iniciar o servidor backend, que é responsável por iniciar o agente e processar as requisições via API. Em paralelo, deve-se executar o comando npm i para instalar as dependencias do projeto e npm run dev dentro da pasta BancoAgil_Front para iniciar o servidor de desenvolvimento do frontend.


## Funcionamento pelo ADK WEB:

É de suma importância lembrar que para rodar com o adk WEB é necessário alterar as insportações do agent.py, adicionando um "." no inicio, exemplo:

from .agents.agente_cambio import create_exchange_agent  # type: ignore

from .agents.agente_credito import create_credit_agent  # type: ignore

from .agents.agente_entrevista import create_interview_agent  # type: ignore


![alt text](image.png)![alt text](image-1.png)

## Funcionamento pelo server:

É de suma importância lembrar que para rodar com o frontend, ou seja, gerando uma api para acessar o agente via requisição web, é necessário alterar as insportações do agent.py, removendo "." no inicio, exemplo:

from agents.agente_cambio import create_exchange_agent  # type: ignore

from agents.agente_credito import create_credit_agent  # type: ignore

from agents.agente_entrevista import create_interview_agent  # type: ignore