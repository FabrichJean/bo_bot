"""
Rule Engine - Moteur de détection et d'apprentissage des messages.
Système évolutif qui apprend à partir des messages validés.
"""

import json
import os
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from difflib import SequenceMatcher
from config import (
    MESSAGE_RULES_FILE,
    LEARNING_HISTORY_FILE,
    CONFIDENCE_THRESHOLDS,
    LEARNING_CONFIG,
    SUPPORTED_ACTIONS,
    SUPPORTED_TARGET_TYPES
)


class MessageExtractor:
    """Extrait les composants d'un message."""
    
    @staticmethod
    def extract_action(message: str) -> Optional[str]:
        """
        Extrait l'action (activate/deactivate) du message.
        Retourne le type d'action ou None.
        """
        message_lower = message.lower()
        
        for action_type, keywords in SUPPORTED_ACTIONS.items():
            for keyword in keywords:
                if keyword in message_lower:
                    return action_type
        
        return None
    
    @staticmethod
    def extract_target_type(message: str) -> Optional[str]:
        """
        Extrait le type de cible (platform/channel) du message.
        Retourne le type ou None.
        """
        message_lower = message.lower()
        
        for target_type, keywords in SUPPORTED_TARGET_TYPES.items():
            for keyword in keywords:
                if keyword in message_lower:
                    return target_type
        
        return None
    
    @staticmethod
    def extract_identifier(message: str) -> Optional[str]:
        """
        Extrait l'identifiant (nom ou ID) de la cible.
        Cherche: "ID:123", "ID 123", ou simplement le nom avant "platform"/"channel".
        """
        # Chercher les patterns ID:123 ou ID 123
        id_pattern = r'(?:ID|id)[:\s]+(\w+)'
        match = re.search(id_pattern, message)
        if match:
            return match.group(1)
        
        # Chercher les mots après "platform" ou "channel"
        words = message.split()
        for i, word in enumerate(words):
            if word.lower() in ['platform', 'channel', 'plateforme', 'canal']:
                if i + 1 < len(words):
                    # Retourner le prochain mot (en enlevant la ponctuation)
                    identifier = re.sub(r'[^\w]', '', words[i + 1])
                    if identifier:
                        return identifier
        
        # Chercher les mots AVANT "platform" ou "channel" si pas après
        for i, word in enumerate(words):
            if word.lower() in ['platform', 'channel', 'plateforme', 'canal']:
                if i > 0:
                    # Chercher le mot significatif avant
                    for j in range(i - 1, -1, -1):
                        candidate = re.sub(r'[^\w]', '', words[j])
                        # Ignorer les articles et prépositions
                        if candidate.lower() not in ['the', 'a', 'an', 'le', 'la', 'l', 'de', 'du', 'des', 'on', 'off', 'turn', 'activate', 'deactivate', 'enable', 'disable']:
                            return candidate
        
        return None
    
    @staticmethod
    def extract_components(message: str) -> Dict:
        """
        Extrait tous les composants du message.
        Retourne un dictionnaire avec action, target_type, identifier.
        """
        return {
            'action': MessageExtractor.extract_action(message),
            'target_type': MessageExtractor.extract_target_type(message),
            'identifier': MessageExtractor.extract_identifier(message),
            'original_message': message
        }


class RuleEngine:
    """Moteur de règles avec apprentissage."""
    
    def __init__(self):
        """Initialise le moteur avec les règles sauvegardées."""
        self.rules = []
        self.learning_history = []
        self.load_rules()
    
    def load_rules(self):
        """Charge les règles depuis le fichier JSON."""
        if os.path.exists(MESSAGE_RULES_FILE):
            try:
                with open(MESSAGE_RULES_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.rules = data.get('rules', [])
                    self.learning_history = data.get('learning_history', [])
                    print(f"[RuleEngine] {len(self.rules)} règles chargées")
            except Exception as e:
                print(f"[RuleEngine] Erreur chargement règles: {e}")
                self.rules = []
                self.learning_history = []
        else:
            print(f"[RuleEngine] {MESSAGE_RULES_FILE} n'existe pas, création...")
            self._create_default_rules()
            self.save_rules()
    
    def _create_default_rules(self):
        """Crée les règles par défaut au premier lancement."""
        self.rules = [
            {
                "id": "activate_platform",
                "pattern": "{action} platform {platform_name}",
                "keywords": ["activate", "enable", "turn on", "on"],
                "action": "activate",
                "target_type": "platform",
                "confidence": 0.85,
                "examples": ["activate platform Wangpai", "enable platform Jincheng"],
                "learned_from": datetime.now().isoformat(),
                "validation_count": 0
            },
            {
                "id": "deactivate_platform",
                "pattern": "{action} platform {platform_name}",
                "keywords": ["deactivate", "disable", "turn off", "off"],
                "action": "deactivate",
                "target_type": "platform",
                "confidence": 0.85,
                "examples": ["deactivate platform Wangpai", "disable platform Jincheng"],
                "learned_from": datetime.now().isoformat(),
                "validation_count": 0
            },
            {
                "id": "activate_channel",
                "pattern": "{action} channel {channel_id}",
                "keywords": ["activate", "enable", "turn on", "on"],
                "action": "activate",
                "target_type": "channel",
                "confidence": 0.85,
                "examples": ["activate channel 156", "enable channel ID:156"],
                "learned_from": datetime.now().isoformat(),
                "validation_count": 0
            },
            {
                "id": "deactivate_channel",
                "pattern": "{action} channel {channel_id}",
                "keywords": ["deactivate", "disable", "turn off", "off"],
                "action": "deactivate",
                "target_type": "channel",
                "confidence": 0.85,
                "examples": ["deactivate channel 156", "disable channel ID:156"],
                "learned_from": datetime.now().isoformat(),
                "validation_count": 0
            }
        ]
    
    def save_rules(self):
        """Sauvegarde les règles dans le fichier JSON."""
        try:
            data = {
                'rules': self.rules,
                'learning_history': self.learning_history,
                'last_updated': datetime.now().isoformat()
            }
            with open(MESSAGE_RULES_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[RuleEngine] Erreur sauvegarde règles: {e}")
    
    def _calculate_keyword_match(self, message: str, rule: Dict) -> float:
        """
        Calcule le score de correspondance des keywords.
        Retourne un score entre 0.0 et 1.0.
        """
        message_lower = message.lower()
        keywords = rule.get('keywords', [])
        
        if not keywords:
            return 0.0
        
        # Compter le nombre de keywords trouvés
        matches = sum(1 for kw in keywords if kw in message_lower)
        
        # Score: au moins 1 keyword trouvé = 0.8, tous = 1.0
        # Formule: 0.7 + (matches / len(keywords)) * 0.3
        return min(1.0, 0.7 + (matches / len(keywords)) * 0.3)
    
    def _calculate_pattern_similarity(self, message: str, rule: Dict) -> float:
        """
        Calcule la similarité entre le message et le pattern.
        Utilise SequenceMatcher pour une comparaison flexible.
        """
        pattern = rule.get('pattern', '')
        # Enlever les placeholders pour la comparaison
        pattern_cleaned = re.sub(r'\{[^}]+\}', '', pattern).lower()
        message_lower = message.lower()
        
        similarity = SequenceMatcher(None, pattern_cleaned, message_lower).ratio()
        return similarity
    
    def _calculate_recency_factor(self, rule: Dict) -> float:
        """
        Calcule un facteur de recentité basé sur la date d'apprentissage.
        Les règles récentes ont un boost, les anciennes un malus.
        """
        try:
            learned_at = datetime.fromisoformat(rule.get('learned_from', ''))
            days_ago = (datetime.now() - learned_at).days
            
            # Boost pour les règles récentes (0-7 jours)
            # Malus pour les anciennes
            if days_ago <= 7:
                return 1.0 + (0.05 * (7 - days_ago) / 7)  # Max +5%
            else:
                return max(0.8, 1.0 - (0.05 * min(days_ago / 30, 1.0)))  # Min 80%
        except:
            return 1.0
    
    def _calculate_validation_boost(self, rule: Dict) -> float:
        """
        Calcule un boost basé sur le nombre de validations.
        Chaque validation augmente la confiance.
        """
        validation_count = rule.get('validation_count', 0)
        # Chaque validation = +1% de boost (max 15%)
        return min(1.15, 1.0 + (validation_count * 0.01))
    
    def _calculate_confidence(self, message: str, rule: Dict) -> float:
        """
        Calcule le score de confiance total pour une règle.
        
        Score = (keyword_match * 0.4 + pattern_similarity * 0.3 + 
                 (validation_count / 10) * 0.2 + recency * 0.1) * validation_boost
        """
        keyword_score = self._calculate_keyword_match(message, rule) * 0.4
        pattern_score = self._calculate_pattern_similarity(message, rule) * 0.3
        validation_score = min(rule.get('validation_count', 0) / 10, 1.0) * 0.2
        recency_score = self._calculate_recency_factor(rule) * 0.1
        
        base_confidence = keyword_score + pattern_score + validation_score + recency_score
        validation_boost = self._calculate_validation_boost(rule)
        
        final_confidence = base_confidence * validation_boost
        return min(1.0, final_confidence)  # Capped at 1.0
    
    def find_matching_rules(self, message: str) -> List[Tuple[Dict, float]]:
        """
        Trouve toutes les règles correspondant au message.
        Retourne une liste de (rule, confidence) triée par confiance décroissante.
        """
        matches = []
        
        # Vérifier que le message contient au moins une action et un type
        components = MessageExtractor.extract_components(message)
        if not components['action'] or not components['target_type']:
            return matches  # Aucun match si composants manquants
        
        for rule in self.rules:
            # Vérifier que la règle correspond à l'action ET au type
            if rule['action'] != components['action'] or rule['target_type'] != components['target_type']:
                continue
            
            confidence = self._calculate_confidence(message, rule)
            if confidence > 0.5:  # Seuil minimum
                matches.append((rule, confidence))
        
        # Trier par confiance décroissante
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches
    
    def find_best_match(self, message: str) -> Optional[Tuple[Dict, float]]:
        """
        Trouve la meilleure règle correspondant au message.
        Retourne (rule, confidence) ou None si aucune match.
        """
        matches = self.find_matching_rules(message)
        return matches[0] if matches else None
    
    def add_learned_message(self, message: str, action: str, target_type: str, 
                          identifier: str, sender: str, status: str = "success"):
        """
        Ajoute un message validé à l'historique d'apprentissage.
        Met à jour la confiance des règles correspondantes.
        """
        # Ajouter à l'historique
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "action": action,
            "target_type": target_type,
            "identifier": identifier,
            "sender": sender,
            "status": status
        }
        self.learning_history.append(history_entry)
        
        # Trouver les règles correspondantes et augmenter leur confiance
        matches = self.find_matching_rules(message)
        
        if matches:
            best_match_rule = matches[0][0]
            
            # Augmenter la confiance et le validation_count
            increment = LEARNING_CONFIG['confidence_increment']
            for rule in self.rules:
                if rule['id'] == best_match_rule['id']:
                    rule['confidence'] = min(
                        1.0, 
                        rule['confidence'] + increment
                    )
                    rule['validation_count'] = rule.get('validation_count', 0) + 1
                    
                    # Ajouter l'exemple si pas encore présent
                    if message not in rule.get('examples', []):
                        examples = rule.get('examples', [])
                        if len(examples) < LEARNING_CONFIG['max_examples_per_rule']:
                            examples.append(message)
                            rule['examples'] = examples
                    
                    print(f"[RuleEngine] Règle '{rule['id']}' mise à jour. "
                          f"Confiance: {rule['confidence']:.2f}, "
                          f"Validations: {rule['validation_count']}")
                    break
        else:
            # Créer une nouvelle règle si aucune correspondance
            self._create_new_rule_from_message(message, action, target_type, identifier)
        
        self.save_rules()
    
    def _create_new_rule_from_message(self, message: str, action: str, 
                                     target_type: str, identifier: str):
        """
        Crée une nouvelle règle basée sur un message validé.
        La nouvelle règle commence avec une confiance de 0.70.
        """
        rule_id = f"{action}_{target_type}_{len(self.rules)}"
        
        new_rule = {
            "id": rule_id,
            "pattern": f"{action} {target_type} {identifier}",
            "keywords": [action],
            "action": action,
            "target_type": target_type,
            "confidence": 0.70,  # Nouvelle règle = confiance moyenne
            "examples": [message],
            "learned_from": datetime.now().isoformat(),
            "validation_count": 1
        }
        
        self.rules.append(new_rule)
        print(f"[RuleEngine] Nouvelle règle créée: '{rule_id}' "
              f"(confiance: 0.70)")
    
    def get_learning_history(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Retourne l'historique d'apprentissage.
        Paramètre limit: None = tout, sinon les N derniers.
        """
        if limit:
            return self.learning_history[-limit:]
        return self.learning_history
    
    def get_rules_stats(self) -> Dict:
        """Retourne des statistiques sur les règles."""
        return {
            "total_rules": len(self.rules),
            "total_history": len(self.learning_history),
            "average_confidence": sum(r['confidence'] for r in self.rules) / len(self.rules) if self.rules else 0,
            "total_validations": sum(r.get('validation_count', 0) for r in self.rules),
            "rules": [
                {
                    "id": r['id'],
                    "confidence": r['confidence'],
                    "validation_count": r.get('validation_count', 0),
                    "examples_count": len(r.get('examples', []))
                }
                for r in self.rules
            ]
        }


# Singleton global
_rule_engine = None

def get_rule_engine() -> RuleEngine:
    """Retourne l'instance globale du RuleEngine."""
    global _rule_engine
    if _rule_engine is None:
        _rule_engine = RuleEngine()
    return _rule_engine
