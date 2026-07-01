"""Feature: gestion des plateformes et canaux de paiement."""

from config import BASE_URL, SCREENSHOT_ELEMENT_SELECTOR
from services.api_client import APIClient
from services.browser import async_screenshot_with_token
from services.screenshot_paths import get_screenshot_path


def register(ctx):
    async def cmd_list_platforms(args=None, context=None):
        """Liste toutes les plateformes de paiement via l'API."""
        try:
            token = ctx.token_gen.generate_token()

            client_api = APIClient(BASE_URL, token=token)
            result = client_api.call_api('/payment/platforms/all', method='POST')

            if result.get('code') != 200:
                return f"❌ Erreur API : {result.get('message', 'Erreur inconnue')}"

            platforms = result.get('data', [])
            if not platforms:
                return "📭 Aucune plateforme disponible"

            response = "📋 Plateformes de paiement :\n\n"
            for platform in platforms:
                status_emoji = "✅" if platform.get('status') == 'active' else "❌"
                response += f"{status_emoji} **{platform.get('name')}** (ID: {platform.get('id')})\n"
                response += f"   Code: `{platform.get('code')}`\n"
                response += f"   Status: {platform.get('status')}\n\n"

            return response
        except Exception as e:
            return f"❌ Erreur lors de la récupération des plateformes : {e}"

    async def cmd_list_channel(args=None, context=None):
        """Liste les canaux d'une plateforme. Usage: /list-channel {nom_plateforme}"""
        try:
            if not args:
                return "❌ /list-channel nécessite un nom de plateforme. Usage: /list-channel Wangpai"

            query = " ".join(args).lower()

            # Étape 1 : Récupérer la liste des plateformes
            token = ctx.token_gen.generate_token()
            client_api = APIClient(BASE_URL, token=token)
            result = client_api.call_api('/payment/platforms/all', method='POST')

            if result.get('code') != 200:
                return f"❌ Erreur lors de la récupération des plateformes : {result.get('message')}"

            platforms = result.get('data', [])
            if not platforms:
                return "📭 Aucune plateforme disponible"

            # Étape 2 : Chercher la plateforme correspondante (exact match, insensible à la casse)
            platform_found = None
            for platform in platforms:
                if platform.get('name', '').lower() == query:
                    platform_found = platform
                    break

            if not platform_found:
                available = ", ".join([p.get('name', 'Unknown') for p in platforms])
                return f"❌ Plateforme '{query}' non trouvée.\nPlateformes disponibles : {available}"

            platform_id = platform_found.get('id')
            platform_name = platform_found.get('name')

            # Étape 3 : Récupérer les canaux de cette plateforme
            token = ctx.token_gen.generate_token()
            client_api = APIClient(BASE_URL, token=token)
            channels_result = client_api.call_api(f'/payment/channels/platform/{platform_id}', method='POST')

            # Gérer les deux formats possibles de réponse (liste directe ou objet avec 'data')
            if isinstance(channels_result, dict) and 'code' in channels_result:
                if channels_result.get('code') != 200:
                    return f"❌ Erreur lors de la récupération des canaux : {channels_result.get('message')}"
                channels = channels_result.get('data', [])
            else:
                channels = channels_result if isinstance(channels_result, list) else []

            if not channels:
                return f"📭 Aucun canal disponible pour la plateforme '{platform_name}'"

            response = f"📡 Canaux pour **{platform_name}** :\n\n"
            for channel in channels:
                status_emoji = "✅" if channel.get('status') == 'active' else "❌"
                response += f"{status_emoji} **{channel.get('name')}** (ID: {channel.get('id')})\n"
                response += f"   Platform ID: {channel.get('platformId')}\n"
                response += f"   Status: {channel.get('status')}\n\n"

            return response
        except Exception as e:
            return f"❌ Erreur lors de la récupération des canaux : {e}"

    async def cmd_active(args=None, context=None):
        """Active un canal par son ID et envoie une screenshot. Usage: /active {id_channel}"""
        try:
            if not args or not args[0].isdigit():
                return "❌ /active nécessite un ID de canal valide. Usage: /active 156"

            sender = context.get('sender') if context else 'admin'
            channel_id = args[0]

            # Étape 1 : Faire l'appel API pour activer le canal
            token = ctx.token_gen.generate_token()
            client_api = APIClient(BASE_URL, token=token)
            update_result = client_api.call_api(f'/payment/channels/{channel_id}/update', method='POST', data={'status': 'active'})

            if update_result.get('code') != 200:
                return f"❌ Erreur lors de l'activation du canal : {update_result.get('message', 'Erreur inconnue')}"

            # Étape 2 : Récupérer le nom de la plateforme
            platform_data = update_result.get('data', {})
            platform = platform_data.get('platform', {})
            platform_name = platform.get('name', '')

            if not platform_name:
                return "❌ Impossible de récupérer le nom de la plateforme"

            # Étape 3 : Prendre une screenshot de la page avec le nom de la plateforme
            url = f'https://xo-admin.99sq20.fun/admin/exchange/payment-platforms?search={platform_name}&toggleFirst=true'
            token = ctx.token_gen.generate_token()

            screenshot_path = get_screenshot_path(sender, 'active')

            image_bytes = await async_screenshot_with_token(
                url,
                token,
                screenshot_path=screenshot_path,
                element_selector=SCREENSHOT_ELEMENT_SELECTOR
            )
            # Étape 4 : Envoyer l'image
            event = context.get('event') if context else None
            if event and image_bytes:
                await event.reply(f"✅ Canal {channel_id} activé pour la plateforme **{platform_name}**")
                await event.reply(file=screenshot_path)
                return None  # L'image a été envoyée directement
            else:
                return f"✅ Canal {channel_id} activé pour la plateforme **{platform_name}**\n📸 Screenshot sauvegardée. Taille : {len(image_bytes)} octets"
        except Exception as e:
            return f"❌ Erreur lors de l'activation du canal : {e}"

    async def cmd_inactive(args=None, context=None):
        """Désactive un canal par son ID et envoie une screenshot. Usage: /inactive {id_channel}"""
        try:
            if not args or not args[0].isdigit():
                return "❌ /inactive nécessite un ID de canal valide. Usage: /inactive 156"

            sender = context.get('sender') if context else 'admin'
            channel_id = args[0]

            # Étape 1 : Faire l'appel API pour désactiver le canal
            token = ctx.token_gen.generate_token()
            client_api = APIClient(BASE_URL, token=token)
            update_result = client_api.call_api(f'/payment/channels/{channel_id}/update', method='POST', data={'status': 'inactive'})

            if update_result.get('code') != 200:
                return f"❌ Erreur lors de la désactivation du canal : {update_result.get('message', 'Erreur inconnue')}"

            # Étape 2 : Récupérer le nom de la plateforme
            platform_data = update_result.get('data', {})
            platform = platform_data.get('platform', {})
            platform_name = platform.get('name', '')

            if not platform_name:
                return "❌ Impossible de récupérer le nom de la plateforme"

            # Étape 3 : Prendre une screenshot de la page avec le nom de la plateforme
            url = f'https://xo-admin.99sq20.fun/admin/exchange/payment-platforms?search={platform_name}&toggleFirst=true'
            token = ctx.token_gen.generate_token()

            screenshot_path = get_screenshot_path(sender, 'inactive')

            image_bytes = await async_screenshot_with_token(
                url,
                token,
                screenshot_path=screenshot_path,
                element_selector=SCREENSHOT_ELEMENT_SELECTOR
            )

            # Étape 4 : Envoyer l'image
            event = context.get('event') if context else None
            if event and image_bytes:
                await event.reply(f"❌ Canal {platform_data.get('name', '')} {channel_id} désactivé pour la plateforme **{platform_name}**")
                await event.reply(file=screenshot_path)
                return None  # L'image a été envoyée directement
            else:
                return f"❌ Canal {channel_id} désactivé pour la plateforme **{platform_name}**\n📸 Screenshot sauvegardée. Taille : {len(image_bytes)} octets"
        except Exception as e:
            return f"❌ Erreur lors de la désactivation du canal : {e}"

    ctx.cmd_handler.register(['list-platforms', 'lp', 'platforms'], cmd_list_platforms, require_auth=True)
    ctx.cmd_handler.register(['list-channel', 'lc', 'channels'], cmd_list_channel, require_auth=True)
    ctx.cmd_handler.register(['active', 'on', 'activate'], cmd_active, require_auth=True)
    ctx.cmd_handler.register(['inactive', 'off', 'deactivate'], cmd_inactive, require_auth=True)
