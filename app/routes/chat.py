import re
from services.geo_service import get_nearest_service_point
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

def extract_coordinates(text: str):
    pattern = r"(-?\d+\.\d+),\s*(-?\d+\.\d+)"
    match = re.search(pattern, text)

    if match:
        return float(match.group(1)), float(match.group(2))

    return None

@router.post("/chat/send")
async def chat(payload: UserMessage):
    try:
        session_id = payload.session_id
        user_message = payload.message

        # salva mensagem do usuário
        memory.add(session_id, "user", user_message)

        # verifica se o usuario enviou uma coordenada
        coords = extract_coordinates(user_message)

        if coords:
            lat, lon = coords

            nearest = await get_nearest_service_point(lat, lon)

            reply = (
                f"O ponto de atendimento mais próximo é:  "
                f"\n{nearest['nome_cto']}  "
                f"(a {nearest['distancia_m']} metros).  "
                f"\nViabilidade de atendimento: {nearest['viabilidade']}."
            )

            # salva resposta do agente
            memory.add(session_id, "assistant", reply)

            return {"reply": reply}
        
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
        print("ERRO NO AGENTE:", repr(e))
        raise HTTPException(500, str(e))
