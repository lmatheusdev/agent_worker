import os
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough


load_dotenv()
api_Key = os.getenv("OPENAI_API_KEY")

loader = DirectoryLoader(
    path="docs/",
    glob="**/*.pdf",
    loader_cls=PyPDFLoader
)

documents = loader.load()

splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=100
)

chunks = splitter.split_documents(documents)


embeddings = GoogleGenerativeAIEmbeddings( # chama o modelo de ia responsavel por gerar os embeddings
    model="models/gemini-embedding-001",
    google_api_key= api_Key
)

vectorstore = FAISS.from_documents(
    chunks,
    embeddings
)

vectorstore.save_local("faiss_index")

vectorstore = FAISS.load_local(
    "faiss_index",
    embeddings,
    allow_dangerous_deserialization=True
)

retriever = vectorstore.as_retriever(
    search_kwargs={"k": 4}
)

llm = ChatGoogleGenerativeAI( # cria a ia
    model="gemini-2.5-flash", # modelo da ia
    temperature=0.0, # temperatura da ia
    api_key= api_Key # chave da api
)

prompt = ChatPromptTemplate.from_template("""
Você é um atendente de service desk.
Use APENAS o contexto abaixo para responder.
Se a resposta não estiver no PDF, diga que não encontrou a informação.

Contexto:
{context}

Pergunta:
{question}
""")

rag_chain = (
    {
        "context": retriever,
        "question": RunnablePassthrough()
    }
    | prompt
    | llm
)
"""
response = rag_chain.invoke("Posso reembolsar a internet?")
print(response.content)"""

def run_agent(user_message: str) -> str:
    resposta_final = rag_chain.invoke({user_message})
    return resposta_final.content