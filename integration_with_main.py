#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Guide d'intégration du système de test/feedback avec main.py

Ce module montre comment:
1. Faire des prédictions avec le modèle
2. Collecter les retours utilisateur
3. Réentraîner le modèle automatiquement
"""

from rule_engine import RuleEngine, MessageExtractor
from data_annotator import DataAnnotator
import json
import time
from datetime import datetime

class ModelTesterIntegration:
    """Intégration du testeur de modèle avec le système principal"""
    
    def __init__(self):
        """Initialise le système"""
        self.engine = RuleEngine()
        self.engine.load_rules()
        
        self.annotator = DataAnnotator()
        
        # Historique des tests
        self.test_history = []
        self.load_test_history()
    
    def load_test_history(self):
        """Charge l'historique des tests"""
        try:
            with open("test_feedback.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                self.test_history = data.get("feedback", [])
        except FileNotFoundError:
            self.test_history = []
    
    def save_test_history(self):
        """Sauvegarde l'historique des tests"""
        with open("test_feedback.json", "w", encoding="utf-8") as f:
            json.dump({"feedback": self.test_history}, f, ensure_ascii=False, indent=2)
    
    def test_message(self, message: str) -> dict:
        """
        Teste un message et retourne la prédiction du modèle
        
        Args:
            message: Message à tester
            
        Returns:
            dict avec action, target_type, identifier, confidence
        """
        result = MessageExtractor.extract_components(message)
        
        if result:
            test_id = f"test_{len(self.test_history)}_{int(time.time())}"
            return {
                "success": True,
                "test_id": test_id,
                "message": message,
                "result": result,
                "action": result.get("action"),
                "target_type": result.get("target_type"),
                "identifier": result.get("identifier"),
                "confidence": result.get("confidence", 0.5)
            }
        else:
            return {
                "success": False,
                "message": message,
                "error": "Aucune prédiction disponible"
            }
    
    def record_feedback(self, test_id: str, message: str, verdict: str,
                       corrected_action = None,
                       corrected_type = None,
                       corrected_id = None) -> dict:
        """
        Enregistre le retour utilisateur et réentraîne le modèle
        
        Args:
            test_id: ID du test
            message: Message testé
            verdict: "correct" | "corrected" | "wrong"
            corrected_action: Action correcte (si corrected)
            corrected_type: Type cible correct (si corrected)
            corrected_id: Identifiant correct (si corrected)
            
        Returns:
            dict avec résultat de l'entraînement
        """
        feedback_entry = {
            "test_id": test_id,
            "message": message,
            "user_verdict": verdict,
            "corrected_action": corrected_action,
            "corrected_target_type": corrected_type,
            "corrected_identifier": corrected_id,
            "timestamp": datetime.now().isoformat()
        }
        
        # Enregistrer le feedback
        self.test_history.append(feedback_entry)
        self.save_test_history()
        
        # Réentraîner le modèle
        if verdict != "wrong":
            self._train_model_from_feedback(feedback_entry)
        
        return {
            "success": True,
            "message": f"Feedback enregistré: {verdict}",
            "feedback_used_for_training": verdict != "wrong"
        }
    
    def _train_model_from_feedback(self, feedback_entry: dict):
        """
        Entraîne le modèle avec le feedback utilisateur
        
        Améliore les règles existantes ou en ajoute de nouvelles
        """
        verdict = feedback_entry.get("user_verdict")
        message = feedback_entry.get("message", "")
        corrected_action = feedback_entry.get("corrected_action")
        corrected_type = feedback_entry.get("corrected_target_type")
        corrected_id = feedback_entry.get("corrected_identifier")
        
        # Chercher les règles qui correspondent
        matching_rules = self.engine.find_matching_rules(message)
        
        if verdict == "correct":
            # Le modèle était correct - augmenter la confiance
            for rule, _ in matching_rules:
                if rule.get("action") == corrected_action:
                    rule["confidence"] = min(1.0, rule["confidence"] + 0.03)
                    if message not in rule.get("examples", []):
                        if "examples" not in rule:
                            rule["examples"] = []
                        rule["examples"].append(message)
        
        elif verdict == "corrected":
            # L'utilisateur a corrigé - augmenter légèrement
            for rule, _ in matching_rules:
                if rule.get("action") == corrected_action:
                    rule["confidence"] = min(1.0, rule["confidence"] + 0.02)
                    if message not in rule.get("examples", []):
                        if "examples" not in rule:
                            rule["examples"] = []
                        rule["examples"].append(message)
            
            # Ajouter à l'historique des annotations
            if "annotated_messages" not in self.annotator.annotations:
                self.annotator.annotations["annotated_messages"] = []
            
            self.annotator.annotations["annotated_messages"].append({
                "message": message,
                "action": corrected_action,
                "target_type": corrected_type,
                "identifier": corrected_id,
                "timestamp": datetime.now().isoformat()
            })
        
        # Sauvegarder les règles améliorées
        self.engine.save_rules()

# EXEMPLE D'UTILISATION:
def example_usage():
    """Exemple d'utilisation du système de test/feedback"""
    
    print("\n" + "="*60)
    print("  EXEMPLE D'INTÉGRATION")
    print("="*60)
    
    tester = ModelTesterIntegration()
    
    # Test 1: Message simple
    message = "启用 Wangpai 平台"
    print(f"\n1️⃣ Test du message: '{message}'")
    
    prediction = tester.test_message(message)
    print(f"   Prédiction: {prediction['result']}")
    print(f"   Confiance: {prediction['confidence']*100:.1f}%")
    
    # Enregistrer le feedback
    test_id = prediction["test_id"]
    feedback = tester.record_feedback(
        test_id=test_id,
        message=message,
        verdict="correct",
        corrected_action="activate",
        corrected_type="platform",
        corrected_id="Wangpai"
    )
    print(f"   Feedback enregistré: {feedback['message']}")
    
    # Test 2: Autre message
    message2 = "关闭 ID:156 频道"
    print(f"\n2️⃣ Test du message: '{message2}'")
    
    prediction2 = tester.test_message(message2)
    print(f"   Prédiction: {prediction2['result']}")
    print(f"   Confiance: {prediction2['confidence']*100:.1f}%")
    
    # Enregistrer une correction
    test_id2 = prediction2["test_id"]
    feedback2 = tester.record_feedback(
        test_id=test_id2,
        message=message2,
        verdict="corrected",
        corrected_action="deactivate",
        corrected_type="channel",
        corrected_id="156"
    )
    print(f"   Feedback enregistré: {feedback2['message']}")
    
    # Afficher les statistiques
    print(f"\n📊 Statistiques:")
    print(f"   Tests effectués: {len(tester.test_history)}")
    
    correct_count = sum(1 for f in tester.test_history if f['user_verdict'] == 'correct')
    corrected_count = sum(1 for f in tester.test_history if f['user_verdict'] == 'corrected')
    wrong_count = sum(1 for f in tester.test_history if f['user_verdict'] == 'wrong')
    
    print(f"   Correct: {correct_count}")
    print(f"   Corrigés: {corrected_count}")
    print(f"   Faux: {wrong_count}")
    
    if len(tester.test_history) > 0:
        accuracy = (correct_count + corrected_count) / len(tester.test_history) * 100
        print(f"   Taux de succès: {accuracy:.1f}%")
    
    print("\n" + "="*60)

# UTILISATION DANS main.py:
"""
EXEMPLE DE COMMENT INTÉGRER DANS main.py:

from integration_with_main import ModelTesterIntegration

# Initialiser une fois au démarrage
model_tester = ModelTesterIntegration()

# Dans un gestionnaire de groupe:
@client.on(events.NewMessage(chats=YOUR_GROUP_ID))
async def handle_message(event):
    message = event.message.text
    
    # Faire une prédiction
    prediction = model_tester.test_message(message)
    
    if prediction['success']:
        action = prediction['action']
        target_type = prediction['target_type']
        identifier = prediction['identifier']
        confidence = prediction['confidence']
        
        # Envoyer la prédiction au groupe
        await event.reply(
            f"🤖 Prédiction:\\n"
            f"Action: {action}\\n"
            f"Type: {target_type}\\n"
            f"Identifiant: {identifier}\\n"
            f"Confiance: {confidence*100:.1f}%\\n\\n"
            f"Correct? ✅ / ✏️ / ❌"
        )
        
        # Garder l'ID du test pour recueillir le feedback
        # Ensuite, traiter les reactions/réponses pour enregistrer le verdict
        
        @client.on(events.MessageReactionUpdated())
        async def handle_reaction(react_event):
            # Récupérer le verdict
            if react_event.reaction == "✅":
                verdict = "correct"
            elif react_event.reaction == "✏️":
                verdict = "corrected"
            else:
                verdict = "wrong"
            
            # Enregistrer le feedback
            model_tester.record_feedback(
                test_id=prediction['test_id'],
                message=message,
                verdict=verdict
            )
"""

if __name__ == "__main__":
    example_usage()
