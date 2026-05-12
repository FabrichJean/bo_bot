import jwt
import time
from typing import Dict, Any, Optional


class TokenGenerator:
    """Classe pour générer des tokens JWT avec un payload et une clé secrète."""
    
    def __init__(self, jwt_secret: str = '49caa9850a1abdf6fghrdf5a9fb093c44aac84dbc46b1f7ab7e4d5c252306919cbdf81', default_payload: Optional[Dict[str, Any]] = None):
        """
        Initialise le générateur de token.
        :param jwt_secret: Clé secrète pour signer le JWT
        :param default_payload: Payload par défaut (optionnel)
        """
        default_payload = default_payload or {
            "id": "296952048098738236",
            "username": "admin",
            "role": "admin",
            "code": "123456",
            "parent_id": "123456"
        }
        self.jwt_secret: str = jwt_secret
        self.default_payload: Dict[str, Any] = default_payload
    
    def generate_token(self, custom_payload: Optional[Dict[str, Any]] = None, expiration_hours: int = 1) -> str:
        """
        Génère un token JWT.
        :param custom_payload: Payload personnalisé à fusionner avec le payload par défaut
        :param expiration_hours: Durée d'expiration en heures (par défaut 1h)
        :return: Token JWT en tant que string
        """
        payload = self.default_payload.copy()
        
        # Fusion avec le payload personnalisé si fourni
        if custom_payload:
            payload.update(custom_payload)
        
        # Ajout des timestamps standard
        now = int(time.time())
        payload.setdefault('iat', now)
        payload.setdefault('exp', now + (expiration_hours * 3600))
        
        # Encoding du JWT
        token = jwt.encode(payload, self.jwt_secret, algorithm='HS256')
        
        # PyJWT >=2.0 retourne str, <2.0 retourne bytes
        if isinstance(token, bytes):
            token = token.decode('utf-8')
        
        return token
    
    def generate_token_with_admin_payload(self, admin_id: Optional[str] = None, username: Optional[str] = None, expiration_hours: int = 1) -> str:
        """
        Génère un token avec un payload d'admin prédéfini.
        :param admin_id: ID de l'admin (utilise le default si None)
        :param username: Nom d'utilisateur (utilise le default si None)
        :param expiration_hours: Durée d'expiration en heures
        :return: Token JWT
        """
        custom_payload = {}
        if admin_id:
            custom_payload['id'] = admin_id
        if username:
            custom_payload['username'] = username
        
        return self.generate_token(custom_payload, expiration_hours)


# Exemple d'utilisation
if __name__ == '__main__':
    JWT_SECRET = '49caa9850a1abdf6fghrdf5a9fb093c44aac84dbc46b1f7ab7e4d5c252306919cbdf81'
    
    # Payload d'admin par défaut
    admin_payload = {
        "id": "296952048098738236",
        "username": "admin",
        "role": "admin",
        "code": "123456",
        "parent_id": "123456"
    }
    
    # Créer un générateur de token
    token_gen = TokenGenerator(JWT_SECRET, default_payload=admin_payload)
    
    # Générer un token avec le payload par défaut
    token = token_gen.generate_token()
    print("Token généré :")
    print(token)
    print()
    
    # Générer un token avec un payload personnalisé
    custom_token = token_gen.generate_token(
        custom_payload={'username': 'other_admin'},
        expiration_hours=2
    )
    print("Token personnalisé :")
    print(custom_token)
