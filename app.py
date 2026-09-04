import threading
import time
from datetime import datetime
import requests
from flask import Flask, jsonify

app = Flask(__name__)

# ==========================================
# ⚙️ CONFIGURAÇÕES DO SEU BOT
# ==========================================
API_KEY_FUTEBOL = "1055e42dd53a435aa872ac485baa5f95"
TELEGRAM_BOT_TOKEN = "8766250524:AAEwp4kcchkyTq0eiml0zkrklnyv42fhZrE"
TELEGRAM_CHAT_ID = "8752935420"
NOME_CANAL = "KAKAROTO ODDS"
# ==========================================

BASE_URL = "https://api.football-data.org/v4"
HEADERS = {"X-Auth-Token": API_KEY_FUTEBOL}

relatorio_analises = []


def enviar_alerta_telegram(mensagem):
    """Envia a mensagem com os palpites diretamente para o seu Telegram."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensagem,
        "parse_mode": "Markdown",
    }
    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("✅ Relatório enviado para o Telegram com sucesso!")
        else:
            print(f"❌ Erro no Telegram: {response.text}")
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")


def analisar_partidas():
    """Busca as partidas do dia e gera o relatório automático."""
    global relatorio_analises
    print(
        f"[{datetime.now().strftime('%H:%M:%S')}] Buscando jogos e gerando análises..."
    )

    endpoint = f"{BASE_URL}/matches"

    try:
        response = requests.get(endpoint, headers=HEADERS)

        # Trata o limite de requisições da API (Rate Limit)
        if response.status_code == 429:
            print("⚠️ Limite de requisições atingido. Aguardando 1 minuto...")
            time.sleep(60)
            return

        if response.status_code != 200:
            print(f"❌ Erro na API de Futebol (Status {response.status_code}).")
            return

        dados = response.json()
        partidas = dados.get("matches", [])

        novas_analises = []

        texto_telegram = f"🔥 *{NOME_CANAL}* 🔥\n"
        texto_telegram += "⚽ *PALPITES E ANÁLISES DO DIA*\n\n"

        for jogo in partidas[:5]:
            mandante = jogo["homeTeam"]["name"]
            visitante = jogo["awayTeam"]["name"]
            campeonato = jogo["competition"]["name"]

            analise = {
                "partida": f"{mandante} vs {visitante}",
                "campeonato": campeonato,
                "palpite": "Over 1.5 Gols / Ambas Marcam",
            }
            novas_analises.append(analise)

            texto_telegram += f"🏆 *{campeonato}*\n"
            texto_telegram += f"⚔️ {mandante} vs {visitante}\n"
            texto_telegram += "💡 *Entrada:* Over 1.5 Gols ou Ambas Marcam\n\n"

        texto_telegram += "🚀 _Bons lucros a todos!_"

        relatorio_analises = novas_analises

        if novas_analises:
            enviar_alerta_telegram(texto_telegram)
        else:
            print("Nenhuma partida encontrada no momento.")

    except Exception as e:
        print(f"❌ Erro durante o processamento: {e}")


def executar_agendador():
    """Roda a checagem diária automática."""
    import schedule

    # Roda todos os dias às 08:00 da manhã
    schedule.every().day.at("08:00").do(analisar_partidas)

    # Executa 1 vez assim que você liga o servidor
    analisar_partidas()

    while True:
        schedule.run_pending()
        time.sleep(60)


@app.route("/analise", methods=["GET"])
def obter_analises():
    return jsonify(relatorio_analises)


if __name__ == "__main__":
    thread = threading.Thread(target=executar_agendador, daemon=True)
    thread.start()
    app.run(host="0.0.0.0", port=5000)
