from flask import Flask, request
import requests
import os

app = Flask(__name__)

TOKEN = "8986961042:AAHR4CxbGVu6f0_Ea-bLHAIOQgx1VOwAwtI"
URL = f"https://api.telegram.org/bot{TOKEN}/"

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")
        
        if text == "/start":
            menu = (
                "🚀 BIENVENUE SUR VORAX EMPIRE BOT 🚀\n\n"
                "Choisis une option ci-dessous :\n\n"
                "1. 📦 Mes Commandes\n"
                "2. 🎧 Support Client\n"
                "3. ❓ FAQ\n"
                "4. 💰 Paiement & Tarifs\n"
                "5. 📞 Nous Contacter"
            )
            keyboard = {
                "keyboard": [
                    ["📦 Mes Commandes", "🎧 Support Client"],
                    ["❓ FAQ", "💰 Paiement & Tarifs"],
                    ["📞 Nous Contacter"]
                ],
                "resize_keyboard": True
            }
            send_message(chat_id, menu, keyboard)
            
        elif text == "📦 Mes Commandes":
            send_message(chat_id, "📦 Pour suivre ta commande, envoie ton numéro de commande.\nEx: #CMD1234")
        elif text == "🎧 Support Client":
            send_message(chat_id, "🎧 SUPPORT\nDécris ton problème ici.\nUn agent te répond entre 9h et 18h.")
        elif text == "❓ FAQ":
            send_message(chat_id, "❓ FAQ VORAX EMPIRE\n1. Délais: 24h - 48h\n2. Paiement: Orange Money, Wave\n3. Livraison: Abidjan et partout CI")
        elif text == "💰 Paiement & Tarifs":
            send_message(chat_id, "💰 TARIFS\nDemande un devis via /support\nPaiement: OM 07 00 00 00 00")
        elif text == "📞 Nous Contacter":
            send_message(chat_id, "📞 CONTACT\nWhatsApp: +225 07 00 00 00 00\nEmail: contact@voraxempire.com")
        elif text == "/help":
            send_message(chat_id, "Tape /start pour voir le menu")
        elif text == "/support":
            send_message(chat_id, "🎧 Décris ton problème ici.")
        else:
            send_message(chat_id, "Choisis une option dans le menu 👇 ou tape /start")
            
    return "ok"

def send_message(chat_id, text, keyboard=None):
    payload = {"chat_id": chat_id, "text": text}
    if keyboard:
        payload["reply_markup"] = keyboard
    requests.post(URL + "sendMessage", json=payload)

@app.route("/")
def home():
    return "VORAX EMPIRE BOT is running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))