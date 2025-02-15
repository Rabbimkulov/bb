import os
import requests
from apify_client import ApifyClient
from yt_dlp import YoutubeDL
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Set these environment variables in Railway (or your hosting platform)
APIFY_TOKEN = os.getenv("apify_api_TgtQwQF4Kcst2NR5aXrwcRfMv4JLEB14rEbA")   # Your Apify API token
BOT_TOKEN   = os.getenv("7587998097:AAHKReRf4VzfcEKAPEVJwD_bF83IE6a-3Ig")       # Your Telegram Bot token

def download_tiktok_video(url: str) -> str:
    # Using Apify's TikTok Video Scraper Actor
    client = ApifyClient(APIFY_TOKEN)
    run_input = {"postURLs": [url]}
    run = client.actor("clockworks/tiktok-video-scraper").call(run_input=run_input)
    dataset_id = run["defaultDatasetId"]
    items = list(client.dataset(dataset_id).iterate_items())
    video_url = items[0].get("videoUrl") if items else None
    if video_url:
        r = requests.get(video_url, stream=True)
        file_path = "tiktok_video.mp4"
        with open(file_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        return file_path
    return None

def download_instagram_video(url: str) -> str:
    # Using Apify's Instagram Videos Downloader Actor
    client = ApifyClient(APIFY_TOKEN)
    run_input = {"url": url}
    run = client.actor("easyapi/instagram-videos-downloader").call(run_input=run_input)
    dataset_id = run["defaultDatasetId"]
    items = list(client.dataset(dataset_id).iterate_items())
    video_url = items[0].get("videoUrl") if items else None
    if video_url:
        r = requests.get(video_url, stream=True)
        file_path = "instagram_video.mp4"
        with open(file_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        return file_path
    return None

def download_youtube_video(url: str) -> str:
    # Use yt-dlp to download the best quality video
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'youtube_video.%(ext)s',
        'quiet': True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    # For simplicity, assume the output is MP4 (adjust as needed)
    return "youtube_video.mp4"

def download_video(url: str) -> str:
    if "tiktok.com" in url:
        return download_tiktok_video(url)
    elif "instagram.com" in url:
        return download_instagram_video(url)
    elif "youtube.com" in url or "youtu.be" in url:
        return download_youtube_video(url)
    else:
        raise ValueError("Unsupported URL format. Please send a TikTok, Instagram, or YouTube URL.")

# Telegram Bot Handlers
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Hey there! Send me a TikTok, Instagram, or YouTube video URL and I'll download the video for you."
    )

def handle_message(update: Update, context: CallbackContext):
    url = update.message.text.strip()
    update.message.reply_text("Processing your URL. This might take a moment...")
    try:
        file_path = download_video(url)
        if file_path and os.path.exists(file_path):
            update.message.reply_text("Download complete! Sending the video...")
            context.bot.send_video(chat_id=update.message.chat_id, video=open(file_path, 'rb'))
            os.remove(file_path)
        else:
            update.message.reply_text("Failed to download the video. Please check the URL and try again.")
    except Exception as e:
        update.message.reply_text(f"An error occurred: {str(e)}")

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
