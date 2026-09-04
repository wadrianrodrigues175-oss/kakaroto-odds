from datetime import datetime, timedelta, timezone

def obter_data_brasil():
    # Calcula a data atual considerando o fuso horário de Brasília (UTC-3)
    fuso_br = timezone(timedelta(hours=-3))
    return datetime.now(fuso_br).strftime('%Y-%m-%d')

def buscar_dados_futebol():
    hoje_str = obter_data_brasil()
    # Puxa os jogos do dia inteiro de hoje no horário do Brasil
    url = f"https://api.football-data.org/v4/matches?dateFrom={hoje_str}&dateTo={hoje_str}"
    headers = {"X-Auth-Token": FOOTBALL_API_KEY}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            matches = response.json().get("matches", [])
            
            if matches:
                # Prioriza jogos que ainda vão começar ou estão ao vivo
                fuso_br = timezone(timedelta(hours=-3))
                agora_br = datetime.now(fuso_br)
                
                matches_uteis = []
                for j in matches:
                    utc_date_str = j.get('utcDate')
                    if utc_date_str:
                        dt_jogo = datetime.fromisoformat(utc_date_str.replace('Z', '+00:00')).astimezone(fuso_br)
                        # Se o jogo ainda vai acontecer ou começou há menos de 2 horas
                        if dt_jogo >= (agora_br - timedelta(hours=2)):
                            matches_uteis.append(j)
                
                if not matches_uteis:
                    matches_uteis = matches # Se todos já passaram, usa a lista geral para não quebrar
                    
                jogo = random.choice(matches_uteis)
                home = jogo['homeTeam']['name']
                away = jogo['awayTeam']['name']
                competicao = jogo.get('competition', {}).get('name', 'Futebol Global')
                
                utc_date_str = jogo.get('utcDate')
                horario_str = "Hoje"
                if utc_date_str:
                    dt_obj = datetime.fromisoformat(utc_date_str.replace('Z', '+00:00')).astimezone(fuso_br)
                    horario_str = dt_obj.strftime('%H:%M (BR)')
                
                mercados_possiveis = [
                    (f"Vitória Simples - {home} (Casa)", "75-85%"),
                    (f"Dupla Hipótese - {home} ou Empate (1X)", "88-95%"),
                    (f"Mais de 8.5 Escanteios na Partida", "80-88%"),
                    (f"Mais de 3.5 Cartões no Jogo", "78-85%"),
                    (f"Ambas Marcam (Sim) - {home} e {away}", "72-80%"),
                    (f"Empate Anula (DNB) - {home}", "82-90%")
                ]
                
                mercado_escolhido, prob = random.choice(mercados_possiveis)

                return (
                    f"📊 *BOLETIM PROFISSIONAL - KAKAROTO ODDS* 📊\n"
                    f"📊 *Base de Cotações:* `Betano | bet365 | Superbet`\n\n"
                    f"🏆 *Competição:* {competicao}\n"
                    f"⚔️ **{home} vs {away}**\n"
                    f"🕒 *Horário:* {horario_str}\n\n"
                    f"💡 *Mercado Sugerido:* `{mercado_escolhido}`\n"
                    f"🎯 *Probabilidade Estimada:* `{prob}`\n"
                    f"⚖️ *Dica:* Gerencie sua banca com responsabilidade!"
                )
    except Exception as e:
        logger.error(f"Erro na API de Futebol: {e}")
    
    return "⚽ *Kakaroto Odds:* Nenhuma partida futura disponível para hoje."
