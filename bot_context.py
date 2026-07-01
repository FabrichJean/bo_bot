from dataclasses import dataclass

from telethon import TelegramClient

from command_handler import CommandHandler
from services.token_service import TokenGenerator
from features.auth.registry import UserRegistry


@dataclass
class BotContext:
    """Regroupe les dépendances partagées entre les features du bot."""
    client: TelegramClient
    cmd_handler: CommandHandler
    token_gen: TokenGenerator
    user_registry: UserRegistry
