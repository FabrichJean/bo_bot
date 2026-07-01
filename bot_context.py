from dataclasses import dataclass

from telethon import TelegramClient

from command_handler import CommandHandler
from services.token_service import TokenGenerator
from services.alarm_server import AlarmServer
from services.alarm_watch_store import AlarmWatchStore
from features.auth.registry import UserRegistry


@dataclass
class BotContext:
    """Regroupe les dépendances partagées entre les features du bot."""
    client: TelegramClient
    cmd_handler: CommandHandler
    token_gen: TokenGenerator
    user_registry: UserRegistry
    alarm_server: AlarmServer
    watch_store: AlarmWatchStore
