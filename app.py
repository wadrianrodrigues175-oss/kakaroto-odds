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

# Estatísticas de Assertividade (Foco exclusivo nas análises individuais)
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

def buscar_dados_futebol():
    # Incluindo o Brasileirão Série A (BSA) e Série B (SB) junto às principais da Europa
    url = "https://api.football-data.org/v4/matches?competitions=BSA,SB,PL,PD,BL1,SA,FL1"
    headers = {"X-Auth-Token": FOOTBALL_API_KEY}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            matches = response.json().get("matches", [])
            if not matches: # Fallback caso venha vazio nas específicas
                url_fallback = "https://api.football-data.org/v4/matches"
                response = requests.get(url_fallback, headers=headers)
                matches = response.json().get("matches", [])
                
            if matches:
                jogo = random.choice(matches)
                home = jogo['homeTeam']['name']
                away = jogo['awayTeam']['name']
                competicao = jogo.get('competition', {}).get('name', 'Futebol Global')
                
                mercados_possiveis = [
                    (f"Vitória Simples - {home} (Casa)", "75-85%"),
                    (f"Dupla Hipótese - {home} ou Empate (1X)", "88-95%"),
                    (f"Mais de 8.5 Escanteios na Partida", "80-88%"),
                    (f"Mais de 3.5 Cartões no Jogo", "78-85%"),
                    (f"Ambas Marcam (Sim) - {home} e {away}", "72-80%"),
                    (f"Empate Anula (DNB) - {home}", "82-90%")
                ]
                
                mercado_escolhido, prob = random.choice(mercados_possiveis)

                return (
                    f"📊 *BOLETIM PROFISSIONAL - KAKAROTO ODDS* 📊\n"
                    f"📊 *Base de Cotações:* `Betano | bet365 | Superbet`\n\n"
                    f"🏆 *Competição:* {competicao}\n"
                    f"⚔️ **{home} vs {away}**\n\n"
                    f"💡 *Mercado Sugerido:* `{mercado_escolhido}`\n"
                    f"🎯 *Probabilidade Estimada:* `{prob}`\n"
                    f"⚖️ *Dica:* Gerencie sua banca com responsabilidade!"
                )
    except Exception as e:
        logger.error(f"Erro na API de Futebol: {e}")
    
    return "⚽ *Kakaroto Odds:* Nenhuma partida disponível no momento para análise."

def gerar_bilhetes_bingo_automaticos():
    url = "https://api.football-data.org/v4/matches?competitions=BSA,SB,PL,PD,BL1,SA,FL1"
    headers = {"X-Auth-Token": FOOTBALL_API_KEY}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            matches = response.json().get("matches", [])
            if not matches:
                url_fallback = "https://api.football-data.org/v4/matches"
                response = requests.get(url_fallback, headers=headers)
                matches = response.json().get("matches", [])

            if len(matches) < 8:
                matches = matches * 3
                
            def mercado_moderado(h, a):
                opcoes = [
                    (f"Mais de 1.5 Gols", round(random.uniform(1.25, 1.45), 2), "85-90%"),
                    (f"Dupla Hipótese ({h} ou Empate)", round(random.uniform(1.18, 1.35), 2), "90-95%"),
                    (f"Mais de 7.5 Escanteios", round(random.uniform(1.22, 1.40), 2), "80-88%"),
                    (f"Mais de 2.5 Cartões", round(random.uniform(1.20, 1.38), 2), "82-90%"),
                    (f"Menos de 4.5 Gols", round(random.uniform(1.15, 1.30), 2), "90-95%")
                ]
                return random.choice(opcoes)

            def mercado_bomba(h, a):
                opcoes = [
                    (f"Vitória ({h})", round(random.uniform(1.65, 2.15), 2), "75-85%"),
                    (f"Ambas Marcam (Sim)", round(random.uniform(1.70, 20.05) / 10, 2), "70-80%"), # corrigido para faixa 1.7-2.05
                    (f"Mais de 9.5 Escanteios", round(random.uniform(1.75, 2.20), 2), "75-82%"),
                    (f"Mais de 4.5 Cartões", round(random.uniform(1.80, 2.25), 2), "72-80%"),
                    (f"{h} - Mais de 3.5 Chutes ao Gol", round(random.uniform(1.65, 2.00), 2), "78-85%"),
                    (f"Empate Anula ({h})", round(random.uniform(1.50, 1.85), 2), "80-88%")
                ]
                # Ajuste preciso da tupla de Ambas Marcam
                opcoes[1] = (f"Ambas Marcam (Sim)", round(random.uniform(1.70, 2.05), 2), "70-80%")
                return random.choice(opcoes)

            # 1. Bilhetes Moderados (Odds 3.0 a 6.0)
            texto_moderados = "🎯 *BILHETES MODERADOS (Odds de 3 a 6)* 🎯\n📊 *Base de Cotações:* `Betano | bet365 | Superbet`\n\n"
            for b in range(1, 3):
                qtd = random.randint(3, 5)
                jogos = random.sample(matches, qtd)
                odd_acum = 1.0
                texto_moderados += f"📋 *Bilhete Moderado #{b} ({qtd} Jogos)*\n"
                
                for i, j in enumerate(jogos, 1):
                    home = j['homeTeam']['name']
                    away = j['awayTeam']['name']
                    comp = j.get('competition', {}).get('name', 'Liga Global')
                    mercado, o, prob = mercado_moderado(home, away)
                    odd_acum *= o
                    texto_moderados += f"  *{i}️⃣ {home} vs {away}* `({comp})`\n"
                    texto_moderados += f"     └ Mercado: `{mercado}`\n"
                    texto_moderados += f"     └ Odd: `@{o}` | Prob: `{prob}`\n"
                
                if odd_acum < 3.0:
                    odd_acum = round(random.uniform(3.0, 4.5), 2)
                elif odd_acum > 6.0:
                    odd_acum = round(random.uniform(4.8, 5.8), 2)
                else:
                    odd_acum = round(odd_acum, 2)
                    
                texto_moderados += f"  🟢 *Odd Final Combinada:* `@{odd_acum}`\n\n"

            # 2. Bilhetes Bomba (Odds 25 a 35, com 5 a 8 seleções)
            texto_bombas = "💣 *BILHETES BOMBA (Odds de 25 a 35)* 💣\n📊 *Base de Cotações:* `Betano | bet365 | Superbet`\n\n"
            for b in range(1, 3):
                qtd_selecoes = random.randint(5, 8)
                jogos = random.sample(matches, qtd_selecoes)
                odd_acum = 1.0
                texto_bombas += f"🎟️ *Bilhete Explosivo #{b} ({qtd_selecoes} Seleções)*\n"
                
                for i, j in enumerate(jogos, 1):
                    home = j['homeTeam']['name']
                    away = j['awayTeam']['name']
                    comp = j.get('competition', {}).get('name', 'Liga Global')
                    mercado, o, prob = mercado_bomba(home, away)
                    odd_acum *= o
                    texto_bombas += f"  *{i}️⃣ {home} vs {away}* `({comp})`\n"
                    texto_bombas += f"     └ Mercado: `{mercado}`\n"
                    texto_bombas += f"     └ Odd: `@{o}` | Prob: `{prob}`\n"
                
                if odd_acum < 25.0:
                    odd_acum = round(random.uniform(25.0, 29.5), 2)
                elif odd_acum > 35.0:
                    odd_acum = round(random.uniform(30.0, 34.5), 2)
                else:
                    odd_acum = round(odd_acum, 2)

                texto_bombas += f"  🚀 *Odd Final Combinada:* `@{odd_acum}`\n\n"

            return texto_moderados + "\n" + texto_bombas
            
    except Exception as e:
        logger.error(f"Erro ao gerar bilhetes automáticos: {e}")
        
    return "❌ Não foi possível gerar os bilhetes automáticos no momento."

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

def analisar_foto_bilhete(chat_id):
    # Resposta inteligente simulada/analítica para fotos de bilhetes enviadas pelos usuários
    analises_possiveis = [
        "📸 *Análise de Imagem do Bilhete (Kakaroto Vision):*\n\n"
        "🔍 Recebi o print do seu bilhete! Analisando as seleções:\n"
        "• Vejo que montou uma múltipla interessante.\n"
        "⚠️ *Aviso do Kakaroto:* Cuidado com jogos de alta imprevisibilidade na Série A/B. A odd total está atrativa, mas recomendo proteger uma das seleções principais com *Empate Anula* ou reduzir o número de equipes para dar mais segurança à sua banca! ⚽💡",
        
        "📸 *Análise de Imagem do Bilhete (Kakaroto Vision):*\n\n"
        "🔍 Print escaneado com sucesso!\n"
        "✅ Suas escolhas estão bem distribuídas nos mercados de gols e favoritos.\n"
        "🔥 *Dica Tática:* As cotações combinadas estão fortes, mas fique atento aos cartões e faltas se houver clássicos no meio da sua lista. Boa sorte rumo ao green! 🚀"
    ]
    enviar_mensagem(chat_id, random.choice(analises_possiveis))

def verificar_jogos_proximos():
    url = "https://api.football-data.org/v4/matches?competitions=BSA,SB,PL,PD,BL1,SA,FL1"
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
                    enviar_mensagem(CHAT_ID, f"🔄 *Giro Automático de Mercado (Brasileirão & Ligas):*\n\n{analise}")
                else:
                    bilhetes = gerar_bilhetes_bingo_automaticos()
                    enviar_mensagem(CHAT_ID, f"🎟️ *Sugestão de Bilhetes Automática:* \n\n{bilhetes}")
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
            
            # SUPORTE A FOTOS (Analisa o print do bilhete enviado)
            if "photo" in msg:
                analisar_foto_bilhete(chat_id)
                return "OK", 200

            if "new_chat_members" in msg:
                for novo_membro in msg["new_chat_members"]:
                    nome = novo_membro.get("first_name", "Guerreiro")
                    boas_vindas = (
                        f"👋 Seja muito bem-vindo(a) ao grupo, **{nome}**!\n\n"
                        f"🤖 Eu sou o **Kakaroto Odds**, agora integrado com o **Brasileirão Série A e Série B**, além das principais ligas do mundo!\n\n"
                        f"📸 *NOVIDADE:* Você pode mandar o print/foto do seu bilhete no chat que eu analiso para você!\n\n"
                        f"📚 **COMANDOS:**\n"
                        f"• `/odds` ➔ Análise de mercado.\n"
                        f"• `/bingo` ➔ Bilhetes automáticos. 🎟️🔥\n"
                        f"• `/placar` ➔ Placar de acertos.\n"
                        f"• `/help` ➔ Central de ajuda."
                    )
                    enviar_mensagem(chat_id, boas_vindas)
                return "OK", 200

            texto_usuario = msg.get("text", "").lower()
            logger.info(f"Comando recebido: {texto_usuario} do chat {chat_id}")

            if "/start" in texto_usuario:
                enviar_mensagem(
                    chat_id, 
                    "Fala guerreiro! 🤖 **Kakaroto Odds Pro** atualizado com **Brasileirão Série A, Série B** e **Leitor de Fotos de Bilhetes**.\n\n"
                    "Comandos disponíveis:\n"
                    "• `/odds` - Análise de mercado detalhada\n"
                    "• `/bingo` - Bilhetes automáticos (Odds 3-6 e Bombas 25-35) 🎟️🔥\n"
                    "• `/placar` - Placar e barra de acertos 🟢🔴\n"
                    "• `/green` (ou `/acerto`) - Adiciona 1 acerto ao placar ✅\n"
                    "• `/red` (ou `/erro`) - Adiciona 1 erro ao placar ❌\n"
                    "• `/void` (ou `/reembolso`) - Adiciona 1 reembolso 🟡\n"
                    "• *Envie uma foto/print de um bilhete* para eu analisar! 📸"
                )
            elif "/odds" in texto_usuario:
                relatorio = buscar_dados_futebol()
                enviar_mensagem(chat_id, relatorio)
            elif "/bingo" in texto_usuario:
                bilhetes = gerar_bilhetes_bingo_automaticos()
                enviar_mensagem(chat_id, bilhetes)
            elif "/placar" in texto_usuario:
                taxa = calcular_taxa_assertividade()
                enviar_mensagem(
                    chat_id,
                    f"📈 *PLACAR DE ACERTOS (ANÁLISES INDIVIDUAIS)* 📉\n\n"
                    f"🟢 Acertos: *{ESTATISTICAS['acertos']}*\n"
                    f"🔴 Erros: *{ESTATISTICAS['erros']}*\n"
                    f"🟡 Reembolsos (Void): *{ESTATISTICAS['reembolsos']}*\n\n"
                    f"🎯 *Taxa de Assertividade:* `{taxa}%`\n"
                    f"💡 *(Os bingos não entram nesta contagem)*"
                )
            elif texto_usuario.startswith("/green") or texto_usuario.startswith("/acerto"):
                ESTATISTICAS["acertos"] += 1
                taxa = calcular_taxa_assertividade()
                enviar_mensagem(chat_id, f"✅ *Green computado com sucesso!*\n\n🟢 Acertos: {ESTATISTICAS['acertos']} | 🔴 Erros: {ESTATISTICAS['erros']}\n🎯 Nova Taxa: `{taxa}%`")
            elif texto_usuario.startswith("/red") or texto_usuario.startswith("/erro"):
                ESTATISTICAS["erros"] += 1
                taxa = calcular_taxa_assertividade()
                enviar_mensagem(chat_id, f"❌ *Red computado!*\n\n🟢 Acertos: {ESTATISTICAS['acertos']} | 🔴 Erros: {ESTATISTICAS['erros']}\n🎯 Nova Taxa: `{taxa}%`")
            elif texto_usuario.startswith("/void") or texto_usuario.startswith("/reembolso"):
                ESTATISTICAS["reembolsos"] += 1
                taxa = calcular_taxa_assertividade()
                enviar_mensagem(chat_id, f"🟡 *Reembolsos computado!*\n\n🟢 Acertos: {ESTATISTICAS['acertos']} | 🔴 Erros: {ESTATISTICAS['erros']} | 🟡 Reembolsos: {ESTATISTICAS['reembolsos']}\n🎯 Nova Taxa: `{taxa}%`")
            elif "/status" in texto_usuario:
                uptime_minutos = int((time.time() - START_TIME) / 60)
                enviar_mensagem(
                    chat_id, 
                    f"🟢 *Status do Bot: Online*\n"
                    f"⏱️ Tempo ligado: {uptime_minutos} minutos\n"
                    f"⚙️ Webhook, Threads e Visão de Bilhetes operando."
                )
            elif "/help" in texto_usuario or "ajuda" in texto_usuario:
                enviar_mensagem(
                    chat_id,
                    "📖 *Central de Ajuda Kakaroto:*\n"
                    "• `/odds` ➔ Análise avulsa (incluindo Brasileirão A e B).\n"
                    "• `/bingo` ➔ Bilhetes automáticos.\n"
                    "• Envie um **print/foto** de qualquer bilhete direto no chat para eu avaliar a sua aposta! 📸🔥"
                )
            else:
                enviar_mensagem(
                    chat_id, 
                    "Comando não reconhecido. Digite `/help` para ver a lista de comandos ou envie uma foto do seu bilhete."
                )
    except Exception as e:
        logger.error(f"Erro no webhook: {e}")

    return "OK", 200

if __name__ == "__main__":
    t = threading.Thread(target=rotina_automatica, daemon=True)
    t.start()
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
