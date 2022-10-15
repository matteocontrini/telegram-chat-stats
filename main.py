import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import telebot
from pyrogram import Client

tz = ZoneInfo('Europe/Rome')

API_ID = os.environ['API_ID']
API_HASH = os.environ['API_HASH']
BOT_TOKEN = os.environ['BOT_TOKEN']
CHAT_ID = os.environ['CHAT_ID']
CHANNEL_ID = os.environ['CHANNEL_ID']
SESSION_NAME = os.environ['SESSION_NAME']

tg = Client(SESSION_NAME, API_ID, API_HASH)
bot = telebot.TeleBot(BOT_TOKEN, parse_mode='HTML')


async def get_yesterday_counts() -> (dict, dict):
    max_date = datetime.now(tz).replace(hour=0, minute=0, second=0, microsecond=0)
    min_date = max_date - timedelta(days=1)

    total = {
        'count': 0,
        'text': 0,
        'media': 0,
        'chars': 0,
    }
    users = {}

    async for message in tg.get_chat_history(CHAT_ID):
        date = message.date.astimezone(tz)
        if date > max_date:
            continue
        if date < min_date:
            break
        name = message.from_user.first_name
        if name not in users:
            users[name] = {
                'count': 0,
                'text': 0,
                'media': 0,
                'chars': 0,
            }
        users[name]['count'] += 1
        total['count'] += 1
        if message.media:
            users[name]['media'] += 1
            total['media'] += 1
            users[name]['chars'] += len(message.caption or '')
            total['chars'] += len(message.caption or '')
        else:
            users[name]['text'] += 1
            users[name]['chars'] += len(message.text)
            total['text'] += 1
            total['chars'] += len(message.text)
    return total, users


async def get_cum() -> int:
    return await tg.search_messages_count(CHAT_ID)


async def main():
    async with tg:
        totals, users = await get_yesterday_counts()

        yesterday = datetime.now(tz).replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
        pretty_date = yesterday.strftime('%Y-%m-%d')

        text = f'🗓 <b>{pretty_date}</b>\n\n'

        text += f'<b>Total</b>:\n'

        text += '<pre>'
        for key, value in totals.items():
            text += f' {key}: <b>{value}</b>\n'
        text += '</pre>'

        for name, users in users.items():
            text += f'\n<b>{name}</b>:\n'
            text += '<pre>'
            for key, value in users.items():
                text += f' {key}: <b>{value}</b>\n'
            text += '</pre>'

        cum = await get_cum()
        text += f'\n📈 <b>Cum:</b> <code>{cum}</code>'

        print(text)

        bot.send_message(CHANNEL_ID, text)


if __name__ == '__main__':
    tg.run(main())
