from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
import os
import time

load_dotenv()
api_Key = os.getenv("OPENAI_API_KEY")

BASE_DIR = os.path.dirname(__file__)
PDF_DIR = os.path.join(BASE_DIR, "data")
VECTOR_DIR = os.path.join(BASE_DIR, "vectorstore")

pdf_files = ["manual1.pdf", "manual2.pdf"]
docs = []

for pdf in pdf_files:
    loader = PyMuPDFLoader(os.path.join(PDF_DIR, pdf))
    docs.extend(loader.load())

splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=150,
    separators=["\n\n", "\n", ".", " ", ""]
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
