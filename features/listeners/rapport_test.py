"""Listener: forwarde vers Saved Messages les messages/médias déclenchés par 'rapport...test'."""

import io
import re

from telethon import events

from config import GROUP_ID_TEST, RAPPORT_TEST_SAVE_DESTINATION


def register(ctx):
    @ctx.client.on(events.NewMessage(chats=GROUP_ID_TEST))
    async def rapport_test_listener(event):
        """Déclencheur: message contenant 'rapport...test' dans cet ordre, insensible à la casse."""
        text = event.message.text or ""
        if not re.search(r'rapport.*test', text, re.IGNORECASE | re.DOTALL):
            return

        sender = await event.get_sender()
        sender_id = getattr(sender, 'id', None)
        trigger_time = event.message.date
        trigger_id = event.message.id

        print(f"\n[rapport_test] Déclencheur msg #{trigger_id} | sender={getattr(sender, 'username', sender_id)}")

        messages_to_forward = []

        if event.message.media:
            # Le message a des médias : sauvegarder ce message et tout son album si groupé
            messages_to_forward.append(event.message)

            if event.message.grouped_id:
                grouped_id = event.message.grouped_id
                nearby_ids = list(range(max(1, trigger_id - 10), trigger_id + 11))
                nearby = await ctx.client.get_messages(event.chat_id, ids=nearby_ids)
                if nearby is None:
                    nearby = []
                elif not isinstance(nearby, (list, tuple)):
                    nearby = [nearby]

                for m in nearby:
                    if m and m.grouped_id == grouped_id and m.id != trigger_id:
                        messages_to_forward.append(m)
        else:
            # Pas de médias directs : chercher des images du même user dans la même minute ou adjacentes
            before = await ctx.client.get_messages(event.chat_id, limit=25, offset_id=trigger_id) or []
            after = await ctx.client.get_messages(event.chat_id, limit=25, min_id=trigger_id, reverse=True) or []

            if not isinstance(before, (list, tuple)):
                before = [before]
            if not isinstance(after, (list, tuple)):
                after = [after]

            # 1. Toutes les images du même user dans la fenêtre ±60s
            for m in list(before) + list(after):
                if m.media and getattr(m, 'sender_id', None) == sender_id:
                    if abs((m.date - trigger_time).total_seconds()) <= 60:
                        messages_to_forward.append(m)

            # 2. Images adjacentes consécutives du même user, avec marge max 1 minute
            #    avant (du plus récent au plus ancien)
            for m in before:
                if abs((m.date - trigger_time).total_seconds()) > 60:
                    break
                if getattr(m, 'sender_id', None) == sender_id:
                    if m.media:
                        messages_to_forward.append(m)
                    else:
                        break

            #    après (du plus ancien au plus récent)
            for m in after:
                if abs((m.date - trigger_time).total_seconds()) > 60:
                    break
                if getattr(m, 'sender_id', None) == sender_id:
                    if m.media:
                        messages_to_forward.append(m)
                    else:
                        break

        if not messages_to_forward:
            print("[rapport_test] Aucune image trouvée")
            return

        # Dédupliquer et trier par ID chronologique
        seen = set()
        unique = []
        for m in sorted(messages_to_forward, key=lambda x: x.id):
            if m.id not in seen:
                seen.add(m.id)
                unique.append(m)

        # Combiner tous les textes (trigger en premier, puis les autres)
        all_texts = []
        if event.message.text:
            all_texts.append(event.message.text)
        for m in unique:
            if m.text and m.id != trigger_id:
                all_texts.append(m.text)
        combined_text = "\n\n".join(all_texts)

        # Télécharger tous les médias en mémoire sous forme de photos (pas documents)
        media_files = []
        for idx, m in enumerate(unique):
            if m.media:
                buffer = io.BytesIO()
                await ctx.client.download_media(m, file=buffer)
                data = buffer.getvalue()
                if isinstance(data, bytes):
                    bio = io.BytesIO(data)
                    bio.name = f"photo_{idx}.jpg"
                    media_files.append(bio)

        if media_files:
            # Envoyer par lots de 10 (limite album Telegram), caption sur le 1er lot
            for i in range(0, len(media_files), 10):
                batch = media_files[i:i + 10]
                if i == 0:
                    await ctx.client.send_file(RAPPORT_TEST_SAVE_DESTINATION, batch, caption=combined_text, force_document=False)
                else:
                    await ctx.client.send_file(RAPPORT_TEST_SAVE_DESTINATION, batch, force_document=False)
            print(f"[rapport_test] ✅ {len(media_files)} photo(s) → Saved Messages")
        elif combined_text:
            await ctx.client.send_message(RAPPORT_TEST_SAVE_DESTINATION, combined_text)
            print("[rapport_test] ✅ texte seul → Saved Messages")
