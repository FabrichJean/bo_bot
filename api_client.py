import requests
import json
from typing import Optional, Dict, Any


class APIClient:
    """Client API pour faire des appels authentifiés avec JWT Bearer token."""
    
    def __init__(self, base_url: str, token: Optional[str] = None):
        """
        Initialise le client API.
        :param base_url: URL de base de l'API (ex: https://xo-back.99sq20.fun)
        :param token: Token JWT optionnel
        """
        self.base_url = base_url.rstrip('/')  # Enlever le slash final s'il existe
        self.token = token
    
    def call_api(self, endpoint: str, method: str = 'GET', data: Optional[Dict[str, Any]] = None, 
                 headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None, 
                 token: Optional[str] = None) -> Dict[str, Any]:
        """
        Fait un appel API avec authentification Bearer.
        :param endpoint: Point de terminaison API (ex: /payment/platforms/all)
        :param method: Méthode HTTP (GET, POST, PUT, DELETE, etc.)
        :param data: Données à envoyer (pour POST/PUT)
        :param headers: Headers additionnels
        :param params: Paramètres de requête
        :param token: Token à utiliser (sinon utilise self.token)
        :return: Réponse JSON
        """
        # Utiliser le token fourni en paramètre ou celui de l'instance
        bearer_token = token or self.token
        
        if not bearer_token:
            raise ValueError("Aucun token fourni pour l'authentification")
        
        # Construire l'URL complète
        url = f"{self.base_url}{endpoint}"
        
        # Préparer les headers avec Bearer token
        req_headers = headers or {}
        req_headers['Authorization'] = f'Bearer {bearer_token}'
        req_headers['Content-Type'] = 'application/json'
        
        response = None
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=req_headers, params=params)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=req_headers, json=data, params=params)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=req_headers, json=data, params=params)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=req_headers, params=params)
            else:
                raise ValueError(f"Méthode HTTP non supportée: {method}")
            
            # Vérifier le statut de la réponse
            response.raise_for_status()
            
            # Retourner la réponse JSON
            return response.json()
        
        except requests.exceptions.RequestException as e:
            print(f"[ERREUR API] {method} {url}: {e}")
            return {'code': 500, 'message': str(e), 'data': None}
        except json.JSONDecodeError:
            if response:
                print(f"[ERREUR API] Réponse non-JSON: {response.text}")
                return {'code': 500, 'message': 'Réponse non-JSON', 'data': response.text}
            return {'code': 500, 'message': 'Erreur de décodage JSON', 'data': None}

