# Telegram Video Details Bot

A Telegram bot that replies to a video (or a forwarded video message) with the metadata available through Telegram's Bot API.

## Features

- Telegram `file_id` and `file_unique_id`
- File size, file name, MIME type, duration, dimensions (when provided)
- Forward-origin details when Telegram makes them available
- Temporary Telegram download URL when `getFile` returns a file path
- GitHub Actions workflow and GitHub Secrets token setup
- No database and no AI API key required

## Important URL limitation

The `getFile` download URL is temporary (Telegram documents it as valid for at least 1 hour, but do not rely on it as a permanent URL). A Telegram `file_id` can be reused by the bot to send/copy the media through Telegram, but it is **not** a public, permanent web video link and will not automatically play on arbitrary websites.

For a permanent web-player URL, add a separate hosting/storage service that permits video playback and follow its access, copyright, and privacy rules. This project does not upload videos to a third-party host.

## Create your bot

1. Open Telegram and message **@BotFather**.
2. Run `/newbot` and follow the instructions.
3. Copy the bot token privately. Never publish it in source code or chat.
4. Create a GitHub repository and upload these files.

## Add GitHub Secret

In your repository, open **Settings → Secrets and variables → Actions → New repository secret**.

- Name: `BOT_TOKEN`
- Secret: your token from BotFather

## Start with GitHub Actions

1. Push the files to the `main` branch.
2. Open the repository's **Actions** tab.
3. Choose **Telegram Video Details Bot**.
4. Click **Run workflow** if it has not started.
5. Keep the workflow run active while you test the bot.

GitHub Actions jobs have runtime limits and are not a dependable always-on host. This workflow runs for up to 5 hours 45 minutes, then stops. For genuine 24/7 operation, run `python bot.py` on an always-on server/hosting service.

## Run locally

Python 3.10+:

```bash
pip install -r requirements.txt
```

Set the `BOT_TOKEN` environment variable, then run:

```bash
python bot.py
```

Linux/macOS:
```bash
export BOT_TOKEN="paste-token-here"
python bot.py
```

Windows PowerShell:
```powershell
$env:BOT_TOKEN="paste-token-here"
python bot.py
```

## Use

1. Open your bot in Telegram and press **Start**.
2. Send a video or forward a video message to it.
3. The bot replies with available file details.

Some metadata may be unavailable depending on the media type and how it was forwarded. Telegram privacy settings may also hide the original source information.
