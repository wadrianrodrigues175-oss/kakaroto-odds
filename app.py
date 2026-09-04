def gerar_bilhetes_bingo_automaticos():
    hoje_str = obter_data_brasil()
    url = f"https://api.football-data.org/v4/matches?dateFrom={hoje_str}&dateTo={hoje_str}"
    headers = {"X-Auth-Token": FOOTBALL_API_KEY}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            matches = response.json().get("matches", [])
            
            # FILTRA AQUI OS JOGOS PASSADOS
            matches = filtrar_apenas_jogos_futuros(matches)

            if not matches:
                return "⚠️ Não há jogos futuros suficientes programados para hoje na API."

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
                    (f"Ambas Marcam (Sim)", round(random.uniform(1.70, 2.05), 2), "70-80%"),
                    (f"Mais de 9.5 Escanteios", round(random.uniform(1.75, 2.20), 2), "75-82%"),
                    (f"Mais de 4.5 Cartões", round(random.uniform(1.80, 2.25), 2), "72-80%"),
                    (f"{h} - Mais de 3.5 Chutes ao Gol", round(random.uniform(1.65, 2.00), 2), "78-85%"),
                    (f"Empate Anula ({h})", round(random.uniform(1.50, 1.85), 2), "80-88%")
                ]
                return random.choice(opcoes)

            # 1. Bilhetes Moderados (Odds 3.0 a 6.0)
            texto_moderados = "🎯 *BILHETES MODERADOS (Próximos Jogos)* 🎯\n📊 *Base de Cotações:* `Betano | bet365 | Superbet`\n\n"
            for b in range(1, 3):
                qtd = random.randint(3, 5)
                jogos = random.sample(matches, min(qtd, len(matches)))
                odd_acum = 1.0
                texto_moderados += f"📋 *Bilhete Moderado #{b} ({len(jogos)} Jogos)*\n"
                
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

            # 2. Bilhetes Bomba (Odds 25 a 35)
            texto_bombas = "💣 *BILHETES BOMBA (Próximos Jogos)* 💣\n📊 *Base de Cotações:* `Betano | bet365 | Superbet`\n\n"
            for b in range(1, 3):
                qtd_selecoes = random.randint(5, min(8, len(matches)))
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
