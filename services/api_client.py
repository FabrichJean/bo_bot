import requests
import jwt
import time
from typing import Optional, Dict, Any

class APIClient:
    def __init__(self, base_url: str, token: Optional[str] = None):
        """
        Initialise le client API.
        :param base_url: URL de base de l'API
        :param token: Token JWT à utiliser pour l'authentification (optionnel)
        """
        self.base_url = base_url
        self.token = token

    def call_api(self, endpoint: str, method: str = 'GET', data: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None, token: Optional[str] = None):
        """
        Fait un appel API avec authentification Bearer token.
        :param endpoint: Endpoint de l'API
        :param method: Méthode HTTP (GET, POST, etc.)
        :param data: Données à envoyer en JSON
        :param headers: En-têtes supplémentaires
        :param params: Paramètres de query
        :param token: Token JWT à utiliser (sinon utilise self.token)
        :return: Réponse JSON de l'API
        """
        url = self.base_url.rstrip('/') + '/' + endpoint.lstrip('/')
        
        # Utiliser le token fourni en paramètre, sinon celui de l'instance
        jwt_token = token or self.token
        if not jwt_token:
            raise ValueError("Aucun token JWT fourni")
        
        req_headers = {'Authorization': f'Bearer {jwt_token}'}
        if headers:
            req_headers.update(headers)
        
        print(f"[APIClient] {method} {url}")
        response = requests.request(method, url, json=data, headers=req_headers, params=params)
        response.raise_for_status()
        return response.json()