from telethon import TelegramClient, events
import requests
from api_client import APIClient
from browser_sim import async_screenshot_with_token
from token_generator import TokenGenerator
from command_handler import CommandHandler
from user_registry import UserRegistry

# --- TES INFOS API TELEGRAM ---
api_id = 37308629  # Ton api_id
api_hash = '698a893741a1019d222c87b9a53851c3'  # Ton api_hash
nom_du_groupe = '91bot运维通知群'
group_id_test = 5156646256  # ID du groupe de test

client = TelegramClient(
    'session_bobot', 
    api_id, 
    api_hash,
    connection_retries=-1,   # Tentatives infinies (utiliser -1 pour infini)
    retry_delay=5,           # Attendre 5 secondes entre chaque tentative
    auto_reconnect=True      # Reconnexion automatique
)

def google_translate(text, target_lang='fr'):
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={target_lang}&dt=t&q={text}"
        response = requests.get(url)
        # L'API renvoie une liste de listes, la traduction est dans le premier élément
        return response.json()[0][0][0]
    except Exception as e:
        return f"[Erreur traduction: {e}]"


# --- Configuration globale pour JWT/API ---
JWT_SECRET = '49caa9850a1abdf6fghrdf5a9fb093c44aac84dbc46b1f7ab7e4d5c252306919cbdf81'
ADMIN_PAYLOAD = {
    "id": "296952048098738236",
    "username": "admin",
    "role": "admin",
    "code": "123456",
    "parent_id": "123456"
}
BASE_URL = 'https://xo-back.99sq20.fun'

# Initialiser le générateur de token global
token_gen = TokenGenerator(JWT_SECRET, default_payload=ADMIN_PAYLOAD)

# --- Initialiser le registre des utilisateurs ---
user_registry = UserRegistry(registry_file='authorized_users.json')

# --- Initialiser le gestionnaire de commandes ---
cmd_handler = CommandHandler(prefix='/', user_registry=user_registry)

# --- Enregistrer les commandes ---
async def cmd_register(args=None, context=None):
    """Enregistre l'utilisateur pour accéder aux commandes protégées."""
    sender = context.get('sender') if context else None
    if not sender:
        return "❌ Impossible de déterminer l'expéditeur"
    
    # Vérifier si déjà enregistré
    if user_registry.is_authorized(sender):
        return f"✅ Vous êtes déjà enregistré : {sender}"
    
    # Enregistrer l'utilisateur
    user_registry.register_user(sender)
    return f"✅ Vous êtes maintenant enregistré : @{sender}\nVous pouvez maintenant utiliser les commandes protégées !"

async def cmd_unregister(args=None, context=None):
    """Désactive l'accès aux commandes protégées pour cet utilisateur."""
    sender = context.get('sender') if context else None
    if not sender:
        return "❌ Impossible de déterminer l'expéditeur"
    
    if not user_registry.is_authorized(sender):
        return f"❌ {sender} n'est pas enregistré"
    
    user_registry.unregister_user(sender)
    return f"❌ Vous avez été désenregistré : {sender}"

async def cmd_help(args=None, context=None):
    """Affiche l'aide des commandes disponibles avec descriptions et raccourcis."""
    help_text = """
🤖 **COMMANDES DISPONIBLES**

📝 **AUTHENTIFICATION**
/register (reg, r) - S'enregistrer pour accéder aux commandes protégées
/unregister (unreg, u) - Se désenregistrer

🔧 **UTILITAIRES**
/help (h, ?) - Afficher cette aide
/ping (p) - Vérifier que le bot est actif
/status (st, info) - Afficher le statut du bot

🌐 **TRADUCTION**
/translate (t, tr) <texte> - Traduire du chinois au français
   Exemple: /translate 你好

📸 **CAPTURES D'ÉCRAN**
/screenshot (ss, snap) - Capturer une screenshot de la page admin
/list-platforms (lp, platforms) - Lister toutes les plateformes de paiement
/list-channel (lc, channels) <plateforme> - Lister les canaux d'une plateforme
   Exemple: /list-channel Wangpai

⚙️ **GESTION DES CANAUX** (nécessite authentification)
/active (on, activate) <id_canal> - Activer un canal et voir la screenshot
/inactive (off, deactivate) <id_canal> - Désactiver un canal et voir la screenshot
   Exemple: /active 156

💡 **NOTES**
✅ Les commandes sans parenthèses sont libres d'accès
🔒 Les commandes en gris nécessitent une authentification (/register)
⚡ Utilisez les raccourcis pour aller plus vite
"""
    return help_text

async def cmd_ping(args=None, context=None):
    """Répond avec Pong."""
    return "🏓 Pong! bo_bot est en vie."

async def cmd_translate(args=None, context=None):
    """Traduit un texte du chinois au français. Usage: /translate texte"""
    if not args:
        return "❌ /translate nécessite un texte. Usage: /translate votre_texte"
    text_to_translate = " ".join(args)
    translation = google_translate(text_to_translate)
    return f"🌐 Traduction :\n{translation}"

async def cmd_screenshot(args=None, context=None):
    """Prend une capture d'écran de la page admin et l'envoie."""
    try:
        url = 'https://xo-admin.99sq20.fun/admin/exchange/payment-platforms?search=Wangpai&toggleFirst=true'
        token = token_gen.generate_token()
        
        image_bytes = await async_screenshot_with_token(
            url, 
            token, 
            screenshot_path='screenshot_admin.png',
            element_selector='div.va-card__content'
        )
        
        # Récupérer l'event depuis le contexte pour envoyer le fichier
        event = context.get('event') if context else None
        if event and image_bytes:
            # Envoyer le fichier image
            await event.reply(file='screenshot_admin.png')
            return None  # L'image a été envoyée directement
        else:
            return f"📸 Capture d'écran sauvegardée. Taille : {len(image_bytes)} octets"
    except Exception as e:
        return f"❌ Erreur lors de la capture d'écran : {e}"

async def cmd_status(args=None, context=None):
    """Affiche le statut du bot."""
    return "✅ Le bot est actif et écoute les messages."

async def cmd_get_group_id(args=None, context=None):
    """Récupère et affiche l'ID du groupe actuel."""
    event = context.get('event') if context else None
    if not event:
        return "❌ Impossible de récupérer l'ID du groupe"
    
    try:
        chat = await event.get_chat()
        group_id = chat.id
        group_name = chat.title or chat.username or "Groupe sans nom"
        return f"📍 **ID du groupe** : `{group_id}`\n📝 **Nom** : {group_name}"
    except Exception as e:
        return f"❌ Erreur lors de la récupération de l'ID du groupe : {e}"

async def cmd_list_platforms(args=None, context=None):
    """Liste toutes les plateformes de paiement via l'API."""
    try:
        # Générer le token frais
        token = token_gen.generate_token()
        
        # Faire l'appel API avec le token généré
        client_api = APIClient(BASE_URL, token=token)
        result = client_api.call_api('/payment/platforms/all', method='POST')
        
        # Vérifier le code de réponse
        if result.get('code') != 200:
            return f"❌ Erreur API : {result.get('message', 'Erreur inconnue')}"
        
        # Formatter les plateformes
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
        
        query = " ".join(args).lower()  # Convertir en minuscules pour comparaison insensible
        
        # Étape 1 : Récupérer la liste des plateformes
        token = token_gen.generate_token()
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
        token = token_gen.generate_token()
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
        
        # Formatter les canaux
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
        
        channel_id = args[0]
        
        # Étape 1 : Faire l'appel API pour activer le canal
        token = token_gen.generate_token()
        client_api = APIClient(BASE_URL, token=token)
        update_result = client_api.call_api(f'/payment/channels/{channel_id}/update', method='POST', data={'status': 'active'})
        
        # Vérifier la réponse
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
        token = token_gen.generate_token()
        
        image_bytes = await async_screenshot_with_token(
            url, 
            token, 
            screenshot_path='screenshot_active_channel.png',
            element_selector='div.va-card__content'
        )
        
        # Étape 4 : Envoyer l'image
        event = context.get('event') if context else None
        if event and image_bytes:
            await event.reply(f"✅ Canal {channel_id} activé pour la plateforme **{platform_name}**")
            await event.reply(file='screenshot_active_channel.png')
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
        
        channel_id = args[0]
        
        # Étape 1 : Faire l'appel API pour désactiver le canal
        token = token_gen.generate_token()
        client_api = APIClient(BASE_URL, token=token)
        update_result = client_api.call_api(f'/payment/channels/{channel_id}/update', method='POST', data={'status': 'inactive'})
        
        # Vérifier la réponse
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
        token = token_gen.generate_token()
        
        image_bytes = await async_screenshot_with_token(
            url, 
            token, 
            screenshot_path='screenshot_inactive_channel.png',
            element_selector='div.va-card__content'
        )
        
        # Étape 4 : Envoyer l'image
        event = context.get('event') if context else None
        if event and image_bytes:
            await event.reply(f"❌ Canal {platform_data.get('name', '')} {channel_id} désactivé pour la plateforme **{platform_name}**")
            await event.reply(file='screenshot_inactive_channel.png')
            return None  # L'image a été envoyée directement
        else:
            return f"❌ Canal {channel_id} désactivé pour la plateforme **{platform_name}**\n📸 Screenshot sauvegardée. Taille : {len(image_bytes)} octets"
    except Exception as e:
        return f"❌ Erreur lors de la désactivation du canal : {e}"

# Enregistrer les commandes avec raccourcis
cmd_handler.register(['register', 'reg', 'r'], cmd_register, require_auth=False)  # Pas d'auth requise
cmd_handler.register(['unregister', 'unreg', 'u'], cmd_unregister, require_auth=True)  # Auth requise
cmd_handler.register(['help', 'h', '?'], cmd_help, require_auth=False)
cmd_handler.register(['ping', 'p'], cmd_ping, require_auth=False)
cmd_handler.register(['translate', 't', 'tr'], cmd_translate, require_auth=True)  # Auth requise
cmd_handler.register(['screenshot', 'ss', 'snap'], cmd_screenshot, require_auth=True)  # Auth requise
cmd_handler.register(['status', 'st', 'info'], cmd_status, require_auth=False)
cmd_handler.register(['get-group-id', 'group-id', 'gid'], cmd_get_group_id, require_auth=False)
cmd_handler.register(['list-platforms', 'lp', 'platforms'], cmd_list_platforms, require_auth=True)  # Auth requise
cmd_handler.register(['list-channel', 'lc', 'channels'], cmd_list_channel, require_auth=True)  # Auth requise
cmd_handler.register(['active', 'on', 'activate'], cmd_active, require_auth=True)  # Auth requise
cmd_handler.register(['inactive', 'off', 'deactivate'], cmd_inactive, require_auth=True)  # Auth requise


# --- Exemple d'appel API dans le handler ---
@client.on(events.NewMessage(chats=group_id_test))
async def handler(event):
    if event.message.text:
        chinois = event.message.text
        
        # Récupérer l'expéditeur du message
        sender = await event.get_sender()
        expediteur = sender.username or sender.first_name or f"User {sender.id}"
        
        print("\n--- MESSAGE REÇU ---")
        print(f"Expéditeur : {expediteur}")
        print(f"Message : {chinois}")
        
        # Vérifier si c'est une commande
        if cmd_handler.is_command(chinois):
            print("→ Commande détectée")
            result = await cmd_handler.execute(chinois, context={'event': event, 'sender': expediteur})
            # Envoyer la réponse seulement si elle n'est pas None (pour les commandes qui envoient directement un fichier)
            if result:
                await event.reply(result)
        else:
            # Sinon, traduire le message
            francais = google_translate(chinois)
            print(f"Français : {francais}")
            await event.reply(f"🌐 Traduction :\n{francais}")

    #     # Appel API avec JWT après la traduction
    #     BASE_URL = 'https://xo-back.99sq20.fun'  # À remplacer
    #     JWT_SECRET = '907097d66729b9273sdea5wd8d5f45a6s4068f8t5t57u79ac1cc42ed24b9dcea547edf97659e1b4bc252232'   # À remplacer
    #     payload = {
    #     "id": 296952048098738236,
    #     "username": "admin",
    #     "role": "admin",
    #     "code": 123456,
    #     "parent_id": 123456
    # }
    #     client_api = APIClient(BASE_URL, JWT_SECRET, jwt_payload=payload)
    #     try:
    #         api_result = client_api.call_api('/payment/channels/158/update', method='POST', data={
    #             'status': 'active'
    #         })
    #         print('Réponse API:', api_result)
    #     except Exception as e:
    #         print('Erreur lors de l’appel API:', e)

        # --- Test browser_sim : capture d'écran avec token dans le localStorage ---
        # try:
        #     url = 'https://xo-admin.99sq20.fun/admin/exchange/payment-platforms?search=Wangpai&toggleFirst=true'  # À remplacer par l'URL cible
        #     # Générer le token dynamiquement avec TokenGenerator
        #     token_gen = TokenGenerator()
        #     # Support several possible token generator APIs to avoid attribute errors
        #     _gen = getattr(token_gen, 'generate_token', None) or getattr(token_gen, 'generate', None) or getattr(token_gen, 'create_token', None) or getattr(token_gen, 'token', None)
        #     if _gen is None:
        #         # Try calling the instance if it's callable
        #         if callable(token_gen):
        #             token = token_gen()
        #         else:
        #             raise AttributeError("TokenGenerator has no 'generate_token', 'generate' or 'create_token' method, nor a 'token' attribute")
        #     else:
        #         token = _gen() if callable(_gen) else _gen
        #     element_selector = 'div.va-card__content'  # Sélecteur CSS de l'élément

        #     image_bytes = await async_screenshot_with_token(
        #         url, 
        #         token, 
        #         screenshot_path='payment_platforms.png',
        #         element_selector=element_selector
        #     )
        #     print(f'Capture sauvegardée dans payment_platforms.png, taille: {len(image_bytes)} octets')
        # except Exception as e:
        #     print('Erreur lors de la capture d’écran avec browser_sim:', e)

# @client.on(events.NewMessage(chats=nom_du_groupe))
# async def handler(event):
#     if event.message.text:
#         chinois = event.message.text
#         francais = google_translate(chinois)
        
#         print("\n--- MESSAGE 91 REÇU ---")
#         print(f"Chinois : {chinois}")
#         print(f"Français : {francais}")

print("🚀 Bobot écoute le groupe avec l'API Google...")
client.start()
client.run_until_disconnected()
