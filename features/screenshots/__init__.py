"""Feature: capture d'écran de la page admin."""

from config import SCREENSHOT_ADMIN_URL, SCREENSHOT_ELEMENT_SELECTOR
from services.browser import async_screenshot_with_token
from services.screenshot_paths import get_screenshot_path


def register(ctx):
    async def cmd_screenshot(args=None, context=None):
        """Prend une capture d'écran de la page admin et l'envoie."""
        try:
            sender = context.get('sender') if context else 'admin'
            url = SCREENSHOT_ADMIN_URL
            token = ctx.token_gen.generate_token()

            screenshot_path = get_screenshot_path(sender, 'admin')

            image_bytes = await async_screenshot_with_token(
                url,
                token,
                screenshot_path=screenshot_path,
                element_selector=SCREENSHOT_ELEMENT_SELECTOR
            )
            event = context.get('event') if context else None
            if event and image_bytes:
                await event.reply(file=screenshot_path)
                return None  # L'image a été envoyée directement
            else:
                return f"📸 Capture d'écran sauvegardée. Taille : {len(image_bytes)} octets"
        except Exception as e:
            return f"❌ Erreur lors de la capture d'écran : {e}"

    ctx.cmd_handler.register(['screenshot', 'ss', 'snap'], cmd_screenshot, require_auth=True)
