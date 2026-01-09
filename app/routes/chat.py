from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.llm import run_agent
from services.chat_memory import ChatMemory

router = APIRouter()
memory = ChatMemory()

class UserMessage(BaseModel):
    session_id: str
    message: str

class AgentResponse(BaseModel):
    reply: str

@router.post("/chat/send")
async def chat(payload: UserMessage):
    try:
        session_id = payload.session_id
        user_message = payload.message

        # salva mensagem do usuário
        memory.add(session_id, "user", user_message)

        # recupera histórico
        chat_history = memory.get(session_id)

        # chama o agente com histórico
        reply = await run_agent(
            question=user_message,
            chat_history=chat_history
        )

        # salva resposta do agente
        memory.add(session_id, "assistant", reply)

        return {"reply": reply}

    except Exception as e:
        print("ERRO NO AGENTE:", e)
        raise HTTPException(500, "Erro no agente de IA")
