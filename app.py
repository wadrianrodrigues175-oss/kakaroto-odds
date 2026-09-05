import os
import requests
from flask import Flask, request

app = Flask(__name__)

BOT_TOKEN = "8766250524:AAEWp4kcchkyTq0eiml0zkrklnyv42fhZrE"
API_KEY = "1055..."
HEADERS = {"X-Auth-Token": API_KEY}

TELEGRAM_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
RENDER_URL = "https://kakaroto-odds.onrender.com/webhook"

# Ativa o webhook automaticamente ao iniciar o app
def configurar_webhook():
    url_reg = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={RENDER_URL}"
    try:
        requests.get(url_reg)
    except:
        pass

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

@app.route("/", methods=["GET"])
def home():
    return "Kakaroto Odds Bot está rodando com sucesso!", 200

@app.route("/webhook", methods=["POST"])
def webhook():
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
        else:
            payload = {"chat_id": chat_id, "text": f"🤖 Bot ativo! Seu Chat ID é: `{chat_id}`", "parse_mode": "Markdown"}
            requests.post(TELEGRAM_URL, json=payload)
            
    return "OK", 200

if __name__ == "__main__":
    configurar_webhook()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
