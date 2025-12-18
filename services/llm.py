import os
from dotenv import load_dotenv
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
import time


load_dotenv()
api_Key = os.getenv("OPENAI_API_KEY")

BASE_DIR = os.path.dirname(__file__)
VECTOR_DIR = os.path.join(BASE_DIR, "../rag/vectorstore")

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vectorstore = FAISS.load_local(
    VECTOR_DIR,
    embeddings,
    allow_dangerous_deserialization=True
)


llm = ChatGoogleGenerativeAI( # cria a ia
    model="gemini-2.5-flash", # modelo da ia
    temperature=0.0, # temperatura da ia
    api_key= api_Key # chave da api
)

def retrieve_context(query: str, min_score: float = 0.35):
    results = vectorstore.similarity_search_with_score(query, k=4)

    filtered_docs = [
        doc for doc, score in results if score >= min_score
    ]
    return "\n\n".join(d.page_content for d in filtered_docs)

async def run_agent(user_message: str):
    context = retrieve_context(user_message)

    if not context:
        return (
            "Não encontrei essa informação nos documentos disponíveis. "
            "Posso te ajudar com outra dúvida?"
        )

    prompt = f"""
Você é um agente de Service Desk.
Responda de forma objetiva e clara.
Use SOMENTE o contexto abaixo.

Contexto:
{context}

Pergunta do usuário:
{user_message}
"""

    response = await llm.ainvoke(prompt)
    return response.content