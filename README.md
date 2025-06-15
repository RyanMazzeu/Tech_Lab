# 💡 Desafio Técnico: Agente Bancário Inteligente

![image](https://github.com/user-attachments/assets/dd9dcd0c-c51d-4398-b353-1a3dcbefacf6)

Um agente de IA conversacional para o banco fictício _Banco Ágil, construído com o Google Agents Development Kit (ADK)_ e _modelos de linguagem avançados (LLMs)_.  
O agente é capaz de autenticar clientes, analisar pedidos de crédito, realizar cotações de câmbio e conduzir entrevistas para coleta de dados.

---

## 🗂️ Sumário
[Desafio Proposto](#desafio-proposto)

[📄 Visão Geral do Projeto](#visao-geral-do-projeto)

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

Este projeto foi desenvolvido como solução para o Desafio Técnico: Agente Bancário Inteligente, que propõe a criação de um sistema de atendimento virtual para um banco digital fictício, o Banco Ágil.

A proposta consiste em construir um agente inteligente capaz de compreender as intenções do cliente e acionar, de forma autônoma, os subagentes e ferramentas necessárias para resolver diferentes demandas bancárias.

A arquitetura foi construída utilizando o Google Agents Development Kit (ADK), um framework para desenvolvimento de agentes inteligentes modulares e escaláveis.

O sistema simula um time de especialistas, cada um responsável por uma área específica do atendimento bancário:

💳 Crédito — Consultas de limite e solicitações de aumento.

💱 Câmbio — Consultas de cotação do dólar em tempo real.

🤝 Entrevistas de Crédito — Reavaliação de perfil financeiro por meio de entrevistas guiadas.

O agente principal atua como um orquestrador, interpretando os comandos do usuário e encaminhando a solicitação ao agente ou ferramenta mais adequada.

### Estrutura Geral:

![image](https://github.com/user-attachments/assets/e56f2dda-2417-445a-847c-2d399d550219)

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

- #### agent.py:

  Esse é o núcleo do agente, sendo responsável por definir a sessão (conversa atual do agente, gerenciando memória, agentes, etc.) e o agente inicial, o autenticador (definido como root_agent para não sair do padrão definido pelo adk). O agente autenticador tem como sub-agentes (agentes que podem ser chamados à partir dele) o agente credito, cambio e entrevista, cada um com a sua devida especialização. O agente autenticador tem como ferramentas (funções python que ele pode invocar) a função autenticar_usuario, que recebe um cpf e uma data de nascimento e retorna os dados do usuário, permitindo assim que o agente possa autenticar pelo chat e passar o contexto para o agente mais adequado.

  #### agent_cambio.py:

  Arquivo responsável por definir o agente especializado em operações de câmbio.  
  Nele, é implementada a lógica para consultar a cotação do dólar em tempo real, utilizando uma API externa.  
  O agente recebe solicitações do agente principal, realiza a chamada à API e retorna a cotação atualizada ao usuário, garantindo respostas rápidas e precisas sobre valores de câmbio.

  Principais pontos:

  - Implementa a função de consulta de câmbio.
  - Integração com APIs externas para obter a cotação do dólar.
  - Retorna informações formatadas para o usuário final.
  - Atua apenas quando acionado pelo agente principal, mantendo o escopo restrito a operações de câmbio.

  #### agent_credito.py:

  Arquivo responsável por definir o agente especializado em operações de crédito.

  Nele, está implementada a lógica para:

  - Consultar o limite de crédito atual do cliente, utilizando informações do arquivo `clientes.csv`.
  - Registrar solicitações de aumento de limite em `solicitacoes_aumento_limite.csv`.
  - Avaliar pedidos de aumento de limite com base no score do cliente, consultando o arquivo `score_limite.csv`.
  - Aprovar ou rejeitar solicitações automaticamente, seguindo critérios definidos.
  - Em caso de rejeição, oferecer ao cliente a opção de ser encaminhado ao Agente de Entrevista de Crédito para reavaliação.

  Principais pontos:

  - Centraliza todas as operações relacionadas a crédito.
  - Garante que apenas clientes autenticados possam solicitar aumento de limite.

  #### agent_entrevista.py:

  Arquivo responsável por definir o agente especializado em entrevistas de crédito.

  Neste módulo, o agente conduz uma entrevista estruturada com o cliente para coletar informações financeiras detalhadas, essenciais para recalcular o score de crédito. O fluxo da entrevista inclui perguntas sobre renda mensal, tipo de emprego, despesas fixas, número de dependentes e dívidas ativas. Com base nas respostas, o agente calcula um novo score (de 0 a 1000) e atualiza o arquivo `clientes.csv` com o valor revisado.

  Principais pontos:

  - Realiza perguntas de forma sequencial e clara, garantindo a coleta de todos os dados necessários.
  - Valida as respostas fornecidas pelo cliente, solicitando correções em caso de inconsistências.
  - Calcula o novo score de crédito utilizando critérios definidos no sistema.
  - Atualiza o cadastro do cliente com o novo score, permitindo uma nova avaliação de crédito.
  - Atua apenas quando acionado pelo agente de crédito, mantendo o escopo restrito à reavaliação de perfil financeiro.

---

<a id="configuracao-de-apis"></a>

## 🔑 Configuração de APIs

O projeto é flexível quanto ao LLM que você pode usar, graças ao _LiteLLM_, que oferece compatibilidade com diversas APIs do mercado.

Para este projeto, utilizei _APIs gratuitas, como o \*\*Mistral_.

> _Observação:_ Usando um modelo pago, a precisão e performance podem melhorar consideravelmente.

### ✅ Variáveis necessárias (.env)

Crie um arquivo chamado .env no mesmo diretório do server.py (BancoAgil) com o seguinte conteúdo:

MISTRAL_API_KEY=xxxx  
TAVILY_API_KEY=xxxx  
GOOGLE_API_KEY=xxxx

### 📌 Links úteis para gerar suas API Keys:

- [🔑 Obter API Key do Tavily](https://app.tavily.com/home)
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
  adk web (no mesmo diretorio que os diretórios BancoAgil e BancoAgil_Front)
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

Para executar o projeto, primeiramente é necessário instalar todas as dependências Python listadas no arquivo requirements.txt localizado na pasta BancoAgil.
Caso deseje utilizar o frontend desenvolvido, basta acessar a pasta BancoAgil_Front e executar o comando npm install para instalar todas as dependências do projeto frontend.
Como o sistema foi desenvolvido utilizando o Google Agents Development Kit (ADK), a forma mais prática de realizar testes é por meio da ferramenta nativa do ADK. Para isso, basta executar o comando adk web na raiz do projeto, que irá disponibilizar um link com o agente “BancoAgil” ativo. Essa ferramenta permite visualizar e depurar todo o fluxo de atendimento do agente, facilitando o processo de desenvolvimento.
Para rodar a aplicação integrada com o frontend, é necessário iniciar o servidor backend, que é responsável por iniciar o agente e processar as requisições via API. Em paralelo, deve-se executar o comando npm i para instalar as dependencias do projeto e npm run dev dentro da pasta BancoAgil_Front para iniciar o servidor de desenvolvimento do frontend.

## Funcionamento pelo ADK WEB:

É de suma importância lembrar que para rodar com o adk WEB é necessário alterar as insportações do agent.py, adicionando um "." no inicio, exemplo:

from .agents.agente_cambio import create_exchange_agent # type: ignore

from .agents.agente_credito import create_credit_agent # type: ignore

from .agents.agente_entrevista import create_interview_agent # type: ignore

## Funcionamento pelo server:

É de suma importância lembrar que para rodar com o frontend, ou seja, gerando uma api para acessar o agente via requisição web, é necessário alterar as insportações do agent.py, removendo "." no inicio, exemplo:

from agents.agente_cambio import create_exchange_agent # type: ignore

from agents.agente_credito import create_credit_agent # type: ignore

from agents.agente_entrevista import create_interview_agent # type: ignore

## Testes:

### 1. Autenticação de Cliente (Agente de Triagem)

- [✔️] Cliente fornece CPF e data de nascimento válidos e é autenticado com sucesso.
![image](https://github.com/user-attachments/assets/5343fd51-99a0-4ea2-98a7-4e1711f3a935)


- [✔️] Cliente fornece CPF ou data de nascimento inválidos e recebe mensagem de erro.
![image](https://github.com/user-attachments/assets/e5d0d59d-aec5-41dc-9b78-eb95e41d38b4)

- [❌] Cliente falha na autenticação 3 vezes e o atendimento é encerrado. Não encontrei ferramentas que permitam ao próprio ADK encerrar a sessão definitivamente pelo chat. Portanto, não consegui cumprir esse objetivo diretamente. No entanto, no frontend, adicionei um botão de encerrar sessão que funciona corretamente.
![image](https://github.com/user-attachments/assets/1cc28ea5-9a36-4dfd-b4c6-6997c148230f)


### 2. Consulta de Limite de Crédito (Agente de Crédito)

- [✔️] Cliente autenticado solicita consulta de limite de crédito e recebe o valor correto.
  ![image](https://github.com/user-attachments/assets/6321c488-b7d9-4068-9b0f-3f66f807bf9c)

- [✔️] Cliente não autenticado tenta consultar limite e é impedido.
  ![image](https://github.com/user-attachments/assets/68561b9f-1add-4349-abda-dbefa1fbdd2f)


### 3. Solicitação de Aumento de Limite (Agente de Crédito)

- [✔️] Cliente autenticado solicita aumento de limite e pedido é registrado em `solicitacoes_aumento_limite.csv`.
![image](https://github.com/user-attachments/assets/57e60b01-3382-41fe-8748-239fdd5ddb1b)
![image](https://github.com/user-attachments/assets/31a41eda-d175-4f87-828d-ec1ecb213715)
![image](https://github.com/user-attachments/assets/da6acc2b-918d-42d9-b1ae-10ced9de37cd)

- [✔️] Pedido de aumento é aprovado automaticamente (score suficiente).
![image](https://github.com/user-attachments/assets/74932e10-21ed-42b7-be07-e5d1fc2e9a0f)
![image](https://github.com/user-attachments/assets/a6622b6f-1127-4ccf-b851-0b257f2f3b52)

- [✔️] Pedido de aumento é rejeitado automaticamente (score insuficiente).
![image](https://github.com/user-attachments/assets/c8b4a754-925c-4d12-87c7-6324dd1be306)

- [✔️] Após rejeição, cliente é convidado a participar da entrevista de crédito.
![image](https://github.com/user-attachments/assets/948359d3-5c4d-428b-846d-63df195992c2)


### 4. Entrevista de Crédito (Agente de Entrevista)

- [✔️] Cliente aceita participar da entrevista após rejeição do aumento de limite.
![image](https://github.com/user-attachments/assets/1ce99377-0c64-4717-afc8-f21be231556d)
![image](https://github.com/user-attachments/assets/90191160-f09e-47b8-ab86-60ed8250b25b)
![image](https://github.com/user-attachments/assets/475fc403-4f1c-402b-bbeb-67474a3cf313)

- [✔️] Todas as perguntas da entrevista são feitas (renda, emprego, despesas, dependentes, dívidas).
![image](https://github.com/user-attachments/assets/0a665d3c-9631-4d60-98a0-5a3cdbfe0839)

- [✔️] Novo score é calculado corretamente e atualizado em `clientes.csv`.
![image](https://github.com/user-attachments/assets/0a9dce58-0d26-41b9-85f2-b33ba37477e1)

![image](https://github.com/user-attachments/assets/762790b7-0c8e-4460-bec6-f360f4196e9a)



### 5. Consulta de Câmbio (Agente de Câmbio)

- [✔️] Cliente autenticado solicita cotação do dólar e recebe valor atualizado da API externa.
![image](https://github.com/user-attachments/assets/7dd1e4a4-7cfb-450a-9de2-1e056fdac13f)


### 6. Fluxo de Atendimento Único

- [✔️] O atendimento é conduzido de forma única, mesmo com múltiplos agentes atuando.
- [❌] O agente não deve falar que transferiu para outro agente.
- [✔️] O contexto do cliente é mantido entre os agentes.

### 7. Controle de Escopo dos Agentes

- [✔️] Cada agente só executa funções dentro do seu escopo (ex: agente de câmbio não acessa dados de crédito).

### 8. Frontend

- [✔️] Frontend comunica corretamente com o backend.
- [✔️] Mensagens e fluxos são exibidos corretamente ao usuário.
![image](https://github.com/user-attachments/assets/8e991017-2f85-4e47-bfc4-40f9f5e7d6fe)
