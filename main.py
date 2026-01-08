from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.chat import router as chat_router
from services.llm import init_rag
import os

app = FastAPI()

PORT = int(os.environ.get("PORT", 8000))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=PORT,
        reload=False
    )

@app.on_event("startup")
async def startup_event():
    init_rag()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React + Vite
    allow_credentials=True,
    allow_methods=["*"],  # POST, GET, OPTIONS, etc
    allow_headers=["*"], 
)

app.include_router(chat_router, prefix="/api")