from telethon.sync import TelegramClient

API_ID = 'ВАШ_API_ID'
API_HASH = 'ВАШ_API_HASH'

with TelegramClient('anon', API_ID, API_HASH) as client:
    print("Сессия создана!")