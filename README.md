# Telegram Chat Stats

Generates and sends a report with counts of messages sent in a given chat in the previous day.

## Usage

Environment variables:

- `API_ID`: Telegram API ID
- `API_HASH`: Telegram API hash
- `BOT_TOKEN`: Telegram bot token
- `CHAT_ID`: Telegram chat ID to calculate the stats for
- `CHANNEL_ID`: Telegram channel ID to send the report to
- `SESSION_NAME`: name of the Pyrogram session (reads/writes to `{SESSION_NAME}.session`)

Run with:

```shell
pipenv install
pipenv run python main.py
```
