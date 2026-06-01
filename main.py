from telethon import TelegramClient, events
import re
import io
import requests
from api_client import APIClient
from browser_sim import async_screenshot_with_token
from token_generator import TokenGenerator
from command_handler import CommandHandler
from user_registry import UserRegistry
from config import *

# Telethon exige un int pour les IDs numériques, pas une string
if isinstance(RAPPORT_TEST_SAVE_DESTINATION, str) and RAPPORT_TEST_SAVE_DESTINATION.lstrip('-').isdigit():
    RAPPORT_TEST_SAVE_DESTINATION = int(RAPPORT_TEST_SAVE_DESTINATION)

# Initialiser le client Telegram
client = TelegramClient(
    TELEGRAM_SESSION_NAME, 
    TELEGRAM_API_ID, 
    TELEGRAM_API_HASH,
    connection_retries=CONNECTION_RETRIES,
    retry_delay=RETRY_DELAY,
    auto_reconnect=AUTO_RECONNECT
)

# --- FONCTIONS UTILITAIRES ---
def load_registration_codes():
    """Charge les codes d'enregistrement depuis le fichier."""
    try:
        with open(REGISTRATION_CODES_FILE, 'r') as f:
            codes = [line.strip().upper() for line in f if line.strip()]
        return codes
    except FileNotFoundError:
        return []

def remove_registration_code(code):
    """Supprime un code d'enregistrement du fichier après utilisation."""
    try:
        with open(REGISTRATION_CODES_FILE, 'r') as f:
            codes = [line.strip() for line in f if line.strip()]
        
        # Supprimer le code (insensible à la casse)
        codes = [c for c in codes if c.upper() != code.upper()]
        
        with open(REGISTRATION_CODES_FILE, 'w') as f:
            for code in codes:
                f.write(code + '\n')
    except Exception as e:
        print(f"Erreur lors de la suppression du code : {e}")

def google_translate(text, target_lang=TRANSLATE_TARGET_LANG):
    """Traduit un texte via l'API Google Translate."""
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl={TRANSLATE_SOURCE_LANG}&tl={target_lang}&dt=t&q={text}"
        response = requests.get(url)
        # L'API renvoie une liste de listes, la traduction est dans le premier élément
        return response.json()[0][0][0]
    except Exception as e:
        return f"[Erreur traduction: {e}]"

def get_screenshot_path(user, status_type, timestamp=None):
    """
    Génère le chemin de screenshot avec la structure: screenshots/{user}/{active|inactive}/{timestamp}.png
    Args:
        user: Nom d'utilisateur
        status_type: 'active' ou 'inactive'
        timestamp: Timestamp optionnel (par défaut: datetime actuel)
    Returns:
        str: Chemin complet du fichier screenshot
    """
    import os
    from datetime import datetime
    
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Créer le chemin complet
    screenshot_dir = os.path.join(SCREENSHOT_ROOT_DIR, user, status_type)
    
    # Créer les dossiers s'ils n'existent pas
    os.makedirs(screenshot_dir, exist_ok=True)
    
    # Construire le chemin complet du fichier
    filename = f"{timestamp}.png"
    full_path = os.path.join(screenshot_dir, filename)
    
    return full_path


async def get_current_user():
    """
    Récupère les informations de l'utilisateur connecté (me) via la session Telethon.
    
    Note: Pour Telethon, on utilise une approche défensive avec getattr.
    Cette fonction essaie plusieurs méthodes pour obtenir l'identité du bot.
    
    Returns:
        str: Identifiant du bot connecté ou None si non disponible
    """
    try:
        # Telethon: client.get_me() retourne un InputPeerUser qui n'a pas tous les attributs
        # On utilise getattr avec des valeurs par défaut pour éviter les erreurs de type
        me = await client.get_me()
        
        # Essayer le username d'abord
        username = getattr(me, 'username', None)
        if username:
            return username
        
        # Puis first_name
        first_name = getattr(me, 'first_name', None)
        if first_name:
            return first_name
        
        # Finalement l'ID
        user_id = getattr(me, 'id', None)
        if user_id:
            return f"User {user_id}"
        
        return None
    except Exception as e:
        print(f"Erreur lors de la récupération de l'utilisateur connecté : {e}")
        return None


# Charger les codes valides au démarrage
VALID_REGISTRATION_CODES = load_registration_codes()

# Initialiser le générateur de token global
token_gen = TokenGenerator(JWT_SECRET, default_payload=ADMIN_PAYLOAD)

# --- Initialiser le registre des utilisateurs ---
user_registry = UserRegistry(registry_file=AUTHORIZED_USERS_FILE)

# --- Initialiser le gestionnaire de commandes ---
cmd_handler = CommandHandler(prefix=COMMAND_PREFIX, user_registry=user_registry)

# --- Enregistrer les commandes ---
async def cmd_register(args=None, context=None):
    """Enregistre l'utilisateur avec un code valide. Usage: /register CODE"""
    global VALID_REGISTRATION_CODES
    
    sender = context.get('sender') if context else None
    if not sender:
        return "❌ Impossible de déterminer l'expéditeur"
    
    # Vérifier si un code a été fourni
    if not args or len(args) == 0:
        return "❌ /register nécessite un code. Usage: /register CODE\n💡 Demandez un code valide à l'administrateur."
    
    code = args[0].upper()  # Convertir en majuscules pour la comparaison
    
    # Vérifier si le code est valide
    if code not in VALID_REGISTRATION_CODES:
        return f"❌ Code invalide: `{code}`\n💡 Le code fourni n'est pas autorisé. Contactez l'administrateur."
    
    # Vérifier si déjà enregistré
    if user_registry.is_authorized(sender):
        return f"✅ Vous êtes déjà enregistré : {sender}"
    
    # Enregistrer l'utilisateur
    user_registry.register_user(sender)
    
    # Supprimer le code du fichier après utilisation
    remove_registration_code(code)
    
    # Recharger les codes depuis le fichier
    VALID_REGISTRATION_CODES = load_registration_codes()
    
    return f"✅ Vous êtes maintenant enregistré : @{sender}\n🔓 Vous pouvez maintenant utiliser les commandes protégées !"

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
/register (reg, r) <code> - S'enregistrer pour accéder aux commandes protégées
/unregister (unreg, u) - Se désenregistrer

🔑 **CODES D'ENREGISTREMENT**
/code (codes, send-codes) - Envoyer un code aux messages enregistrés
/code @username - Envoyer directement un code à l'utilisateur spécifié
   Exemple: /code @john_doe

🔧 **UTILITAIRES**
/help (h, ?) - Afficher cette aide
/ping (p) - Vérifier que le bot est actif
/status (st, info) - Afficher le statut du bot
/get-group-id (gid) - Récupérer l'ID du groupe actuel

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
        sender = context.get('sender') if context else 'admin'
        url = SCREENSHOT_ADMIN_URL
        token = token_gen.generate_token()
        
        # Générer le chemin de screenshot
        screenshot_path = get_screenshot_path(sender, 'admin')
        
        image_bytes = await async_screenshot_with_token(
            url, 
            token, 
            screenshot_path=screenshot_path,
            element_selector=SCREENSHOT_ELEMENT_SELECTOR
        )
        # Récupérer l'event depuis le contexte pour envoyer le fichier
        event = context.get('event') if context else None
        if event and image_bytes:
            # Envoyer le fichier image
            await event.reply(file=screenshot_path)
            return None  # L'image a été envoyée directement
        else:
            return f"📸 Capture d'écran sauvegardée. Taille : {len(image_bytes)} octets"
    except Exception as e:
        return f"❌ Erreur lors de la capture d'écran : {e}"

async def cmd_status(args=None, context=None):
    """Affiche le statut du bot."""
    return "✅ Le bot est actif et écoute les messages."

async def cmd_get_group_id(args=None, context=None):
    """Récupère l'ID du groupe courant ou d'un groupe par nom/username. Usage: /gid [@username|nom]"""
    # Sans argument : groupe courant
    if not args:
        event = context.get('event') if context else None
        if not event:
            return "❌ Impossible de récupérer l'ID du groupe"
        try:
            chat = await event.get_chat()
            name = getattr(chat, 'title', None) or getattr(chat, 'username', None) or "Groupe sans nom"
            return f"📍 **ID du groupe** : `{chat.id}`\n📝 **Nom** : {name}"
        except Exception as e:
            return f"❌ Erreur : {e}"

    # Avec argument : chercher par username ou nom
    query = " ".join(args).strip()
    query_clean = query.lstrip('@')

    # 1. Résolution directe (fonctionne pour les groupes/canaux publics)
    try:
        entity = await client.get_entity(query)
        name = getattr(entity, 'title', None) or getattr(entity, 'username', None) or str(entity.id)
        return f"📍 **ID** : `{entity.id}`\n📝 **Nom** : {name}"
    except Exception:
        pass

    # 2. Recherche dans les dialogues (groupes privés dont on est membre)
    try:
        matches = []
        async for dialog in client.iter_dialogs():
            e = dialog.entity
            name = getattr(e, 'title', None) or getattr(e, 'username', None) or ""
            if query_clean.lower() in name.lower():
                matches.append(f"📍 `{e.id}` — {name}")
        if matches:
            return "\n".join(matches)
        return f"❌ Aucun groupe trouvé pour : `{query}`"
    except Exception as e:
        return f"❌ Erreur lors de la recherche : {e}"

async def cmd_send_codes(args=None, context=None):
    """
    Envoie un code d'enregistrement.
    Usage: 
      - /code : Envoyer aux messages enregistrés (Saved Messages) - accessible à tous
      - /code @username : Envoyer directement à l'utilisateur spécifié - seulement pour le propriétaire du bot
    """
    try:
        # Récupérer le sender
        sender = context.get('sender') if context else 'Utilisateur inconnu'
        
        # Recharger les codes depuis le fichier
        codes = load_registration_codes()
        
        if not codes:
            return "❌ Aucun code disponible."
        
        # Prendre le premier code disponible
        code = codes[0]
        
        # Vérifier si un destinataire a été spécifié
        target_user = None
        if args and len(args) > 0:
            target_user = args[0]
            # Nettoyer le @ si présent
            if target_user.startswith('@'):
                target_user = target_user[1:]
            
            # Vérifier si l'expéditeur est autorisé à envoyer directement
            # L'utilisateur doit être le propriétaire du bot (logged-in user)
            current_user = await get_current_user()
            
            if sender != current_user:
                return f"❌ Seul le propriétaire du bot peut envoyer un code directement à un utilisateur.\n💡 Utilisez `/code` sans argument pour envoyer aux messages enregistrés."
        
        # Formater le message
        codes_text = f"🔐 **CODE D'ENREGISTREMENT**\n\n"
        codes_text += f"👤 Demandé par: @{sender}\n\n"
        codes_text += f"Code: `{code}`\n\n"
        codes_text += f"💡 Utilise: `/register {code}` pour t'enregistrer"
        
        # Envoyer à la destination appropriée
        try:
            if target_user:
                # Envoyer directement à l'utilisateur spécifié
                await client.send_message(target_user, codes_text)
                return f"✅ Code envoyé à @{target_user}"
            else:
                # Envoyer aux messages enregistrés (Saved Messages)
                await client.send_message('me', codes_text)
                return f"✅ Code envoyé aux messages enregistrés"
        except Exception as e:
            return f"❌ Erreur lors de l'envoi du code : {e}"
    
    except Exception as e:
        return f"❌ Erreur : {e}"

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
        
        sender = context.get('sender') if context else 'admin'
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
        
        # Générer le chemin de screenshot avec structure: screenshots/{user}/active/{timestamp}.png
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
        
        # Générer le chemin de screenshot avec structure: screenshots/{user}/inactive/{timestamp}.png
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

# Enregistrer les commandes avec raccourcis
cmd_handler.register(['register', 'reg', 'r'], cmd_register, require_auth=False)  # Pas d'auth requise
cmd_handler.register(['unregister', 'unreg', 'u'], cmd_unregister, require_auth=True)  # Auth requise
cmd_handler.register(['help', 'h', '?'], cmd_help, require_auth=False)
cmd_handler.register(['ping', 'p'], cmd_ping, require_auth=False)
cmd_handler.register(['translate', 't', 'tr'], cmd_translate, require_auth=True)  # Auth requise
cmd_handler.register(['screenshot', 'ss', 'snap'], cmd_screenshot, require_auth=True)  # Auth requise
cmd_handler.register(['status', 'st', 'info'], cmd_status, require_auth=False)
cmd_handler.register(['get-group-id', 'group-id', 'gid'], cmd_get_group_id, require_auth=False)
cmd_handler.register(['code', 'codes', 'send-codes'], cmd_send_codes, require_auth=False)
cmd_handler.register(['list-platforms', 'lp', 'platforms'], cmd_list_platforms, require_auth=True)  # Auth requise
cmd_handler.register(['list-channel', 'lc', 'channels'], cmd_list_channel, require_auth=True)  # Auth requise
cmd_handler.register(['active', 'on', 'activate'], cmd_active, require_auth=True)  # Auth requise
cmd_handler.register(['inactive', 'off', 'deactivate'], cmd_inactive, require_auth=True)  # Auth requise


# --- HANDLER PRINCIPAL ---
@client.on(events.NewMessage(chats=GROUP_ID_TEST))
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

@client.on(events.NewMessage(chats=GROUP_ID_TEST))
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
            nearby = await client.get_messages(event.chat_id, ids=nearby_ids)
            if nearby is None:
                nearby = []
            elif not isinstance(nearby, (list, tuple)):
                nearby = [nearby]

            for m in nearby:
                if m and m.grouped_id == grouped_id and m.id != trigger_id:
                    messages_to_forward.append(m)
    else:
        # Pas de médias directs : chercher des images du même user dans la même minute ou adjacentes
        before = await client.get_messages(event.chat_id, limit=25, offset_id=trigger_id) or []
        after = await client.get_messages(event.chat_id, limit=25, min_id=trigger_id, reverse=True) or []

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
            await client.download_media(m, file=buffer)
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
                await client.send_file(RAPPORT_TEST_SAVE_DESTINATION, batch, caption=combined_text, force_document=False)
            else:
                await client.send_file(RAPPORT_TEST_SAVE_DESTINATION, batch, force_document=False)
        print(f"[rapport_test] ✅ {len(media_files)} photo(s) → Saved Messages")
    elif combined_text:
        await client.send_message(RAPPORT_TEST_SAVE_DESTINATION, combined_text)
        print("[rapport_test] ✅ texte seul → Saved Messages")


print("🚀 Bobot écoute le groupe avec l'API Google...")
client.start()
client.run_until_disconnected()
