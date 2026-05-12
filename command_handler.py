from typing import Callable, Dict, Any, Optional
import asyncio


class CommandHandler:
    """Gestionnaire de commandes pour le bot Telegram."""
    
    def __init__(self, prefix: str = '/', user_registry = None):
        """
        Initialise le gestionnaire de commandes.
        :param prefix: Préfixe pour identifier une commande (par défaut '/')
        :param user_registry: Instance de UserRegistry pour vérifier les permissions
        """
        self.prefix = prefix
        self.commands: Dict[str, Callable] = {}
        self.user_registry = user_registry
        self.require_auth: Dict[str, bool] = {}  # Commandes nécessitant une authentification
    
    def register(self, command_name, callback: Callable, require_auth: bool = False):
        """
        Enregistre une ou plusieurs commandes avec sa fonction de callback.
        :param command_name: Nom de la commande (ex: 'help', 'screenshot') ou liste de noms ['help', 'h']
        :param callback: Fonction asynchrone à exécuter
        :param require_auth: Si True, seuls les utilisateurs autorisés peuvent exécuter
        """
        # Accepter soit une string soit une liste de strings
        command_names = command_name if isinstance(command_name, list) else [command_name]
        
        for cmd in command_names:
            cmd_lower = cmd.lower()
            self.commands[cmd_lower] = callback
            self.require_auth[cmd_lower] = require_auth
            print(f"[CommandHandler] Commande enregistrée : {self.prefix}{cmd}" + (" (authentification requise)" if require_auth else ""))
    
    def is_command(self, text: str) -> bool:
        """Vérifie si le texte est une commande."""
        return text.startswith(self.prefix)
    
    def parse_command(self, text: str) -> tuple:
        """
        Parse un texte de commande.
        :return: (nom_commande, [arguments])
        """
        if not self.is_command(text):
            return None, []
        
        # Enlever le préfixe et splitter par espaces
        text = text[len(self.prefix):]
        parts = text.split()
        
        if not parts:
            return None, []
        
        command_name = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        return command_name, args
    
    async def execute(self, text: str, context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Exécute une commande si elle existe et si l'utilisateur est autorisé.
        :param text: Texte du message contenant la commande
        :param context: Contexte à passer au callback (ex: event, sender, etc)
        :return: Résultat de l'exécution ou None
        """
        if not self.is_command(text):
            return None
        
        command_name, args = self.parse_command(text)
        
        if not command_name or command_name not in self.commands:
            return f"❌ Commande inconnue : {self.prefix}{command_name}"
        
        # Vérifier les permissions si nécessaire
        if self.require_auth.get(command_name, False):
            if not self.user_registry:
                return "❌ Système d'authentification non configuré"
            
            sender = context.get('sender') if context else None
            if not sender or not self.user_registry.is_authorized(sender):
                return f"❌ Vous n'êtes pas autorisé à exécuter cette commande. Utilisez /code pour demander l'accès."
        
        try:
            callback = self.commands[command_name]
            # Passer le contexte et les arguments au callback
            result = await callback(args=args, context=context or {})
            return result
        except Exception as e:
            return f"❌ Erreur lors de l'exécution de la commande : {e}"
    
    def list_commands(self) -> str:
        """Retourne la liste des commandes disponibles."""
        if not self.commands:
            return "Aucune commande enregistrée."
        
        commands_list = "\n".join([f"{self.prefix}{cmd}" for cmd in sorted(self.commands.keys())])
        return f"Commandes disponibles :\n{commands_list}"


# Exemple d'utilisation
if __name__ == '__main__':
    handler = CommandHandler(prefix='/')
    
    # Enregistrer des commandes
    async def cmd_help(args=None, context=None):
        return "Ceci est l'aide du bot"
    
    async def cmd_ping(args=None, context=None):
        return "Pong! 🏓"
    
    async def cmd_echo(args=None, context=None):
        if not args:
            return "❌ /echo nécessite un argument"
        return " ".join(args)
    
    handler.register('help', cmd_help)
    handler.register('ping', cmd_ping)
    handler.register('echo', cmd_echo)
    
    # Tester
    async def test():
        result = await handler.execute('/ping')
        print(result)
        
        result = await handler.execute('/echo hello world')
        print(result)
        
        result = await handler.execute('/unknown')
        print(result)
        
        print(handler.list_commands())
    
    asyncio.run(test())
