import os
import threading
from flask import Flask
import requests

app = Flask(__name__)

# Configurações do Telegram
TOKEN = "8766250524:AA..." # Seu token completo
CHAT_ID = "8752935420"

@app.route('/')
def home():
    return "KAKAROTO ODDS BOT IS RUNNING!"

def bot_polling():
    # Executa o polling ou a rotina de envio do robô
    import telebot
    bot = telebot.TeleBot(TOKEN)

    @bot.message_handler(commands=['start', 'odds'])
    def send_welcome(message):
        bot.reply_to(message, "Bot KAKAROTO ODDS ativado e pronto para enviar análises!")

    bot.infinity_polling()

if __name__ == "__main__":
    # Inicia o polling do Telegram em uma thread separada
    t = threading.Thread(target=bot_polling)
    t.daemon = True
    t.start()
    
    # Inicia a API do Flask na porta correta requisitada pelo Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
