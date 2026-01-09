from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes.chat import router as chat_router
from .services.llm import init_rag
import uvicorn
import os

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    # init_rag()
    pass

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React + Vite
    allow_credentials=True,
    allow_methods=["*"],  # POST, GET, OPTIONS, etc
    allow_headers=["*"], 
)

app.include_router(chat_router, prefix="/api")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)