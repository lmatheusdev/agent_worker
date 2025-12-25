from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
import os

load_dotenv()
api_Key = os.getenv("OPENAI_API_KEY")

BASE_DIR = os.path.dirname(__file__)
MD_DIR = os.path.join(BASE_DIR, "data")
VECTOR_DIR = os.path.join(BASE_DIR, "vectorstore")

os.makedirs(VECTOR_DIR, exist_ok=True)

md_files = ["atendimento.md", "financeiro.md"]

docs = []

for md in md_files:
    path = os.path.join(MD_DIR, md)
    loader = TextLoader(path, encoding="utf-8")
    docs.extend(loader.load())

splitter = RecursiveCharacterTextSplitter(
    chunk_size=700,
    chunk_overlap=120,
    separators=[
        "\n## ",   # seções
        "\n### ",
        "\n|",
        "\n\n",
        "\n",
        ". ",
        " "
    ]
)

chunks = splitter.split_documents(docs)

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vectorstore = FAISS.from_documents(
    chunks,
    embeddings
)

vectorstore.save_local(VECTOR_DIR)
