import os
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# 1. CONFIG
TOKEN = os.getenv("TELEGRAM_TOKEN")

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

app = Flask(__name__)
application = Application.builder().token(TOKEN).build()

# 2. TES COMMANDES DU BOT
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔥 Bienvenue sur VORAX EMPIRE 🔥\n\n"
        "Tape /menu pour voir les options"
    )

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 MENU VORAX:\n"
        "/start - Accueil\n"
        "/aide - Aide"
   