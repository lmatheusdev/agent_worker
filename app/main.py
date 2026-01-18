from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.chat import router as chat_router
import uvicorn
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor

app = FastAPI()

executor = ThreadPoolExecutor(max_workers=1)

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

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # React + Vite
    allow_credentials=True,
    allow_methods=["*"],  # POST, GET, OPTIONS, etc
    allow_headers=["*"], 
)

app.include_router(chat_router, prefix="/api")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)