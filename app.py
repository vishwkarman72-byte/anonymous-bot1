import os
import json
from flask import Flask, request
import telebot

TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

waiting_users = []
active_chats = {}

@app.route('/')
def home():
    return "Bot Running 🚀"

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
        "👋 Welcome to Anonymous Chat\n\n"
        "/next - Find Partner\n"
        "/stop - Stop Chat"
    )

@bot.message_handler(commands=['next'])
def next_chat(message):
    user_id = str(message.chat.id)

    if user_id in active_chats:
        partner = active_chats[user_id]
        bot.send_message(int(partner), "❌ Partner left the chat.")
        del active_chats[partner]
        del active_chats[user_id]

    if waiting_users:
        partner = waiting_users.pop(0)
        active_chats[user_id] = partner
        active_chats[partner] = user_id
        bot.send_message(int(user_id), "✅ Connected!")
        bot.send_message(int(partner), "✅ Connected!")
    else:
        waiting_users.append(user_id)
        bot.send_message(int(user_id), "⏳ Waiting for partner...")

@bot.message_handler(commands=['stop'])
def stop_chat(message):
    user_id = str(message.chat.id)

    if user_id in active_chats:
        partner = active_chats[user_id]
        bot.send_message(int(partner), "❌ Partner stopped the chat.")
        del active_chats[partner]
        del active_chats[user_id]
        bot.send_message(int(user_id), "Chat ended.")
    else:
        bot.send_message(int(user_id), "You are not in chat.")

@bot.message_handler(func=lambda message: True)
def relay(message):
    user_id = str(message.chat.id)

    if user_id in active_chats:
        partner = active_chats[user_id]
        bot.send_message(int(partner), message.text)
    else:
        bot.send_message(message.chat.id, "Use /next to find partner.")

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"https://https://anonymous-bot1.onrender.com/{TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
