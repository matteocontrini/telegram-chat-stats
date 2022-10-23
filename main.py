import os
from datetime import datetime, timedelta, date
from zoneinfo import ZoneInfo

import telebot
import pyrogram

tz = ZoneInfo('Europe/Rome')

API_ID = os.environ['API_ID']
API_HASH = os.environ['API_HASH']
BOT_TOKEN = os.environ['BOT_TOKEN']
CHAT_ID = os.environ['CHAT_ID']
CHANNEL_ID = os.environ['CHANNEL_ID']
SESSION_NAME = os.environ['SESSION_NAME']

tg = pyrogram.Client(SESSION_NAME, API_ID, API_HASH)
bot = telebot.TeleBot(BOT_TOKEN, parse_mode='HTML')

excluded_media = [None, pyrogram.enums.MessageMediaType.WEB_PAGE] 
link_types = [pyrogram.enums.MessageEntityType.TEXT_LINK, pyrogram.enums.MessageEntityType.URL]


async def get_day_counts(day: date) -> (dict, dict):
    min_date = datetime.combine(day, datetime.min.time(), tzinfo=tz)
    max_date = min_date + timedelta(days=1)

    total = {
        'count': 0,
        'chars': 0,
        'data': 0,
        'text': 0,
        'links': 0,
        'media': 0,
    }
    users = {}

    chat_id = int(CHAT_ID) if CHAT_ID.isdigit() else CHAT_ID

    async for message in tg.get_chat_history(chat_id):
        date = message.date.astimezone(tz)
        if date > max_date:
            continue
        if date < min_date:
            break

        name = message.from_user.first_name
        if name not in users:
            users[name] = total.copy()  

        users[name]['count'] += 1
        users[name]['chars'] += len(message.caption or message.text or '')

        # Count links from message and caption entities
        entities = message.entities or []
        caption_entities = message.caption_entities or []
        for entity in entities + caption_entities:
            if entity.type in link_types:
                users[name]['links'] += 1
    
        if message.media not in excluded_media:
            users[name]['media'] += 1
            # Sum file size if the media has a size
            media = getattr(message, message.media.name.lower(), '')
            if hasattr(media, 'file_size'):
                users[name]['data'] += media.file_size
        else:
            users[name]['text'] += 1

    for name in users:
        # Compute totals
        for key in total:
            total[key] += users[name][key]

        data_mb = (users[name]['data'] + users[name]['chars']) / 2 ** 20
        users[name]['data'] = f'{data_mb:.2f} MB'

    data_mb = (total['data'] + total['chars']) / 2 ** 20
    total['data'] = f'{data_mb:.2f} MB'

    return total, users


async def get_cum() -> int:
    return await tg.search_messages_count(CHAT_ID)


def render_counts(counts: dict) -> str:
    text = '<pre>'
    max_key_len = max([len(key) for key in counts.keys()])
    for key, value in counts.items():
        padding = ' ' * (max_key_len - len(key))
        text += f' {key}: {padding}{value}\n'
    text += '</pre>'
    return text


async def main():
    async with tg:
        day = date.today() - timedelta(days=1)
        totals, users = await get_day_counts(day)

        pretty_date = day.strftime('%Y-%m-%d')
        text = f'🗓 <b>{pretty_date}</b>\n\n'

        text += f'<b>Total</b>:\n'
        text += render_counts(totals)

        for name, users in sorted(users.items()):
            text += f'\n<b>{name}</b>:\n'
            text += render_counts(users)

        cum = await get_cum()
        text += f'\n📈 <b>Cum:</b> <pre>{cum}</pre>'

        print(text)

        bot.send_message(CHANNEL_ID, text)


if __name__ == '__main__':
    tg.run(main())
