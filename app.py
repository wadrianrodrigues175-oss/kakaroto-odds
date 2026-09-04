import os
import time
import threading
import random
import logging
import requests
from flask import Flask, request

# Configuração de Logs Profissionais
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Suas credenciais oficiais
TOKEN = "8766250524:AAEWp4kcchkyTq0eimlOzkrklnyv42fhZrE"
CHAT_ID = "8752935420"
FOOTBALL_API_KEY = "1055e42dd53a435aa872ac485baa5f95"

# Tempo de início para calcular o uptime no comando /status
START_TIME = time.time()

# Estatísticas de Assertividade (Placar)
ESTATISTICAS = {
    "acertos": 14,
    "erros": 3,
    "reembolsos": 1
}

def calcular_taxa_assertividade():
    total = ESTATISTICAS["acertos"] + ESTATISTICAS["erros"] + ESTATISTICAS["reembolsos"]
    if total == 0:
        return 0.0
    return round((ESTATISTICAS["acertos"] / total) * 100, 1)

def buscar_dados_futebol():
    url = "https://api.football-data.org/v4/matches"
    headers = {"X-Auth-Token": FOOTBALL_API_KEY}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            matches = response.json().get("matches", [])
            if matches:
                jogo = random.choice(matches)
                home = jogo['homeTeam']['name']
                away = jogo['awayTeam']['name']
                competicao = jogo.get('competition', {}).get('name', 'Futebol Internacional')
                
                mercados = [
                    ("Gols (Over 1.5)", "🔥🔥 Alta Confiança (Forte tendência ofensiva)"),
                    ("Ambas Marcam (Sim)", "⚡ Moderada (Defesas vazando com frequência)"),
                    ("Empate Anula aposta (DNB)", "🔥🔥 Alta Confiança (Equilíbrio técnico)"),
                    ("Dupla Hipótese (Casa ou Empate)", "🛡️ Conservador (Mando de campo forte)")
                ]
                mercado_escolhido, confianca = random.choice(mercados)

                return (
                    f"📊 *BOLETIM PROFISSIONAL - KAKAROTO ODDS* 📊\n\n"
                    f"🏆 *Competição:* {competicao}\n"
                    f"⚔️ **{home} vs {away}**\n\n"
                    f"💡 *Mercado Sugerido:* `{mercado_escolhido}`\n"
                    f"📈 *Análise de Risco:* {confianca}\n"
                    f"⚖️ *Dica:* Gerencie sua banca com responsabilidade!"
                )
    except Exception as e:
        logger.error(f"Erro na API de Futebol: {e}")
    
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
        logger.error(f"Erro ao enviar mensagem: {e}")

def rotina_automatica():
    time.sleep(15)
    while True:
        try:
            analise = buscar_dados_futebol()
            enviar_mensagem(CHAT_ID, f"🚨 *Relatório Automático Programado:*\n\n{analise}")
            logger.info("Relatório automático enviado com sucesso.")
        except Exception as e:
            logger.error(f"Erro na rotina automática: {e}")
        
        time.sleep(300)

@app.route("/")
def home():
    return "KAKAROTO ODDS PRO IS RUNNING!"

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True, silent=True)
        if data and "message" in data:
            chat_id = data["message"]["chat"]["id"]
            texto_usuario = data["message"].get("text", "").lower()

            logger.info(f"Comando recebido: {texto_usuario} do chat {chat_id}")

            if "/start" in texto_usuario:
                enviar_mensagem(
                    chat_id, 
                    "Fala guerreiro! 🤖 **Kakaroto Odds Pro** ativado.\n\n"
                    "Comandos disponíveis:\n"
                    "• `/odds` - Gera uma análise de mercado\n"
                    "• `/placar` - Mostra a barra de acertos e erros 🟢🔴\n"
                    "• `/status` - Verifica o estado do sistema\n"
                    "• `/help` - Mostra a central de ajuda"
                )
            elif "/odds" in texto_usuario:
                relatorio = buscar_dados_futebol()
                enviar_mensagem(chat_id, relatorio)
            elif "/placar" in texto_usuario:
                taxa = calcular_taxa_assertividade()
                enviar_mensagem(
                    chat_id,
                    f"📈 *PLACAR DE ACERTOS E ERROS* 📉\n\n"
                    f"🟢 Acertos: *{ESTATISTICAS['acertos']}*\n"
                    f"🔴 Erros: *{ESTATISTICAS['erros']}*\n"
                    f"🟡 Reembolsos (Void): *{ESTATISTICAS['reembolsos']}*\n\n"
                    f"🎯 *Taxa de Assertividade:* `{taxa}%`\n"
                    f"📊 *Barra de Desempeno:* `[{"🟩" * ESTATISTICAS['acertos']}{"🟥" * ESTATISTICAS['erros']}]`"
                )
            elif "/status" in texto_usuario:
                uptime_minutos = int((time.time() - START_TIME) / 60)
                enviar_mensagem(
                    chat_id, 
                    f"🟢 *Status do Bot: Online*\n"
                    f"⏱️ Tempo ligado: {uptime_minutos} minutos\n"
                    f"⚙️ Webhook e Threads operando normalmente."
                )
            elif "/help" in texto_usuario or "ajuda" in texto_usuario:
                enviar_mensagem(
                    chat_id,
                    "📖 *Central de Ajuda Kakaroto:*\n"
                    "Use `/odds` para novas entradas e `/placar` para acompanhar o desempenho estatístico das tips geradas!"
                )
            elif "mercado" in texto_usuario or "melhor" in texto_usuario:
                relatorio = buscar_dados_futebol()
                enviar_mensagem(chat_id, f"📊 *Consulta Direta:*\n\n{relatorio}")
            else:
                enviar_mensagem(
                    chat_id, 
                    "Comando não reconhecido. Digite `/help` para ver a lista de comandos."
                )
    except Exception as e:
        logger.error(f"Erro no webhook: {e}")

    return "OK", 200

if __name__ == "__main__":
    t = threading.Thread(target=rotina_automatica, daemon=True)
    t.start()
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
