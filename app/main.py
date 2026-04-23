from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import httpx
from routes import state
from routes.chat import router as chat_router
from routes.webhook import router as webhook_router
import uvicorn
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor

app = FastAPI()
load_dotenv()

executor = ThreadPoolExecutor(max_workers=1)

WEBHOOK_URL = os.getenv("GEO_API_URL")

def background_warmup():
    try:
        from services.llm import init_rag, vectorstore
        init_rag()
        if vectorstore:
            # Força a API do Hugging Face a acordar logo no boot
            vectorstore.similarity_search("olá", k=1)
            print("Hugging Face API acordada com sucesso!")
    except Exception as e:
        print(f"Erro no warmup silencioso: {e}")

@app.on_event("startup")
async def startup_event():
    # Isso dispara o warmup em uma thread separada
    loop = asyncio.get_event_loop()
    loop.run_in_executor(executor, background_warmup)

    print("Buscando pontos de atendimento no n8n...")
    try:
        async with httpx.AsyncClient() as client:
            # Faz o GET exatamente como você fez no Postman
            response = await client.get(WEBHOOK_URL, timeout=10.0)
            
            if response.status_code == 200:
                dados = response.json()
                # Salva na variável global que o geo_service usa
                state.pontos_cache = dados
                print(f"--- SUCESSO: {len(state.pontos_cache)} pontos carregados diretamente do n8n ---")
            else:
                print(f"--- ERRO: n8n retornou status {response.status_code} ---")
                
    except Exception as e:
        print(f"--- ERRO AO BUSCAR DADOS DO N8N: {e} ---")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # React + Vite
    allow_credentials=True,
    allow_methods=["*"],  # POST, GET, OPTIONS, etc
    allow_headers=["*"], 
)

app.include_router(chat_router, prefix="/api")
app.include_router(webhook_router, prefix="/webhook")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)