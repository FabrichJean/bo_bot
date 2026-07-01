"""Feature: commandes génériques du bot (aide, ping, statut, infos groupe)."""


def register(ctx):
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
            entity = await ctx.client.get_entity(query)
            name = getattr(entity, 'title', None) or getattr(entity, 'username', None) or str(entity.id)
            return f"📍 **ID** : `{entity.id}`\n📝 **Nom** : {name}"
        except Exception:
            pass

        # 2. Recherche dans les dialogues (groupes privés dont on est membre)
        try:
            matches = []
            async for dialog in ctx.client.iter_dialogs():
                e = dialog.entity
                name = getattr(e, 'title', None) or getattr(e, 'username', None) or ""
                if query_clean.lower() in name.lower():
                    matches.append(f"📍 `{e.id}` — {name}")
            if matches:
                return "\n".join(matches)
            return f"❌ Aucun groupe trouvé pour : `{query}`"
        except Exception as e:
            return f"❌ Erreur lors de la recherche : {e}"

    ctx.cmd_handler.register(['help', 'h', '?'], cmd_help, require_auth=False)
    ctx.cmd_handler.register(['ping', 'p'], cmd_ping, require_auth=False)
    ctx.cmd_handler.register(['status', 'st', 'info'], cmd_status, require_auth=False)
    ctx.cmd_handler.register(['get-group-id', 'group-id', 'gid'], cmd_get_group_id, require_auth=False)
