from flask import Flask, request
import telebot
import requests
import instaloader
import os

TOKEN = os.getenv("7587998097:AAHKReRf4VzfcEKAPEVJwD_bF83IE6a-3Ig")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
loader = instaloader.Instaloader()

# Store user language preferences
user_languages = {}

LANGUAGES = {
    "uz": "Videoni yuklashim uchun menga Instagram yoki TikTok videosi havolasini yuboring",
    "ru": "Чтобы загрузить видео, отправьте мне ссылку на видео Instagram или TikTok",
    "en": "Send me an Instagram or TikTok video link to download it",
}

@app.route("/", methods=["GET"])
def home():
    return "Bot is running!"

@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json()
    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text", "")

        if text == "/start":
            keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            keyboard.add("🇺🇿 Uzbek", "🇷🇺 Russian", "🇬🇧 English")
            bot.send_message(chat_id, "Tilni tanlang | Выберите язык | Select a language:", reply_markup=keyboard)

        elif text in ["🇺🇿 Uzbek", "🇷🇺 Russian", "🇬🇧 English"]:
            lang_code = {"🇺🇿 Uzbek": "uz", "🇷🇺 Russian": "ru", "🇬🇧 English": "en"}[text]
            user_languages[chat_id] = lang_code
            bot.send_message(chat_id, LANGUAGES[lang_code], reply_markup=telebot.types.ReplyKeyboardRemove())

        elif "instagram.com" in text:
            msg = bot.send_message(chat_id, "Downloading Instagram media...", disable_notification=True)
            media_url = download_instagram(text)
            bot.delete_message(chat_id, msg.message_id)  # Remove the temporary message
            if media_url.startswith("http"):  # Ensure it's a valid link
                bot.send_video(chat_id, media_url, caption="Thanks for using me!")
            else:
                bot.send_message(chat_id, f"Error: {media_url}")  # Handle errors properly

        elif "tiktok.com" in text:
            msg = bot.send_message(chat_id, "Downloading TikTok video...", disable_notification=True)
            media_url = download_tiktok(text)
            bot.delete_message(chat_id, msg.message_id)  # Remove the temporary message
            if media_url.startswith("http"):
                bot.send_video(chat_id, media_url, caption="Thanks for using me!")
            else:
                bot.send_message(chat_id, f"Error: {media_url}")

    return "OK", 200

def download_instagram(url):
    try:
        shortcode = url.split("/")[-2]
        post = instaloader.Post.from_shortcode(loader.context, shortcode)
        return post.video_url if post.is_video else post.url
    except Exception as e:
        return f"Error: {e}"

def download_tiktok(url):
    try:
        api_url = f"https://www.tikwm.com/api/?url={url}"
        response = requests.get(api_url).json()
        return response["data"]["play"] if "data" in response else "Failed to fetch video"
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
