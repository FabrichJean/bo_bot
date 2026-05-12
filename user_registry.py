import json
import os
from typing import Set, List, Optional


class UserRegistry:
    """Gère l'enregistrement et les permissions des utilisateurs."""
    
    def __init__(self, registry_file: str = 'authorized_users.json'):
        """
        Initialise le registre des utilisateurs.
        :param registry_file: Fichier JSON pour persister les utilisateurs autorisés
        """
        self.registry_file = registry_file
        self.authorized_users: Set[str] = set()
        self.admin_users: Set[str] = set()
        self._load()
    
    def _load(self):
        """Charge les utilisateurs depuis le fichier JSON."""
        if os.path.exists(self.registry_file):
            try:
                with open(self.registry_file, 'r') as f:
                    data = json.load(f)
                    self.authorized_users = set(data.get('authorized_users', []))
                    self.admin_users = set(data.get('admin_users', []))
                print(f"[UserRegistry] Chargé {len(self.authorized_users)} utilisateurs autorisés")
            except Exception as e:
                print(f"[UserRegistry] Erreur lors du chargement : {e}")
        else:
            self.authorized_users = set()
            self.admin_users = set()
    
    def _save(self):
        """Sauvegarde les utilisateurs dans le fichier JSON."""
        try:
            with open(self.registry_file, 'w') as f:
                json.dump({
                    'authorized_users': sorted(list(self.authorized_users)),
                    'admin_users': sorted(list(self.admin_users))
                }, f, indent=2)
            print(f"[UserRegistry] Sauvegardé {len(self.authorized_users)} utilisateurs")
        except Exception as e:
            print(f"[UserRegistry] Erreur lors de la sauvegarde : {e}")
    
    def register_user(self, username: str, is_admin: bool = False) -> bool:
        """
        Enregistre un nouvel utilisateur autorisé.
        :param username: Nom d'utilisateur ou ID
        :param is_admin: Si True, l'utilisateur est admin
        :return: True si enregistré, False si déjà existant
        """
        if username in self.authorized_users:
            return False  # Déjà enregistré
        
        self.authorized_users.add(username)
        if is_admin:
            self.admin_users.add(username)
        
        self._save()
        return True
    
    def unregister_user(self, username: str) -> bool:
        """
        Désenregistre un utilisateur.
        :param username: Nom d'utilisateur ou ID
        :return: True si supprimé, False si n'existait pas
        """
        if username not in self.authorized_users:
            return False
        
        self.authorized_users.discard(username)
        self.admin_users.discard(username)
        self._save()
        return True
    
    def is_authorized(self, username: str) -> bool:
        """Vérifie si un utilisateur est autorisé."""
        return username in self.authorized_users
    
    def is_admin(self, username: str) -> bool:
        """Vérifie si un utilisateur est admin."""
        return username in self.admin_users
    
    def promote_to_admin(self, username: str) -> bool:
        """Promeut un utilisateur en admin."""
        if username not in self.authorized_users:
            return False
        
        self.admin_users.add(username)
        self._save()
        return True
    
    def demote_from_admin(self, username: str) -> bool:
        """Rétrograde un admin."""
        if username not in self.admin_users:
            return False
        
        self.admin_users.discard(username)
        self._save()
        return True
    
    def list_authorized_users(self) -> List[str]:
        """Retourne la liste des utilisateurs autorisés."""
        return sorted(list(self.authorized_users))
    
    def list_admin_users(self) -> List[str]:
        """Retourne la liste des admins."""
        return sorted(list(self.admin_users))
    
    def get_stats(self) -> str:
        """Retourne les statistiques du registre."""
        total = len(self.authorized_users)
        admins = len(self.admin_users)
        users = total - admins
        return f"👥 Utilisateurs : {users}\n🔑 Admins : {admins}\n📊 Total : {total}"


# Exemple d'utilisation
if __name__ == '__main__':
    registry = UserRegistry()
    
    # Enregistrer des utilisateurs
    registry.register_user('alice', is_admin=True)
    registry.register_user('bob')
    registry.register_user('charlie')
    
    # Vérifier permissions
    print(f"alice autorisée ? {registry.is_authorized('alice')}")
    print(f"alice admin ? {registry.is_admin('alice')}")
    print(f"bob admin ? {registry.is_admin('bob')}")
    
    # Lister
    print(f"Utilisateurs : {registry.list_authorized_users()}")
    print(f"Admins : {registry.list_admin_users()}")
    
    # Stats
    print(registry.get_stats())
