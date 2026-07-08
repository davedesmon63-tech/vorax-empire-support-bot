import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("TELEGRAM_TOKEN") # Render va lire ça tout seul

app = Flask(__name__)
application = Application.builder().token(TOKEN).build()

# 1. Tes commandes du bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bienvenue sur VORAX EMPIRE 🔥")

application.add_handler(CommandHandler("start", start))


# 2. La route que Render va utiliser
@app.route('/webhook', methods=['POST'])
def webhook():
    application.update_queue.put(Update.de_json(request.get_json(), application.bot))
    return "ok"


# 3. Lancer le serveur web pour Render
if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    application.run_webhook(
        listen="0.0.0.0",
        port=port,
        webhook_url=f"https://vorax-bot.onrender.com/webhook" # Change par ton URL Render
    ) 