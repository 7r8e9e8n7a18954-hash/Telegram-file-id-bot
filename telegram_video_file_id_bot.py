#!/usr/bin/env python3
"""
Telegram Video File ID Bot
Python 3.10+
Install: pip install python-telegram-bot
Run:     set BOT_TOKEN=YOUR_BOT_TOKEN   (Windows CMD)
         python bot.py
Linux/macOS: export BOT_TOKEN="YOUR_BOT_TOKEN" && python bot.py
"""

import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters


def human_size(size):
    if size is None:
        return "Unknown"
    value = float(size)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024 or unit == "TB":
            return f"{value:.2f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(
        "🎬 Video File ID Bot में आपका स्वागत है!\n\n"
        "मुझे कोई वीडियो भेजें या किसी चैट से यहाँ वीडियो Forward करें।\n"
        "मैं उसका file_id और उपलब्ध जानकारी दिखाऊँगा।"
    )


async def show_video_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    if not msg:
        return

    media = None
    media_type = "Unknown"

    if msg.video:
        media, media_type = msg.video, "Video"
    elif msg.document and (
        (msg.document.mime_type or "").startswith("video/")
        or (msg.document.file_name or "").lower().endswith(
            (".mp4", ".mov", ".mkv", ".webm", ".avi", ".m4v", ".3gp")
        )
    ):
        media, media_type = msg.document, "Video document"
    elif msg.animation:
        media, media_type = msg.animation, "Animation/GIF"

    if not media:
        await msg.reply_text(
            "कृपया वीडियो भेजें। अगर वीडियो document के रूप में है, तो वह भी चलेगा।"
        )
        return

    file_id = media.file_id
    file_unique_id = media.file_unique_id
    file_size = getattr(media, "file_size", None)
    duration = getattr(media, "duration", None)
    width = getattr(media, "width", None)
    height = getattr(media, "height", None)
    file_name = getattr(media, "file_name", None)
    mime_type = getattr(media, "mime_type", None)

    lines = [
        "✅ वीडियो की जानकारी",
        f"प्रकार: {media_type}",
        f"File ID:\n{file_id}",
        f"File Unique ID:\n{file_unique_id}",
        f"Size: {human_size(file_size)}",
    ]
    if duration is not None:
        lines.append(f"Duration: {duration} seconds")
    if width is not None and height is not None:
        lines.append(f"Resolution: {width} × {height}")
    if file_name:
        lines.append(f"File name: {file_name}")
    if mime_type:
        lines.append(f"MIME type: {mime_type}")

    # Keep the reply within Telegram's message-size limit.
    await msg.reply_text("\n\n".join(lines))


def main():
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        raise SystemExit(
            "BOT_TOKEN नहीं मिला। पहले environment variable में BotFather token सेट करें।"
        )

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(
        filters.VIDEO | filters.Document.ALL | filters.ANIMATION,
        show_video_info
    ))
    print("Bot चालू है. बंद करने के लिए Ctrl+C दबाएँ.")
    app.run_polling()


if __name__ == "__main__":
    main()
