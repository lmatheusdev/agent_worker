import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

BASE_DIR = os.path.dirname(__file__)
VECTOR_DIR = os.path.join(BASE_DIR, "../rag/vectorstore")

if not API_KEY:
    print("AVISO: API_KEY não encontrada!")

embeddings = None
vectorstore = None
llm = None

def init_rag():
    global embeddings, vectorstore, llm

    if embeddings is None:
        print("Carregando modelo de embeddings...")
        embeddings = HuggingFaceEndpointEmbeddings(
            huggingfacehub_api_token=HF_API_KEY, 
            model="sentence-transformers/all-MiniLM-L6-v2",
        )

    if vectorstore is None:
        print("Carregando vectorstore...")
        vectorstore = FAISS.load_local(
            VECTOR_DIR,
            embeddings,
            allow_dangerous_deserialization=True
        )

    if llm is None:
        print("Inicializando LLM...")
        llm = ChatGoogleGenerativeAI( # cria a ia
            model="gemini-2.5-flash", # modelo da ia
            temperature=0.0, # temperatura da ia
            api_key= API_KEY # chave da api
        )

    try:
        vectorstore.similarity_search("warmup", k=1)
        print("RAG inicializado com sucesso")
    except Exception as e:
        print("Erro ao inicializar o RAG:", str(e))




def retrieve_context(query: str, min_score: float = 0.35):
    results = vectorstore.similarity_search_with_score(query, k=4)

    filtered_docs = [
        doc for doc, score in results if score >= min_score
    ]
    return "\n\n".join(d.page_content for d in filtered_docs)

def format_history(chat_history):
    return "\n".join(
        f"{m['role']}: {m['content']}"
        for m in chat_history
    )

async def run_agent(question: str, chat_history: list):
    context = retrieve_context(question)

    if not context:
        return (
            "Não encontrei essa informação nos documentos disponíveis. "
            "Posso te ajudar com outra dúvida?"
        )

    prompt = f"""
Você é um agente que deve atuar como assistente de atendimento para os colabores da RDF Telecom.
Quando o contexto contiver tabelas, extraia e interprete os valores para responder de forma clara e direta.
Se houver múltiplos valores, apresente um resumo objetivo.
Responda de forma clara, objetiva e mantendo coerência com a conversa.
Responda usando o histórico de conversa e o contexto abaixo.


Histórico de conversa:
{format_history(chat_history)}

Contexto:
{context}

Pergunta atual do usuário:
{question}
"""

    response = await llm.ainvoke(prompt)
    return response.content