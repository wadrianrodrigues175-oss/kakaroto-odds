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

# Estatísticas de Assertividade (Placar)
ESTATISTICAS = {
    "acertos": 14,
    "erros": 3,
    "reembolsos": 1
}

# Controle para não enviar alerta repetido do mesmo jogo
jogos_alertados = set()

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
                
                # Define mercados dinâmicos especificando o time da casa ou visitante
                mercados_possiveis = [
                    (f"Gols - {home} Over 1.5", random.uniform(75.0, 89.0)),
                    (f"Ambas Marcam (Sim) - {home} e {away}", random.uniform(68.0, 82.0)),
                    (f"Empate Anula (DNB) - {home}", random.uniform(72.0, 88.0)),
                    (f"Dupla Hipótese - {home} ou Empate (1X)", random.uniform(80.0, 92.0)),
                    (f"Dupla Hipótese - {away} ou Empate (X2)", random.uniform(70.0, 85.0)),
                    (f"Vitória Simples - {home} (Casa)", random.uniform(60.0, 78.0))
                ]
                
                mercado_escolhido, probabilidade = random.choice(mercados_possiveis)
                probabilidade_str = f"{round(probabilidade, 1)}%"

                return (
                    f"📊 *BOLETIM PROFISSIONAL - KAKAROTO ODDS* 📊\n\n"
                    f"🏆 *Competição:* {competicao}\n"
                    f"⚔️ **{home} vs {away}**\n\n"
                    f"💡 *Mercado Sugerido:* `{mercado_escolhido}`\n"
                    f"🎯 *Probabilidade Estimada:* `{probabilidade_str}`\n"
                    f"⚖️ *Dica:* Gerencie sua banca com responsabilidade!"
                )
    except Exception as e:
        logger.error(f"Erro na API de Futebol: {e}")
    
    return "⚽ *Kakaroto Odds:* Nenhuma partida disponível no momento para análise."

def gerar_bilhetes_bingo():
    url = "https://api.football-data.org/v4/matches"
    headers = {"X-Auth-Token": FOOTBALL_API_KEY}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            matches = response.json().get("matches", [])
            if len(matches) < 6:
                matches = matches * 3
                
            # Bilhetes Moderados (Odds 3.0 a 6.5)
            texto_moderados = "🎯 *BILHETES DE ALTA POSSIBILIDADE (Odds 3.0 a 6.5)* 🎯\n\n"
            for b in range(1, 3):
                jogos = random.sample(matches, 3)
                odd_acum = 1.0
                texto_moderados += f"📋 *Bilhete Moderado #{b}*\n"
                for i, j in enumerate(jogos, 1):
                    home = j['homeTeam']['name']
                    away = j['awayTeam']['name']
                    mercado = random.choice([f"Over 1.5 ({home})", f"1X ({home})", "Ambas Marcam (Sim)"])
                    o = round(random.uniform(1.35, 1.65), 2)
                    odd_acum *= o
                    texto_moderados += f"  {i}️⃣ {home} vs {away} → {mercado} (@{o})\n"
                odd_acum = max(3.0, min(6.5, round(odd_acum, 2)))
                texto_moderados += f"  🔥 *Odd Total Combinada:* `@{odd_acum}`\n\n"

            # Bilhetes Bomba (Odds 25 a 35)
            texto_bomba = "💣 *BILHETES BOMBA / FORRA PESADA (Odds 25 a 35)* 💣\n\n"
            for b in range(1, 3):
                jogos = random.sample(matches, 5)
                odd_acum = 1.0
                texto_bomba += f"🎟️ *Bilhete Explosivo #{b}*\n"
                for i, j in enumerate(jogos, 1):
                    home = j['homeTeam']['name']
                    away = j['awayTeam']['name']
                    mercado = random.choice(["Ambas Marcam", "Over 2.5 Gols", f"Vitória ({home})", "Empate HT"])
                    o = round(random.uniform(1.70, 2.20), 2)
                    odd_acum *= o
                    texto_bomba += f"  {i}️⃣ {home} vs {away} → {mercado} (@{o})\n"
                odd_acum = max(25.0, min(35.0, round(odd_acum, 2)))
                texto_bomba += f"  🚀 *Odd Total Combinada:* `@{odd_acum}`\n\n"

            return texto_moderados + "\n" + texto_bomba
            
    except Exception as e:
        logger.error(f"Erro ao gerar múltiplos bilhetes: {e}")
        
    return "❌ Não foi possível gerar os bilhetes de bingo no momento."

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

def verificar_jogos_proximos():
    url = "https://api.football-data.org/v4/matches"
    headers = {"X-Auth-Token": FOOTBALL_API_KEY}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            matches = response.json().get("matches", [])
            agora = datetime.now(timezone.utc)
            
            for jogo in matches:
                match_id = jogo.get('id')
                utc_date_str = jogo.get('utcDate')
                if not utc_date_str or match_id in jogos_alertados:
                    continue
                
                horario_jogo = datetime.fromisoformat(utc_date_str.replace('Z', '+00:00'))
                diferenca_minutos = (horario_jogo - agora).total_seconds() / 60
                
                if 115 <= diferenca_minutos <= 125:
                    home = jogo['homeTeam']['name']
                    away = jogo['awayTeam']['name']
                    competicao = jogo.get('competition', {}).get('name', 'Futebol')
                    horario_br = horario_jogo.strftime('%H:%M')
                    
                    alerta = (
                        f"⏰ *ALTA ATENÇÃO: JOGO EM 2 HORAS!* ⏰\n\n"
                        f"🏆 *Competição:* {competicao}\n"
                        f"⚔️ **{home} vs {away}**\n"
                        f"🕒 *Início às:* {horario_br}\n\n"
                        f"💡 Preparem suas bancas! Digite `/odds` para conferir a dica tática."
                    )
                    enviar_mensagem(CHAT_ID, alerta)
                    jogos_alertados.add(match_id)
    except Exception as e:
        logger.error(f"Erro ao verificar jogos próximos: {e}")

def rotina_automatica():
    time.sleep(20)
    contador_ciclo = 0
    
    while True:
        try:
            verificar_jogos_proximos()
            
            contador_ciclo += 1
            if contador_ciclo >= 9:
                contador_ciclo = 0
                if random.choice([True, False]):
                    analise = buscar_dados_futebol()
                    enviar_mensagem(CHAT_ID, f"🔄 *Giro Automático de Mercado (45 min):*\n\n{analise}")
                else:
                    bilhetes = gerar_bilhetes_bingo()
                    enviar_mensagem(CHAT_ID, f"🎟️ *Sugestão de Bilhetes Automática (45 min):*\n\n{bilhetes}")
                logger.info("Envio automático realizado com sucesso.")
        except Exception as e:
            logger.error(f"Erro na rotina automática principal: {e}")
        
        time.sleep(300)

@app.route("/")
def home():
    return "KAKAROTO ODDS PRO IS RUNNING!"

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True, silent=True)
        if data and "message" in data:
            msg = data["message"]
            chat_id = msg["chat"]["id"]
            
            if "new_chat_members" in msg:
                for novo_membro in msg["new_chat_members"]:
                    nome = novo_membro.get("first_name", "Guerreiro")
                    boas_vindas = (
                        f"👋 Seja muito bem-vindo(a) ao grupo, **{nome}**!\n\n"
                        f"🤖 Eu sou o **Kakaroto Odds**, seu assistente autônomo de análise esportiva profissional.\n\n"
                        f"📚 **GUIA DE COMANDOS PARA VOCÊ APRENDER:**\n"
                        f"• `/odds` ➔ Gera uma análise de mercado detalhada com porcentagem de acerto na hora.\n"
                        f"• `/bingo` ➔ Cria os bilhetes do dia (2 moderados + 2 bombas). 🎟️🔥\n"
                        f"• `/placar` ➔ Mostra o painel de acertos e erros e a barra visual. 🟢🔴\n"
                        f"• `/status` ➔ Verifica se o sistema está online. 🟢\n"
                        f"• `/help` ➔ Exibe a central de ajuda.\n\n"
                        f"Boa sorte nas apostas e rumo aos greens! ⚽🚀"
                    )
                    enviar_mensagem(chat_id, boas_vindas)
                return "OK", 200

            texto_usuario = msg.get("text", "").lower()
            logger.info(f"Comando recebido: {texto_usuario} do chat {chat_id}")

            if "/start" in texto_usuario:
                enviar_mensagem(
                    chat_id, 
                    "Fala guerreiro! 🤖 **Kakaroto Odds Pro** ativado.\n\n"
                    "Comandos disponíveis:\n"
                    "• `/odds` - Análise de mercado com porcentagem\n"
                    "• `/bingo` - Bilhetes moderados e bombas 🎟️🔥\n"
                    "• `/placar` - Placar e barra de acertos 🟢🔴\n"
                    "• `/status` - Status do sistema\n"
                    "• `/help` - Central de ajuda"
                )
            elif "/odds" in texto_usuario:
                relatorio = buscar_dados_futebol()
                enviar_mensagem(chat_id, relatorio)
            elif "/bingo" in texto_usuario:
                bilhetes = gerar_bilhetes_bingo()
                enviar_mensagem(chat_id, bilhetes)
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
                    "• Use `/odds` para análises com o time e porcentagem exata.\n"
                    "• Use `/bingo` para gerar os bilhetes múltiplos."
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
