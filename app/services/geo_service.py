import math
from dotenv import load_dotenv
import httpx
import tracemalloc
import os
from routes import state

tracemalloc.start()

load_dotenv()

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

async def get_google_route_distance(lat1, lon1, lat2, lon2):
    """
    Consulta a Distance Matrix API do Google para obter a distância real.
    """
    origins = f"{lat1},{lon1}"
    destinations = f"{lat2},{lon2}"

    url = (
        f"https://maps.googleapis.com/maps/api/distancematrix/json"
        f"?origins={origins}"
        f"&destinations={destinations}"
        f"&mode=driving"
        f"&key={GOOGLE_MAPS_API_KEY}"
    )
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            data = response.json()
            
            # DEBUG: Ver o status principal da requisição
            if data.get("status") != "OK":
                print(f"ERRO API GOOGLE: {data.get('status')} - {data.get('error_message', 'Sem mensagem')}")
                return None

            # Verificação de segurança para evitar o 'out of range'
            if "rows" in data and len(data["rows"]) > 0:
                elements = data["rows"][0].get("elements", [])
                
                if len(elements) > 0:
                    element = elements[0]
                    status_rota = element.get("status")
                    
                    if status_rota == "OK":
                        return element["distance"]["value"] # Distância em metros
                    else:
                        print(f"AVISO: Rota não encontrada entre os pontos ({status_rota})")
                else:
                    print("ERRO: Lista de elementos vazia na resposta do Google.")
            else:
                print("ERRO: Lista de linhas (rows) vazia na resposta do Google.")

    except Exception as e:
        print(f"Erro inesperado ao consultar Google Maps: {e}")
    
    return None
    
async def get_nearest_service_point(user_lat, user_lon):
    pontos = state.pontos_cache
    
    if not pontos:
        raise Exception("Nenhum ponto disponível")

    # 1. Filtro rápido (Linha reta)
    candidates = []
    for ponto in pontos:
        dist_air = haversine(user_lat, user_lon, float(ponto["latitude"]), float(ponto["longitude"]))
        candidates.append({"ponto": ponto, "dist_air": dist_air})
    
    # Pega os 5 mais próximos em linha reta para validar no mapa
    candidates = sorted(candidates, key=lambda x: x["dist_air"])[:5]

    best_ponto = None
    min_real_dist = float("inf")

    # 2. Validação Real (Caminho de estrada)
    for cand in candidates:
        p = cand["ponto"]

        real_dist = await get_google_route_distance(user_lat, user_lon, p["latitude"], p["longitude"])

        # PROTEÇÃO: Só prossegue se 'real_dist' não for None
        if real_dist is not None:
            distancia = real_dist
    
            if distancia < min_real_dist:
                min_real_dist = distancia
                best_ponto = p
        else:
            # Caso o Google falhe, opcionalmente use a linha reta para não travar o chat
            print(f"Pulando ponto {p.get('nome_cto')} devido a erro na API do Google.")


    return {
        "nome_cto": best_ponto["nome_cto"],
        "distancia_m": round(min_real_dist, 1),
        "viabilidade": "Alta" if min_real_dist < 150 else "Média" if min_real_dist < 300 else "Baixa"
    }