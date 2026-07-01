from telethon import TelegramClient, events

from config import *
from command_handler import CommandHandler
from services.token_service import TokenGenerator
from services.alarm_server import AlarmServer
from services.alarm_watch_store import AlarmWatchStore
from features.auth.registry import UserRegistry
from bot_context import BotContext
from features import auth, core, translate, screenshots, payments
from features.listeners import rapport_test, jkbot_relay, message_alarm

# Initialiser le client Telegram
client = TelegramClient(
    TELEGRAM_SESSION_NAME,
    TELEGRAM_API_ID,
    TELEGRAM_API_HASH,
    connection_retries=CONNECTION_RETRIES,
    retry_delay=RETRY_DELAY,
    auto_reconnect=AUTO_RECONNECT
)

# Initialiser le générateur de token global
token_gen = TokenGenerator(JWT_SECRET, default_payload=ADMIN_PAYLOAD)

# Initialiser le registre des utilisateurs
user_registry = UserRegistry(registry_file=AUTHORIZED_USERS_FILE)

# Initialiser le gestionnaire de commandes
cmd_handler = CommandHandler(prefix=COMMAND_PREFIX, user_registry=user_registry)

# Initialiser le store des chats/users surveillés (configurable depuis l'app Android)
watch_store = AlarmWatchStore()

# Initialiser le serveur d'alarme (WebSocket vers l'app Android)
alarm_server = AlarmServer(ALARM_WS_HOST, ALARM_WS_PORT, ALARM_WS_TOKEN, client, watch_store)

ctx = BotContext(
    client=client,
    cmd_handler=cmd_handler,
    token_gen=token_gen,
    user_registry=user_registry,
    alarm_server=alarm_server,
    watch_store=watch_store,
)

# --- Enregistrer chaque feature (commandes + listeners) ---
auth.register(ctx)
core.register(ctx)
translate.register(ctx)
screenshots.register(ctx)
payments.register(ctx)
rapport_test.register(ctx)
jkbot_relay.register(ctx)
message_alarm.register(ctx)


# --- HANDLER PRINCIPAL (routeur générique de commandes) ---
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


if __name__ == '__main__':
    print("🚀 Bobot écoute le groupe avec l'API Google...")
    client.start()
    client.loop.create_task(alarm_server.start())
    client.run_until_disconnected()
