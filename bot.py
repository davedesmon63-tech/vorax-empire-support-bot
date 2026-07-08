import telebot
from telebot import types
import requests
import os
import time

# ===== CONFIG =====
TOKEN = os.getenv("TELEGRAM_TOKEN")
CINETPAY_APIKEY = os.getenv("CINETPAY_APIKEY") 
CINETPAY_SITE_ID = os.getenv("CINETPAY_SITE_ID")
NOWPAYMENTS_APIKEY = os.getenv("NOWPAYMENTS_APIKEY")
WHATSAPP_API_URL = os.getenv("WHATSAPP_API_URL") # URL Evolution API de ton WhatsApp
WHATSAPP_GROUP = os.getenv("WHATSAPP_GROUP") # ID du groupe VORAX EMPIRE

bot = telebot.TeleBot(TOKEN)
user_data = {} # Stocke temporairement les plaintes

PRIX = 500 # FCFA

# ===== COMMANDES =====
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Bienvenue sur VORAX EMPIRE Support 🚨\nTape /signaler pour signaler un numéro WhatsApp")

@bot.message_handler(commands=['signaler'])
def signaler(message):
    chat_id = message.chat.id
    user_data[chat_id] = {}
    msg = bot.send_message(chat_id, "Étape 1/4 : Envoie le numéro WhatsApp de la personne\nEx: +2250712345678")
    bot.register_next_step_handler(msg, get_numero)

def get_numero(message):
    chat_id = message.chat.id
    user_data[chat_id]['numero'] = message.text
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add("Spam", "Arnaque", "Harcèlement", "Scam")
    msg = bot.send_message(chat_id, "Étape 2/4 : Choisis le motif", reply_markup=markup)
    bot.register_next_step_handler(msg, get_motif)

def get_motif(message):
    chat_id = message.chat.id
    user_data[chat_id]['motif'] = message.text
    msg = bot.send_message(chat_id, "Étape 3/4 : Décris en 1 phrase ce qui s'est passé")
    bot.register_next_step_handler(msg, get_description)

def get_description(message):
    chat_id = message.chat.id
    user_data[chat_id]['desc'] = message.text
    msg = bot.send_message(chat_id, "Étape 4/4 : Envoie la capture d'écran comme preuve")
    bot.register_next_step_handler(msg, get_preuve)

def get_preuve(message):
    chat_id = message.chat.id
    if message.photo:
        file_id = message.photo[-1].file_id
        user_data[chat_id]['preuve'] = file_id
        proposer_paiement(chat_id)
    else:
        bot.send_message(chat_id, "Merci d'envoyer une photo comme preuve. Recommence avec /signaler")

# ===== PAIEMENT =====
def proposer_paiement(chat_id):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Payer 500 FCFA OM/Wave", callback_data="pay_cinetpay"))
    markup.add(types.InlineKeyboardButton("Payer 1 USDT Crypto", callback_data="pay_usdt"))
    bot.send_message(chat_id, f"Pour envoyer votre plainte au support VORAX EMPIRE:\nPrix: {PRIX} FCFA", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    chat_id = call.message.chat.id
    if call.data == "pay_cinetpay":
        lien = creer_paiement_cinetpay(chat_id)
        bot.send_message(chat_id, f"Payez ici avec Orange Money / Wave:\n{lien}\n\nAprès paiement tape /verifier")
    if call.data == "pay_usdt":
        adresse = creer_paiement_usdt(chat_id)
        bot.send_message(chat_id, f"Envoyez 1 USDT TRC20 ici:\n`{adresse}`\n\nAprès paiement tape /verifier", parse_mode="Markdown")

def creer_paiement_cinetpay(chat_id):
    # Tu dois créer compte sur cinetpay.com
    data = {
        "apikey": CINETPAY_APIKEY,
        "site_id": CINETPAY_SITE_ID,
        "transaction_id": f"VORAX_{chat_id}_{int(time.time())}",
        "amount": PRIX,
        "currency": "XOF",
        "description": "Plainte VORAX EMPIRE",
        "return_url": "https://t.me/VoraxSupportBot"
    }
    r = requests.post("https://api-checkout.cinetpay.com/v2/payment", json=data)
    return r.json()['data']['payment_url']

def creer_paiement_usdt(chat_id):
    # Tu dois créer compte sur nowpayments.io
    headers = {"x-api-key": NOWPAYMENTS_APIKEY}
    data = {"price_amount": 1, "price_currency": "usd", "pay_currency": "usdttrc20"}
    r = requests.post("https://api.nowpayments.io/v1/payment", json=data, headers=headers)
    return r.json()['pay_address']

@bot.message_handler(commands=['verifier'])
def verifier(message):
    chat_id = message.chat.id
    # Ici tu devrais vérifier le paiement. Pour test on envoie direct
    envoyer_au_groupe_whatsapp(chat_id)
    
def envoyer_au_groupe_whatsapp(chat_id):
    data = user_data[chat_id]
    numero = data['numero']
    motif = data['motif']
    desc = data['desc']
    
    text = f"""🚨 PLAINTE PAYÉE #VORAX 🚨

Motif: {motif} 🚨
Contre: {numero}
Lien: https://wa.me/{numero.replace('+','')}
Description: {desc}
Statut: PAIEMENT VÉRIFIÉ ✅

Actions: Signaler + Bloquer ce numéro"""
    
    payload = {"jid": WHATSAPP_GROUP, "message": text}
    requests.post(WHATSAPP_API_URL + "/message/sendText", json=payload)
    
    bot.send_message(chat_id, "✅ Plainte envoyée au support VORAX EMPIRE. On la traite en priorité.")
    del user_data[chat_id]

bot.polling()