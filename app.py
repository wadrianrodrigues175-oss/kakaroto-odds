import os
import time
import threading
import random
import requests
from flask import Flask, request

app = Flask(__name__)

# Suas credenciais oficiais
TOKEN = "8766250524:AAEWp4kcchkyTq0eimlOzkrklnyv42fhZrE"
CHAT_ID = "8752935420"
FOOTBALL_API_KEY = "1055e42dd53a435aa872ac485baa5f95"

def buscar_dados_futebol():
    url = "https://api.football-data.org/v4/matches"
    headers = {"X-Auth-Token": FOOTBALL_API_KEY}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            matches = response.json().get("matches", [])
            if matches:
                # Pega um jogo aleatório da lista de partidas do dia para variar sempre!
                jogo = random.choice(matches)
                home = jogo['homeTeam']['name']
                away = jogo['awayTeam']['name']
                competicao = jogo.get('competition', {}).get('name', 'Futebol Internacional')
                
                mercados = [
                    "Gols (Over 1.5)", 
                    "Ambas Marcam (Sim)", 
                    "Empate Anula aposta (DNB)", 
                    "Dupla Hipótese"
                ]
                dica_mercado = random.choice(mercados)

                return (
                    f"⚽ *Análise do Kakaroto Odds* ⚽\n"
                    f"🏆 *Competição:* {competicao}\n"
                    f"⚔️ **{home} vs {away}**\n"
                    f"💡 *Melhor Mercado Sugerido:* {dica_mercado}"
                )
    except Exception as e:
        print(f"Erro na API de Futebol: {e}")
    
    return "⚽ *Kakaroto Odds:* Nenhuma partida disponível no momento para análise."

def enviar_mensagem(chat_id, texto):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": texto,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")

def rotina_automatica():
    time.sleep(10)
    while True:
        try:
            analise = buscar_dados_futebol()
            enviar_mensagem(CHAT_ID, f"🚨 *Relatório Automático do Kakaroto:*\n\n{analise}")
        except Exception as e:
            print(f"Erro na rotina automática: {e}")
        
        # Intervalo de 5 minutos (300 segundos) para testes
        time.sleep(300)

@app.route("/")
def home():
    return "KAKAROTO ODDS BOT IS RUNNING!"

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True, silent=True)
        if data and "message" in data:
            chat_id = data["message"]["chat"]["id"]
            texto_usuario = data["message"].get("text", "").lower()

            if "/start" in texto_usuario:
                enviar_mensagem(chat_id, "Fala guerreiro! 🤖 Kakaroto Odds ativado com variação de partidas do mundo todo!")
            elif "/odds" in texto_usuario:
                relatorio = buscar_dados_futebol()
                enviar_mensagem(chat_id, relatorio)
            elif "mercado" in texto_usuario or "melhor" in texto_usuario:
                relatorio = buscar_dados_futebol()
                enviar_mensagem(chat_id, f"📊 *Consulta de Mercado:*\n\n{relatorio}")
            else:
                enviar_mensagem(chat_id, "Comando recebido! Use /odds para ver uma análise nova.")
    except Exception as e:
        print(f"Erro no webhook: {e}")

    return "OK", 200

if __name__ == "__main__":
    t = threading.Thread(target=rotina_automatica, daemon=True)
    t.start()
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
