import json
from typing import List
from fastapi import APIRouter
from routes import state

router = APIRouter()

@router.post("/webhook")
async def receive_webhook(data: List):
  state.pontos_cache = data
  with open("pontos_temp.json", "w") as f:
        json.dump(data, f)
  print(f"ID do state no WEBHOOK: {id(state)}")
  print(f"DEBUG: Webhook atualizou state.pontos_cache com {len(state.pontos_cache)} pontos")
  
  return {"status": "success"}