import math
import httpx
import tracemalloc
from routes import state

tracemalloc.start()


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

async def get_real_route_distance(lat1, lon1, lat2, lon2):
    """
    Calcula a distância real por estradas usando OSRM (OpenStreetMap).
    Retorna a distância em metros.
    """
    url = f"http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=false"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                # A distância vem em metros
                return data['routes'][0]['distance']
    except Exception as e:
        print(f"Erro ao consultar rota real: {e}")
        return None # Caso falhe, podemos tratar no serviço principal

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

    nearest_ponto = None
    min_real_dist = float("inf")

    # 2. Validação Real (Caminho de estrada)
    for cand in candidates:
        p = cand["ponto"]
        real_dist = await get_real_route_distance(user_lat, user_lon, float(p["latitude"]), float(p["longitude"]))
        
        if real_dist and real_dist < min_real_dist:
            min_real_dist = real_dist
            nearest_ponto = p

    return {
        "nome_cto": nearest_ponto["nome_cto"],
        "distancia_km": round(min_real_dist / 1000, 2), # Converte metros para km
        "viabilidade": "Alta" if min_real_dist < 300 else "Baixa" # Exemplo de regra de negócio
    }