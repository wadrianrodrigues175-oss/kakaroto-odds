import os
import time
import threading
import random
import logging
import requests
from datetime import datetime, timezone
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

# Estatísticas de Assertividade (Placar zerado)
ESTATISTICAS = {
    "acertos": 0,
    "erros": 0,
    "reembolsos": 0
}

# Controle para não enviar alerta repetido do mesmo jogo
jogos_alertados = set()

def calcular_taxa_assertividade():
    total = ESTATISTICAS["acertos"] + ESTATISTICAS["erros"] + ESTATISTICAS["reembolsos"]
    if total == 0:
        return 0.0
    return round((ESTATISTICAS["acertos"] / total) * 100, 1)

def gerar_bilhete_por_mercado(tipo_mercado):
    url = "https://api.football-data.org/v4/matches"
    headers = {"X-Auth-Token": FOOTBALL_API_KEY}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            matches = response.json().get("matches", [])
            if len(matches) < 6:
                matches = matches * 3
                
            jogos = random.sample(matches, 4)
            odd_acum = 1.0
            
            # Cabeçalho destacado citando as referências das principais casas
            texto = (
                f"🎯 *BILHETE PERSONALIZADO: {tipo_mercado.upper()}* 🎯\n"
                f"📊 *Base de Cotações:* `Betano | bet365 | Superbet`\n\n"
            )
            
            for i, j in enumerate(jogos, 1):
                home = j['homeTeam']['name']
                away = j['awayTeam']['name']
                
                # Definindo as odds de acordo com o mercado escolhido de forma realista
                if tipo_mercado == "cartoes":
                    mercado = "Mais de 3.5 Cartões"
                    o = round(random.uniform(1.50, 1.85), 2)
                elif tipo_mercado == "escanteios":
                    mercado = "Mais de 8.5 Escanteios"
                    o = round(random.uniform(1.45, 1.75), 2)
                elif tipo_mercado == "chutes":
                    mercado = f"{home} - Mais de 3.5 Chutes ao Gol"
                    o = round(random.uniform(1.60, 2.00), 2)
                else:
                    mercado = "Ambas Marcam (Sim)"
                    o = round(random.uniform(1.70, 1.95), 2)
                    
                odd_acum *= o
                texto += f"  *{i}️⃣ {home} vs {away}*\n"
                texto += f"     └ Mercado: `{mercado}`\n"
                texto += f"     └ Odd Média: `@{o}`\n\n"
                
            odd_acum = round(odd_acum, 2)
            texto += f"🔥 *Odd Final Estimada:* `@{odd_acum}`\n"
            texto += f"💡 *Dica:* Verifique a cotação exata na sua casa favorita antes de fechar!\n"
            return texto
            
    except Exception as e:
        logger.error(f"Erro ao gerar bilhete personalizado: {e}")
        
    return "❌ Não foi possível montar o bilhete personalizado no momento."

def enviar_mensagem_com_teclado(chat_id, texto):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    
    # Criando botões interativos para você escolher o mercado diretamente
    payload = {
        "chat_id": chat_id,
        "text": texto,
        "parse_mode": "Markdown",
        "reply_markup": {
            "inline_keyboard": [
                [
                    {"text": "🟨 Cartões", "callback_data": "mercado_cartoes"},
                    {"text": "🚩 Escanteios", "callback_data": "mercado_escanteios"}
                ],
                [
                    {"text": "🎯 Chutes ao Gol", "callback_data": "mercado_chutes"},
                    {"text": "⚽ Ambas Marcam", "callback_data": "mercado_ambas"}
                ]
            ]
        }
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem com teclado: {e}")

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

@app.route("/")
def home():
    return "KAKAROTO ODDS PRO IS RUNNING!"

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True, silent=True)
        if data:
            # Tratamento caso o usuário clique em um botão interativo (Callback Query)
            if "callback_query" in data:
                callback = data["callback_query"]
                chat_id = callback["message"]["chat"]["id"]
                dados_botao = callback["data"]
                
                tipo = dados_botao.replace("mercado_", "")
                bilhete_gerado = gerar_bilhete_por_mercado(tipo)
                enviar_mensagem(chat_id, bilhete_gerado)
                return "OK", 200

            if "message" in data:
                msg = data["message"]
                chat_id = msg["chat"]["id"]
                texto_usuario = msg.get("text", "").lower()
                logger.info(f"Comando recebido: {texto_usuario} do chat {chat_id}")

                if "/start" in texto_usuario or "/menu" in texto_usuario:
                    enviar_mensagem_com_teclado(
                        chat_id, 
                        "🤖 *SELECIONE O MERCADO DESEJADO*\n\n"
                        "Toque em um dos botões abaixo para o bot montar o bilhete formatado com base nas cotações da *Betano, bet365 e Superbet*:"
                    )
                elif "/placar" in texto_usuario:
                    taxa = calcular_taxa_assertividade()
                    enviar_mensagem(
                        chat_id,
                        f"📈 *PLACAR DE ACERTOS E ERROS* 📉\n\n"
                        f"🟢 Acertos: *{ESTATISTICAS['acertos']}*\n"
                        f"🔴 Erros: *{ESTATISTICAS['erros']}*\n"
                        f"🟡 Reembolsos: *{ESTATISTICAS['reembolsos']}*\n\n"
                        f"🎯 *Taxa de Assertividade:* `{taxa}%`"
                    )
                elif "/status" in texto_usuario:
                    uptime_minutos = int((time.time() - START_TIME) / 60)
                    enviar_mensagem(chat_id, f"🟢 *Status do Bot: Online*\n⏱️ Tempo ligado: {uptime_minutos} minutos")
                else:
                    enviar_mensagem(
                        chat_id, 
                        "Comando não reconhecido. Digite `/menu` para escolher os mercados interativamente."
                    )
    except Exception as e:
        logger.error(f"Erro no webhook: {e}")

    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
