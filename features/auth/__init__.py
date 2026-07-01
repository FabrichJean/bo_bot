"""Feature: enregistrement des utilisateurs et gestion des codes d'accès."""

from .codes import load_registration_codes, remove_registration_code


def register(ctx):
    valid_codes = load_registration_codes()

    async def get_current_user():
        """
        Récupère les informations de l'utilisateur connecté (me) via la session Telethon.

        Note: Pour Telethon, on utilise une approche défensive avec getattr.
        Cette fonction essaie plusieurs méthodes pour obtenir l'identité du bot.
        """
        try:
            me = await ctx.client.get_me()

            username = getattr(me, 'username', None)
            if username:
                return username

            first_name = getattr(me, 'first_name', None)
            if first_name:
                return first_name

            user_id = getattr(me, 'id', None)
            if user_id:
                return f"User {user_id}"

            return None
        except Exception as e:
            print(f"Erreur lors de la récupération de l'utilisateur connecté : {e}")
            return None

    async def cmd_register(args=None, context=None):
        """Enregistre l'utilisateur avec un code valide. Usage: /register CODE"""
        nonlocal valid_codes

        sender = context.get('sender') if context else None
        if not sender:
            return "❌ Impossible de déterminer l'expéditeur"

        if not args or len(args) == 0:
            return "❌ /register nécessite un code. Usage: /register CODE\n💡 Demandez un code valide à l'administrateur."

        code = args[0].upper()

        if code not in valid_codes:
            return f"❌ Code invalide: `{code}`\n💡 Le code fourni n'est pas autorisé. Contactez l'administrateur."

        if ctx.user_registry.is_authorized(sender):
            return f"✅ Vous êtes déjà enregistré : {sender}"

        ctx.user_registry.register_user(sender)

        remove_registration_code(code)
        valid_codes = load_registration_codes()

        return f"✅ Vous êtes maintenant enregistré : @{sender}\n🔓 Vous pouvez maintenant utiliser les commandes protégées !"

    async def cmd_unregister(args=None, context=None):
        """Désactive l'accès aux commandes protégées pour cet utilisateur."""
        sender = context.get('sender') if context else None
        if not sender:
            return "❌ Impossible de déterminer l'expéditeur"

        if not ctx.user_registry.is_authorized(sender):
            return f"❌ {sender} n'est pas enregistré"

        ctx.user_registry.unregister_user(sender)
        return f"❌ Vous avez été désenregistré : {sender}"

    async def cmd_send_codes(args=None, context=None):
        """
        Envoie un code d'enregistrement.
        Usage:
          - /code : Envoyer aux messages enregistrés (Saved Messages) - accessible à tous
          - /code @username : Envoyer directement à l'utilisateur spécifié - seulement pour le propriétaire du bot
        """
        try:
            sender = context.get('sender') if context else 'Utilisateur inconnu'

            codes = load_registration_codes()

            if not codes:
                return "❌ Aucun code disponible."

            code = codes[0]

            target_user = None
            if args and len(args) > 0:
                target_user = args[0]
                if target_user.startswith('@'):
                    target_user = target_user[1:]

                current_user = await get_current_user()

                if sender != current_user:
                    return "❌ Seul le propriétaire du bot peut envoyer un code directement à un utilisateur.\n💡 Utilisez `/code` sans argument pour envoyer aux messages enregistrés."

            codes_text = "🔐 **CODE D'ENREGISTREMENT**\n\n"
            codes_text += f"👤 Demandé par: @{sender}\n\n"
            codes_text += f"Code: `{code}`\n\n"
            codes_text += f"💡 Utilise: `/register {code}` pour t'enregistrer"

            try:
                if target_user:
                    await ctx.client.send_message(target_user, codes_text)
                    return f"✅ Code envoyé à @{target_user}"
                else:
                    await ctx.client.send_message('me', codes_text)
                    return "✅ Code envoyé aux messages enregistrés"
            except Exception as e:
                return f"❌ Erreur lors de l'envoi du code : {e}"

        except Exception as e:
            return f"❌ Erreur : {e}"

    ctx.cmd_handler.register(['register', 'reg', 'r'], cmd_register, require_auth=False)
    ctx.cmd_handler.register(['unregister', 'unreg', 'u'], cmd_unregister, require_auth=True)
    ctx.cmd_handler.register(['code', 'codes', 'send-codes'], cmd_send_codes, require_auth=False)
