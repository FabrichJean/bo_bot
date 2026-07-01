"""Listener: log tous les messages des chats surveillés (ctx.watch_store,
configurable à chaud depuis l'app Android), quel que soit l'expéditeur, et
déclenche l'alarme sur le téléphone Android connecté via ctx.alarm_server.

Les utilisateurs listés dans ctx.watch_store.excluded_users sont ignorés.
"""

from telethon import events


def register(ctx):
    @ctx.client.on(events.NewMessage())
    async def message_alarm_listener(event):
        if not ctx.watch_store.is_watched(event.chat_id):
            return

        if not event.message.text:
            return

        sender = await event.get_sender()
        sender_id = getattr(sender, 'id', None)
        username = getattr(sender, 'username', None)

        if ctx.watch_store.is_excluded(sender_id, username):
            return

        expediteur = username or getattr(sender, 'first_name', None) or f"User {sender_id}"
        print(f"[message_alarm] {expediteur}: {event.message.text}")
        await ctx.alarm_server.broadcast_alarm(expediteur, event.message.text)
