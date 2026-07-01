"""
Message Processor - Traite les messages du groupe et exécute les actions.
Utilise le RuleEngine pour détecter et apprendre automatiquement.
"""

from typing import Dict, Optional
from rule_engine import get_rule_engine, MessageExtractor
from config import CONFIDENCE_THRESHOLDS, BASE_URL
from services.api_client import APIClient
from services.browser import async_screenshot_with_token


class MessageProcessor:
    """Traite les messages et exécute les actions correspondantes."""
    
    def __init__(self, api_client: Optional[APIClient] = None):
        """Initialise le processeur."""
        self.rule_engine = get_rule_engine()
        self.api_client = api_client or APIClient(base_url=BASE_URL)
        self.pending_validations = {}  # {message_id: {action_details}}
    
    async def process_message(self, message: str, sender: str, message_id: int) -> Dict:
        """
        Traite un message reçu.
        
        Retourne un dictionnaire avec:
        {
            'processed': bool,
            'confidence': float,
            'action': str,
            'target_type': str,
            'identifier': str,
            'status': str,  # 'executed' | 'pending_confirmation' | 'ignored'
            'response': str,  # Message de réponse
            'error': str  # Si erreur
        }
        """
        result = {
            'processed': False,
            'confidence': 0.0,
            'action': None,
            'target_type': None,
            'identifier': None,
            'status': 'ignored',
            'response': None,
            'error': None
        }
        
        # Étape 1: Chercher une règle correspondante
        match = self.rule_engine.find_best_match(message)
        
        if not match:
            result['response'] = "Je n'ai pas compris ce message."
            return result
        
        rule, confidence = match
        result['confidence'] = confidence
        
        # Étape 2: Extraire les composants
        components = MessageExtractor.extract_components(message)
        result['action'] = components['action']
        result['target_type'] = components['target_type']
        result['identifier'] = components['identifier']
        result['processed'] = True
        
        # Étape 3: Valider les composants
        if not all([components['action'], components['target_type'], components['identifier']]):
            result['status'] = 'ignored'
            result['response'] = (
                f"Message détecté mais incomplet.\n"
                f"Format attendu: <action> <type> <identifiant>\n"
                f"Exemple: activate platform Wangpai"
            )
            return result
        
        # Étape 4: Vérifier les seuils de confiance
        if confidence >= CONFIDENCE_THRESHOLDS['auto_execute']:
            # Exécution directe
            result['status'] = 'executed'
            response = await self._execute_action(
                action=components['action'],
                target_type=components['target_type'],
                identifier=components['identifier'],
                sender=sender,
                message=message
            )
            result['response'] = response
            
            # Apprendre du succès
            if 'erreur' not in response.lower() and 'error' not in response.lower():
                self.rule_engine.add_learned_message(
                    message=message,
                    action=components['action'],
                    target_type=components['target_type'],
                    identifier=components['identifier'],
                    sender=sender,
                    status='success'
                )
        
        elif confidence >= CONFIDENCE_THRESHOLDS['ask_confirmation']:
            # Demander confirmation
            result['status'] = 'pending_confirmation'
            result['response'] = (
                f"⚠️ Confiance: {confidence:.0%}\n\n"
                f"Action détectée:\n"
                f"  • Action: {components['action'].upper()}\n"
                f"  • Type: {components['target_type'].upper()}\n"
                f"  • Cible: {components['identifier']}\n\n"
                f"Confirmez avec /validate ou /cancel"
            )
            
            # Sauvegarder pour validation
            self.pending_validations[message_id] = {
                'message': message,
                'action': components['action'],
                'target_type': components['target_type'],
                'identifier': components['identifier'],
                'sender': sender,
                'confidence': confidence
            }
        
        else:
            # Confiance trop basse
            result['status'] = 'ignored'
            result['response'] = (
                f"Confiance trop basse ({confidence:.0%}).\n"
                f"Utilisez le format explicite: /active <ID>"
            )
        
        return result
    
    async def _execute_action(self, action: str, target_type: str, 
                             identifier: str, sender: str, message: str) -> str:
        """
        Exécute l'action (activate/deactivate).
        Retourne le message de réponse.
        """
        try:
            # Mapper l'action aux endpoints API
            api_action = "active" if action == "activate" else "inactive"
            
            # Appel API
            if target_type == "platform":
                response = await self._activate_platform(identifier, api_action)
            elif target_type == "channel":
                response = await self._activate_channel(identifier, api_action)
            else:
                return f"❌ Type de cible non supporté: {target_type}"
            
            if response.get('success'):
                return (
                    f"✅ {action.upper()} effectué avec succès!\n"
                    f"  • {target_type.upper()}: {identifier}\n"
                    f"  • Status: {response.get('status', 'OK')}\n"
                    f"  • Exécuteur: @{sender}"
                )
            else:
                return f"❌ Erreur: {response.get('error', 'Erreur inconnue')}"
        
        except Exception as e:
            return f"❌ Erreur lors de l'exécution: {str(e)}"
    
    async def _activate_platform(self, platform_id: str, action: str) -> Dict:
        """
        Active ou désactive une plateforme via l'API.
        """
        try:
            # Appel API (endpoint à adapter selon votre API)
            endpoint = f"/platform/{platform_id}/{action}"
            response = self.api_client.call_api(endpoint, method='POST', data={})
            
            return {
                'success': True,
                'status': action.upper()
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _activate_channel(self, channel_id: str, action: str) -> Dict:
        """
        Active ou désactive un canal via l'API.
        """
        try:
            # Appel API (endpoint à adapter selon votre API)
            endpoint = f"/channel/{channel_id}/{action}"
            response = self.api_client.call_api(endpoint, method='POST', data={})
            
            return {
                'success': True,
                'status': action.upper()
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def validate_pending(self, message_id: int) -> str:
        """
        Valide une action en attente de confirmation.
        """
        if message_id not in self.pending_validations:
            return "❌ Aucune action en attente à valider."
        
        details = self.pending_validations.pop(message_id)
        
        response = await self._execute_action(
            action=details['action'],
            target_type=details['target_type'],
            identifier=details['identifier'],
            sender=details['sender'],
            message=details['message']
        )
        
        # Apprendre du succès
        self.rule_engine.add_learned_message(
            message=details['message'],
            action=details['action'],
            target_type=details['target_type'],
            identifier=details['identifier'],
            sender=details['sender'],
            status='success'
        )
        
        return response
    
    async def cancel_pending(self, message_id: int) -> str:
        """
        Annule une action en attente de confirmation.
        """
        if message_id not in self.pending_validations:
            return "❌ Aucune action en attente à annuler."
        
        details = self.pending_validations.pop(message_id)
        
        # Apprendre du rejet
        decrement = CONFIDENCE_THRESHOLDS.get('reject_decrement', 0.05)
        
        return (
            f"❌ Action annulée:\n"
            f"  • {details['action'].upper()} {details['target_type']}\n"
            f"  • Cible: {details['identifier']}"
        )
    
    def get_stats(self) -> Dict:
        """Retourne les statistiques du processeur."""
        return {
            'pending_validations': len(self.pending_validations),
            'rule_engine_stats': self.rule_engine.get_rules_stats()
        }
