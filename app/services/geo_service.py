import math
from routes import state

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


def get_nearest_service_point(user_lat, user_lon):
    pontos = state.pontos_cache

    print(f"DEBUG GEO: Verificando cache. Total de pontos: {len(pontos) if pontos else 0}")

    if not pontos:
        print(f"ID do state no GEO: {id(state)}")
        raise Exception("Nenhum ponto disponível (webhook ainda não enviou dados)")
    
    nearest = None
    min_distance = float("inf")

    for ponto in pontos:
        distance = haversine(
            user_lat,
            user_lon,
            float(ponto["latitude"]),
            float(ponto["longitude"]),
        )

        if distance < min_distance:
            min_distance = distance
            nearest = ponto

    return {
        "nome_cto": nearest["nome_cto"],
        "distancia_km": round(min_distance, 2),
    }