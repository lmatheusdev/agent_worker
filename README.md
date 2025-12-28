# Worker Backend

## Agente de IA - Auxiliar de atendimento

O WorkChat é um agente de IA que atua como assistente de atendimento para os colabores da RDF Telecom.  
Respondendo a dúvidas e consultas e consultas dos setores de suporte ao cliente e financeiro.

## Stach usada

- Python 3.11.1
- langchain 1.2.0
- FastAPI 0.124.4
- uvicorn 0.38.0

## Como rodar

- git clone "[url](https://github.com/lmatheusdev/agent_worker.git)"
- cd agent_worker
- python -m venv .venv (criar ambiente virtual)
- crie um arquivo .env na raiz do projeto e adicione a chave da api llm
- python -m pip install python-dotenv (instala dotenv para carregar arquivos .env)

**Dependências:**

- pip install -q --upgrade langchain langchain-google-genai google-generativeai langchain_community faiss-cpu langchain-text-splitters langchain-huggingface==1.2.0
- pip install "fastapi[standard]"
- pip install "uvicorn[standard]"

**Executar:**

- uvicorn main:app --reload

## Resumo

O agente responde com base no contexto e no histórico de conversa. O contexto atualmente são dois arquivos .md contendo informações sobre os setores de atendimento e financeiro, como preços, tipos e caracteristicas dos planos de internet, e regras de boas práticas de atendimento. Atuamente são guardadas para o historico de conversa as últimas 10 mensagens do usuário e do agente.

**RAG - Retrieval Augmented Generation:**

- Retrieval: Busca no vectorstore (onde são armazenados os embeddings) o contexto relevante para a pergunta do usuário.
A lógica da leitura dos arquivos e da criação dos embeddings estão em "rag/ingest_docs.py".

- Augmented: injeta o contexto e o historico de conversa no prompt do agente.
A lógica de criação do prompt para o agente está em "services/llm.py".
A lógica do historico de conversa para o agente está em "services/chat_memory.py".

- Generation: gera a resposta do agente.
A lógica da invocação do agente e da resposta está em "services/llm.py".

**API:**

- FastAPI: cria uma API REST para o agente de IA.
A lógica da API está em "main.py" e "routes/chat.py".

- uvicorn: cria o servidor HTTP para a API.
