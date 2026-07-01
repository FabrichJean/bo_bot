import json
import os
from typing import List

from config import MESSAGE_ALARM_CHATS, EXCLUDED_USERS


class AlarmWatchStore:
    """Persiste (et permet de modifier à chaud) les chats surveillés et les
    utilisateurs exclus pour la feature message_alarm. Configurable depuis
    l'app Android via services/alarm_server.py."""

    def __init__(self, path: str = 'alarm_watch_config.json'):
        self.path = path
        self.chats: List[int] = list(MESSAGE_ALARM_CHATS)
        self.excluded_users: List[str] = list(EXCLUDED_USERS)
        self._load()

    def _load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, 'r') as f:
                    data = json.load(f)
                self.chats = list(data.get('chats', self.chats))
                self.excluded_users = list(data.get('excluded_users', self.excluded_users))
                print(f"[AlarmWatchStore] Chargé : {len(self.chats)} chat(s), {len(self.excluded_users)} exclu(s)")
            except Exception as e:
                print(f"[AlarmWatchStore] Erreur lors du chargement : {e}")

    def _save(self):
        try:
            with open(self.path, 'w') as f:
                json.dump({'chats': self.chats, 'excluded_users': self.excluded_users}, f, indent=2)
        except Exception as e:
            print(f"[AlarmWatchStore] Erreur lors de la sauvegarde : {e}")

    def set_config(self, chats: List[int], excluded_users: List[str]):
        self.chats = [int(c) for c in chats]
        self.excluded_users = [str(u) for u in excluded_users]
        self._save()
        print(f"[AlarmWatchStore] Mis à jour : {len(self.chats)} chat(s), {len(self.excluded_users)} exclu(s)")

    def is_watched(self, chat_id: int) -> bool:
        return chat_id in self.chats

    def is_excluded(self, sender_id, username) -> bool:
        excluded_lower = {str(u).lower() for u in self.excluded_users}
        identifiers = {str(sender_id)}
        if username:
            identifiers.add(username.lower())
        return bool(identifiers & excluded_lower)
