import asyncio
from telethon import TelegramClient
from telethon.tl.types import Chat, Channel
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_SESSION_NAME

async def main():
    client = TelegramClient(TELEGRAM_SESSION_NAME, TELEGRAM_API_ID, TELEGRAM_API_HASH)
    await client.start()
    print("Tous les groupes/canaux de la session:\n")
    async for dialog in client.iter_dialogs():
        if isinstance(dialog.entity, (Chat, Channel)):
            print(f"  [{dialog.id}] {dialog.name}")
    await client.disconnect()

asyncio.run(main())
