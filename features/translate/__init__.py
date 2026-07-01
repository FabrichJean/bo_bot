"""Feature: traduction de texte via Google Translate."""

from services.translation import google_translate


def register(ctx):
    async def cmd_translate(args=None, context=None):
        """Traduit un texte du chinois au français. Usage: /translate texte"""
        if not args:
            return "❌ /translate nécessite un texte. Usage: /translate votre_texte"
        text_to_translate = " ".join(args)
        translation = google_translate(text_to_translate)
        return f"🌐 Traduction :\n{translation}"

    ctx.cmd_handler.register(['translate', 't', 'tr'], cmd_translate, require_auth=True)
