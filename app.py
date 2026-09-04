import os
import time
import threading
import requests
from flask import Flask, request

app = Flask(__name__)

# Suas credenciais oficiais
TOKEN = "8766250524:AAEWp4kcchkyTq0eimlOzkrklnyv42fhZrE"
CHAT_ID = "8752935420"  # Seu Chat ID para os envios automáticos
FOOTBALL_API_KEY = "1055e42dd53a435aa872ac485baa5f95"


def buscar_dados_futebol():
  url = "https://api.football-data.org/v4/matches"
  headers = {"X-Auth-Token": FOOTBALL_API_KEY}
  try:
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
      matches = response.json().get("matches", [])
      if matches:
        jogo = matches[0]
        home = jogo["homeTeam"]["name"]
        away = jogo["awayTeam"]["name"]
        return (
            f"⚽ *Análise Automática (Kakaroto Odds):*\n"
            f"⚔️ **{home} vs {away}**\n"
            f"💡 *Dica de Mercado:* Jogo equilibrado, olho no mercado de Gols (Over 1.5) ou Ambas Marcam!"
        )
  except Exception as e:
    print(f"Erro na API de Futebol: {e}")
  return (
      "⚽ *Kakaroto Odds:* Nenhuma partida importante encontrada no momento."
  )


def enviar_mensagem(chat_id, texto):
  url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
  payload = {"chat_id": chat_id, "text": texto, "parse_mode": "Markdown"}
  try:
    requests.post(url, json=payload)
  except Exception as e:
    print(f"Erro ao enviar mensagem: {e}")


# Função que roda em segundo plano mandando análises automáticas
def rotina_automatica():
  # Aguarda 10 segundos após o app subir para iniciar a primeira mensagem
  time.sleep(10)
  while True:
    try:
      analise = buscar_dados_futebol()
      enviar_mensagem(CHAT_ID, f"🚨 *Relatório Automático do Kakaroto:*\n\n{analise}")
    except Exception as e:
      print(f"Erro na rotina automática: {e}")
    
    # Intervalo de tempo entre os envios (ex: a cada 2 horas = 7200 segundos)
    # Coloquei 300 segundos (5 minutos) para você testar logo se está funcionando, depois pode aumentar!
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
        enviar_mensagem(
            chat_id,
            "Fala guerreiro! 🤖 Kakaroto Odds ativado com envio automático e inteligência de comandos ligada!",
        )
      elif "/odds" in texto_usuario:
        relatorio = buscar_dados_futebol()
        enviar_mensagem(chat_id, relatorio)
      elif "mercado" in texto_usuario or "melhor" in texto_usuario:
        enviar_mensagem(
            chat_id,
            "📊 Analisando o mercado atual... Para este jogo, recomendo cautela e foco em Gols ou Empate Anula aposta!",
        )
      else:
        enviar_mensagem(
            chat_id,
            "Comando recebido! Use /odds para ver a análise atualizada da partida.",
        )
  except Exception as e:
    print(f"Erro no webhook: {e}")

  return "OK", 200


if __name__ == "__main__":
  # Inicia a thread automática em segundo plano junto com o servidor Flask
  t = threading.Thread(target=rotina_automatica, daemon=True)
  t.start()

  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)
