from datetime import datetime, timedelta, timezone

def obter_data_brasil():
    fuso_br = timezone(timedelta(hours=-3))
    return datetime.now(fuso_br).strftime('%Y-%m-%d')

def filtrar_apenas_jogos_futuros(matches):
    fuso_br = timezone(timedelta(hours=-3))
    agora_br = datetime.now(fuso_br)
    
    matches_futuros = []
    for j in matches:
        utc_date_str = j.get('utcDate')
        if utc_date_str:
            dt_jogo = datetime.fromisoformat(utc_date_str.replace('Z', '+00:00')).astimezone(fuso_br)
            # Mantém apenas se o jogo for daqui para frente (ou começou há menos de 10 minutos)
            if dt_jogo >= (agora_br - timedelta(minutes=10)):
                matches_futuros.append(j)
                
    # Se a API retornou apenas jogos passados e a lista ficou vazia, 
    # retornamos a original para evitar que quebre, mas priorizamos os futuros.
    return matches_futuros if matches_futuros else matches
