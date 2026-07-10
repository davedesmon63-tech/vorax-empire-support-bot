from flask import Flask, request
import requests
import os

app = Flask(__name__)

TOKEN = "8986961042:AAHR4CxbGVu6f0_Ea-bLHAIOQgx1VOwAwtI"
URL = f"https://api.telegram.org/bot{TOKEN}/"
ADMIN_ID = 8851256338 # TON ID ICI

users = set() # Pour stocker les IDs des utilisateurs

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")
        users.add(chat_id) # On enregistre chaque user
        
        # ===== MENU CLIENT =====
        if text == "/start":
            menu = (
                "🚀 BIENVENUE SUR VORAX EMPIRE BOT 🚀\n\n"
                "Choisis une option ci-dessous :"
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
            send_message(chat_id, "📦 Envoie ton numéro de commande. Ex: #CMD1234")
        elif text == "🎧 Support Client":
            send_message(chat_id, "🎧 SUPPORT\nDécris ton problème. Un agent te répond entre 9h et 18h.")
        elif text == "❓ FAQ":
            send_message(chat_id, "❓ FAQ\n1. Délais: 24h - 48h\n2. Paiement: Orange Money, Wave\n3. Livraison: Abidjan et partout CI")
        elif text == "💰 Paiement & Tarifs":
            send_message(chat_id, "💰 TARIFS\nDemande un devis via /support\nPaiement: OM 07 00 00 00 00")
        elif text == "📞 Nous Contacter":
            send_message(chat_id, "📞 CONTACT\nWhatsApp: +225 07 00 00 00 00\nEmail: contact@voraxempire.com")
            
        # ===== PANEL ADMIN =====
        elif text == "/admin" and chat_id == ADMIN_ID:
            admin_menu = (
                "👑 PANEL ADMIN VORAX EMPIRE 👑\n\n"
                "/stats - Voir statistiques\n"
                "/users - Voir nb d'utilisateurs\n"
                "/broadcast message - Envoyer à tous\n"
                "/reply ID message - Répondre à un client"
            )
            send_message(chat_id, admin_menu)
            
        elif text == "/stats" and chat_id == ADMIN_ID:
            send_message(chat_id, f"📊 STATISTIQUES\nUtilisateurs totaux: {len(users)}")
            
        elif text == "/users" and chat_id == ADMIN_ID:
            send_message(chat_id, f"👥 Utilisateurs: {len(users)}\nIDs: {list(users)}")
            
        elif text.startswith("/broadcast") and chat_id == ADMIN_ID:
            message = text.replace("/broadcast ", "")
            for user_id in users:
                send_message(user_id, f"📢 ANNONCE VORAX EMPIRE:\n\n{message}")
            send_message(chat_id, f"✅ Message envoyé à {len(users)} utilisateurs")
            
        elif text.startswith("/reply") and chat_id == ADMIN_ID:
            try:
                parts = text.split(" ", 2)
                target_id = int(parts[1])
                reply_msg = parts[2]
                send_message(target_id, f"🎧 SUPPORT VORAX EMPIRE:\n\n{reply_msg}")
                send_message(chat_id, "✅ Réponse envoyée")
            except:
                send_message(chat_id, "Erreur. Format: /reply ID message")
                
        elif chat_id == ADMIN_ID and not text.startswith("/"):
            pass # L'admin peut taper normal
            
        else:
            if chat_id!= ADMIN_ID:
                send_message(ADMIN_ID, f"💬 NOUVEAU MESSAGE de {chat_id}:\n{text}")
                send_message(chat_id, "✅ Ton message a été envoyé au support")

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