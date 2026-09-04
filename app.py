import os
import requests
from flask import Flask, request

app = Flask(__name__)

# Credenciais e Configurações
BOT_TOKEN = "8766..."
CHAT_ID = "8752..."
API_KEY = "1055..."
HEADERS = {"X-Auth-Token": API_KEY}

TELEGRAM_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

def enviar_mensagem(texto):
    payload = {
        "chat_id": CHAT_ID,
        "text": texto,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(TELEGRAM_URL, json=payload)
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")

def buscar_jogos_ao_vivo():
    url = "https://api.football-data.org/v4/matches?status=LIVE"
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            dados = response.json()
            partidas = dados.get("matches", [])
            
            if not partidas:
                return "⚽ Nenhuma partida ao vivo no momento."
            
            texto = "🔴 *Jogos Ao Vivo:* \n\n"
            for p in partidas:
                home = p['homeTeam']['name']
                away = p['awayTeam']['name']
                score_home = p['score']['fullTime']['home']
                score_away = p['score']['fullTime']['away']
                competicao = p['competition']['name']
                
                texto += f"🏆 {competicao}\n🎮 {home} {score_home} x {score_away} {away}\n\n"
                
            return texto
        else:
            return "⚠️ Erro ao buscar partidas ao vivo na API."
    except Exception as e:
        return f"⚠️ Erro de conexão com a API: {e}"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "POST":
        data = request.json
        if data and "message" in data:
            chat_id = data["message"]["chat"]["id"]
            text = data["message"].get("text", "").lower()
            
            if "/aovivo" in text:
                resultado = buscar_jogos_ao_vivo()
                payload = {"chat_id": chat_id, "text": resultado, "parse_mode": "Markdown"}
                requests.post(TELEGRAM_URL, json=payload)
            elif "/odds" in text:
                payload = {"chat_id": chat_id, "text": "⚽ Kakaroto Odds: Nenhuma partida futura disponível para hoje no momento.", "parse_mode": "Markdown"}
                requests.post(TELEGRAM_URL, json=payload)
                
        return "OK", 200
    return "Kakaroto Odds Bot está rodando com sucesso!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
