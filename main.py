from flask import Flask, request
import requests
import os
from datetime import datetime

app = Flask(__name__)

TOKEN = os.environ.get("TOKEN")
URL = f"https://api.telegram.org/bot{TOKEN}/"
CODE_ACCES = "VORAX1K2025"
ESSAIS_GRATUITS = 3
NUMERO_WAVE = "+225 05 46 51 81 67"
user_data = {}

def send_message(chat_id, text):
    requests.post(URL + "sendMessage", json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"})

def send_buttons(chat_id, text, buttons):
    keyboard = {"inline_keyboard": buttons}
    requests.post(URL + "sendMessage", json={"chat_id": chat_id, "text": text, "reply_markup": keyboard, "parse_mode": "Markdown"})

def creer_ticket_whatsapp(data, type_compte):
    date = datetime.now().strftime("%d/%m/%Y %H:%M")
    ticket_id = f"VX{datetime.now().strftime('%d%m%H%M')}"
    
    # === LA MAGIE POUR LA PRIORITÉ ===
    if type_compte == "VIP" and data.get('urgence') == "URGENT":
        header = f"🚨 *ALERTE TICKET URGENT VIP* 🚨🚨%0A"
        statut = f"🔴 *TRAITEMENT IMMÉDIAT - MOINS DE 2H* 🔴"
    elif type_compte == "VIP":
        header = f"👑 *TICKET SUPPORT VIP* 👑%0A"
        statut = f"🟡 *TRAITEMENT PRIORITAIRE - MOINS DE 2H* 🟡"
    else: # Gratuit
        header = f"📝 *TICKET SUPPORT STANDARD* 📝%0A"
        statut = f"⚪ *TRAITEMENT STANDARD - 24H* ⚪"

    msg = f"{header}"
    msg += f"━━━━━━━━━━%0A"
    msg += f"*ID:* {ticket_id} | *Date:* {date}%0A"
    msg += f"*Statut:* {statut}%0A"
    msg += f"━━━━━━━━━━%0A%0A"
    msg += f"*👤 CLIENT:* {data.get('nom', '')}%0A"
    msg += f"*📞 Contact:* {data.get('contact', '')}%0A%0A"
    msg += f"*🛍️ PRODUIT:* {data.get('produit', '')}%0A"
    msg += f"*📋 CATÉGORIE:* {data.get('probleme', '')}%0A%0A"
    msg += f"*📝 DESCRIPTION:*%0A_{data.get('details', '')}_%0A%0A"
    msg += f"━━━━━━━━━━%0A"
    msg += f"_Ne pas ignorer. Client {type_compte} Vorax Empire_"
    
    lien = f"https://wa.me/2250546518167?text={msg}"
    return lien, ticket_id

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")
        if chat_id not in user_data: user_data[chat_id] = {"essais": 0, "vip": False, "step": ""}

        step = user_data[chat_id]["step"]

        if text == "/start":
            essais_restants = ESSAIS_GRATUITS - user_data[chat_id]["essais"]
            if user_data[chat_id]["vip"]:
                send_message(chat_id, "👑 *COMPTE VIP ACTIF*\nAccès illimité + Priorité 2H")
            elif essais_restants > 0:
                buttons = [[{"text": "🆓 Essai Gratuit", "callback_data": "gratuit"}], [{"text": "💳 Devenir VIP 1000F", "callback_data": "acheter"}]]
                send_message(chat_id, f"👋 *SUPPORT VORAX EMPIRE*\n\n🆓 *{essais_restants} essais gratuits restants*\n_Pas de priorité. Réponse 24H_\n\n👑 *VIP 1000F/mois*\n_Réponse 2H + Ticket Prioritaire_")
            else:
                buttons = [[{"text": "💳 Acheter VIP 1000F", "callback_data": "acheter"}]]
                send_message(chat_id, "😅 *3 essais terminés*\nPasse VIP pour débloquer le support prioritaire.")

        elif text == CODE_ACCES:
            user_data[chat_id] = {"essais": user_data[chat_id]["essais"], "vip": True, "step": "nom"}
            send_message(chat_id, "✅ *VIP ACTIVÉ*\n*1/5* Nom et Prénom :")

        elif step == "nom":
            user_data[chat_id].update({"nom": text, "step": "contact"})
            send_message(chat_id, "*2/5* Votre numéro :")
        elif step == "contact":
            user_data[chat_id].update({"contact": text, "step": "produit"})
            send_message(chat_id, "*3/5* Produit/Service :")
        elif step == "produit":
            user_data[chat_id].update({"produit": text, "step": "probleme"})
            buttons = [[{"text": "Réclamation", "callback_data": "Réclamation"}], [{"text": "Paiement", "callback_data": "Paiement"}], [{"text": "Livraison", "callback_data": "Livraison"}], [{"text": "Info", "callback_data": "Info"}]]
            send_buttons(chat_id, "*4/5* Catégorie :", buttons)
        elif step == "details":
            user_data[chat_id]["details"] = text
            type_compte = "VIP" if user_data[chat_id]["vip"] else "GRATUIT"
            lien, ticket = creer_ticket_whatsapp(user_data[chat_id], type_compte)
            if not user_data[chat_id]["vip"]: user_data[chat_id]["essais"] += 1
            essais_restants = ESSAIS_GRATUITS - user_data[chat_id]["essais"]
            msg_fin = f"✅ *TICKET {type_compte} PRÊT*\n" if user_data[chat_id]["vip"] else f"✅ *TICKET {type_compte} PRÊT*\n_Il reste {essais_restants} essais_"
            send_buttons(chat_id, msg_fin, [[{"text": f"🚀 ENVOYER TICKET {ticket}", "url": lien}]])
            user_data[chat_id]["step"] = ""

    if "callback_query" in data:
        chat_id = data["callback_query"]["message"]["chat"]["id"]
        data_btn = data["callback_query"]["data"]
        if chat_id not in user_data: user_data[chat_id] = {"essais": 0, "vip": False, "step": ""}
        
        if data_btn == "gratuit":
            if user_data[chat_id]["essais"] < ESSAIS_GRATUITS:
                user_data[chat_id]["step"] = "nom"
                send_message(chat_id, "🆓 *MODE GRATUIT*\n_Réponse 24H_\n*1/5* Nom :")
            else: send_message(chat_id, "❌ Plus d'essais.")
        elif data_btn == "acheter":
            send_message(chat_id, f"💳 *1000F VIA WAVE*\nEnvoie à {NUMERO_WAVE}\nPuis capture + `CODE VIP` au {NUMERO_WAVE}")
        elif user_data[chat_id]["step"] == "probleme":
            user_data[chat_id].update({"probleme": data_btn, "step": "urgence"})
            if user_data[chat_id]["vip"]:
                buttons = [[{"text": "🔴 URGENT - 2H", "callback_data": "URGENT"}], [{"text": "🟡 NORMAL - 24H", "callback_data": "NORMAL"}]]
            else: buttons = [[{"text": "🟡 NORMAL - 24H", "callback_data": "NORMAL"}]]
            send_buttons(chat_id, "*5/5* Priorité :", buttons)
        elif user_data[chat_id]["step"] == "urgence":
            user_data[chat_id].update({"urgence": data_btn, "step": "details"})
            send_message(chat_id, "Décrivez le problème en détail :")

    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
