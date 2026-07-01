"""Listener: relaie les messages de JKbot vers GROUP_ID_TEST, traduits en français."""

from telethon import events

from config import GROUP_ID_TEST
from services.translation import google_translate


def register(ctx):
    @ctx.client.on(events.NewMessage(chats=5205859116, from_users=92983875))
    async def jkbot_relay_listener(event):
        """Messages de JKbot (92983875) dans GROUP_MAIN → traduit en FR → GROUP_ID_TEST."""
        text = event.message.text
        if not text:
            return

        print(f"\n[jkbot_relay] Message reçu : {text[:80]}")
        traduction = google_translate(text)
        print(f"[jkbot_relay] Traduction : {traduction[:80]}")

        await ctx.client.send_message(GROUP_ID_TEST, f"🌐 **[JKbot]** {traduction}")
