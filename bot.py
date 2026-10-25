import os
import logging
from datetime import datetime, timezone

from telegram import Update
from telegram.constants import ChatType
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    level=logging.INFO,
)
logging.getLogger("httpx").setLevel(logging.WARNING)
log = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()


def human_size(size):
    if size is None:
        return "Not provided"
    value = float(size)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024 or unit == "TB":
            return f"{value:.2f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024
    return f"{value:.2f} TB"


def safe(value):
    return str(value) if value not in (None, "") else "Not available"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "👋 <b>Telegram Video Details Bot</b>\n\n"
        "मुझे कोई वीडियो या वीडियो वाला Telegram message forward/send करें। "
        "मैं उपलब्ध metadata, File ID और temporary download URL दिखाऊँगा.\n\n"
        "Commands:\n"
        "/start — शुरू करें\n"
        "/help — मदद\n\n"
        "⚠️ Temporary URL स्थायी public link नहीं है; यह expire हो सकता है।"
    )
    await update.effective_message.reply_text(text, parse_mode="HTML")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)


async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    if not message:
        return

    media = message.video or message.document or message.animation
    media_type = "video" if message.video else (
        "document" if message.document else "animation" if message.animation else None
    )

    # Support video messages and video files sent as documents/animations.
    if media is None:
        await message.reply_text(
            "इस संदेश में पहचानने योग्य वीडियो/फाइल नहीं मिली। "
            "कृपया वीडियो को सीधे भेजें या वीडियो वाला message forward करें।"
        )
        return

    # Avoid treating arbitrary documents as video unless Telegram identifies them as video.
    mime = getattr(media, "mime_type", None)
    if media_type == "document" and mime and not mime.startswith("video/"):
        await message.reply_text("यह document वीडियो MIME type का नहीं दिखता, इसलिए इसे वीडियो की तरह प्रोसेस नहीं किया।")
        return

    file_id = media.file_id
    unique_id = media.file_unique_id
    file_size = getattr(media, "file_size", None)
    file_name = getattr(media, "file_name", None)
    duration = getattr(media, "duration", None)
    width = getattr(media, "width", None)
    height = getattr(media, "height", None)

    try:
        telegram_file = await context.bot.get_file(file_id)
        file_path = telegram_file.file_path
        # Telegram's Bot API download URL is temporary and should not be treated as permanent.
        file_url = file_path or None
    except Exception as exc:
        log.warning("get_file failed: %s", exc)
        file_path = None
        file_url = None

    forward_origin = getattr(message, "forward_origin", None)
    forward_info = safe(forward_origin) if forward_origin else "Not available (not forwarded or hidden by Telegram)"

    lines = [
        "🎬 <b>VIDEO / FILE DETAILS</b>",
        "",
        f"<b>Media type:</b> {safe(media_type)}",
        f"<b>File ID:</b>\n<code>{file_id}</code>",
        f"<b>Unique File ID:</b>\n<code>{unique_id}</code>",
        f"<b>File name:</b> {safe(file_name)}",
        f"<b>MIME type:</b> {safe(mime)}",
        f"<b>File size:</b> {human_size(file_size)}",
        f"<b>Duration:</b> {str(duration) + ' seconds' if duration is not None else 'Not available'}",
        f"<b>Dimensions:</b> {str(width) + ' × ' + str(height) if width and height else 'Not available'}",
        f"<b>Forward origin:</b> {forward_info}",
        "",
        "<b>Temporary download URL:</b>",
        f"<code>{file_url}</code>" if file_url else "Not available from Telegram right now",
        "",
        "<b>Important:</b> Telegram download URLs expire (typically within about 1 hour). "
        "File ID is for use with this bot/API, not a permanent public web-player link.",
    ]
    await message.reply_text("\n".join(lines), parse_mode="HTML", disable_web_page_preview=True)


async def handle_other(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    if message:
        await message.reply_text(
            "मुझे वीडियो भेजें या वीडियो वाला Telegram message forward करें। "
            "फिर मैं उपलब्ध file details निकाल दूँगा।"
        )


def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN environment variable is missing. Add it to GitHub Secrets.")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(
        filters.VIDEO | filters.Document.ALL | filters.ANIMATION,
        handle_video
    ))
    app.add_handler(MessageHandler(filters.ALL, handle_other))
    log.info("Bot polling started")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
