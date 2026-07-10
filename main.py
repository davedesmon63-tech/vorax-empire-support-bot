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
            send_message(chat_id, "Bot online ✅\nBienvenue sur VORAX EMPIRE BOT")
        elif text == "/help":
            send_message(chat_id, "Commandes:\n/start - Démarrer\n/support - Support")
        else:
            send_message(chat_id, "Tape /start pour commencer")
            
    return "ok"

def send_message(chat_id, text):
    requests.post(URL + "sendMessage", json={"chat_id": chat_id, "text": text})

@app.route("/")
def home():
    return "VORAX EMPIRE BOT is running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))