"""Serveur WebSocket maison qui relaie les déclenchements d'alarme vers l'app Android,
et lui permet de configurer les chats surveillés / utilisateurs exclus.

Protocole JSON minimal :
- Client -> serveur (premier message obligatoire) : {"type": "auth", "token": "..."}
- Serveur -> client : {"type": "auth_ok"} si le token est valide, sinon la
  connexion est fermée.
- Serveur -> client (à chaque déclenchement) : {"type": "alarm", "sender": ..., "text": ..., "ts": ...}

Une fois authentifié, le client peut aussi envoyer :
- {"type": "list_chats"} -> {"type": "chats", "data": [{"id":.., "name":..}, ...]}
- {"type": "list_excludable_users"} -> {"type": "users", "data": [{"id":.., "name":..}, ...]}
  (membres des chats déjà enregistrés dans watch_store, dédupliqués)
- {"type": "get_config"} -> {"type": "config", "chats": [...], "excluded_users": [...]}
- {"type": "set_config", "chats": [...], "excluded_users": [...]} -> {"type": "config_ok"}
"""

import asyncio
import json
import secrets
import time

import websockets


class AlarmServer:
    """Accepte une connexion websocket authentifiée par token, lui diffuse les
    alarmes et lui permet de consulter/modifier les chats/users surveillés."""

    AUTH_TIMEOUT_SECONDS = 10
    PARTICIPANTS_LIMIT = 200

    def __init__(self, host: str, port: int, token: str, client, watch_store):
        self.host = host
        self.port = port
        self.token = token
        self.client = client
        self.watch_store = watch_store
        self._server = None
        self._clients = set()

    async def start(self):
        self._server = await websockets.serve(self._handle_client, self.host, self.port)
        print(f"[AlarmServer] En écoute sur {self.host}:{self.port}")

    async def _handle_client(self, websocket):
        remote = websocket.remote_address
        print(f"[AlarmServer] Nouvelle connexion depuis {remote}")

        try:
            raw = await asyncio.wait_for(websocket.recv(), timeout=self.AUTH_TIMEOUT_SECONDS)
        except asyncio.TimeoutError:
            print(f"[AlarmServer] {remote} : aucun message d'auth reçu sous {self.AUTH_TIMEOUT_SECONDS}s, fermeture")
            await websocket.close()
            return
        except Exception as e:
            print(f"[AlarmServer] {remote} : connexion fermée avant l'auth ({e})")
            return

        print(f"[AlarmServer] {remote} : message reçu = {raw!r}")

        try:
            message = json.loads(raw)
        except Exception as e:
            print(f"[AlarmServer] {remote} : message non-JSON ({e})")
            await websocket.close()
            return

        if message.get('type') != 'auth':
            print(f"[AlarmServer] {remote} : premier message n'est pas de type 'auth' ({message.get('type')!r})")
            await websocket.close()
            return

        if not secrets.compare_digest(str(message.get('token', '')), self.token):
            print(f"[AlarmServer] {remote} : token invalide (reçu={message.get('token')!r})")
            await websocket.close()
            return

        await websocket.send(json.dumps({'type': 'auth_ok'}))
        self._clients.add(websocket)
        print(f"[AlarmServer] {remote} : authentifié ({len(self._clients)} connecté(s))")

        try:
            async for raw in websocket:
                await self._dispatch(websocket, raw)
        except websockets.exceptions.ConnectionClosed:
            pass  # déconnexion normale côté mobile (réseau coupé, app tuée, etc.)
        finally:
            self._clients.discard(websocket)
            print(f"[AlarmServer] {remote} : déconnecté ({len(self._clients)} connecté(s))")

    async def _dispatch(self, websocket, raw):
        try:
            message = json.loads(raw)
        except Exception as e:
            print(f"[AlarmServer] Message non-JSON reçu après auth : {e}")
            return

        msg_type = message.get('type')

        if msg_type == 'list_chats':
            await self._send_chats(websocket)
        elif msg_type == 'list_excludable_users':
            await self._send_excludable_users(websocket)
        elif msg_type == 'get_config':
            await self._send_config(websocket)
        elif msg_type == 'set_config':
            self.watch_store.set_config(
                message.get('chats', []),
                message.get('excluded_users', []),
            )
            await websocket.send(json.dumps({'type': 'config_ok'}))
        else:
            print(f"[AlarmServer] Type de message inconnu : {msg_type!r}")

    async def _send_chats(self, websocket):
        chats = []
        try:
            async for dialog in self.client.iter_dialogs():
                chats.append({'id': dialog.id, 'name': dialog.name or str(dialog.id)})
        except Exception as e:
            print(f"[AlarmServer] Erreur récupération des chats : {e}")
        await websocket.send(json.dumps({'type': 'chats', 'data': chats}))

    async def _send_excludable_users(self, websocket):
        users = {}
        for chat_id in self.watch_store.chats:
            try:
                async for user in self.client.iter_participants(chat_id, limit=self.PARTICIPANTS_LIMIT):
                    name = user.username or user.first_name or f"User {user.id}"
                    users[user.id] = {'id': user.id, 'username': user.username, 'name': name}
            except Exception as e:
                print(f"[AlarmServer] Erreur récupération des membres de {chat_id} : {e}")
        await websocket.send(json.dumps({'type': 'users', 'data': list(users.values())}))

    async def _send_config(self, websocket):
        await websocket.send(json.dumps({
            'type': 'config',
            'chats': self.watch_store.chats,
            'excluded_users': self.watch_store.excluded_users,
        }))

    async def broadcast_alarm(self, sender: str, text: str):
        if not self._clients:
            print("[AlarmServer] broadcast_alarm appelé mais aucun client connecté")
            return

        payload = json.dumps({
            'type': 'alarm',
            'sender': sender,
            'text': text,
            'ts': int(time.time()),
        })
        print(f"[AlarmServer] Envoi de l'alarme à {len(self._clients)} client(s) : {payload}")
        for client in list(self._clients):
            try:
                await client.send(payload)
            except Exception as e:
                print(f"[AlarmServer] Erreur d'envoi à un client : {e}")
