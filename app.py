import os
import requests
from flask import Flask, request

app = Flask(__name__)

# Suas credenciais oficiais
TOKEN = "8766250524:AAEWp4kcchkyTq0eimlOzkrklnyv42fhZrE"
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
            f"⚽ *Próxima Partida Analisada (Kakaroto Odds):*\n{home} vs"
            f" {away}\nStatus: Pronto para o jogo!"
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
            "Fala guerreiro! 🤖 Kakaroto Odds ativado com sucesso! Envie /odds"
            " para ver as análises.",
        )
      elif "/odds" in texto_usuario:
        relatorio = buscar_dados_futebol()
        enviar_mensagem(chat_id, relatorio)
      else:
        enviar_mensagem(
            chat_id,
            "Comando não reconhecido. Use /start ou /odds para ver os comandos.",
        )
  except Exception as e:
    print(f"Erro no webhook: {e}")

  return "OK", 200


if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)
