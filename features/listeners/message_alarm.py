"""Listener: log tous les messages du groupe, quel que soit l'expéditeur.

Les utilisateurs listés dans EXCLUDED_USERS (variable d'env, voir config.py)
sont ignorés.
"""

from telethon import events

from config import GROUP_ID_TEST, EXCLUDED_USERS


def register(ctx):
    excluded = {u.lower() for u in EXCLUDED_USERS}

    @ctx.client.on(events.NewMessage(chats=GROUP_ID_TEST))
    async def message_logger_listener(event):
        if not event.message.text:
            return

        sender = await event.get_sender()
        sender_id = getattr(sender, 'id', None)
        username = getattr(sender, 'username', None)

        identifiers = {str(sender_id)}
        if username:
            identifiers.add(username.lower())

        if identifiers & excluded:
            return

        expediteur = username or getattr(sender, 'first_name', None) or f"User {sender_id}"
        print(f"[message_logger] {expediteur}: {event.message.text}")
