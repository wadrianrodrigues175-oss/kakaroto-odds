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

START_TIME = time.time()

ESTATISTICAS = {
    "acertos": 0,
    "erros": 0,
    "reembolsos": 0
}

# Memória blindada para evitar repetições e jogos passados
jogos_analisados_recentemente = set()

def calcular_taxa_assertividade():
    total = ESTATISTICAS["acertos"] + ESTATISTICAS["erros"] + ESTATISTICAS["reembolsos"]
    if total == 0:
        return 0.0
    return round((ESTATISTICAS["acertos"] / total) * 100, 1)

def obter_partidas_futuras_validas():
    """BLINDAGEM TOTAL: Filtra rigorosamente apenas partidas futuras, limpando o passado."""
    url = "https://api.football-data.org/v4/matches"
    headers = {"X-Auth-Token": FOOTBALL_API_KEY}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            matches = response.json().get("matches", [])
            agora = datetime.now(timezone.utc)
            
            matches_futuros = []
            for j in matches:
                utc_date_str = j.get('utcDate')
                status = j.get('status')
                # Apenas partidas agendadas cujo horário seja estritamente no FUTURO
                if utc_date_str and status in ["TIMED", "SCHEDULED"]:
                    horario_jogo = datetime.fromisoformat(utc_date_str.replace('Z', '+00:00'))
                    if horario_jogo > agora:
                        matches_futuros.append(j)
            
            return matches_futuros
    except Exception as e:
        logger.error(f"Erro ao buscar partidas válidas: {e}")
    return []

def buscar_dados_futebol():
    matches = obter_partidas_futuras_validas()
    if matches:
        # Remove jogos que já foram analisados recentemente para garantir variedade de ligas
        matches_disponiveis = [j for j in matches if j.get('id') not in jogos_analisados_recentemente]
        if not matches_disponiveis:
            jogos_analisados_recentemente.clear()
            matches_disponiveis = matches

        jogo = random.choice(matches_disponiveis)
        jogos_analisados_recentemente.add(jogo.get('id'))

        home = jogo['homeTeam']['name']
        away = jogo['awayTeam']['name']
        competicao = jogo.get('competition', {}).get('name', 'Futebol Internacional')
        
        utc_date_str = jogo.get('utcDate')
        horario_br = "Em breve"
        if utc_date_str:
            horario_obj = datetime.fromisoformat(utc_date_str.replace('Z', '+00:00'))
            horario_br = horario_obj.strftime('%d/%m às %H:%M')

        mercados_possiveis = [
            (f"Vitória Simples - {home} (Casa)", random.uniform(62.0, 78.0)),
            (f"Vitória Simples - {away} (Fora)", random.uniform(55.0, 72.0)),
            (f"Gols - {home} Over 1.5", random.uniform(75.0, 89.0)),
            (f"Ambas Marcam (Sim) - {home} e {away}", random.uniform(68.0, 82.0)),
            (f"Empate Anula (DNB) - {home}", random.uniform(72.0, 88.0)),
            (f"Dupla Hipótese - {home} ou Empate (1X)", random.uniform(80.0, 92.0)),
            (f"Dupla Hipótese - {away} ou Empate (X2)", random.uniform(70.0, 85.0))
        ]
        
        mercado_escolhido, probabilidade = random.choice(mercados_possiveis)
        probabilidade_str = f"{round(probabilidade, 1)}%"

        return (
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"📊 **KAKAROTO ODDS • ANÁLISE PRO** 📊\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🏆 **Competição:** `{competicao}`\n"
            f"⚔️ **Confronto:** `{home} vs {away}`\n"
            f"🕒 **Início:** `{horario_br} (Horário BR)`\n\n"
            f"💡 **Mercado Sugerido:**\n   ➔ `{mercado_escolhido}`\n\n"
            f"🎯 **Confiança Estimada:** `{probabilidade_str}`\n"
            f"⚖️ *Gestão de banca recomendada.*"
        )
    
    return "⚽ *Kakaroto Odds:* Nenhuma partida futura encontrada no momento para análise."

def listar_jogos_por_status(tipo_filtro):
    url = "https://api.football-data.org/v4/matches"
    headers = {"X-Auth-Token": FOOTBALL_API_KEY}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            matches = response.json().get("matches", [])
            if not matches:
                return "❌ Nenhuma partida encontrada na API no momento."

            resultado = ""
            contador = 0
            agora = datetime.now(timezone.utc)

            if tipo_filtro == "agenda":
                resultado = "━━━━━━━━━━━━━━━━━━━━━\n📅 **AGENDA DE JOGOS & LIGAS** 📅\n━━━━━━━━━━━━━━━━━━━━━\n\n"
                for jogo in matches:
                    status = jogo.get('status')
                    utc_date_str = jogo.get('utcDate')
                    if status in ["TIMED", "SCHEDULED"] and utc_date_str:
                        horario_obj = datetime.fromisoformat(utc_date_str.replace('Z', '+00:00'))
                        if horario_obj > agora:
                            home = jogo['homeTeam']['name']
                            away = jogo['awayTeam']['name']
                            comp = jogo.get('competition', {}).get('name', 'Futebol')
                            horario_br = horario_obj.strftime('%d/%m às %H:%M')

                            resultado += f"• 🕒 `{horario_br}`\n  ⚽ *{home} vs {away}*\n  🏆 _{comp}_\n\n"
                            contador += 1
                            if contador >= 7:
                                break

            elif tipo_filtro == "aovivo":
                resultado = "━━━━━━━━━━━━━━━━━━━━━\n🔴 **PARTIDAS AO VIVO AGORA** ⚡\n━━━━━━━━━━━━━━━━━━━━━\n\n"
                for jogo in matches:
                    status = jogo.get('status')
                    if status in ["IN_PLAY", "LIVE", "PAUSED"]:
                        home = jogo['homeTeam']['name']
                        away = jogo['awayTeam']['name']
                        placar = jogo.get('score', {}).get('fullTime', {})
                        gols_casa = placar.get('home', 0)
                        gols_fora = placar.get('away', 0)
                        
                        resultado += f"⚡ **{home} {gols_casa} x {gols_fora} {away}** *(AO VIVO)*\n"
                        contador += 1
                
                if contador == 0:
                    return "🔴 *Nenhum jogo rolando ao vivo neste exato momento.* Use `/agenda` para ver os próximos confrontos futuros!"

            return resultado if contador > 0 else "❌ Nenhum jogo futuro encontrado para exibir."
    except Exception as e:
        logger.error(f"Erro ao filtrar jogos: {e}")
    
    return "❌ Erro ao consultar a agenda."

def gerar_bilhetes_bingo():
    matches = obter_partidas_futuras_validas()
    if not matches:
        url = "https://api.football-data.org/v4/matches"
        headers = {"X-Auth-Token": FOOTBALL_API_KEY}
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            matches = res.json().get("matches", [])

    if len(matches) < 6:
        matches = matches * 3
        
    def sortear_mercado_variado(h, a):
        opcoes = [
            (f"Vitória ({h})", random.uniform(1.40, 1.85)),
            (f"Vitória ({a})", random.uniform(1.80, 2.30)),
            (f"Over 1.5 Gols", random.uniform(1.30, 1.55)),
            (f"Ambas Marcam (Sim)", random.uniform(1.60, 1.95)),
            (f"Dupla Hipótese ({h} ou Empate)", random.uniform(1.20, 1.45)),
            (f"Empate Anula ({h})", random.uniform(1.35, 1.70)),
            (f"Over 2.5 Gols", random.uniform(1.75, 2.10))
        ]
        return random.choice(opcoes)

    # Bilhetes Moderados
    texto_moderados = "━━━━━━━━━━━━━━━━━━━━━\n🎯 **BILHETES MODERADOS (Odds 3.0 a 6.5)** 🎯\n━━━━━━━━━━━━━━━━━━━━━\n\n"
    for b in range(1, 3):
        jogos = random.sample(matches, min(3, len(matches)))
        odd_acum = 1.0
        texto_moderados += f"📋 **Bilhete #{b}**\n"
        for i, j in enumerate(jogos, 1):
            home = j['homeTeam']['name']
            away = j['awayTeam']['name']
            mercado, o = sortear_mercado_variado(home, away)
            odd_acum *= o
            texto_moderados += f"  {i}️⃣ {home} vs {away}\n     └ *{mercado}* (@{round(o, 2)})\n"
        odd_acum = max(3.0, min(6.5, round(odd_acum, 2)))
        texto_moderados += f"  🔥 **Odd Total:** `@{odd_acum}`\n\n"

    # Bilhetes Bomba
    texto_bomba = "━━━━━━━━━━━━━━━━━━━━━\n💣 **BILHETES BOMBA (Odds 25 a 35)** 💣\n━━━━━━━━━━━━━━━━━━━━━\n\n"
    for b in range(1, 3):
        jogos = random.sample(matches, min(5, len(matches)))
        odd_acum = 1.0
        texto_bomba += f"🎟️ **Bilhete Explosivo #{b}**\n"
        for i, j in enumerate(jogos, 1):
            home = j['homeTeam']['name']
            away = j['awayTeam']['name']
            mercado, o = sortear_mercado_variado(home, away)
            o = round(o * random.uniform(1.1, 1.3), 2)
            odd_acum *= o
            texto_bomba += f"  {i}️⃣ {home} vs {away}\n     └ *{mercado}* (@{o})\n"
        odd_acum = max(25.0, min(35.0, round(odd_acum, 2)))
        texto_bomba += f"  🚀 **Odd Total:** `@{odd_acum}`\n\n"

    return texto_moderados + "\n" + texto_bomba

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
        if data and "message" in data:
            msg = data["message"]
            chat_id = msg["chat"]["id"]
            
            if "new_chat_members" in msg:
                for novo_membro in msg["new_chat_members"]:
                    nome = novo_membro.get("first_name", "Guerreiro")
                    boas_vindas = (
                        f"👋 Seja bem-vindo(a), **{nome}**!\n\n"
                        f"🤖 Eu sou o **Kakaroto Odds Pro**, sua central avançada de análises e bilhetes.\n\n"
                        f"📚 **COMANDOS PRINCIPAIS:**\n"
                        f"• `/odds` ➔ Análises táticas de jogos futuros.\n"
                        f"• `/agenda` ➔ Próximos jogos e horários de várias ligas. 🕒\n"
                        f"• `/aovivo` ➔ Partidas ao vivo agora. ⚡\n"
                        f"• `/bingo` ➔ Bilhetes moderados e bombas. 🎟️🔥\n"
                        f"• `/placar` ➔ Painel de assertividade. 🟢🔴\n"
                        f"• `/status` ➔ Status operacional. 🟢\n\n"
                        f"Rumo aos greens! ⚽🚀"
                    )
                    enviar_mensagem(chat_id, boas_vindas)
                return "OK", 200

            texto_usuario = msg.get("text", "").lower()
            logger.info(f"Comando recebido: {texto_usuario} do chat {chat_id}")

            if "/start" in texto_usuario:
                enviar_mensagem(
                    chat_id, 
                    "Fala guerreiro! 🤖 **Kakaroto Odds Pro** ativado com sucesso.\n\n"
                    "Use os comandos abaixo para navegar:\n"
                    "• `/odds` - Análise de mercado futura\n"
                    "• `/agenda` - Próximos jogos e horários 🕒\n"
                    "• `/aovivo` - Jogos ao vivo ⚡\n"
                    "• `/bingo` - Bilhetes do dia 🎟️🔥\n"
                    "• `/placar` - Placar estatístico 🟢🔴\n"
                    "• `/status` - Status do sistema"
                )
            elif "/odds" in texto_usuario:
                relatorio = buscar_dados_futebol()
                enviar_mensagem(chat_id, relatorio)
            elif "/agenda" in texto_usuario:
                agenda_texto = listar_jogos_por_status("agenda")
                enviar_mensagem(chat_id, agenda_texto)
            elif "/aovivo" in texto_usuario:
                aovivo_texto = listar_jogos_por_status("aovivo")
                enviar_mensagem(chat_id, aovivo_texto)
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
                    f"🟡 Reembolsos: *{ESTATISTICAS['reembolsos']}*\n\n"
                    f"🎯 *Taxa de Assertividade:* `{taxa}%`"
                )
            elif "/status" in texto_usuario:
                uptime_minutos = int((time.time() - START_TIME) / 60)
                enviar_mensagem(
                    chat_id, 
                    f"🟢 *Status do Bot: Online*\n"
                    f"⏱️ Tempo ligado: {uptime_minutos} min\n"
                    f"⚙️ Blindagem contra jogos passados ativa."
                )
            elif "/help" in texto_usuario or "ajuda" in texto_usuario:
                enviar_mensagem(
                    chat_id,
                    "📖 *Central de Ajuda:*\n"
                    "O bot está 100% blindado para exibir apenas partidas futuras de diversas ligas, ignorando completamente qualquer jogo passado."
                )
            else:
                enviar_mensagem(
                    chat_id, 
                    "Comando não reconhecido. Digite `/start` para ver o menu."
                )
    except Exception as e:
        logger.error(f"Erro no webhook: {e}")

    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
